#!/usr/bin/env python3
"""
Test script for FastAPI Backend
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🩺 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_generate_blog(topic: str = "artificial intelligence trends"):
    """Test blog generation endpoint"""
    print(f"📝 Testing blog generation for topic: '{topic}'...")
    try:
        payload = {"topic": topic}
        response = requests.post(
            f"{BASE_URL}/generate", 
            json=payload,
            timeout=120  # Generous timeout for AI processing
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Blog generated successfully!")
            print(f"   📄 Word count: ~{len(data['markdown'].split())} words")
            print(f"   📚 Sources: {len(data['references'])} references")
            print(f"   🖼️  Images: {len(data['images'])} images")
            print(f"   🆔 Post ID: {data['id']}")
            
            # Show first 200 characters of the blog
            preview = data['markdown'][:200].replace('\n', ' ')
            print(f"   📖 Preview: {preview}...")
            
            return data
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_edit_blog(markdown: str, instruction: str = "Add a brief conclusion"):
    """Test blog editing endpoint"""
    print(f"✏️  Testing blog editing with instruction: '{instruction}'...")
    try:
        payload = {
            "markdown": markdown,
            "instruction": instruction
        }
        response = requests.post(
            f"{BASE_URL}/edit", 
            json=payload,
            timeout=60
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Blog edited successfully!")
            print(f"   📄 New word count: ~{len(data['markdown'].split())} words")
            
            # Show the edit change preview
            old_lines = markdown.split('\n')
            new_lines = data['markdown'].split('\n')
            print(f"   📊 Lines changed: {len(old_lines)} → {len(new_lines)}")
            
            return data['markdown']
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_get_blog(post_id: str):
    """Test retrieving a blog post"""
    print(f"📖 Testing blog retrieval for post ID: {post_id}...")
    try:
        response = requests.get(f"{BASE_URL}/post/{post_id}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Blog retrieved successfully!")
            print(f"   📄 Topic: {data.get('topic', 'N/A')}")
            print(f"   📅 Created: {data.get('created_at', 'N/A')}")
            print(f"   📝 Word count: ~{len(data['content'].split())} words")
            return data
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_list_posts():
    """Test listing all blog posts"""
    print("📋 Testing blog posts listing...")
    try:
        response = requests.get(f"{BASE_URL}/posts")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data)} posts")
            
            for post in data[:3]:  # Show first 3 posts
                print(f"   📄 {post['id']}: {post['topic']} ({post['created_at']})")
            
            if len(data) > 3:
                print(f"   ... and {len(data) - 3} more posts")
                
            return data
        else:
            print(f"   ❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    """Run all backend tests"""
    print("🚀 Testing AI Blog Writer Backend API")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health_check():
        print("❌ Backend not responding. Make sure server is running on port 8000")
        return
    
    print("\n" + "=" * 50)
    
    # Test 2: Generate a blog post
    blog_data = test_generate_blog("sustainable technology innovations")
    if not blog_data:
        print("❌ Blog generation failed. Check API keys and backend logs.")
        return
    
    print("\n" + "=" * 50)
    
    # Test 3: Edit the blog post
    edited_markdown = test_edit_blog(
        blog_data['markdown'], 
        "Add a section about renewable energy and make the tone more optimistic"
    )
    
    print("\n" + "=" * 50)
    
    # Test 4: Retrieve the blog post
    retrieved_data = test_get_blog(blog_data['id'])
    
    print("\n" + "=" * 50)
    
    # Test 5: List all posts
    all_posts = test_list_posts()
    
    print("\n" + "=" * 50)
    print("🎉 Backend testing completed!")
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"✅ Health Check: {'Passed' if True else 'Failed'}")
    print(f"✅ Blog Generation: {'Passed' if blog_data else 'Failed'}")
    print(f"✅ Blog Editing: {'Passed' if edited_markdown else 'Failed'}")
    print(f"✅ Blog Retrieval: {'Passed' if retrieved_data else 'Failed'}")
    print(f"✅ Posts Listing: {'Passed' if all_posts else 'Failed'}")
    
    if all([blog_data, edited_markdown, retrieved_data, all_posts]):
        print("\n🎊 All tests passed! Backend is fully functional!")
    else:
        print("\n⚠️  Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()
