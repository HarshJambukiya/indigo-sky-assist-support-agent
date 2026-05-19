"""
backend/main.py
----------------
FastAPI application entry point.
This is what runs inside Google Colab via uvicorn.
"""

import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ── Internal imports ──────────────────────────────────────────────────────────
from backend.rag.vector_store   import VectorStore
from backend.rag.retriever      import Retriever
from backend.rag.ingestor       import ingest_all_docs, ingest_resume
from backend.agents.router      import AgentRouter
from backend.api.schemas        import ChatRequest, ChatResponse, UploadResponse, HealthResponse
from backend.memory.chat_history import get_full_history, clear_session

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "✈️ IndiGo AI Support API",
    description = "Multi-Agent Customer Service System with RAG",
    version     = "1.0.0",
)

# ── CORS (allow all origins so Lovable frontend can connect) ──────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_methods     = ["*"],
    allow_headers     = ["*"],
    allow_credentials = False,
)

# ── Initialize shared services (once at startup) ──────────────────────────────
print("[Main] Initializing vector store...")
vector_store = VectorStore()

print("[Main] Initializing retriever...")
retriever = Retriever(vector_store)

print("[Main] Loading documents into ChromaDB...")
ingest_all_docs(vector_store)   # Reads all PDFs from backend/data/docs/

print("[Main] Initializing agent router...")
router = AgentRouter(retriever)

print("[Main] ✅ All systems ready!")


# ═══════════════════════════════════════════════════════════════════════════════
#  API ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", tags=["Root"])
async def root():
    return {"message": "✈️ IndiGo AI Support API is running!", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Check if API + ChromaDB are running."""
    return HealthResponse(
        status   = "ok",
        db_docs  = vector_store.collection_count(),
        agents   = ["TRIAGE", "FAQ", "BOOKING", "BAGGAGE", "ESCALATE", "RESUME"],
    )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Accepts user message + session_id, returns agent response.
    """
    try:
        result = router.route(
            user_message = request.message,
            session_id   = request.session_id,
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-resume", response_model=UploadResponse, tags=["Upload"])
async def upload_resume(
    file       : UploadFile = File(...),
    session_id : str        = "default_session"
):
    """
    Upload a PDF resume.
    Parses, embeds, and stores in user's personal ChromaDB collection.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_bytes    = await file.read()
    chunks_added = ingest_resume(pdf_bytes, session_id, vector_store)

    if chunks_added == 0:
        return UploadResponse(
            status       = "warning",
            chunks_added = 0,
            message      = "Could not extract text from PDF. Try a text-based PDF."
        )

    return UploadResponse(
        status       = "success",
        chunks_added = chunks_added,
        message      = f"Resume processed! {chunks_added} sections indexed. Ask me anything about your experience!"
    )


@app.get("/history/{session_id}", tags=["History"])
async def get_chat_history(session_id: str):
    """Get full chat history for a session."""
    history = get_full_history(session_id)
    return {"session_id": session_id, "messages": history, "count": len(history)}


@app.delete("/history/{session_id}", tags=["History"])
async def delete_session(session_id: str):
    """Clear chat history for a session."""
    clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}


@app.get("/session/new", tags=["Session"])
async def new_session():
    """Generate a new unique session ID."""
    return {"session_id": str(uuid.uuid4())}
