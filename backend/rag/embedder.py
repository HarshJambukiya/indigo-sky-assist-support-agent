"""
backend/rag/embedder.py
------------------------
Embedding model wrapper using sentence-transformers (100% free, runs locally).
Uses GPU if available (free T4 in Google Colab).
"""

import torch
from sentence_transformers import SentenceTransformer

# ── Load once at startup (expensive to reload) ───────────────────────────────
_device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[Embedder] Loading model on device: {_device}")

_model = SentenceTransformer("all-MiniLM-L6-v2", device=_device)
print(f"[Embedder] Model ready — embedding dim: 384")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Convert a list of text strings into embedding vectors.

    Args:
        texts : List of strings to embed

    Returns:
        List of 384-dim float vectors
    """
    if not texts:
        return []

    vectors = _model.encode(
        texts,
        show_progress_bar=len(texts) > 10,  # Show bar only for large batches
        batch_size=32,
        convert_to_numpy=True,
    )
    return vectors.tolist()


def embed_query(query: str) -> list[float]:
    """
    Embed a single query string.
    Used during retrieval (not ingestion).
    """
    return _model.encode([query]).tolist()[0]
