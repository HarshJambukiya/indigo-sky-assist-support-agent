"""
backend/agents/base.py
----------------------
Shared Groq client and base LLM call function.
All agents import from here.
"""

import os
from groq import Groq

# ── Groq client (API key from env / Colab Secrets) ──────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── Model names ──────────────────────────────────────────────────────────────
FAST_MODEL  = os.environ.get("GROQ_MODEL_FAST",  "llama3-8b-8192")   # cheap + fast
SMART_MODEL = os.environ.get("GROQ_MODEL_SMART", "llama3-70b-8192")  # smarter


def call_groq(messages: list[dict], model: str = FAST_MODEL, temperature: float = 0.1) -> str:
    """
    Send messages to Groq and return the assistant reply as a string.

    Args:
        messages    : list of {"role": "...", "content": "..."}
        model       : groq model name (default: fast model)
        temperature : 0.0 = deterministic, 1.0 = creative

    Returns:
        Assistant reply string
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[Groq Error] {e}")
        return "Sorry, I'm having trouble connecting to the AI. Please try again."
