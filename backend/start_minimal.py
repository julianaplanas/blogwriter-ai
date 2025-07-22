#!/usr/bin/env python3
"""
Minimal FastAPI app for testing Render deployment
This bypasses all the complex imports to test basic functionality
"""

import os

def create_minimal_app():
    """Create a minimal FastAPI app without complex dependencies."""
    from fastapi import FastAPI
    
    app = FastAPI(title="Minimal Test App")
    
    @app.get("/")
    def read_root():
        return {"message": "Hello from minimal FastAPI app!"}
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "message": "Minimal app is running"}
    
    return app

def main():
    """Start the minimal app."""
    print("Starting minimal FastAPI app for Render testing...")
    
    # Get port
    port = int(os.environ.get('PORT', 8000))
    print(f"Port: {port}")
    
    # Create app
    app = create_minimal_app()
    print(f"App created: {type(app)}")
    
    # Start server
    import uvicorn
    print(f"Starting server on 0.0.0.0:{port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
