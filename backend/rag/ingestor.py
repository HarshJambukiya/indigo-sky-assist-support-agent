"""
backend/rag/ingestor.py
------------------------
Document ingestion pipeline.
Reads PDFs and text files → chunks → embeds → stores in ChromaDB.
Run this ONCE to load your IndiGo policy documents.
"""

import os
import fitz  # PyMuPDF
from .embedder     import embed_texts
from .vector_store import VectorStore


DOCS_DIR = os.environ.get("DOCS_DIR", "./backend/data/docs")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks.

    Args:
        text       : Full document text
        chunk_size : Max characters per chunk
        overlap    : Overlap between chunks (for context continuity)

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if len(chunk) > 30:   # Skip tiny fragments
            chunks.append(chunk)
        start = end - overlap
    return chunks


def ingest_pdf(pdf_path: str, category: str, vector_store: VectorStore):
    """
    Ingest a single PDF into ChromaDB.

    Args:
        pdf_path     : Full path to the PDF file
        category     : Category tag (e.g. "baggage", "faq", "booking")
        vector_store : VectorStore instance
    """
    print(f"[Ingestor] Processing: {pdf_path}")
    doc = fitz.open(pdf_path)
    all_chunks    = []
    all_metadatas = []
    all_ids       = []

    for page_num, page in enumerate(doc):
        page_text = page.get_text()
        page_chunks = chunk_text(page_text)

        for i, chunk in enumerate(page_chunks):
            chunk_id = f"{category}_p{page_num + 1}_c{i}"
            all_chunks.append(chunk)
            all_metadatas.append({
                "source"  : os.path.basename(pdf_path),
                "page"    : page_num + 1,
                "category": category,
            })
            all_ids.append(chunk_id)

    if not all_chunks:
        print(f"[Ingestor] No text found in {pdf_path}")
        return

    # Embed all chunks (uses GPU if available)
    print(f"[Ingestor] Embedding {len(all_chunks)} chunks...")
    embeddings = embed_texts(all_chunks)

    # Store in ChromaDB
    col = vector_store.get_main_collection()
    col.upsert(
        documents=all_chunks,
        embeddings=embeddings,
        ids=all_ids,
        metadatas=all_metadatas,
    )
    print(f"[Ingestor] ✅ Ingested {len(all_chunks)} chunks from {os.path.basename(pdf_path)}")


def ingest_text(text: str, source_name: str, category: str, vector_store: VectorStore):
    """
    Ingest raw text (e.g. FAQ markdown) directly.
    """
    chunks     = chunk_text(text)
    embeddings = embed_texts(chunks)
    col        = vector_store.get_main_collection()

    ids       = [f"{category}_{source_name}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": source_name, "page": 1, "category": category}] * len(chunks)

    col.upsert(documents=chunks, embeddings=embeddings, ids=ids, metadatas=metadatas)
    print(f"[Ingestor] ✅ Ingested {len(chunks)} chunks from {source_name}")


def ingest_all_docs(vector_store: VectorStore):
    """
    Ingest all PDF files from the DOCS_DIR folder.
    File naming convention: <category>_<name>.pdf
    Example: baggage_policy.pdf → category = "baggage"
    """
    if not os.path.exists(DOCS_DIR):
        print(f"[Ingestor] Docs dir not found: {DOCS_DIR}")
        return

    pdf_files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".pdf")]

    if not pdf_files:
        print("[Ingestor] No PDF files found. Add PDFs to backend/data/docs/")
        return

    for filename in pdf_files:
        # Derive category from filename prefix
        category = filename.split("_")[0] if "_" in filename else "general"
        path = os.path.join(DOCS_DIR, filename)
        ingest_pdf(path, category, vector_store)

    print(f"\n[Ingestor] 🎉 Total docs in DB: {vector_store.collection_count()}")


def ingest_resume(pdf_bytes: bytes, session_id: str, vector_store: VectorStore):
    """
    Ingest a user's resume into their personal ChromaDB collection.

    Args:
        pdf_bytes  : Raw PDF bytes from file upload
        session_id : User's session ID (used as collection name)
        vector_store : VectorStore instance
    """
    import io
    doc    = fitz.open(stream=pdf_bytes, filetype="pdf")
    chunks = []

    for page in doc:
        chunks.extend(chunk_text(page.get_text()))

    if not chunks:
        return 0

    embeddings = embed_texts(chunks)
    col        = vector_store.get_user_collection(session_id)
    ids        = [f"resume_chunk_{i}" for i in range(len(chunks))]
    metadatas  = [{"source": "resume", "page": 1, "category": "resume"}] * len(chunks)

    col.upsert(documents=chunks, embeddings=embeddings, ids=ids, metadatas=metadatas)
    print(f"[Ingestor] ✅ Ingested {len(chunks)} resume chunks for session {session_id[:8]}")
    return len(chunks)
