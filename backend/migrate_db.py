#!/usr/bin/env python3
"""
Database migration script to fix schema issues
Run this if you get sqlite3.OperationalError about missing columns
"""

import sqlite3
import json
import os

def migrate_database():
    """Migrate database to latest schema."""
    db_path = 'blog_posts.db'
    
    if not os.path.exists(db_path):
        print("No database found - will be created automatically")
        return
    
    print(f"Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current schema
    cursor.execute("PRAGMA table_info(blog_posts)")
    columns = [row[1] for row in cursor.fetchall()]
    
    print(f"Current columns: {columns}")
    
    # Add metadata column if missing
    if 'metadata' not in columns:
        print("Adding metadata column...")
        cursor.execute('ALTER TABLE blog_posts ADD COLUMN metadata TEXT')
        
        # Update existing rows with default metadata
        cursor.execute('''
            UPDATE blog_posts 
            SET metadata = ? 
            WHERE metadata IS NULL
        ''', (json.dumps({"provider": "legacy", "model": "unknown"}),))
        
        print("Updated existing rows with default metadata")
    
    conn.commit()
    
    # Verify the fix
    cursor.execute("SELECT COUNT(*) FROM blog_posts")
    count = cursor.fetchone()[0]
    print(f"Database migration complete. Total posts: {count}")
    
    conn.close()

if __name__ == "__main__":
    migrate_database()
