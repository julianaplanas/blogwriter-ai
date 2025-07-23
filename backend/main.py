#!/usr/bin/env python3
"""
Heroku-compatible FastAPI app with AI via direct HTTP requests
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
from typing import Dict, Any, List, List
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, rely on system environment
    pass

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
            # Use configurable database path for Heroku
            db_path = os.getenv('DATABASE_PATH', 'blog_posts.db')
            # Set connection timeout and enable WAL mode for better concurrency
            conn = sqlite3.connect(db_path, timeout=30.0)
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
        
        # Create main blog_posts table
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
        
        # Create versions table for edit history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS versions (
                id TEXT PRIMARY KEY,
                post_id TEXT,
                content TEXT NOT NULL,
                instruction TEXT,
                created_at TEXT,
                version_number INTEGER
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
        
        # Add current_version_id column if missing
        cursor.execute("PRAGMA table_info(blog_posts)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'current_version_id' not in columns:
            logger.info("Adding current_version_id column to blog_posts table")
            cursor.execute('ALTER TABLE blog_posts ADD COLUMN current_version_id TEXT')
            cursor.execute('UPDATE blog_posts SET current_version_id = NULL')
        
        conn.commit()
        logger.info("Database initialized with proper schema")

# Import modular agents
from backend.agents import ResearchAgent, WritingAgent, ImageAgent, EditingAgent

# Place helpers at module level
import re

def insert_images_into_markdown(markdown: str, images: list) -> str:
    """
    Insert images after major headings in the markdown, with captions and source attribution.
    Images are distributed as evenly as possible after headings (## or ###).
    """
    if not images:
        return markdown
    lines = markdown.split('\n')
    heading_indices = [i for i, line in enumerate(lines) if re.match(r'^(##+ )', line)]
    if not heading_indices:
        # If no headings, just add all images at the end
        for img in images:
            lines.append(f'![{img["alt"]}]({img["medium_url"]})')
            lines.append(f'*Photo by {img["photographer"]} ([source]({img["url"]}))*')
        return '\n'.join(lines)
    # Distribute images after headings
    img_idx = 0
    for idx in heading_indices:
        if img_idx >= len(images):
            break
        img = images[img_idx]
        caption = f'![{img["alt"]}]({img["medium_url"]})\n*Photo by {img["photographer"]} ([source]({img["url"]}))*'
        lines.insert(idx + 1 + img_idx, caption)
        img_idx += 1
    # If images remain, add them at the end
    for img in images[img_idx:]:
        lines.append(f'![{img["alt"]}]({img["medium_url"]})')
        lines.append(f'*Photo by {img["photographer"]} ([source]({img["url"]}))*')
    return '\n'.join(lines)

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
            "features": [
                "AI blog generation", 
                "database storage", 
                "direct API calls",
                "research integration",
                "image search",
                "enhanced blog generation"
            ]
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
        """Generate a blog post using the WritingAgent."""
        topic = request.get("topic", "Technology Trends")
        try:
            writing_agent = WritingAgent()
            content = writing_agent.generate(topic)
            word_count = len(content.split())
            # Save to database
            post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with get_db_connection() as conn:
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
    
    @app.post("/research")
    def research_topic(request: Dict[str, Any]):
        """Research a topic using the ResearchAgent."""
        topic = request.get("topic", "")
        if not topic:
            raise HTTPException(status_code=400, detail="Topic is required")
        try:
            research_agent = ResearchAgent()
            sources = research_agent.search(topic)
            return {
                "topic": topic,
                "sources": sources,
                "count": len(sources),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Research failed: {e}")
            return {"error": str(e), "sources": []}
    
    @app.post("/images")
    def search_images(request: Dict[str, Any]):
        """Search for images using the ImageAgent."""
        query = request.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        try:
            image_agent = ImageAgent()
            images = image_agent.search(query)
            return {
                "query": query,
                "images": images,
                "count": len(images),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Image search failed: {e}")
            return {"error": str(e), "images": []}
    
    @app.post("/generate-enhanced")
    def generate_enhanced_blog_post(request: Dict[str, Any]):
        """Generate a blog post with research and images using agents."""
        topic = request.get("topic", "Technology Trends")
        try:
            research_agent = ResearchAgent()
            writing_agent = WritingAgent()
            image_agent = ImageAgent()
            # Research
            sources = research_agent.search(topic)
            research_context = ""
            if sources:
                research_context = "\n\nRecent research sources:\n"
                for source in sources[:3]:
                    research_context += f"- {source['title']}: {source['description']}\n"
            # Generate content
            content = writing_agent.generate(topic, research_context)
            # Images
            images = image_agent.search(topic)
            # Insert images into markdown (only in backend)
            content_with_images = insert_images_into_markdown(content, images)
            word_count = len(content_with_images.split())
            post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with get_db_connection() as conn:
                cursor = conn.cursor()
                enhanced_metadata = {
                    "provider": "groq-enhanced",
                    "model": "llama3-70b-8192",
                    "research_enabled": bool(sources),
                    "images_enabled": bool(images),
                    "source_count": len(sources),
                    "image_count": len(images),
                    "sources": sources[:3],
                    "images": images[:3]
                }
                cursor.execute('''
                    INSERT INTO blog_posts (id, topic, content, word_count, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    post_id,
                    topic,
                    content_with_images,
                    word_count,
                    datetime.now().isoformat(),
                    json.dumps(enhanced_metadata)
                ))
                conn.commit()
            logger.info(f"Successfully generated enhanced blog post: {post_id}")
            return {
                "id": post_id,
                "topic": topic,
                "content": content_with_images,
                "word_count": word_count,
                "sources": sources,
                "images": images,
                "status": "success",
                "metadata": {
                    "provider": "groq-enhanced",
                    "model": "llama3-70b-8192",
                    "research_enabled": bool(sources),
                    "images_enabled": bool(images),
                    "created_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Enhanced generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/edit")
    def edit_blog_post(request: Dict[str, Any]):
        """Edit a blog post using the EditingAgent."""
        content = request.get("content", "")
        instruction = request.get("instruction", "")
        if not content or not instruction:
            raise HTTPException(status_code=400, detail="Content and instruction are required")
        try:
            editing_agent = EditingAgent()
            edited_content = editing_agent.edit(content, instruction)
            version_id = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT MAX(version_number) FROM versions WHERE post_id = ?', (request.get("post_id", "current"),))
                max_version = cursor.fetchone()[0] or 0
                cursor.execute('''
                    INSERT INTO versions (id, post_id, content, instruction, created_at, version_number)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    version_id,
                    request.get("post_id", "current"),
                    edited_content,
                    instruction,
                    datetime.now().isoformat(),
                    max_version + 1
                ))
                conn.commit()
            return {
                "content": edited_content,
                "instruction_applied": instruction,
                "model_used": "llama3-70b-8192",
                "provider_used": "groq-direct",
                "edited_at": datetime.now().isoformat(),
                "version_id": version_id,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Edit failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/edit/history/{post_id}")
    def get_version_history(post_id: str = "current"):
        """Get version history for a post."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, content, instruction, created_at, version_number
                    FROM versions 
                    WHERE post_id = ?
                    ORDER BY version_number DESC
                    LIMIT 10
                ''', (post_id,))
                
                versions = []
                for row in cursor.fetchall():
                    versions.append({
                        "version_id": row[0],
                        "content": row[1],
                        "instruction": row[2],
                        "timestamp": row[3],
                        "version_number": row[4]
                    })
                
                # Get current version from blog_posts
                cursor.execute('SELECT current_version_id FROM blog_posts WHERE id = ?', (post_id,))
                row = cursor.fetchone()
                current_version = row[0] if row and row[0] else (versions[0]["version_id"] if versions else None)
                
                return {
                    "versions": versions,
                    "current_version": current_version,
                    "count": len(versions)
                }
                
        except Exception as e:
            logger.error(f"Failed to get version history: {e}")
            return {"versions": [], "current_version": None, "count": 0}
    
    @app.post("/edit/undo/{version_id}")
    def undo_to_version(version_id: str):
        """Revert to a specific version."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get the version content
                cursor.execute('''
                    SELECT content, instruction, post_id, version_number
                    FROM versions 
                    WHERE id = ?
                ''', (version_id,))
                
                row = cursor.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Version not found")
                
                content, instruction, post_id, version_number = row
                
                # Set this version as current in blog_posts
                cursor.execute('UPDATE blog_posts SET current_version_id = ? WHERE id = ?', (version_id, post_id))
                conn.commit()
                
                return {
                    "markdown": content,
                    "version_restored": version_id,
                    "instruction": instruction,
                    "version_number": version_number,
                    "status": "success"
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Undo failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/edit/history/{post_id}")
    def clear_version_history(post_id: str = "current"):
        """Clear version history for a post."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM versions WHERE post_id = ?', (post_id,))
                conn.commit()
                
            return {"status": "success", "message": "Version history cleared"}
            
        except Exception as e:
            logger.error(f"Failed to clear version history: {e}")
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
