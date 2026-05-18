"""
backend/agents/resume_agent.py
-------------------------------
Resume Agent — parses uploaded CVs and answers career/job questions.
Stores resume chunks in a user-specific ChromaDB collection.
"""

from .base import call_groq, SMART_MODEL

RESUME_SYSTEM = """
You are IndiGo Airlines career counselor and HR assistant.

A candidate has uploaded their resume. Use the RESUME CONTENT below to:
1. Answer questions about their qualifications
2. Match their skills to IndiGo job roles
3. Suggest improvements to their application
4. Explain if they qualify for specific positions

CANDIDATE RESUME:
{resume_context}

AVAILABLE INDIGO ROLES TO MATCH:
- Cabin Crew: 12th pass, 18-27 years, 155cm+ height, fluent English
- Ground Staff: Graduate, customer service experience, local language
- Pilot: DGCA CPL, 200+ hours flying experience
- IT Engineer: B.Tech CS/IT, Python/Java, 1-3 years experience
- Data Analyst: Statistics background, SQL, Python/R experience

Be encouraging but honest. Always suggest next steps.
"""


def resume_agent_answer(user_message: str, chat_history: list, retriever, session_id: str) -> str:
    """
    Answer career/resume questions using user's uploaded resume as context.

    Args:
        user_message : User's question about their resume / career
        chat_history : Past messages
        retriever    : RAG retriever (will search user's personal collection)
        session_id   : Used to find the user's resume collection in ChromaDB
    """
    # Retrieve from user's personal resume collection
    resume_context = retriever.retrieve_from_user_collection(
        query=user_message,
        session_id=session_id,
        n_results=5
    )

    if not resume_context:
        return (
            "I don't see a resume uploaded yet! 📄\n\n"
            "Please use the **Upload Resume** button to share your CV, "
            "and I'll analyze it and answer your career questions."
        )

    messages = [
        {"role": "system", "content": RESUME_SYSTEM.format(resume_context=resume_context)},
        *chat_history[-4:],
        {"role": "user", "content": user_message},
    ]

    return call_groq(messages, model=SMART_MODEL)  # Use smarter model for career advice
