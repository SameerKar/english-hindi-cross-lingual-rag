#!/usr/bin/env bash
# English-Hindi Cross-Lingual Academic RAG Platform Launcher (macOS & Linux)

set -e

echo "====================================================================="
echo "  English-Hindi Cross-Lingual Academic RAG Experimentation Platform"
echo "====================================================================="
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 is not installed or not in PATH."
    echo "Please install Python 3.10+ from https://www.python.org/ or via your package manager."
    exit 1
fi

# 2. Resolve script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

if [ -f "cross_lingual_rag/server.py" ]; then
    cd cross_lingual_rag
fi

# 3. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "[*] Activating virtual environment..."
source .venv/bin/activate

# 4. Check & Install Dependencies
echo "[*] Checking dependencies..."
if ! python3 -c "import fastapi, uvicorn, pypdf, sentence_transformers, deep_translator" &> /dev/null; then
    echo "[*] Installing dependencies from requirements.txt..."
    pip install -r requirements.txt || echo "[WARNING] Some dependencies failed to install."
fi

# 5. Setup Environment File
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "[*] Initializing .env from .env.example..."
    cp .env.example .env
fi

# 6. Launch Browser and Server
PORT=8000
echo "[*] Starting Cross-Lingual RAG Studio on http://127.0.0.1:${PORT}..."

if command -v xdg-open &> /dev/null; then
    xdg-open "http://127.0.0.1:${PORT}" &
elif command -v open &> /dev/null; then
    open "http://127.0.0.1:${PORT}" &
fi

python3 server.py

