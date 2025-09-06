from setuptools import setup, find_packages

setup(
    name="nlweb",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "sentence-transformers",
        "rank-bm25",
        "faiss-cpu",  # or faiss-gpu if you have CUDA
    ],
)
