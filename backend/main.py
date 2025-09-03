from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import routers
from api.routers import automl as automl_router

app = FastAPI(title="NLWeb AutoRAG API",
              description="API for NLWeb AutoRAG with AutoML capabilities",
              version="0.1.0")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(automl_router.router)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    context: Dict[str, Any] = {}

class Document(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any] = {}

# In-memory storage for demo purposes
knowledge_base = []

# Embedding model and FAISS index
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
try:
    embedder = SentenceTransformer(MODEL_NAME)
    EMBEDDING_DIM = embedder.get_sentence_embedding_dimension()
except Exception as e:
    # Delay failure to runtime endpoint call, but keep variables defined
    embedder = None
    EMBEDDING_DIM = 384  # default for the chosen model

# Cosine similarity with FAISS uses IndexFlatIP on normalized vectors
index = faiss.IndexFlatIP(EMBEDDING_DIM)
id_to_doc: Dict[int, Dict[str, Any]] = {}
next_vector_id = 0

def ensure_model_loaded():
    global embedder, EMBEDDING_DIM, index
    if embedder is None:
        embedder = SentenceTransformer(MODEL_NAME)
        EMBEDDING_DIM = embedder.get_sentence_embedding_dimension()
        # Recreate index if needed
        if index is None or index.d != EMBEDDING_DIM:
            faiss.reset()  # no-op but explicit
            # WARNING: resetting here would lose existing vectors
            pass

def _normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
    return vectors / norms

@app.post("/query")
async def process_query(request: QueryRequest):
    """Process natural language query using vector search over the knowledge base."""
    try:
        ensure_model_loaded()
        if index.ntotal == 0:
            return {
                "answer": "No documents in the knowledge base yet. Please add documents first.",
                "sources": [],
                "confidence": 0.0,
            }

        # Embed and normalize query
        q_emb = embedder.encode([request.query], convert_to_numpy=True)
        q_emb = _normalize(q_emb.astype("float32"))

        top_k = max(1, min(request.top_k, min(5, index.ntotal)))
        scores, idxs = index.search(q_emb, top_k)
        scores = scores[0]
        idxs = idxs[0]

        retrieved = []
        for score, idx in zip(scores, idxs):
            if idx == -1:
                continue
            doc = id_to_doc.get(idx)
            if not doc:
                continue
            retrieved.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc.get("metadata", {}),
                "score": float(score),
            })

        # Simple synthesis: echo top passage and list sources
        if not retrieved:
            return {
                "answer": "I couldn't find relevant content in the knowledge base.",
                "sources": [],
                "confidence": 0.0,
            }

        top = retrieved[0]
        sources = [r["id"] for r in retrieved]
        synthesized = (
            f"Answer based on retrieved context:\n\n"
            f"Top passage (ID={top['id']}):\n{top['content']}\n\n"
            f"Query: {request.query}"
        )

        # Heuristic confidence from top score (cosine similarity in [0,1])
        # Note: IndexFlatIP with normalized vectors yields cosine similarity in [-1,1], clip to [0,1]
        conf = float(max(0.0, min(1.0, (top["score"] + 1.0) / 2.0)))

        return {
            "answer": synthesized,
            "sources": sources,
            "confidence": conf,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents")
async def add_document(doc: Document):
    """Add a document to the knowledge base and index it for retrieval."""
    try:
        ensure_model_loaded()
        knowledge_base.append(doc.dict())

        emb = embedder.encode([doc.content], convert_to_numpy=True).astype("float32")
        emb = _normalize(emb)

        global next_vector_id
        index.add(emb)
        id_to_doc[next_vector_id] = doc.dict()
        assigned_id = next_vector_id
        next_vector_id += 1

        return {"status": "success", "document_id": doc.id, "vector_id": assigned_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    """List all documents in the knowledge base"""
    return knowledge_base

@app.get("/health")
async def health():
    return {"status": "ok", "docs": len(knowledge_base), "indexed": index.ntotal}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
