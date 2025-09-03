import sys
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('automl_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent))

def load_test_data() -> tuple[List[Dict], List[Dict]]:
    """Load test documents and queries"""
    # Sample documents
    documents = [
        {
            "id": "doc1",
            "content": "The quick brown fox jumps over the lazy dog. This is a test document about animals.",
            "metadata": {"source": "test", "type": "animals"}
        },
        {
            "id": "doc2", 
            "content": "The five boxing wizards jump quickly. This is a test document about wizards.",
            "metadata": {"source": "test", "type": "fantasy"}
        },
        {
            "id": "doc3",
            "content": "Pack my box with five dozen liquor jugs. This is a test document about packing.",
            "metadata": {"source": "test", "type": "activity"}
        },
        {
            "id": "doc4",
            "content": "How vexingly quick daft zebras jump! This is another test document about animals.",
            "metadata": {"source": "test", "type": "animals"}
        },
        {
            "id": "doc5",
            "content": "The quick brown fox is a skilled jumper. This is yet another test document about animals.",
            "metadata": {"source": "test", "type": "animals"}
        }
    ]
    
    # Sample test queries with relevant documents and reference answers
    test_queries = [
        {
            "query": "quick fox jumping",
            "relevant_docs": ["doc1", "doc5"],
            "reference_answer": "The quick brown fox jumps over the lazy dog and is a skilled jumper."
        },
        {
            "query": "wizards jumping quickly",
            "relevant_docs": ["doc2"],
            "reference_answer": "The five boxing wizards jump quickly."
        },
        {
            "query": "zebras jumping",
            "relevant_docs": ["doc4"],
            "reference_answer": "Daft zebras jump quickly and vexingly."
        }
    ]
    
    return documents, test_queries

def run_automl_test():
    """Run a test of the AutoML system with hybrid retriever and prompt templates"""
    try:
        logger.info("Starting AutoML integration test...")
        
        # Import required modules
        from models import Document
        from automl.orchestrator import AutoMLOrchestrator
        from prompt_templates import TemplateType
        
        # Load test data
        logger.info("Loading test data...")
        raw_docs, test_queries = load_test_data()
        
        # Convert to Document objects
        documents = [
            Document(
                id=doc["id"],
                content=doc["content"],
                metadata=doc.get("metadata", {})
            )
            for doc in raw_docs
        ]
        
        # Create output directory if it doesn't exist
        os.makedirs("automl_test_results", exist_ok=True)
        
        # Initialize AutoML orchestrator
        logger.info("Initializing AutoMLOrchestrator...")
        automl = AutoMLOrchestrator(
            output_dir="automl_test_results",
            max_workers=2  # Use 2 workers for parallel testing
        )
        
        # Define base configuration
        base_config = {
            "chunk_size": 256,
            "chunk_overlap": 50,
            "chunking_strategy": "sentence",
            "top_k": 3,
            "prompt_template": TemplateType.SIMPLE.value
        }
        
        # Run AutoML optimization
        logger.info("Starting AutoML optimization...")
        results = automl.run(
            train_documents=documents,
            test_queries=test_queries,
            base_config=base_config,
            num_configs=3,  # Test with a small number of configurations
            max_iterations=2  # Limit iterations for testing
        )
        
        # Save results
        output_file = "automl_test_results/results_summary.json"
        with open(output_file, 'w') as f:
            json.dump({
                "best_config": results['best_config'],
                "best_score": results['best_score'],
                "num_configs_tested": len(results['results'])
            }, f, indent=2)
        
        logger.info(f"Test completed successfully! Results saved to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error in AutoML test: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = run_automl_test()
    if success:
        print("\n✅ AutoML integration test completed successfully!")
    else:
        print("\n❌ AutoML integration test failed. Check the logs for details.")
        sys.exit(1)
