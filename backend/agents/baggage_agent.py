"""
backend/agents/baggage_agent.py
--------------------------------
Baggage Agent — answers baggage policy questions using RAG.
Specializes in: allowance, fees, restricted items, lost luggage.
"""

from .base import call_groq, FAST_MODEL

BAGGAGE_SYSTEM = """
You are IndiGo Airlines baggage support specialist.

Use the CONTEXT below to answer questions about:
- Cabin and checked baggage allowances
- Excess baggage fees
- Restricted / prohibited items
- Special items (sports equipment, musical instruments, medical)
- Lost or damaged baggage claims

CONTEXT:
{context}

RULES:
1. Always quote specific weights (kg) and fees (₹/USD)
2. Recommend adding extra baggage at booking (cheaper than airport)
3. For lost baggage: advise filing PIR report within 24 hours
4. Be empathetic for lost baggage situations

Is there anything else I can help you with?
"""


def baggage_agent_answer(user_message: str, chat_history: list, retriever) -> str:
    """
    Answer baggage questions using policy RAG context.
    """
    # Filter retrieval to baggage category only
    context = retriever.retrieve(
        query=user_message,
        n_results=3,
        category_filter="baggage"   # Only pull baggage-related chunks
    )

    if not context:
        # Fall back to general search if no baggage-specific docs
        context = retriever.retrieve(user_message, n_results=3)

    messages = [
        {"role": "system", "content": BAGGAGE_SYSTEM.format(
            context=context or "Baggage policy details not available."
        )},
        *chat_history[-4:],
        {"role": "user", "content": user_message},
    ]

    return call_groq(messages, model=FAST_MODEL)
