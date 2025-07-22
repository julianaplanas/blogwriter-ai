#!/bin/bash
echo "🚀 Starting AI Blog Writer Backend in Production Mode..."

# Load environment variables
export ENVIRONMENT=production

# Start the server
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
