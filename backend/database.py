"""
Database manager for storing blog posts and metadata using SQLite
"""

import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from api_models import BlogPost

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    SQLite database manager for blog post persistence
    """
    
    def __init__(self, db_path: str = "blog_posts.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        
    def init_db(self):
        """Initialize the database and create tables"""
        try:
            with self._get_connection() as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS blog_posts (
                        id TEXT PRIMARY KEY,
                        topic TEXT NOT NULL,
                        content TEXT NOT NULL,
                        word_count INTEGER DEFAULT 0,
                        sources TEXT,  -- JSON array of URLs
                        images TEXT,   -- JSON array of image metadata
                        provider TEXT DEFAULT 'groq',
                        model TEXT DEFAULT 'auto',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                ''')
                
                # Create index for faster queries
                conn.execute('CREATE INDEX IF NOT EXISTS idx_topic ON blog_posts(topic)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON blog_posts(created_at)')
                
                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def save_blog_post(self, blog_post: BlogPost) -> bool:
        """
        Save a blog post to the database
        
        Args:
            blog_post: BlogPost model to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO blog_posts 
                    (id, topic, content, word_count, sources, images, provider, model, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    blog_post.id,
                    blog_post.topic,
                    blog_post.content,
                    blog_post.word_count,
                    json.dumps(blog_post.sources),
                    json.dumps(blog_post.images),
                    blog_post.provider,
                    blog_post.model,
                    blog_post.created_at.isoformat(),
                    blog_post.updated_at.isoformat()
                ))
                conn.commit()
                
            logger.info(f"Blog post saved: {blog_post.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save blog post {blog_post.id}: {e}")
            return False
    
    def get_blog_post(self, post_id: str) -> Optional[BlogPost]:
        """
        Retrieve a blog post by ID
        
        Args:
            post_id: Unique identifier of the blog post
            
        Returns:
            BlogPost or None if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    'SELECT * FROM blog_posts WHERE id = ?',
                    (post_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return self._row_to_blog_post(row)
                
        except Exception as e:
            logger.error(f"Failed to retrieve blog post {post_id}: {e}")
            return None
    
    def list_blog_posts(self, limit: int = 10, offset: int = 0) -> List[BlogPost]:
        """
        List blog posts with pagination
        
        Args:
            limit: Maximum number of posts to return
            offset: Number of posts to skip
            
        Returns:
            List of BlogPost objects
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    'SELECT * FROM blog_posts ORDER BY created_at DESC LIMIT ? OFFSET ?',
                    (limit, offset)
                )
                rows = cursor.fetchall()
                
                return [self._row_to_blog_post(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to list blog posts: {e}")
            return []
    
    def delete_blog_post(self, post_id: str) -> bool:
        """
        Delete a blog post by ID
        
        Args:
            post_id: Unique identifier of the blog post
            
        Returns:
            bool: True if deleted, False if not found or error
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    'DELETE FROM blog_posts WHERE id = ?',
                    (post_id,)
                )
                conn.commit()
                
                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Blog post deleted: {post_id}")
                else:
                    logger.warning(f"Blog post not found for deletion: {post_id}")
                    
                return deleted
                
        except Exception as e:
            logger.error(f"Failed to delete blog post {post_id}: {e}")
            return False
    
    def search_blog_posts(self, query: str, limit: int = 10) -> List[BlogPost]:
        """
        Search blog posts by topic or content
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching BlogPost objects
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    '''
                    SELECT * FROM blog_posts 
                    WHERE topic LIKE ? OR content LIKE ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                    ''',
                    (f'%{query}%', f'%{query}%', limit)
                )
                rows = cursor.fetchall()
                
                return [self._row_to_blog_post(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to search blog posts: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with database stats
        """
        try:
            with self._get_connection() as conn:
                # Total posts
                total_cursor = conn.execute('SELECT COUNT(*) as total FROM blog_posts')
                total = total_cursor.fetchone()['total']
                
                # Total words
                words_cursor = conn.execute('SELECT SUM(word_count) as total_words FROM blog_posts')
                total_words = words_cursor.fetchone()['total_words'] or 0
                
                # Recent posts (last 7 days)
                recent_cursor = conn.execute('''
                    SELECT COUNT(*) as recent FROM blog_posts 
                    WHERE created_at > datetime('now', '-7 days')
                ''')
                recent = recent_cursor.fetchone()['recent']
                
                # Most used models
                models_cursor = conn.execute('''
                    SELECT model, COUNT(*) as count FROM blog_posts 
                    GROUP BY model ORDER BY count DESC LIMIT 5
                ''')
                models = [{'model': row['model'], 'count': row['count']} 
                         for row in models_cursor.fetchall()]
                
                return {
                    'total_posts': total,
                    'total_words': total_words,
                    'recent_posts': recent,
                    'popular_models': models,
                    'avg_words_per_post': round(total_words / total, 2) if total > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    def _row_to_blog_post(self, row: sqlite3.Row) -> BlogPost:
        """
        Convert database row to BlogPost model
        
        Args:
            row: SQLite row object
            
        Returns:
            BlogPost object
        """
        return BlogPost(
            id=row['id'],
            topic=row['topic'],
            content=row['content'],
            word_count=row['word_count'],
            sources=json.loads(row['sources']) if row['sources'] else [],
            images=json.loads(row['images']) if row['images'] else [],
            provider=row['provider'],
            model=row['model'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
