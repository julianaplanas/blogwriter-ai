#!/bin/bash

# AI Blog Writer Backend Startup Script

echo "🚀 Starting AI Blog Writer Backend..."

# Check if we're in the correct directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check for .env file
if [ ! -f "../.env" ]; then
    echo "❌ Error: .env file not found in parent directory."
    echo "Please create a .env file with your API keys:"
    echo "  BRAVE_API_KEY=your_key_here"
    echo "  GROQ_API_KEY=your_key_here"
    echo "  PEXELS_API_KEY=your_key_here (optional)"
    exit 1
fi

# Check for virtual environment
if [ -z "$VIRTUAL_ENV" ] && [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Copy .env file to backend directory if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📋 Copying environment file..."
    cp ../.env .env
fi

# Start the server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation available at http://localhost:8000/docs"
echo "🔄 Server will auto-reload on code changes"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
