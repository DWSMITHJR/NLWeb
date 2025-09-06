import sys
import logging
import traceback
from pathlib import Path

# Set up logging with debug level
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('debug.log')
    ]
)
logger = logging.getLogger(__name__)

# Add backend directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
logger.debug(f"Added to sys.path: {project_root}")

def main():
    try:
        logger.info("Starting hybrid retriever test...")
        
        logger.info("Importing modules...")
        try:
            from models import Document
            from automl.retrievers.hybrid_retriever import HybridRetriever
            logger.debug("Successfully imported modules")
        except ImportError as e:
            logger.error(f"Failed to import modules: {e}")
            logger.debug(traceback.format_exc())
            return

        logger.info("Creating test documents...")
        documents = [
            Document(
                id="doc1",
                content="The quick brown fox jumps over the lazy dog.",
                metadata={"source": "test"},
            ),
            Document(
                id="doc2",
                content="The five boxing wizards jump quickly.",
                metadata={"source": "test"},
            ),
            Document(
                id="doc3",
                content="Pack my box with five dozen liquor jugs.",
                metadata={"source": "test"},
            ),
        ]
        logger.debug(f"Created {len(documents)} test documents")

        logger.info("Initializing HybridRetriever...")
        try:
            hybrid = HybridRetriever(
                bm25_weight=0.5,
                faiss_weight=0.5,
                faiss_model_name="sentence-transformers/all-MiniLM-L6-v2",
            )
            logger.debug("Successfully initialized HybridRetriever")
        except Exception as e:
            logger.error(f"Failed to initialize HybridRetriever: {e}")
            logger.debug(traceback.format_exc())
            return

        logger.info("Adding documents...")
        try:
            hybrid.add_documents(documents)
            logger.debug(f"Successfully added {len(documents)} documents")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            logger.debug(traceback.format_exc())
            return

        query = "quick fox jumping"
        logger.info(f"Querying: {query}")

        try:
            results = hybrid.retrieve(query, top_k=2)
            logger.info(f"Retrieved {len(results)} results:")

            for i, result in enumerate(results, 1):
                doc = result.get('document', {})
                if hasattr(doc, 'content'):
                    content = doc.content
                elif isinstance(doc, dict):
                    content = doc.get('content', 'No content')
                else:
                    content = str(doc)
                
                logger.info(
                    f"{i}. {content} (Score: {result.get('score', 0):.4f})"
                )
            logger.info("Test completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            logger.debug(traceback.format_exc())

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    main()
