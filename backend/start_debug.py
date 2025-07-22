#!/usr/bin/env python3
"""
Minimal start script for debugging Render deployment issues
"""

import os
import sys

def main():
    """Minimal FastAPI startup for debugging."""
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir('.')}")
    print(f"PORT environment variable: {os.environ.get('PORT', 'Not set')}")
    
    # Check if main.py exists
    if not os.path.exists('main.py'):
        print("ERROR: main.py not found!")
        sys.exit(1)
    
    # Try to import uvicorn
    try:
        import uvicorn
        print("✓ uvicorn imported successfully")
    except ImportError as e:
        print(f"ERROR: Cannot import uvicorn: {e}")
        sys.exit(1)
    
    # Try to import the app
    try:
        from main import app
        print(f"✓ FastAPI app imported: {type(app)}")
    except Exception as e:
        print(f"ERROR: Cannot import app from main: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Start server
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting server on port {port}...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=port,
        log_level="debug"
    )

if __name__ == "__main__":
    main()
