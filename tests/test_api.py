#!/usr/bin/env python3
"""
Test script for AI Blog Writer Backend API

This script tests all the main API endpoints to ensure they work correctly.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

API_BASE = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("[*] Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Agents status: {data['agents']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_blog_generation():
    """Test blog post generation"""
    print("\n✍️  Testing blog generation...")
    
    payload = {
        "topic": "sustainable energy technologies",
        "provider": "groq",
        "research_count": 3,
        "include_images": True,
        "image_count": 2,
        "embed_images": True
    }
    
    try:
        print("   Sending generation request...")
        response = requests.post(f"{API_BASE}/generate", json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Blog generation successful!")
            print(f"   Post ID: {data['id']}")
            print(f"   Word count: {data['metadata']['word_count']}")
            print(f"   Sources: {data['metadata']['sources_count']}")
            print(f"   Images: {data['metadata']['images_count']}")
            print(f"   Content preview: {data['markdown'][:100]}...")
            return data['id']
        else:
            print(f"❌ Blog generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Blog generation error: {e}")
        return None

def test_blog_retrieval(post_id: str):
    """Test retrieving a specific blog post"""
    print(f"\n📖 Testing blog retrieval for ID: {post_id}")
    
    try:
        response = requests.get(f"{API_BASE}/post/{post_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Blog retrieval successful!")
            print(f"   Topic: {data['topic']}")
            print(f"   Word count: {data['word_count']}")
            print(f"   Created: {data['created_at']}")
            return True
        else:
            print(f"❌ Blog retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Blog retrieval error: {e}")
        return False

def test_blog_editing(post_id: str):
    """Test editing a blog post"""
    print(f"\n✏️  Testing blog editing for ID: {post_id}")
    
    # First get the blog post content
    try:
        response = requests.get(f"{API_BASE}/post/{post_id}")
        if response.status_code != 200:
            print("❌ Cannot retrieve post for editing")
            return False
        
        original_content = response.json()['content']
        
        # Now edit it
        payload = {
            "markdown": original_content,
            "instruction": "Add a brief conclusion paragraph",
            "provider": "groq"
        }
        
        edit_response = requests.post(f"{API_BASE}/edit", json=payload, timeout=30)
        
        if edit_response.status_code == 200:
            data = edit_response.json()
            print("✅ Blog editing successful!")
            print(f"   Original length: {len(original_content)} chars")
            print(f"   Edited length: {len(data['markdown'])} chars")
            print(f"   Instruction: {data['instruction_applied']}")
            return True
        else:
            print(f"❌ Blog editing failed: {edit_response.status_code}")
            print(f"   Error: {edit_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Blog editing error: {e}")
        return False

def test_blog_listing():
    """Test listing blog posts"""
    print("\n📝 Testing blog listing...")
    
    try:
        response = requests.get(f"{API_BASE}/posts?limit=5")
        
        if response.status_code == 200:
            posts = response.json()
            print(f"✅ Blog listing successful! Found {len(posts)} posts")
            for i, post in enumerate(posts):
                print(f"   {i+1}. {post['topic']} ({post['word_count']} words)")
            return True
        else:
            print(f"❌ Blog listing failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Blog listing error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AI Blog Writer Backend API Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code != 200:
            print(f"❌ Server not responding at {API_BASE}")
            print("   Please start the server with: ./start.sh")
            sys.exit(1)
    except Exception:
        print(f"❌ Cannot connect to server at {API_BASE}")
        print("   Please start the server with: ./start.sh")
        sys.exit(1)
    
    print(f"✅ Server is running at {API_BASE}")
    
    # Run tests
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Health check
    if test_health_check():
        tests_passed += 1
    
    # Test 2: Blog generation (this takes the longest)
    post_id = test_blog_generation()
    if post_id:
        tests_passed += 1
        
        # Test 3: Blog retrieval
        if test_blog_retrieval(post_id):
            tests_passed += 1
            
        # Test 4: Blog editing
        if test_blog_editing(post_id):
            tests_passed += 1
    else:
        print("⚠️  Skipping retrieval and editing tests (no post generated)")
        total_tests -= 2
    
    # Test 5: Blog listing
    if test_blog_listing():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Backend is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
