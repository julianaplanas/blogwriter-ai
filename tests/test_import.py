#!/usr/bin/env python3
"""
Simple test to verify that the FastAPI app can be imported correctly.
Run this from the tests directory to test the import.
"""

import sys
import os

# Add paths to import from backend and src directories
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, 'backend')
src_dir = os.path.join(project_root, 'src')

sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)
sys.path.insert(0, src_dir)

try:
    print(f"Current directory: {current_dir}")
    print(f"Project root: {project_root}")
    print(f"Backend directory: {backend_dir}")
    print(f"Src directory: {src_dir}")
    print(f"Backend directory exists: {os.path.exists(backend_dir)}")
    print(f"Src directory exists: {os.path.exists(src_dir)}")
    print(f"Files in backend: {os.listdir(backend_dir) if os.path.exists(backend_dir) else 'N/A'}")
    print(f"Files in src: {os.listdir(src_dir) if os.path.exists(src_dir) else 'N/A'}")
    
    # Import from backend/main.py
    sys.path.insert(0, backend_dir)
    import main
    app = main.app
    print(f"[+] Successfully imported app: {app}")
    print(f"App type: {type(app)}")
    
    # Test that it's a FastAPI instance
    print(f"FastAPI title: {app.title}")
    print("[+] App import test passed!")
    # Test that it's a FastAPI instance
    print(f"FastAPI title: {app.title}")
    print("✅ App import test passed!")
    
except Exception as e:
    print(f"[-] Failed to import app: {e}")
    import traceback
    traceback.print_exc()
