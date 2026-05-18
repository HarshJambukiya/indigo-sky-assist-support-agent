# ✈️ IndiGo Airlines AI Customer Service Chatbot

> Multi-Agent | RAG | Human Handoff | Resume Parser | Google Colab + FastAPI

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green) ![Groq](https://img.shields.io/badge/Groq-LLaMA3-orange) ![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-purple) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 What This Project Does

A **production-grade AI customer service system** for IndiGo Airlines with:

- 🤖 **6 Specialized AI Agents** — Triage, FAQ, Booking, Baggage, Handoff, Resume
- 📚 **RAG Pipeline** — Retrieval-Augmented Generation over policy docs
- 🔁 **Agent Handoff** — Smart routing between agents with state passing
- 🧠 **Memory** — Chat history persisted across turns
- 📄 **Resume Upload** — Parse your CV and get career answers
- 👤 **Human Handoff Simulation** — Escalation with notification
- ⚡ **Groq LLM** — Ultra-fast llama3 inference (free tier)

---

## 🏗️ Architecture

```
User → Lovable UI → ngrok → FastAPI (Colab) → Agent Router
                                                    ├── Triage Agent (Groq)
                                                    ├── FAQ Agent (ChromaDB RAG)
                                                    ├── Booking Agent (Mock DB)
                                                    ├── Baggage Agent (Policy RAG)
                                                    ├── Handoff Agent (Escalation)
                                                    └── Resume Agent (PyMuPDF)
                                              ChromaDB ← Google Drive
                                              SQLite   ← Google Drive
```

---

## 🛠️ Tech Stack (All Free)

| Layer | Tool |
|-------|------|
| LLM | Groq API (llama3-70b / llama3-8b) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB (persisted to Google Drive) |
| Backend | FastAPI + uvicorn |
| Runtime | Google Colab (free T4 GPU) |
| Public URL | ngrok free tunnel |
| Storage | Google Drive (15GB free) |
| Frontend | Lovable + plain HTML |
| Orchestration | n8n cloud free |
| Deploy (prod) | Render.com + Vercel |

---

## 🚀 Quick Start (Google Colab)

1. Upload `colab_notebooks/00_setup.py` to Colab
2. Add secrets: `GROQ_API_KEY`, `NGROK_AUTH_TOKEN`
3. Run all cells in order
4. Copy the ngrok URL printed in Cell 4
5. Open `frontend/index.html` and paste the URL

---

## 📁 Project Structure

```
indigo-ai-support/
├── backend/
│   ├── main.py              ← FastAPI app entry point
│   ├── agents/              ← All 6 AI agents
│   ├── rag/                 ← RAG pipeline
│   ├── memory/              ← Chat history
│   ├── tools/               ← Helper tools
│   ├── api/                 ← Routes + schemas
│   └── data/                ← FAQs + policy docs
├── colab_notebooks/         ← Ready-to-run Colab cells
├── frontend/                ← Chat UI (HTML + JS)
├── n8n-workflows/           ← n8n JSON exports
└── requirements.txt
```

---

## 📄 License

MIT — Free to use, modify, share.

---

*Built for AI Hackathon 2026 | Google Colab + Groq + ChromaDB*
