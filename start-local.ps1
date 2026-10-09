# Run OrionForge locally (Windows). No account, no hosted services, no API keys required to start.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment (.venv)..."
    python -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
# The app defaults to cache-only model loading (for the hosted deploy). On a fresh machine, allow the one-time download.
$env:HF_HUB_OFFLINE = "0"; $env:TRANSFORMERS_OFFLINE = "0"
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
Set-Location orion-ui-standalone
$port = if ($env:PORT) { $env:PORT } else { "8989" }
Write-Host "OrionForge is starting on http://localhost:$port  (first launch downloads a ~90 MB embedding model)"
python -m uvicorn web.app:app --host 127.0.0.1 --port $port
