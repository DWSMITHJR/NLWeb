from typing import List, Dict, Any, Optional, Tuple, Union
import random
import time
import json
import os
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.models import (
    Document,
    DocumentProcessorConfig,
    ChunkingStrategy,
    DocumentChunk,
)
from backend.document_processor import DocumentProcessor
from backend.prompt_templates import PromptTemplateManager, TemplateType, PromptTemplate
from backend.automl.retrievers.base import BaseRetriever
from backend.automl.retrievers.faiss_retriever import FAISSRetriever
from backend.automl.retrievers.bm25_retriever import BM25Retriever
from backend.automl.retrievers.hybrid_retriever import HybridRetriever
from backend.evaluation import RetrievalMetrics, AnswerQualityMetrics, EvaluationResult


class AutoMLOrchestrator:
    """Orchestrates the AutoML process for optimizing RAG components."""

    def __init__(self, output_dir: str = "automl_results", max_workers: int = 4):
        """
        Initializes the AutoMLOrchestrator.

        Args:
            output_dir: The directory to save the AutoML results.
            max_workers: The maximum number of parallel workers to use for evaluation.
        """
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.results = []
        self.best_config = None
        self.best_score = -float("inf")

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _create_retriever(self, config: Dict[str, Any]) -> BaseRetriever:
        """Creates a retriever instance based on the given configuration."""
        retriever_type = config.get("retriever_type", "faiss")

        if retriever_type == "faiss":
            return FAISSRetriever(
                model_name=config.get(
                    "embedding_model", "sentence-transformers/all-MiniLM-L6-v2"
                ),
                normalize_embeddings=config.get("normalize_embeddings", True),
            )
        elif retriever_type == "bm25":
            from .retrievers.bm25_retriever import BM25Retriever

            return BM25Retriever()
        elif retriever_type == "hybrid":
            from .retrievers.hybrid_retriever import HybridRetriever

            return HybridRetriever(
                bm25_weight=config.get("bm25_weight", 0.5),
                faiss_weight=config.get("faiss_weight", 0.5),
                faiss_model_name=config.get(
                    "embedding_model", "sentence-transformers/all-MiniLM-L6-v2"
                ),
                normalize_embeddings=config.get("normalize_embeddings", True),
            )
        else:
            raise ValueError(f"Unsupported retriever type: {retriever_type}")

    def _create_processor_config(
        self, config: Dict[str, Any]
    ) -> DocumentProcessorConfig:
        """Creates a DocumentProcessorConfig instance from the configuration."""
        return DocumentProcessorConfig(
            chunk_size=config.get("chunk_size", 256),
            chunk_overlap=config.get("chunk_overlap", 50),
            chunking_strategy=ChunkingStrategy(
                config.get("chunking_strategy", "fixed")
            ),
        )

    def _evaluate_retrieval(
        self,
        retriever: BaseRetriever,
        test_queries: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Evaluates the retrieval performance of a given retriever.

        Args:
            retriever: The retriever to evaluate.
            test_queries: A list of test queries with relevant document IDs.
            top_k: The number of documents to retrieve per query.

        Returns:
            A dictionary containing detailed and mean retrieval metrics.
        """
        metrics = []

        for query_data in test_queries:
            query = query_data["query"]
            relevant_docs = query_data.get("relevant_docs", [])

            # Get retrieved documents
            retrieved = retriever.retrieve(query, top_k=top_k)

            # Convert to DocumentChunk format for evaluation
            retrieved_chunks = [
                DocumentChunk(
                    id=doc["document"]["id"],
                    document_id=doc["document"]["id"],
                    content=doc["document"]["content"],
                    metadata=doc["document"].get("metadata", {}),
                    chunk_index=0,  # Default chunk index
                    chunk_strategy=ChunkingStrategy.FIXED  # Default chunking strategy
                )
                for doc in retrieved
            ]

            relevant_chunks = [
                DocumentChunk(
                    id=doc["id"],
                    document_id=doc["id"],
                    content=doc["content"],
                    metadata=doc.get("metadata", {}),
                    chunk_index=0,  # Default chunk index
                    chunk_strategy=ChunkingStrategy.FIXED  # Default chunking strategy
                )
                for doc in relevant_docs
            ]

            # Calculate metrics
            metrics.append(
                {
                    "query": query,
                    **RetrievalMetrics.calculate_precision_recall(
                        retrieved_chunks, relevant_chunks, k=top_k
                    ),
                    "mrr": RetrievalMetrics.calculate_mrr(
                        retrieved_chunks, relevant_chunks
                    ),
                }
            )

        # Calculate mean metrics
        mean_metrics = {}
        for metric in ["precision", "recall", "f1", "mrr"]:
            values = [m[metric] for m in metrics if metric in m]
            if values:
                mean_metrics[f"mean_{metric}"] = float(np.mean(values))
                mean_metrics[f"std_{metric}"] = float(np.std(values))

        return {"metrics": metrics, "mean_metrics": mean_metrics}

    def _evaluate_answer_quality(
        self,
        retriever: BaseRetriever,
        test_queries: List[Dict[str, Any]],
        template: PromptTemplate,
        top_k: int = 5,
    ) -> Dict[str, float]:
        """
        Evaluates the answer quality for a given retriever and prompt template.

        Args:
            retriever: The retriever to use for context retrieval.
            test_queries: A list of test queries with reference answers.
            template: The prompt template to use for generating answers.
            top_k: The number of documents to retrieve for context.

        Returns:
            A dictionary of mean answer quality metrics.
        """
        metrics = {"rouge_1_f1": [], "rouge_2_f1": [], "bleu": []}

        for query_data in test_queries:
            if "reference_answer" not in query_data:
                continue

            query = query_data["query"]
            reference_answer = query_data["reference_answer"]

            # Retrieve relevant documents
            retrieved = retriever.retrieve(query, top_k=top_k)

            # Combine retrieved documents into context
            context = "\n\n".join([doc["document"]["content"] for doc in retrieved])

            # Format prompt
            prompt = template.format(question=query, context=context)

            # In a real implementation, you would call an LLM here to generate an answer
            # For now, we'll use a simple placeholder
            # TODO: Integrate with an actual LLM
            generated_answer = f"Generated answer for: {query}"

            # Calculate metrics
            if generated_answer and reference_answer:
                # ROUGE-1 F1
                rouge_1 = AnswerQualityMetrics.calculate_rouge(
                    generated_answer, reference_answer, n_gram=1
                )["rouge_1"]["f1"]

                # ROUGE-2 F1
                rouge_2 = AnswerQualityMetrics.calculate_rouge(
                    generated_answer, reference_answer, n_gram=2
                )["rouge_2"]["f1"]

                # BLEU
                bleu = AnswerQualityMetrics.calculate_bleu(
                    generated_answer, reference_answer
                )["bleu"]

                metrics["rouge_1_f1"].append(rouge_1)
                metrics["rouge_2_f1"].append(rouge_2)
                metrics["bleu"].append(bleu)

        # Calculate mean metrics
        mean_metrics = {}
        for metric, values in metrics.items():
            if values:
                mean_metrics[f"mean_{metric}"] = float(np.mean(values))
                mean_metrics[f"std_{metric}"] = float(np.std(values))

        return mean_metrics

    def _evaluate_configuration(
        self,
        config: Dict[str, Any],
        train_documents: List[Document],
        test_queries: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Evaluates a single RAG configuration.

        Args:
            config: The configuration to evaluate.
            train_documents: The documents to use for training the retriever.
            test_queries: The test queries for evaluation.

        Returns:
            A dictionary containing the evaluation results.
        """
        start_time = time.time()

        try:
            # Create and train retriever
            retriever = self._create_retriever(config)

            # Process documents with current configuration
            processor_config = self._create_processor_config(config)
            processor = DocumentProcessor(processor_config)

            # Add documents to retriever
            for doc in train_documents:
                # Process document into chunks
                chunks = processor.process_document(doc)

                # Add each chunk as a separate document to the retriever
                for chunk in chunks:
                    chunk_doc = Document(
                        id=chunk.id,
                        content=chunk.content,
                        metadata={
                            **chunk.metadata,
                            "chunk_index": chunk.chunk_index,
                            "document_id": chunk.document_id,
                        },
                    )
                    retriever.add_documents([chunk_doc])

            # Get prompt template
            prompt_manager = PromptTemplateManager()
            template_type = config.get("prompt_template", TemplateType.SIMPLE)

            try:
                template = prompt_manager.get_template(template_type)
                config["prompt_template"] = (
                    template.name
                )  # Store template name in config
            except ValueError:
                # If template not found, use default
                template = prompt_manager.get_template(TemplateType.SIMPLE)
                config["prompt_template"] = "simple"

            # Evaluate retrieval
            retrieval_results = self._evaluate_retrieval(
                retriever=retriever,
                test_queries=test_queries,
                top_k=config.get("top_k", 5),
            )

            # If we have reference answers, evaluate answer quality
            answer_metrics = {}
            if any("reference_answer" in q for q in test_queries):
                answer_metrics = self._evaluate_answer_quality(
                    retriever=retriever,
                    test_queries=test_queries,
                    template=template,
                    top_k=config.get("top_k", 5),
                )

            # Calculate overall score (weighted combination of metrics)
            mean_metrics = retrieval_results["mean_metrics"]

            # Base score on retrieval metrics
            retrieval_score = (
                0.4 * mean_metrics.get("mean_precision", 0)
                + 0.4 * mean_metrics.get("mean_recall", 0)
                + 0.2 * mean_metrics.get("mean_mrr", 0)
            )

            # If we have answer quality metrics, include them in the score
            if answer_metrics:
                answer_score = (
                    0.5 * answer_metrics.get("mean_rouge_1_f1", 0)
                    + 0.3 * answer_metrics.get("mean_rouge_2_f1", 0)
                    + 0.2 * answer_metrics.get("mean_bleu", 0)
                )
                # Weighted average of retrieval and answer quality scores
                score = 0.6 * retrieval_score + 0.4 * answer_score
            else:
                score = retrieval_score

            # Update best configuration if needed
            if score > self.best_score:
                self.best_score = score
                self.best_config = config

            # Prepare results
            result = {
                "config": config,
                "score": score,
                "retrieval_metrics": retrieval_results["mean_metrics"],
                "evaluation_time": time.time() - start_time,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Add answer quality metrics if available
            if answer_metrics:
                result["answer_metrics"] = answer_metrics

            return result

        except Exception as e:
            return {
                "config": config,
                "error": str(e),
                "evaluation_time": time.time() - start_time,
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _generate_configurations(
        self, base_config: Dict[str, Any], num_configs: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generates a list of configurations to test based on a search space.

        Args:
            base_config: A base configuration to build upon.
            num_configs: The number of random configurations to generate.

        Returns:
            A list of generated configurations.
        """
        # Get available prompt templates
        prompt_manager = PromptTemplateManager()
        available_templates = list(TemplateType)

        # Define search space
        search_space = {
            "retriever_type": ["faiss", "bm25", "hybrid"],
            "chunk_size": [128, 256, 512, 1024],
            "chunk_overlap": [0, 25, 50],
            "chunking_strategy": ["fixed", "sentence", "paragraph"],
            "embedding_model": [
                "sentence-transformers/all-MiniLM-L6-v2",
                "sentence-transformers/all-mpnet-base-v2",
                "sentence-transformers/multi-qa-mpnet-base-dot-v1",
            ],
            "normalize_embeddings": [True, False],
            "top_k": [3, 5, 10],
            # Hybrid-specific parameters
            "bm25_weight": [0.3, 0.5, 0.7],
            "faiss_weight": [0.3, 0.5, 0.7],
            # Prompt template parameters
            "prompt_template": [t.value for t in available_templates],
        }

        # Generate random configurations
        configs = []
        for _ in range(num_configs):
            config = base_config.copy()

            # Randomly sample from search space
            for param, values in search_space.items():
                if param not in config or param in [
                    "chunk_size",
                    "chunk_overlap",
                    "top_k",
                    "bm25_weight",
                    "faiss_weight",
                    "prompt_template",
                ]:
                    config[param] = random.choice(values)

            # Ensure chunk_overlap < chunk_size
            if config["chunk_overlap"] >= config["chunk_size"]:
                config["chunk_overlap"] = max(0, config["chunk_size"] - 10)

            # Ensure valid weights for hybrid retriever
            if config["retriever_type"] == "hybrid":
                # Ensure weights sum to 1.0
                total = config.get("bm25_weight", 0.5) + config.get("faiss_weight", 0.5)
                config["bm25_weight"] = config.get("bm25_weight", 0.5) / total
                config["faiss_weight"] = config.get("faiss_weight", 0.5) / total

            # Ensure prompt template is valid
            if "prompt_template" in config and config["prompt_template"] not in [
                t.value for t in available_templates
            ]:
                config["prompt_template"] = random.choice(
                    [t.value for t in available_templates]
                )

            configs.append(config)

        return configs

    def run(
        self,
        train_documents: List[Document],
        test_queries: List[Dict[str, Any]],
        base_config: Optional[Dict[str, Any]] = None,
        num_configs: int = 20,
        save_every: int = 5,
    ) -> Dict[str, Any]:
        """
        Runs the AutoML optimization process.

        Args:
            train_documents: The documents to use for training the retrievers.
            test_queries: The test queries for evaluation.
            base_config: A base configuration to build upon.
            num_configs: The number of configurations to test.
            save_every: The frequency at which to save intermediate results.

        Returns:
            A dictionary containing the best configuration, score, and all results.
        """
        if base_config is None:
            base_config = {}

        # Generate configurations to test
        configs = self._generate_configurations(base_config, num_configs)

        # Evaluate configurations in parallel
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self._evaluate_configuration, config, train_documents, test_queries
                ): i
                for i, config in enumerate(configs)
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)

                    # Save intermediate results
                    if len(results) % save_every == 0:
                        self._save_results(results)

                except Exception as e:
                    print(f"Error evaluating configuration: {e}")

        # Save final results
        self._save_results(results)

        # Find best configuration
        valid_results = [r for r in results if "score" in r]
        if valid_results:
            best_result = max(valid_results, key=lambda x: x["score"])
            self.best_config = best_result["config"]
            self.best_score = best_result["score"]

        return {
            "best_config": self.best_config,
            "best_score": self.best_score,
            "all_results": results,
        }

    def _save_results(self, results: List[Dict[str, Any]]) -> None:
        """Saves the evaluation results to a JSON file."""
        if not results:
            return

        # Create timestamped filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"automl_results_{timestamp}.json"

        # Save results
        with open(filename, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "results": results,
                    "best_config": self.best_config,
                    "best_score": self.best_score,
                },
                f,
                indent=2,
            )

        print(f"Saved results to {filename}")

    def get_best_config(self) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Returns the best configuration and score found so far.

        Returns:
            A tuple containing the best configuration and its score.
        """
        return self.best_config, self.best_score
