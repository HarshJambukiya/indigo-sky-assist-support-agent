"""
backend/agents/handoff_agent.py
--------------------------------
Human Handoff Agent — escalates frustrated customers to a human agent.
Triggers notification and updates session state.
"""

import os
import requests
from datetime import datetime


HANDOFF_RESPONSE = """
I completely understand your frustration, and I sincerely apologize for the inconvenience. 🙏

I'm now connecting you to a **Senior IndiGo Support Agent** who will be able to fully resolve your issue.

📋 **Ticket Created:** #{ticket_id}
⏰ **Expected Wait:** 3-5 minutes
📞 **Reference Number:** {ticket_id}

Our agent will have your full conversation history, so you won't need to repeat anything.

Thank you for your patience. We value your trust in IndiGo Airlines. ✈️
"""


def handoff_agent_trigger(user_message: str, chat_history: list, session_id: str) -> dict:
    """
    Trigger human handoff:
    1. Generate a ticket
    2. Send Slack/email notification (optional)
    3. Return handoff message + flag for frontend

    Returns:
        {
          "response": "...",
          "handoff": True,
          "ticket_id": "IND-2026-001"
        }
    """
    ticket_id = _generate_ticket(session_id)

    # ── Optional: Send Slack notification ────────────────────────────────────
    slack_url = os.environ.get("SLACK_WEBHOOK_URL")
    if slack_url:
        _notify_slack(slack_url, session_id, ticket_id, user_message, chat_history)

    return {
        "response": HANDOFF_RESPONSE.format(ticket_id=ticket_id),
        "handoff": True,
        "ticket_id": ticket_id,
    }


def _generate_ticket(session_id: str) -> str:
    """Generate a fake support ticket ID."""
    ts = datetime.now().strftime("%Y%m%d%H%M")
    short = session_id[:6].upper()
    return f"IND-{ts}-{short}"


def _notify_slack(webhook_url: str, session_id: str, ticket_id: str,
                  last_message: str, history: list):
    """Send a Slack notification when a handoff is triggered."""
    try:
        # Get last 3 messages as context
        recent = "\n".join(
            [f"*{m['role'].upper()}*: {m['content'][:80]}..." for m in history[-3:]]
        )
        payload = {
            "text": f"🚨 *Human Handoff Requested*\n"
                    f"*Ticket:* {ticket_id}\n"
                    f"*Session:* {session_id}\n"
                    f"*Last message:* {last_message[:100]}\n\n"
                    f"*Recent conversation:*\n{recent}"
        }
        requests.post(webhook_url, json=payload, timeout=5)
        print(f"[Handoff] Slack notified for ticket {ticket_id}")
    except Exception as e:
        print(f"[Handoff] Slack notification failed: {e}")
