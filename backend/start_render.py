#!/usr/bin/env python3
"""
Render-compatible FastAPI app
This version avoids Rust dependencies while maintaining core functionality
"""

import os
import sys
import logging
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def create_app():
    """Create FastAPI app compatible with older pydantic."""
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(
        title="AI-Powered Blog Writer API",
        description="Generate and edit blog posts using AI agents",
        version="1.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Temporarily allow all for testing
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    def read_root():
        return {
            "message": "AI Blog Writer API", 
            "status": "running",
            "version": "1.0.0"
        }
    
    @app.get("/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "AI Blog Writer Backend",
            "version": "1.0.0",
            "dependencies": {
                "groq": "disabled (avoiding rust deps)",
                "database": "basic mode",
                "images": "disabled"
            }
        }
    
    @app.post("/generate")
    def generate_blog_post(request: Dict[str, Any]):
        """Placeholder endpoint - will implement once dependencies are working."""
        return {
            "message": "Blog generation temporarily disabled",
            "reason": "Avoiding Rust dependencies for initial deployment",
            "request_received": request
        }
    
    @app.get("/posts")
    def list_posts():
        """Placeholder endpoint."""
        return {
            "posts": [],
            "message": "Database disabled for initial deployment"
        }
    
    return app

def main():
    """Start the FastAPI application."""
    logger.info("Starting AI Blog Writer Backend (Render-compatible mode)...")
    
    # Get port
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Port: {port}")
    
    # Create app
    app = create_app()
    logger.info("FastAPI app created successfully")
    
    # Start server
    import uvicorn
    logger.info(f"Starting server on 0.0.0.0:{port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
