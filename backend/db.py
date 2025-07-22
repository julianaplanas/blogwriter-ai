"""
Blog Storage Layer - SQLite Database Management

This module provides a SQLite-based persistence layer for storing blog posts,
including content, metadata, and edit history.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging

# Configure logging
logger = logging.getLogger(__name__)

class BlogStorage:
    """SQLite-based blog post storage with versioning support"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the blog storage with SQLite database
        
        Args:
            db_path: Path to SQLite database file. If None, uses environment variable
                    or defaults to 'blog.db'
        """
        if db_path is None:
            db_path = os.environ.get('BLOG_DB_PATH', 'blog.db')
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign key constraints
                
                # Create blog_posts table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS blog_posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic TEXT NOT NULL,
                        markdown TEXT NOT NULL,
                        source_refs TEXT,  -- JSON string for references/sources
                        images TEXT,      -- JSON string
                        metadata TEXT,    -- JSON string for additional metadata
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create blog_post_versions table for edit history
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS blog_post_versions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER NOT NULL,
                        version_number INTEGER NOT NULL,
                        markdown TEXT NOT NULL,
                        edit_instruction TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES blog_posts(id) ON DELETE CASCADE,
                        UNIQUE(post_id, version_number)
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_posts_created_at ON blog_posts(created_at)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_posts_topic ON blog_posts(topic)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_versions_post_id ON blog_post_versions(post_id)')
                
                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")
                
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def save_blog_post(self, topic: str, markdown: str, references: List[Dict] = None, 
                      images: List[Dict] = None, metadata: Dict = None) -> int:
        """
        Save a new blog post to the database
        
        Args:
            topic: Blog post topic/title
            markdown: Markdown content
            references: List of reference dictionaries
            images: List of image dictionaries  
            metadata: Additional metadata dictionary
            
        Returns:
            int: The ID of the saved blog post
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Convert lists/dicts to JSON strings
                references_json = json.dumps(references or [])
                images_json = json.dumps(images or [])
                metadata_json = json.dumps(metadata or {})
                
                cursor = conn.execute('''
                    INSERT INTO blog_posts (topic, markdown, source_refs, images, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (topic, markdown, references_json, images_json, metadata_json))
                
                post_id = cursor.lastrowid
                
                # Save initial version
                conn.execute('''
                    INSERT INTO blog_post_versions (post_id, version_number, markdown, edit_instruction)
                    VALUES (?, 1, ?, ?)
                ''', (post_id, markdown, "Initial version"))
                
                conn.commit()
                logger.info(f"Saved blog post with ID {post_id}")
                return post_id
                
        except sqlite3.Error as e:
            logger.error(f"Failed to save blog post: {e}")
            raise
        except json.JSONEncodeError as e:
            logger.error(f"Failed to encode JSON data: {e}")
            raise
    
    def get_blog_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a blog post by ID
        
        Args:
            post_id: The blog post ID
            
        Returns:
            Dictionary containing post data or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                
                cursor = conn.execute('''
                    SELECT * FROM blog_posts WHERE id = ?
                ''', (post_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Convert row to dictionary and parse JSON fields
                post = dict(row)
                post['references'] = json.loads(post['source_refs']) if post['source_refs'] else []
                post['images'] = json.loads(post['images']) if post['images'] else []
                post['metadata'] = json.loads(post['metadata']) if post['metadata'] else {}
                
                logger.info(f"Retrieved blog post {post_id}")
                return post
                
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve blog post {post_id}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON data: {e}")
            raise
    
    def list_blog_posts(self, limit: int = 100, offset: int = 0, 
                       order_by: str = 'created_at', order_dir: str = 'DESC') -> List[Dict[str, Any]]:
        """
        List all blog posts with pagination
        
        Args:
            limit: Maximum number of posts to return
            offset: Number of posts to skip
            order_by: Column to order by ('created_at', 'updated_at', 'topic', 'id')
            order_dir: Order direction ('ASC' or 'DESC')
            
        Returns:
            List of blog post dictionaries
        """
        # Validate parameters
        valid_columns = ['created_at', 'updated_at', 'topic', 'id']
        valid_directions = ['ASC', 'DESC']
        
        if order_by not in valid_columns:
            order_by = 'created_at'
        if order_dir.upper() not in valid_directions:
            order_dir = 'DESC'
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute(f'''
                    SELECT * FROM blog_posts 
                    ORDER BY {order_by} {order_dir.upper()}
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
                
                posts = []
                for row in cursor.fetchall():
                    post = dict(row)
                    # Parse JSON fields
                    post['references'] = json.loads(post['source_refs']) if post['source_refs'] else []
                    post['images'] = json.loads(post['images']) if post['images'] else []
                    post['metadata'] = json.loads(post['metadata']) if post['metadata'] else {}
                    posts.append(post)
                
                logger.info(f"Retrieved {len(posts)} blog posts")
                return posts
                
        except sqlite3.Error as e:
            logger.error(f"Failed to list blog posts: {e}")
            raise
    
    def update_blog_post(self, post_id: int, markdown: str, edit_instruction: str = None) -> bool:
        """
        Update a blog post's markdown content and create a new version
        
        Args:
            post_id: The blog post ID to update
            markdown: New markdown content
            edit_instruction: Description of the edit made
            
        Returns:
            bool: True if update was successful, False if post not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if post exists
                cursor = conn.execute('SELECT id FROM blog_posts WHERE id = ?', (post_id,))
                if not cursor.fetchone():
                    logger.warning(f"Blog post {post_id} not found for update")
                    return False
                
                # Update the main post
                conn.execute('''
                    UPDATE blog_posts 
                    SET markdown = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (markdown, post_id))
                
                # Get next version number
                cursor = conn.execute('''
                    SELECT COALESCE(MAX(version_number), 0) + 1 
                    FROM blog_post_versions 
                    WHERE post_id = ?
                ''', (post_id,))
                version_number = cursor.fetchone()[0]
                
                # Add new version
                conn.execute('''
                    INSERT INTO blog_post_versions (post_id, version_number, markdown, edit_instruction)
                    VALUES (?, ?, ?, ?)
                ''', (post_id, version_number, markdown, edit_instruction or f"Edit #{version_number}"))
                
                conn.commit()
                logger.info(f"Updated blog post {post_id}, version {version_number}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Failed to update blog post {post_id}: {e}")
            raise
    
    def get_post_versions(self, post_id: int) -> List[Dict[str, Any]]:
        """
        Get all versions of a blog post
        
        Args:
            post_id: The blog post ID
            
        Returns:
            List of version dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute('''
                    SELECT * FROM blog_post_versions 
                    WHERE post_id = ? 
                    ORDER BY version_number ASC
                ''', (post_id,))
                
                versions = [dict(row) for row in cursor.fetchall()]
                logger.info(f"Retrieved {len(versions)} versions for post {post_id}")
                return versions
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get versions for post {post_id}: {e}")
            raise
    
    def delete_blog_post(self, post_id: int) -> bool:
        """
        Delete a blog post and all its versions
        
        Args:
            post_id: The blog post ID to delete
            
        Returns:
            bool: True if deletion was successful, False if post not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('DELETE FROM blog_posts WHERE id = ?', (post_id,))
                
                if cursor.rowcount == 0:
                    logger.warning(f"Blog post {post_id} not found for deletion")
                    return False
                
                conn.commit()
                logger.info(f"Deleted blog post {post_id}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Failed to delete blog post {post_id}: {e}")
            raise
    
    def search_blog_posts(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search blog posts by topic or content
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching blog post dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Search in both topic and markdown content
                search_pattern = f"%{query}%"
                cursor = conn.execute('''
                    SELECT * FROM blog_posts 
                    WHERE topic LIKE ? OR markdown LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (search_pattern, search_pattern, limit))
                
                posts = []
                for row in cursor.fetchall():
                    post = dict(row)
                    # Parse JSON fields
                    post['references'] = json.loads(post['source_refs']) if post['source_refs'] else []
                    post['images'] = json.loads(post['images']) if post['images'] else []
                    post['metadata'] = json.loads(post['metadata']) if post['metadata'] else {}
                    posts.append(post)
                
                logger.info(f"Found {len(posts)} posts matching '{query}'")
                return posts
                
        except sqlite3.Error as e:
            logger.error(f"Failed to search blog posts: {e}")
            raise
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get database statistics
        
        Returns:
            Dictionary with count statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM blog_posts')
                post_count = cursor.fetchone()[0]
                
                cursor = conn.execute('SELECT COUNT(*) FROM blog_post_versions')
                version_count = cursor.fetchone()[0]
                
                return {
                    'total_posts': post_count,
                    'total_versions': version_count
                }
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get stats: {e}")
            raise


# Convenience functions for backward compatibility and ease of use
_storage_instance = None

def get_storage() -> BlogStorage:
    """Get or create a global BlogStorage instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = BlogStorage()
    return _storage_instance

def save_blog_post(topic: str, markdown: str, references: List[Dict] = None, 
                  images: List[Dict] = None, metadata: Dict = None) -> int:
    """Convenience function to save a blog post"""
    return get_storage().save_blog_post(topic, markdown, references, images, metadata)

def get_blog_post(post_id: int) -> Optional[Dict[str, Any]]:
    """Convenience function to get a blog post"""
    return get_storage().get_blog_post(post_id)

def list_blog_posts(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """Convenience function to list blog posts"""
    return get_storage().list_blog_posts(limit, offset)

def update_blog_post(post_id: int, markdown: str, edit_instruction: str = None) -> bool:
    """Convenience function to update a blog post"""
    return get_storage().update_blog_post(post_id, markdown, edit_instruction)

def search_blog_posts(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Convenience function to search blog posts"""
    return get_storage().search_blog_posts(query, limit)
