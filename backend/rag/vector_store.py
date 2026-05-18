"""
backend/rag/vector_store.py
----------------------------
ChromaDB wrapper.
Creates and manages the vector collections on Google Drive.
"""

import os
import chromadb
from chromadb.config import Settings


# ── Default paths (overridden by env vars in Colab) ──────────────────────────
CHROMA_PATH = os.environ.get(
    "CHROMA_PATH",
    "./backend/data/chroma_db"          # local fallback for testing
)


class VectorStore:
    """
    Manages ChromaDB collections.

    Collections:
        indigo_knowledge_base   ← policy docs, FAQs (shared)
        resume_{session_id}     ← per-user resume chunks
    """

    def __init__(self):
        # Persistent client saves to disk (Google Drive in Colab)
        self.client = chromadb.PersistentClient(
            path=CHROMA_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        print(f"[VectorStore] ChromaDB ready at: {CHROMA_PATH}")

    def get_main_collection(self):
        """Get or create the shared IndiGo knowledge collection."""
        return self.client.get_or_create_collection(
            name="indigo_knowledge_base",
            metadata={"hnsw:space": "cosine"}   # cosine similarity
        )

    def get_user_collection(self, session_id: str):
        """Get or create a personal collection for a user's resume."""
        safe_id = session_id.replace("-", "_")[:32]   # ChromaDB name rules
        return self.client.get_or_create_collection(
            name=f"resume_{safe_id}",
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, texts: list[str], embeddings: list,
                       ids: list[str], metadatas: list[dict], collection_name: str = "main"):
        """
        Add chunked documents + their embeddings to a collection.
        """
        if collection_name == "main":
            col = self.get_main_collection()
        else:
            col = self.client.get_or_create_collection(collection_name)

        col.add(
            documents=embeddings,       # ChromaDB stores embeddings
            ids=ids,
            metadatas=metadatas,
        )
        # Also store raw text in metadata for retrieval display
        col.upsert(
            documents=texts,
            ids=ids,
            metadatas=metadatas,
        )
        print(f"[VectorStore] Added {len(texts)} chunks to '{collection_name}'")

    def collection_count(self, collection_name: str = "main") -> int:
        """Return number of documents in a collection."""
        try:
            if collection_name == "main":
                return self.get_main_collection().count()
            return self.client.get_collection(collection_name).count()
        except Exception:
            return 0
