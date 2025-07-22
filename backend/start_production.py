#!/usr/bin/env python3
"""
Production start script for Render deployment
Simplified and robust version focused on production deployment.
"""

import os
import sys
import logging

# Simple logging configuration for Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def main():
    """Start the FastAPI application for production."""
    logger.info("Starting AI Blog Writer Backend for Render...")
    
    # Get port from Render's environment variable
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Port: {port}")
    
    # Log basic environment info
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python version: {sys.version.split()[0]}")
    
    # Check if main.py exists
    if not os.path.exists('main.py'):
        logger.error("main.py not found in current directory")
        logger.error(f"Directory contents: {os.listdir('.')}")
        sys.exit(1)
    
    try:
        # Import uvicorn and the app
        import uvicorn
        logger.info("Uvicorn imported successfully")
        
        # Import the FastAPI app
        from main import app
        logger.info(f"FastAPI app imported: {type(app)}")
        
        # Start the server with minimal configuration
        logger.info(f"Starting server on 0.0.0.0:{port}")
        uvicorn.run(
            "main:app",  # Use string reference instead of app object
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        # List what's available in the current directory
        logger.error("Available files:")
        for file in os.listdir('.'):
            logger.error(f"  {file}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
