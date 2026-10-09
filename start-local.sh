#!/usr/bin/env bash
# Run OrionForge locally (macOS / Linux). No account, no hosted services, no API keys required to start.
set -e
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
if [ ! -d .venv ]; then
  echo "Creating virtual environment (.venv)..."
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
# The app defaults to cache-only model loading (for the hosted deploy). On a fresh machine, allow the one-time download.
export HF_HUB_OFFLINE=0 TRANSFORMERS_OFFLINE=0
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
cd orion-ui-standalone
echo "OrionForge is starting on http://localhost:8989  (first launch downloads a ~90 MB embedding model)"
exec python -m uvicorn web.app:app --host 127.0.0.1 --port "${PORT:-8989}"
