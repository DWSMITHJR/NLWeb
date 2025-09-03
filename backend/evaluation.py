from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
from .models import DocumentChunk

class RetrievalMetrics:
    """Class for calculating retrieval metrics"""
    
    @staticmethod
    def calculate_precision_recall(
        retrieved: List[DocumentChunk],
        relevant: List[DocumentChunk],
        k: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Calculate precision and recall at k
        
        Args:
            retrieved: List of retrieved document chunks
            relevant: List of relevant document chunks
            k: Number of top results to consider (None for all)
            
        Returns:
            Dictionary containing precision and recall metrics
        """
        if k is not None:
            retrieved = retrieved[:k]
            
        retrieved_ids = {chunk.id for chunk in retrieved}
        relevant_ids = {chunk.id for chunk in relevant}
        
        if not retrieved:
            return {
                'precision': 0.0,
                'recall': 0.0,
                'f1': 0.0
            }
            
        # Calculate true positives (retrieved AND relevant)
        tp = len(retrieved_ids & relevant_ids)
        
        precision = tp / len(retrieved_ids) if retrieved_ids else 0.0
        recall = tp / len(relevant_ids) if relevant_ids else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    @staticmethod
    def calculate_mrr(
        retrieved: List[DocumentChunk],
        relevant: List[DocumentChunk]
    ) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR)
        
        Args:
            retrieved: List of retrieved document chunks
            relevant: List of relevant document chunks
            
        Returns:
            MRR score
        """
        relevant_ids = {chunk.id for chunk in relevant}
        
        for rank, chunk in enumerate(retrieved, 1):
            if chunk.id in relevant_ids:
                return 1.0 / rank
                
        return 0.0

class AnswerQualityMetrics:
    """Class for calculating answer quality metrics"""
    
    @staticmethod
    def calculate_rouge(
        generated: str,
        reference: str,
        n_gram: int = 1
    ) -> Dict[str, float]:
        """
        Calculate ROUGE-N score (simplified version)
        
        Args:
            generated: Generated answer
            reference: Reference answer
            n_gram: N-gram size (1 for unigram, 2 for bigram, etc.)
            
        Returns:
            Dictionary containing precision, recall, and f1 scores
        """
        def get_ngrams(text, n):
            words = text.lower().split()
            return [tuple(words[i:i+n]) for i in range(len(words)-n+1)]
        
        gen_ngrams = get_ngrams(generated, n_gram)
        ref_ngrams = get_ngrams(reference, n_gram)
        
        if not gen_ngrams or not ref_ngrams:
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
        
        gen_ngrams_set = set(gen_ngrams)
        ref_ngrams_set = set(ref_ngrams)
        
        # Calculate overlapping n-grams
        overlapping = gen_ngrams_set.intersection(ref_ngrams_set)
        
        precision = len(overlapping) / len(gen_ngrams_set) if gen_ngrams_set else 0.0
        recall = len(overlapping) / len(ref_ngrams_set) if ref_ngrams_set else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            f'rouge_{n_gram}': {
                'precision': precision,
                'recall': recall,
                'f1': f1
            }
        }
    
    @staticmethod
    def calculate_bleu(
        generated: str,
        reference: str,
        max_n: int = 4,
        weights: Optional[List[float]] = None
    ) -> Dict[str, float]:
        """
        Calculate BLEU score (simplified version)
        
        Args:
            generated: Generated answer
            reference: Reference answer
            max_n: Maximum n-gram order
            weights: Weights for n-gram precisions
            
        Returns:
            Dictionary containing BLEU score and n-gram precisions
        """
        def get_ngrams(text, n):
            words = text.lower().split()
            return [tuple(words[i:i+n]) for i in range(len(words)-n+1)]
        
        if weights is None:
            weights = [1.0/max_n] * max_n  # Uniform weights
        
        # Calculate modified n-gram precisions
        precisions = []
        gen_ngrams_list = []
        ref_ngrams_list = []
        
        for n in range(1, max_n + 1):
            gen_ngrams = get_ngrams(generated, n)
            ref_ngrams = get_ngrams(reference, n)
            
            if not gen_ngrams or not ref_ngrams:
                precisions.append(0.0)
                continue
                
            # Count n-gram matches (clipped by reference count)
            gen_count = {}
            for gram in gen_ngrams:
                gen_count[gram] = gen_count.get(gram, 0) + 1
                
            ref_count = {}
            for gram in ref_ngrams:
                ref_count[gram] = ref_count.get(gram, 0) + 1
                
            # Clip counts
            clip_count = {}
            for gram, count in gen_count.items():
                clip_count[gram] = min(count, ref_count.get(gram, 0))
                
            # Calculate precision
            total_clip = sum(clip_count.values())
            total_gen = sum(gen_count.values())
            
            precisions.append(total_clip / total_gen if total_gen > 0 else 0.0)
        
        # Calculate brevity penalty
        gen_len = len(generated.split())
        ref_len = len(reference.split())
        brevity_penalty = min(1.0, np.exp(1 - ref_len / gen_len)) if gen_len > 0 else 0.0
        
        # Calculate BLEU score
        if min(precisions) == 0:
            bleu = 0.0
        else:
            bleu = brevity_penalty * np.exp(sum(w * np.log(p) for w, p in zip(weights, precisions) if p > 0))
        
        result = {'bleu': bleu}
        for n, p in enumerate(precisions, 1):
            result[f'bleu_{n}'] = p
            
        return result

class EvaluationResult:
    """Class to store and aggregate evaluation results"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration"""
        self.config = config
        self.metrics = {
            'retrieval': [],
            'answer_quality': []
        }
        
    def add_retrieval_metrics(self, metrics: Dict[str, float]):
        """Add retrieval metrics"""
        self.metrics['retrieval'].append(metrics)
        
    def add_answer_quality_metrics(self, metrics: Dict[str, float]):
        """Add answer quality metrics"""
        self.metrics['answer_quality'].append(metrics)
        
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {
            'config': self.config,
            'retrieval_metrics': {},
            'answer_quality_metrics': {}
        }
        
        # Calculate mean metrics for retrieval
        if self.metrics['retrieval']:
            retrieval_metrics = {}
            for metric in self.metrics['retrieval'][0].keys():
                values = [m[metric] for m in self.metrics['retrieval'] if metric in m]
                if values:
                    retrieval_metrics[f'mean_{metric}'] = float(np.mean(values))
                    retrieval_metrics[f'std_{metric}'] = float(np.std(values))
            summary['retrieval_metrics'] = retrieval_metrics
            
        # Calculate mean metrics for answer quality
        if self.metrics['answer_quality']:
            answer_metrics = {}
            for metric in self.metrics['answer_quality'][0].keys():
                values = [m[metric] for m in self.metrics['answer_quality'] if metric in m]
                if values:
                    answer_metrics[f'mean_{metric}'] = float(np.mean(values))
                    answer_metrics[f'std_{metric}'] = float(np.std(values))
            summary['answer_quality_metrics'] = answer_metrics
            
        return summary
