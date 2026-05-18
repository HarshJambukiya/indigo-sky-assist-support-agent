"""
backend/rag/retriever.py
-------------------------
Retriever — searches ChromaDB for relevant chunks given a query.
Used by FAQ Agent, Baggage Agent, and Resume Agent.
"""

from .embedder     import embed_query
from .vector_store import VectorStore


class Retriever:
    """
    Handles similarity search over ChromaDB collections.
    """

    def __init__(self, vector_store: VectorStore):
        self.vs = vector_store

    def retrieve(self, query: str, n_results: int = 3,
                 category_filter: str = None) -> str:
        """
        Search the main IndiGo knowledge base for relevant chunks.

        Args:
            query           : User's question
            n_results       : How many chunks to return
            category_filter : Optional — filter by category (e.g. "baggage")

        Returns:
            Concatenated relevant text chunks as a single string
        """
        collection = self.vs.get_main_collection()

        if collection.count() == 0:
            return ""

        # ── Build query vector ────────────────────────────────────────────────
        query_vector = embed_query(query)

        # ── Optional category filter ──────────────────────────────────────────
        where_clause = {"category": category_filter} if category_filter else None

        # ── Run similarity search ─────────────────────────────────────────────
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=min(n_results, collection.count()),
            where=where_clause,
            include=["documents", "metadatas", "distances"],
        )

        docs      = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        # ── Format results with source citation ───────────────────────────────
        chunks = []
        for doc, meta, dist in zip(docs, metadatas, distances):
            source = meta.get("source", "IndiGo Docs")
            page   = meta.get("page", "?")
            score  = round(1 - dist, 2)   # cosine similarity score
            chunks.append(f"[Source: {source}, Page {page}, Score: {score}]\n{doc}")

        return "\n\n---\n\n".join(chunks)

    def retrieve_from_user_collection(self, query: str, session_id: str,
                                       n_results: int = 5) -> str:
        """
        Search a user's personal resume collection.
        Used by Resume Agent.
        """
        try:
            collection = self.vs.get_user_collection(session_id)

            if collection.count() == 0:
                return ""

            query_vector = embed_query(query)
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=min(n_results, collection.count()),
                include=["documents"],
            )
            return "\n\n".join(results["documents"][0])

        except Exception as e:
            print(f"[Retriever] User collection error: {e}")
            return ""
