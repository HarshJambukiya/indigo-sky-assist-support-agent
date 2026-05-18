# ==============================================================================
# GOOGLE COLAB SETUP NOTEBOOK — indigo-ai-support
# Copy each section into a separate Colab cell and run in order.
# ==============================================================================


# ── CELL 1: Mount Google Drive ─────────────────────────────────────────────────
"""
CELL 1 — Run this EVERY time you open Colab
"""
from google.colab import drive
drive.mount('/content/drive')

import os

PROJECT_DIR = '/content/drive/MyDrive/indigo-ai-support'
os.makedirs(f'{PROJECT_DIR}/chroma_db', exist_ok=True)
os.makedirs(f'{PROJECT_DIR}/uploads',   exist_ok=True)
os.makedirs(f'{PROJECT_DIR}/docs',      exist_ok=True)

print("✅ Google Drive mounted")
print(f"📁 Project folder: {PROJECT_DIR}")


# ── CELL 2: Install Dependencies ───────────────────────────────────────────────
"""
CELL 2 — Install all required packages
Takes ~2-3 minutes the first time
"""
!pip install -q \
    fastapi==0.110.0 \
    uvicorn[standard]==0.29.0 \
    pyngrok==7.1.6 \
    groq==0.8.0 \
    chromadb==0.5.0 \
    sentence-transformers==2.7.0 \
    pymupdf==1.24.1 \
    python-multipart==0.0.9 \
    aiofiles==23.2.1 \
    nest_asyncio==1.6.0 \
    pydantic==2.7.1

print("✅ All packages installed!")


# ── CELL 3: Load API Keys from Colab Secrets ───────────────────────────────────
"""
CELL 3 — Set API Keys
BEFORE running this:
  1. Click the 🔑 (Secrets) icon in the Colab left sidebar
  2. Add these secrets:
     - GROQ_API_KEY       → get from console.groq.com (free)
     - NGROK_AUTH_TOKEN   → get from dashboard.ngrok.com (free)
"""
from google.colab import userdata

os.environ['GROQ_API_KEY']       = userdata.get('GROQ_API_KEY')
os.environ['NGROK_AUTH_TOKEN']   = userdata.get('NGROK_AUTH_TOKEN')

# Set Google Drive paths for all services
os.environ['CHROMA_PATH'] = f'{PROJECT_DIR}/chroma_db'
os.environ['SQLITE_PATH'] = f'{PROJECT_DIR}/chat_history.db'
os.environ['UPLOAD_DIR']  = f'{PROJECT_DIR}/uploads'
os.environ['DOCS_DIR']    = f'{PROJECT_DIR}/docs'

print("✅ API keys loaded from Colab Secrets")
print(f"   GROQ_API_KEY:     {'*' * 20}{os.environ['GROQ_API_KEY'][-4:]}")
print(f"   CHROMA_PATH:      {os.environ['CHROMA_PATH']}")
print(f"   SQLITE_PATH:      {os.environ['SQLITE_PATH']}")


# ── CELL 4: Clone/Update GitHub Repo ──────────────────────────────────────────
"""
CELL 4 — Get the project code from GitHub
First time: uncomment the git clone line
Later sessions: just run git pull
"""
import subprocess

REPO_URL  = "https://github.com/YOUR_USERNAME/indigo-ai-support.git"
REPO_DIR  = "/content/indigo-ai-support"

# First time only — uncomment below:
# !git clone {REPO_URL} {REPO_DIR}

# Every session — pull latest changes:
if os.path.exists(REPO_DIR):
    result = subprocess.run(['git', '-C', REPO_DIR, 'pull'], capture_output=True, text=True)
    print(result.stdout or "Already up to date")
else:
    print(f"⚠️  Repo not found at {REPO_DIR}")
    print(f"Run:  !git clone {REPO_URL} {REPO_DIR}")

# Add repo to Python path so imports work
import sys
if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

print(f"✅ Repo ready at {REPO_DIR}")


# ── CELL 5: Start FastAPI + ngrok ─────────────────────────────────────────────
"""
CELL 5 — Launch the server
After running this cell, you'll see a public URL like:
  🚀 FastAPI running at: https://abc123.ngrok-free.app

Copy that URL → paste into your frontend's API_URL setting
"""
import nest_asyncio
import uvicorn
from pyngrok import ngrok, conf
from threading import Thread

nest_asyncio.apply()

# Authenticate ngrok
conf.get_default().auth_token = os.environ['NGROK_AUTH_TOKEN']
ngrok.kill()  # Kill any old tunnels

# Import FastAPI app
from backend.main import app

# Start tunnel
tunnel     = ngrok.connect(8000)
PUBLIC_URL = tunnel.public_url

print("\n" + "="*60)
print(f"🚀 FastAPI running at:  {PUBLIC_URL}")
print(f"📡 API Docs at:         {PUBLIC_URL}/docs")
print(f"❤️  Health check:        {PUBLIC_URL}/health")
print("="*60)
print("\n⚠️  Copy the URL above → paste into your frontend!")

# Start server in background thread (non-blocking)
def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")

server_thread = Thread(target=run_server, daemon=True)
server_thread.start()


# ── CELL 6: Test the API ───────────────────────────────────────────────────────
"""
CELL 6 — Quick test to verify everything works
"""
import requests
import json

BASE_URL = PUBLIC_URL  # From Cell 5

# Test 1: Health check
health = requests.get(f"{BASE_URL}/health").json()
print("Health:", health)

# Test 2: Chat
response = requests.post(f"{BASE_URL}/chat", json={
    "message"    : "What is IndiGo's baggage allowance?",
    "session_id" : "test-session-001"
}).json()

print(f"\n💬 Agent: {response['agent']} (confidence: {response['confidence']})")
print(f"📝 Response:\n{response['response'][:300]}...")

# Test 3: New session
session = requests.get(f"{BASE_URL}/session/new").json()
print(f"\n🆕 New session ID: {session['session_id']}")
