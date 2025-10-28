#!/usr/bin/env bash
# run.sh - start the API locally
export PYTHONPATH=$(pwd)
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1 --reload
