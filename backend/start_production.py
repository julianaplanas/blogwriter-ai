#!/usr/bin/env python3
"""
Production start script for Render deployment
This script provides better error handling and logging for deployment issues.
"""

import os
import sys
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start the FastAPI application with error handling."""
    logger.info("Starting AI Blog Writer Backend...")
    
    # Log environment info
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path[:3]}...")  # First 3 entries
    
    # Check for required environment variables
    required_env_vars = ['BRAVE_API_KEY', 'GROQ_API_KEY', 'PEXELS_API_KEY']
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("The app will still start, but some features may not work")
    else:
        logger.info("All required environment variables are set")
    
    # Get port from environment
    port = int(os.getenv('PORT', 8000))
    logger.info(f"Using port: {port}")
    
    try:
        # Try to import the FastAPI app
        logger.info("Attempting to import FastAPI app...")
        from main import app
        logger.info(f"Successfully imported app: {app}")
        
        # Start the server
        logger.info(f"Starting uvicorn server on 0.0.0.0:{port}")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        logger.error(f"Failed to import FastAPI app: {e}")
        logger.error(f"Working directory: {os.getcwd()}")
        logger.error(f"Directory contents: {os.listdir('.')}")
        
        # Try to see what's in the parent directory
        try:
            parent_dir = os.path.dirname(os.getcwd())
            logger.error(f"Parent directory: {parent_dir}")
            logger.error(f"Parent contents: {os.listdir(parent_dir)}")
        except:
            pass
            
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
