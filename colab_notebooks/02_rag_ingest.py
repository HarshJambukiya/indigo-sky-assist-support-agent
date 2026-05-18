# ==============================================================================
# COLAB NOTEBOOK: RAG Document Ingestion
# Run this AFTER 00_setup.py to load IndiGo docs into ChromaDB
# ==============================================================================


# ── CELL 1: Ingest the FAQ Markdown file ──────────────────────────────────────
"""
This loads the built-in FAQ text into ChromaDB.
Run once — data is saved to Google Drive permanently.
"""
import sys
sys.path.insert(0, '/content/indigo-ai-support')

from backend.rag.vector_store import VectorStore
from backend.rag.ingestor     import ingest_text

vs = VectorStore()

# Read the FAQ markdown file
with open('/content/indigo-ai-support/backend/data/faqs/indigo_faq.md', 'r') as f:
    faq_text = f.read()

ingest_text(faq_text, source_name="indigo_faq.md", category="faq", vector_store=vs)
print(f"\n✅ Total documents in ChromaDB: {vs.collection_count()}")


# ── CELL 2: Ingest PDF Files (if you have them) ────────────────────────────────
"""
Upload your policy PDFs to Google Drive first:
  /content/drive/MyDrive/indigo-ai-support/docs/

Then run this cell to ingest them all.

Naming convention:
  baggage_policy.pdf   → category = "baggage"
  faq_general.pdf      → category = "faq"
  booking_rules.pdf    → category = "booking"
"""
from backend.rag.ingestor import ingest_all_docs

ingest_all_docs(vs)
print(f"\n✅ Total documents after PDF ingestion: {vs.collection_count()}")


# ── CELL 3: Test RAG Retrieval ─────────────────────────────────────────────────
"""
Test that retrieval is working correctly.
"""
from backend.rag.retriever import Retriever

retriever = Retriever(vs)

test_queries = [
    "What is the baggage allowance for economy class?",
    "How do I cancel my flight?",
    "Can I select my seat for free?",
    "What happens if IndiGo cancels my flight?",
]

for query in test_queries:
    context = retriever.retrieve(query, n_results=2)
    print(f"\n🔍 Query: {query}")
    print(f"📄 Context preview: {context[:200]}...")
    print("-" * 60)


# ── CELL 4: Check DB Stats ────────────────────────────────────────────────────
import chromadb
import os

client = chromadb.PersistentClient(path=os.environ.get(
    'CHROMA_PATH', '/content/drive/MyDrive/indigo-ai-support/chroma_db'
))

collections = client.list_collections()
print(f"\n📊 ChromaDB Collections:")
for col in collections:
    c = client.get_collection(col.name)
    print(f"   {col.name}: {c.count()} documents")
