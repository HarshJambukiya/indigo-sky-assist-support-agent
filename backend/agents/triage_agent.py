"""
backend/agents/triage_agent.py
-------------------------------
The FIRST agent that sees every user message.
Classifies intent and decides which specialist agent handles it.
"""

import json
from .base import call_groq, FAST_MODEL

# ── System prompt for intent classification ──────────────────────────────────
TRIAGE_PROMPT = """
You are a smart routing agent for IndiGo Airlines customer service.

Analyze the user's message and classify it into EXACTLY ONE of these categories:

- FAQ       : General questions about policies, rules, check-in, seat selection, meals
- BOOKING   : Flight booking, cancellation, date change, PNR lookup, refund status
- BAGGAGE   : Baggage allowance, lost luggage, extra baggage fees, special items
- ESCALATE  : Angry customer, complaint, unresolved issue, asking for human/manager
- RESUME    : User uploaded resume, asking about jobs, careers at IndiGo
- GREETING  : Hello, hi, greetings, general intro messages

Rules:
- Read the FULL message before deciding
- If unsure between two, pick the most likely one
- NEVER respond with anything else

Respond with ONLY this JSON (no extra text):
{"intent": "<CATEGORY>", "confidence": <0.0 to 1.0>, "reason": "<one sentence why>"}
"""


def classify_intent(user_message: str) -> dict:
    """
    Classify user intent using Groq.

    Returns:
        {
          "intent": "FAQ",
          "confidence": 0.95,
          "reason": "User asked about baggage weight limits"
        }
    """
    messages = [
        {"role": "system", "content": TRIAGE_PROMPT},
        {"role": "user",   "content": user_message},
    ]

    raw = call_groq(messages, model=FAST_MODEL, temperature=0.0)

    # ── Parse JSON safely ────────────────────────────────────────────────────
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # If Groq returns something weird, default to FAQ
        result = {"intent": "FAQ", "confidence": 0.5, "reason": "Could not parse intent"}

    return result
