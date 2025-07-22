#!/usr/bin/env python3
"""
Enhanced Render-compatible FastAPI app with AI functionality
Building on successful basic deployment
"""

import os
import sys
import logging
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Simple database setup using built-in sqlite3
def init_database():
    """Initialize simple SQLite database."""
    conn = sqlite3.connect('blog_posts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blog_posts (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            word_count INTEGER,
            created_at TEXT,
            metadata TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized")

def create_app():
    """Create FastAPI app with enhanced functionality."""
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    
    # Initialize database
    init_database()
    
    app = FastAPI(
        title="AI-Powered Blog Writer API",
        description="Generate and edit blog posts using AI agents",
        version="1.0.1"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    def read_root():
        return {
            "message": "AI Blog Writer API", 
            "status": "running",
            "version": "1.0.1",
            "features": ["basic blog generation", "database storage"]
        }
    
    @app.get("/health")
    def health_check():
        # Test AI service availability
        ai_status = "unknown"
        try:
            import groq
            ai_status = "available"
        except ImportError:
            ai_status = "disabled"
        
        return {
            "status": "healthy",
            "service": "AI Blog Writer Backend",
            "version": "1.0.1",
            "dependencies": {
                "groq": ai_status,
                "database": "sqlite3 (built-in)",
                "images": "disabled for now"
            }
        }
    
    @app.post("/generate")
    def generate_blog_post(request: Dict[str, Any]):
        """Generate a blog post with AI (if available)."""
        topic = request.get("topic", "Default Topic")
        
        try:
            # Try to use Groq for AI generation
            import groq
            
            # Initialize Groq client
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not set")
            
            client = groq.Groq(api_key=api_key)
            
            # Generate blog post
            prompt = f"Write a comprehensive blog post about {topic}. Include an introduction, main content with key points, and a conclusion."
            
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            word_count = len(content.split())
            
            # Save to database
            post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            conn = sqlite3.connect('blog_posts.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO blog_posts (id, topic, content, word_count, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                post_id,
                topic,
                content,
                word_count,
                datetime.now().isoformat(),
                json.dumps({"provider": "groq", "model": "llama3-70b-8192"})
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "id": post_id,
                "topic": topic,
                "content": content,
                "word_count": word_count,
                "status": "success",
                "metadata": {
                    "provider": "groq",
                    "model": "llama3-70b-8192",
                    "created_at": datetime.now().isoformat()
                }
            }
            
        except ImportError:
            # Fallback to simple text generation
            content = f"""# {topic}

This is a sample blog post about {topic}. 

## Introduction
Welcome to this discussion about {topic}. This is an important topic that deserves attention.

## Main Content
Here are some key points about {topic}:

- Point 1: {topic} is relevant in today's world
- Point 2: Understanding {topic} can help in various scenarios
- Point 3: {topic} has multiple applications and benefits

## Conclusion
In conclusion, {topic} is a fascinating subject that continues to evolve. This basic implementation will be enhanced with AI capabilities once dependencies are fully working.

*Note: This is a fallback response. Enable Groq API for AI-generated content.*
"""
            
            word_count = len(content.split())
            post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Save to database
            conn = sqlite3.connect('blog_posts.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO blog_posts (id, topic, content, word_count, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                post_id,
                topic,
                content,
                word_count,
                datetime.now().isoformat(),
                json.dumps({"provider": "fallback", "model": "template"})
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "id": post_id,
                "topic": topic,
                "content": content,
                "word_count": word_count,
                "status": "success (fallback mode)",
                "metadata": {
                    "provider": "fallback",
                    "model": "template",
                    "created_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating blog post: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate blog post: {str(e)}")
    
    @app.get("/posts")
    def list_posts():
        """List all blog posts."""
        try:
            conn = sqlite3.connect('blog_posts.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, topic, word_count, created_at, metadata
                FROM blog_posts
                ORDER BY created_at DESC
                LIMIT 20
            ''')
            
            posts = []
            for row in cursor.fetchall():
                posts.append({
                    "id": row[0],
                    "topic": row[1],
                    "word_count": row[2],
                    "created_at": row[3],
                    "metadata": json.loads(row[4]) if row[4] else {}
                })
            
            conn.close()
            
            return {
                "posts": posts,
                "count": len(posts),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error listing posts: {e}")
            return {"posts": [], "error": str(e)}
    
    @app.get("/post/{post_id}")
    def get_post(post_id: str):
        """Get a specific blog post."""
        try:
            conn = sqlite3.connect('blog_posts.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, topic, content, word_count, created_at, metadata
                FROM blog_posts
                WHERE id = ?
            ''', (post_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                raise HTTPException(status_code=404, detail="Post not found")
            
            return {
                "id": row[0],
                "topic": row[1],
                "content": row[2],
                "word_count": row[3],
                "created_at": row[4],
                "metadata": json.loads(row[5]) if row[5] else {}
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting post: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

def main():
    """Start the enhanced FastAPI application."""
    logger.info("Starting AI Blog Writer Backend (Enhanced mode)...")
    
    # Get port
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Port: {port}")
    
    # Create app
    app = create_app()
    logger.info("Enhanced FastAPI app created successfully")
    
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
