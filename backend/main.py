#!/usr/bin/env python3
"""
Render-compatible FastAPI app with AI via direct HTTP requests
Avoids groq package by using direct API calls
"""

import os
import sys
import logging
import sqlite3
import json
import requests
import threading
from datetime import datetime
from typing import Dict, Any
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Database lock for thread safety
db_lock = threading.Lock()

@contextmanager
def get_db_connection():
    """Context manager for database connections to prevent locking issues."""
    with db_lock:
        conn = None
        try:
            # Set connection timeout and enable WAL mode for better concurrency
            conn = sqlite3.connect('blog_posts.db', timeout=30.0)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.execute('PRAGMA temp_store=memory')
            conn.execute('PRAGMA mmap_size=268435456')  # 256MB
            yield conn
        finally:
            if conn:
                conn.close()

def init_database():
    """Initialize simple SQLite database with proper schema migration."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create table with all columns
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
        
        # Check if metadata column exists and add it if missing
        cursor.execute("PRAGMA table_info(blog_posts)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'metadata' not in columns:
            logger.info("Adding metadata column to existing table")
            cursor.execute('ALTER TABLE blog_posts ADD COLUMN metadata TEXT')
            # Update existing rows with default metadata
            cursor.execute('''
                UPDATE blog_posts 
                SET metadata = '{"provider": "legacy", "model": "unknown"}' 
                WHERE metadata IS NULL
            ''')
        
        conn.commit()
        logger.info("Database initialized with proper schema")

def generate_with_groq_api(topic: str, api_key: str) -> str:
    """Generate blog content using direct Groq API calls."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"Write a comprehensive blog post about {topic}. Include an introduction, main content with key points, and a conclusion. Make it engaging and informative."
    
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    return result["choices"][0]["message"]["content"]

