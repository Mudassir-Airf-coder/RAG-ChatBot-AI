#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "Checking Qdrant..."
if ! curl -sf http://localhost:6333/collections > /dev/null 2>&1; then
    echo "Qdrant not running. Starting container..."
    docker rm -f rag-qdrant 2>/dev/null || true
    docker run -d --name rag-qdrant -p 6333:6333 qdrant/qdrant > /dev/null
    echo "Waiting for Qdrant..."
    for i in $(seq 1 20); do
        curl -sf http://localhost:6333/collections > /dev/null 2>&1 && break
        sleep 1
    done
fi
echo "Qdrant ready."

echo "Starting backend..."
uv run uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --reload-dir app \
    --reload-dir tests \
    --reload-exclude '*.pyc' \
    --reload-exclude '__pycache__/*' \
    --reload-exclude '.venv/*' \
    --reload-exclude 'uploads/*' \
    --reload-exclude 'data/*' \
    --reload-exclude '.pytest_cache/*'
