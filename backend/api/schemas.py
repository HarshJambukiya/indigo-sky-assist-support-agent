"""
backend/api/schemas.py
-----------------------
Pydantic models for FastAPI request/response validation.
"""

from pydantic import BaseModel, Field
from typing   import Optional


class ChatRequest(BaseModel):
    """Incoming chat message from the frontend."""
    message    : str = Field(..., min_length=1, max_length=2000,
                             description="User's message text")
    session_id : str = Field(..., min_length=8,
                             description="Unique session identifier")


class ChatResponse(BaseModel):
    """Outgoing structured response to the frontend."""
    response   : str            = Field(..., description="Agent's reply text")
    agent      : str            = Field(..., description="Which agent handled it")
    confidence : float          = Field(..., ge=0.0, le=1.0)
    handoff    : bool           = Field(default=False)
    ticket_id  : Optional[str]  = Field(default=None)
    session_id : str


class UploadResponse(BaseModel):
    """Response after a resume/document upload."""
    status      : str
    chunks_added: int
    message     : str


class HealthResponse(BaseModel):
    """Health check response."""
    status     : str
    db_docs    : int
    agents     : list[str]
