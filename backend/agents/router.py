"""
backend/agents/router.py
-------------------------
The AgentRouter — central dispatcher that:
1. Calls Triage Agent to classify intent
2. Routes to the correct specialist agent
3. Saves messages to chat history
4. Returns structured response to FastAPI
"""

from .triage_agent   import classify_intent
from .faq_agent      import faq_agent_answer
from .booking_agent  import booking_agent_answer
from .baggage_agent  import baggage_agent_answer
from .handoff_agent  import handoff_agent_trigger
from .resume_agent   import resume_agent_answer
from ..memory.chat_history import get_history, save_message


GREETING_RESPONSE = """
👋 Welcome to **IndiGo Airlines Customer Support**!

I'm your AI assistant, ready to help you with:
- ✈️ **Flight bookings** & PNR lookup
- 🧳 **Baggage** policies & fees
- ❓ **FAQs** about check-in, meals, seats
- 📄 **Resume upload** for career queries
- 👤 **Human agent** connection if needed

How can I assist you today?
"""


class AgentRouter:
    """
    Central router that connects all agents together.
    Initialized once when FastAPI starts.
    """

    def __init__(self, retriever):
        """
        Args:
            retriever : RAG retriever instance (shared across agents)
        """
        self.retriever = retriever

    def route(self, user_message: str, session_id: str) -> dict:
        """
        Process a user message end-to-end.

        Returns:
            {
              "response"   : "Answer text...",
              "agent"      : "FAQ",
              "confidence" : 0.92,
              "handoff"    : False,
              "ticket_id"  : None
            }
        """
        # ── Step 1: Load chat history for this session ───────────────────────
        history = get_history(session_id)

        # ── Step 2: Classify intent ──────────────────────────────────────────
        intent_data = classify_intent(user_message)
        intent      = intent_data.get("intent", "FAQ")
        confidence  = intent_data.get("confidence", 0.5)

        print(f"[Router] Session={session_id} | Intent={intent} ({confidence:.0%})")

        # ── Step 3: Route to correct agent ───────────────────────────────────
        handoff   = False
        ticket_id = None

        if intent == "GREETING":
            response = GREETING_RESPONSE

        elif intent == "FAQ":
            response = faq_agent_answer(user_message, history, self.retriever)

        elif intent == "BOOKING":
            response = booking_agent_answer(user_message, history)

        elif intent == "BAGGAGE":
            response = baggage_agent_answer(user_message, history, self.retriever)

        elif intent == "ESCALATE":
            result    = handoff_agent_trigger(user_message, history, session_id)
            response  = result["response"]
            handoff   = result["handoff"]
            ticket_id = result["ticket_id"]

        elif intent == "RESUME":
            response = resume_agent_answer(user_message, history, self.retriever, session_id)

        else:
            response = faq_agent_answer(user_message, history, self.retriever)

        # ── Step 4: Save messages to chat history ────────────────────────────
        save_message(session_id, role="user",      content=user_message)
        save_message(session_id, role="assistant", content=response)

        # ── Step 5: Return structured response ───────────────────────────────
        return {
            "response"   : response,
            "agent"      : intent,
            "confidence" : round(confidence, 2),
            "handoff"    : handoff,
            "ticket_id"  : ticket_id,
            "session_id" : session_id,
        }
