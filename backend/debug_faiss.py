import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent))

logger.info("Starting FAISS debug test...")

try:
    logger.info("Importing FAISS...")
    import faiss

    logger.info("FAISS imported successfully")

    logger.info("Importing numpy...")
    import numpy as np

    logger.info("NumPy imported successfully")

    logger.info("Creating test embeddings...")
    embeddings = np.random.rand(5, 384).astype("float32")
    logger.info(f"Embeddings shape: {embeddings.shape}")

    logger.info("Creating FAISS index...")
    index = faiss.IndexFlatIP(embeddings.shape[1])
    logger.info("Adding embeddings to index...")
    index.add(embeddings)

    logger.info("Performing search...")
    query = np.random.rand(1, 384).astype("float32")
    distances, indices = index.search(query, 2)

    logger.info(f"Search results - Distances: {distances}, Indices: {indices}")
    logger.info("FAISS test completed successfully!")

except Exception as e:
    logger.error(f"Error in FAISS test: {str(e)}", exc_info=True)
