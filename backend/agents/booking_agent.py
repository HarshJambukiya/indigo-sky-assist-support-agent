"""
backend/agents/booking_agent.py
--------------------------------
Booking Agent — handles flight booking, PNR lookup, cancellations.
Uses a mock database to simulate real booking system.
"""

from .base import call_groq, FAST_MODEL
from ..tools.booking_simulator import lookup_pnr, cancel_booking, get_available_flights

BOOKING_SYSTEM = """
You are IndiGo Airlines booking support agent.
Help customers with: PNR lookup, cancellations, date changes, refund status.

MOCK BOOKING DATA (use this for your responses):
{booking_data}

RULES:
1. Always ask for PNR if not provided
2. Be specific about fees and timelines
3. For actual changes, say "I've initiated the request"
4. Cancellation: 24hr = full refund, <24hr = 50% refund, <2hr = no refund
5. Always confirm before processing any change

Is there anything else I can help you with?
"""


def booking_agent_answer(user_message: str, chat_history: list) -> str:
    """
    Handle booking-related queries with mock data simulation.
    """
    # ── Extract PNR from message if present ──────────────────────────────────
    pnr = _extract_pnr(user_message)
    booking_data = "No PNR found in message. Please ask user for their PNR number."

    if pnr:
        data = lookup_pnr(pnr)
        if data:
            booking_data = f"""
PNR: {data['pnr']}
Flight: {data['flight']}
Route: {data['from']} → {data['to']}
Date: {data['date']}
Passenger: {data['passenger']}
Status: {data['status']}
Seat: {data['seat']}
"""
        else:
            booking_data = f"PNR '{pnr}' not found in system."

    # ── Check for cancellation request ───────────────────────────────────────
    if pnr and any(w in user_message.lower() for w in ["cancel", "cancellation", "refund"]):
        cancel_result = cancel_booking(pnr)
        booking_data += f"\nCancellation Status: {cancel_result}"

    messages = [
        {"role": "system", "content": BOOKING_SYSTEM.format(booking_data=booking_data)},
        *chat_history[-4:],
        {"role": "user", "content": user_message},
    ]

    return call_groq(messages, model=FAST_MODEL)


def _extract_pnr(text: str) -> str | None:
    """Extract PNR (6 alphanumeric chars) from text."""
    import re
    match = re.search(r'\b[A-Z]{2}[0-9A-Z]{4}\b', text.upper())
    return match.group() if match else None
