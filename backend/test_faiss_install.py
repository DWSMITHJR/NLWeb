import sys
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Testing FAISS installation...")

    try:
        logger.info("Importing NumPy...")
        import numpy as np

        logger.info("NumPy version: %s", np.__version__)

        logger.info("Importing FAISS...")
        import faiss

        logger.info("FAISS version: %s", faiss.__version__)

        # Create test data
        d = 64  # dimension
        nb = 100000  # database size
        nq = 10000  # nb of queries
        np.random.seed(1234)  # make reproducible
        xb = np.random.random((nb, d)).astype("float32")
        xb[:, 0] += np.arange(nb) / 1000.0
        xq = np.random.random((nq, d)).astype("float32")
        xq[:, 0] += np.arange(nq) / 1000.0

        # Build the index
        logger.info("Building FAISS index...")
        index = faiss.IndexFlatL2(d)  # build the index
        logger.info("Training FAISS index...")
        index.add(xb)  # add vectors to the index
        logger.info("Index size: %s", index.ntotal)

        # Search
        k = 4  # we want to see 4 nearest neighbors
        logger.info("Performing search...")
        D, I = index.search(xq, k)  # actual search

        logger.info("First 5 results:")
        for i in range(5):
            logger.info("Query %d: %s", i, I[i])

        logger.info("FAISS test completed successfully!")
        return 0

    except Exception as e:
        logger.error("FAISS test failed: %s", str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