def create_app():
    """Create FastAPI app with AI functionality via HTTP requests."""
    # Initialize database
    init_database()
    
    app = FastAPI(
        title="AI-Powered Blog Writer API",
        description="Generate and edit blog posts using AI agents",
        version="1.1.0"
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
            "version": "1.1.0",
            "features": ["AI blog generation", "database storage", "direct API calls"]
        }
    
    @app.get("/health")
    def health_check():
        # Test API key availability
        api_key = os.getenv("GROQ_API_KEY")
        ai_status = "available" if api_key else "missing API key"
        
        return {
            "status": "healthy",
            "service": "AI Blog Writer Backend",
            "version": "1.1.0",
            "dependencies": {
                "groq": f"direct API - {ai_status}",
                "database": "sqlite3 (built-in)",
                "http_client": "requests"
            }
        }
    
    @app.post("/generate")
    def generate_blog_post(request: Dict[str, Any]):
        """Generate a blog post using direct Groq API calls."""
        topic = request.get("topic", "Technology Trends")
        
        try:
            # Try to use Groq API directly
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not set")
            
            logger.info(f"Generating blog post about: {topic}")
            content = generate_with_groq_api(topic, api_key)
            word_count = len(content.split())
            
            # Save to database
            post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO blog_posts (id, topic, content, word_count, sources, images, provider, model, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post_id,
                    topic,
                    content,
                    word_count,
                    "",  # sources
                    "",  # images
                    "groq-direct",  # provider
                    "llama3-70b-8192",  # model
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),  # updated_at
                    json.dumps({"provider": "groq-direct", "model": "llama3-70b-8192"})
                ))
                
                conn.commit()
            
            logger.info(f"Successfully generated blog post: {post_id}")
            
            return {
                "id": post_id,
                "topic": topic,
                "content": content,
                "word_count": word_count,
                "status": "success",
                "metadata": {
                    "provider": "groq-direct",
                    "model": "llama3-70b-8192",
                    "created_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.warning(f"AI generation failed: {e}, using fallback")
            
            # Fallback to template generation
            content = f"""# {topic}

This is a comprehensive blog post about {topic}.

## Introduction

{topic} is an important subject that deserves careful consideration in today's rapidly evolving landscape. Understanding the nuances and implications of {topic} can provide valuable insights for both professionals and enthusiasts.

## Key Points

### Understanding {topic}

{topic} encompasses several important aspects that are worth exploring:

- **Relevance**: {topic} plays a crucial role in modern applications
- **Impact**: The influence of {topic} extends across multiple domains  
- **Future Outlook**: {topic} continues to evolve with emerging trends

### Practical Applications

The practical applications of {topic} include:

1. **Industry Integration**: How {topic} is being adopted across industries
2. **Best Practices**: Proven approaches for implementing {topic}
3. **Common Challenges**: Typical obstacles and how to overcome them

### Benefits and Considerations

When working with {topic}, consider these benefits:

- Enhanced efficiency and productivity
- Improved decision-making capabilities  
- Better resource optimization
- Increased competitive advantage

## Implementation Strategies

To successfully implement {topic} in your context:

1. **Assessment**: Evaluate your current situation and needs
2. **Planning**: Develop a comprehensive strategy
3. **Execution**: Implement changes systematically
4. **Monitoring**: Track progress and adjust as needed

## Conclusion

{topic} represents a significant opportunity for growth and improvement. By understanding its core principles and practical applications, organizations and individuals can leverage {topic} to achieve their goals more effectively.

The key to success lies in careful planning, thoughtful implementation, and continuous learning. As {topic} continues to evolve, staying informed and adaptable will be crucial for maximizing its benefits.

---

*Note: This content was generated using a fallback template. Enable AI functionality by setting the GROQ_API_KEY environment variable.*
"""
            
            word_count = len(content.split())
            post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Save to database
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO blog_posts (id, topic, content, word_count, sources, images, provider, model, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post_id,
                    topic,
                    content,
                    word_count,
                    "",  # sources
                    "",  # images  
                    "fallback",  # provider
                    "template",  # model
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),  # updated_at
                    json.dumps({"provider": "fallback", "model": "template"})
                ))
                
                conn.commit()
            
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
    
    @app.get("/posts")
    def list_posts():
        """List all blog posts."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, topic, word_count, created_at, metadata
                    FROM blog_posts
                    ORDER BY created_at DESC
                    LIMIT 20
                ''')
                
                posts = []
                for row in cursor.fetchall():
                    metadata = {}
                    try:
                        if row[4]:  # metadata column
                            metadata = json.loads(row[4])
                    except (json.JSONDecodeError, TypeError):
                        metadata = {"provider": "legacy", "model": "unknown"}
                    
                    posts.append({
                        "id": row[0],
                        "topic": row[1],
                        "word_count": row[2],
                        "created_at": row[3],
                        "metadata": metadata
                    })
                
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
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, topic, content, word_count, created_at, metadata
                    FROM blog_posts
                    WHERE id = ?
                ''', (post_id,))
                
                row = cursor.fetchone()
                
                if not row:
                    raise HTTPException(status_code=404, detail="Post not found")
                
                metadata = {}
                try:
                    if row[5]:  # metadata column
                        metadata = json.loads(row[5])
                except (json.JSONDecodeError, TypeError):
                    metadata = {"provider": "legacy", "model": "unknown"}
                
                return {
                    "id": row[0],
                    "topic": row[1],
                    "content": row[2],
                    "word_count": row[3],
                    "created_at": row[4],
                    "metadata": metadata
                }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting post: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

def main():
    """Start the FastAPI application."""
    logger.info("Starting AI Blog Writer Backend (Direct API mode)...")
    
    # Get port
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Port: {port}")
    
    # Create app
    app = create_app()
    logger.info("FastAPI app with direct API integration created successfully")
    
    # Start server
    import uvicorn
    logger.info(f"Starting server on 0.0.0.0:{port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

# Create app instance at module level for uvicorn compatibility
app = create_app()

if __name__ == "__main__":
    main()
