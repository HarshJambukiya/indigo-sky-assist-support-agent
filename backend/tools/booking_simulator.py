"""
backend/tools/booking_simulator.py
------------------------------------
Mock booking database.
Simulates a real airline booking system for demo purposes.
"""

from datetime import datetime, timedelta

# ── Mock flight database ──────────────────────────────────────────────────────
MOCK_BOOKINGS = {
    "AB1234": {
        "pnr"      : "AB1234",
        "flight"   : "6E-204",
        "from"     : "Delhi (DEL)",
        "to"       : "Mumbai (BOM)",
        "date"     : "2026-07-15",
        "time"     : "06:30",
        "passenger": "Rahul Sharma",
        "status"   : "Confirmed",
        "seat"     : "14A",
        "class"    : "Economy",
        "fare"     : "₹4,250",
    },
    "CD5678": {
        "pnr"      : "CD5678",
        "flight"   : "6E-502",
        "from"     : "Bangalore (BLR)",
        "to"       : "Hyderabad (HYD)",
        "date"     : "2026-07-20",
        "time"     : "14:15",
        "passenger": "Priya Patel",
        "status"   : "Confirmed",
        "seat"     : "22C",
        "class"    : "Economy",
        "fare"     : "₹3,100",
    },
    "EF9012": {
        "pnr"      : "EF9012",
        "flight"   : "6E-801",
        "from"     : "Chennai (MAA)",
        "to"       : "Kolkata (CCU)",
        "date"     : "2026-06-30",
        "time"     : "09:45",
        "passenger": "Amit Kumar",
        "status"   : "Cancelled",
        "seat"     : "8B",
        "class"    : "Economy",
        "fare"     : "₹5,600",
    },
}

# ── Mock available flights ─────────────────────────────────────────────────
MOCK_FLIGHTS = [
    {"flight": "6E-204", "from": "Delhi", "to": "Mumbai",    "date": "2026-07-20", "fare": "₹3,999"},
    {"flight": "6E-310", "from": "Mumbai", "to": "Delhi",    "date": "2026-07-21", "fare": "₹4,200"},
    {"flight": "6E-502", "from": "Bangalore", "to": "Delhi", "date": "2026-07-22", "fare": "₹5,100"},
]


def lookup_pnr(pnr: str) -> dict | None:
    """Look up a booking by PNR. Returns booking dict or None."""
    return MOCK_BOOKINGS.get(pnr.upper())


def cancel_booking(pnr: str) -> str:
    """
    Simulate booking cancellation with refund calculation.
    Rules: 24hr+ = full, <24hr = 50%, <2hr = no refund
    """
    booking = MOCK_BOOKINGS.get(pnr.upper())
    if not booking:
        return f"PNR {pnr} not found."

    if booking["status"] == "Cancelled":
        return "This booking is already cancelled."

    # Simulate refund based on time (always show full refund in demo)
    MOCK_BOOKINGS[pnr]["status"] = "Cancelled"
    return (
        f"Booking {pnr} successfully cancelled. "
        f"Refund of {booking['fare']} will be processed in 5-7 business days."
    )


def get_available_flights(origin: str = None, destination: str = None) -> list[dict]:
    """Return mock available flights, optionally filtered."""
    if origin and destination:
        return [
            f for f in MOCK_FLIGHTS
            if origin.lower() in f["from"].lower()
            and destination.lower() in f["to"].lower()
        ]
    return MOCK_FLIGHTS
