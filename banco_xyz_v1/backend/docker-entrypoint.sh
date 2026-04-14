#!/usr/bin/env bash
set -e

python -m app.bootstrap_vectorstore
exec uvicorn app.main:app --host 0.0.0.0 --port 8000