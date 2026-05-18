"""
backend/agents/faq_agent.py
----------------------------
FAQ Agent — answers general IndiGo policy questions using RAG.
Retrieves relevant chunks from ChromaDB, then asks Groq to answer.
"""

from .base import call_groq, FAST_MODEL

# ── System prompt injected with RAG context ──────────────────────────────────
FAQ_SYSTEM = """
You are a helpful IndiGo Airlines customer support agent.
Your job is to answer customer questions using ONLY the information provided below.

RULES:
1. Only use facts from the CONTEXT section
2. If the answer is not in context, say: "I don't have that information right now. Let me connect you with our support team."
3. Always be polite and professional
4. End with: "Is there anything else I can help you with?"
5. Keep answers concise — under 150 words

CONTEXT:
{context}
"""


def faq_agent_answer(user_message: str, chat_history: list, retriever) -> str:
    """
    Answer a FAQ using RAG retrieval + Groq.

    Args:
        user_message : The user's question
        chat_history : List of previous messages [{"role":..., "content":...}]
        retriever    : The RAG retriever object (from rag/retriever.py)

    Returns:
        Answer string
    """
    # Step 1: Retrieve relevant context from ChromaDB
    context = retriever.retrieve(user_message, n_results=3)

    # Step 2: Build messages with context + last 4 history messages
    system_msg = FAQ_SYSTEM.format(context=context if context else "No context available.")

    messages = [
        {"role": "system", "content": system_msg},
        *chat_history[-4:],        # Keep last 4 messages for memory
        {"role": "user", "content": user_message},
    ]

    # Step 3: Call Groq
    return call_groq(messages, model=FAST_MODEL)
