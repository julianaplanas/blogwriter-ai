"""
FastAPI Backend for AI-Powered Blog Writer

This module provides REST API endpoints for blog generation and editing
using the multi-agent architecture (Research, Blog Writer, Image agents).
"""

import os
import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our agents
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from research_agent import ResearchAgent
    from blog_writer_agent import BlogWriterAgent
    from image_agent import ImageAgent, fetch_blog_images
    from editing_agent import EditingAgent, EditResult
except ImportError as e:
    logging.error(f"Failed to import agents: {e}")
    raise

from db import BlogStorage
from api_models import (
    BlogPost, GenerateRequest, EditRequest, BlogResponse, ImageMetadata,
    EnhancedEditRequest, EditResponse, VersionHistoryResponse
)

# Blog storage instance
blog_storage = BlogStorage()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting up AI Blog Writer API...")
    # blog_storage will initialize itself automatically on first use
    logger.info("Blog storage ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Blog Writer API...")

# Create FastAPI app
app = FastAPI(
    title="AI-Powered Blog Writer API",
    description="Generate and edit blog posts using AI agents for research, writing, and images",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instances (initialized on first use)
research_agent = None
blog_writer_agent = None
image_agent = None
editing_agent = None

def get_research_agent() -> ResearchAgent:
    """Get or initialize research agent"""
    global research_agent
    if research_agent is None:
        try:
            research_agent = ResearchAgent()
            logger.info("Research agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize research agent: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Research agent initialization failed. Check BRAVE_API_KEY."
            )
    return research_agent

def get_blog_writer_agent() -> BlogWriterAgent:
    """Get or initialize blog writer agent"""
    global blog_writer_agent
    if blog_writer_agent is None:
        try:
            blog_writer_agent = BlogWriterAgent()
            logger.info("Blog writer agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize blog writer agent: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Blog writer agent initialization failed. Check GROQ_API_KEY."
            )
    return blog_writer_agent

def get_image_agent() -> Optional[ImageAgent]:
    """Get or initialize image agent (optional)"""
    global image_agent
    if image_agent is None:
        try:
            image_agent = ImageAgent()
            logger.info("Image agent initialized successfully")
        except Exception as e:
            logger.warning(f"Image agent not available: {e}")
            image_agent = False  # Mark as unavailable
    return image_agent if image_agent is not False else None

def get_editing_agent() -> EditingAgent:
    """Get or initialize editing agent"""
    global editing_agent
    if editing_agent is None:
        try:
            editing_agent = EditingAgent(llm_provider="groq")  # Use Groq by default
            logger.info("Editing agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize editing agent: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Editing agent initialization failed. Check GROQ_API_KEY."
            )
    return editing_agent

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI-Powered Blog Writer API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "generate": "POST /generate",
            "edit": "POST /edit (enhanced)",
            "edit_simple": "POST /edit/simple (backward compatible)",
            "edit_history": "GET /edit/history",
            "undo": "POST /edit/undo/{version_id}",
            "clear_history": "DELETE /edit/history",
            "get_post": "GET /post/{post_id}",
            "list_posts": "GET /posts",
            "search_posts": "GET /posts/search",
            "blog_stats": "GET /posts/stats",
            "post_versions": "GET /post/{post_id}/versions",
            "edit_saved_post": "POST /post/{post_id}/edit",
            "delete_post": "DELETE /post/{post_id}",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check agent availability
    agents_status = {
        "research_agent": False,
        "blog_writer_agent": False,
        "image_agent": False,
        "editing_agent": False
    }
    
    try:
        get_research_agent()
        agents_status["research_agent"] = True
    except:
        pass
    
    try:
        get_blog_writer_agent()
        agents_status["blog_writer_agent"] = True
    except:
        pass
    
    try:
        agent = get_image_agent()
        agents_status["image_agent"] = agent is not None
    except:
        pass
    
    try:
        get_editing_agent()
        agents_status["editing_agent"] = True
    except:
        pass
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": agents_status
    }

@app.post("/generate", response_model=BlogResponse)
async def generate_blog_post(request: GenerateRequest):
    """
    Generate a complete blog post with research and images
    
    This endpoint orchestrates all AI agents:
    1. Research Agent: Finds relevant articles and sources
    2. Blog Writer Agent: Generates the blog content
    3. Image Agent: Fetches relevant images (optional)
    """
    logger.info(f"Starting blog generation for topic: {request.topic}")
    
    try:
        # Step 1: Research
        logger.info("Step 1: Conducting research...")
        research_agent = get_research_agent()
        research_results = research_agent.search_articles(
            request.topic, 
            count=request.research_count
        )
        
        if not research_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No research results found for the topic"
            )
        
        logger.info(f"Research completed: {len(research_results)} articles found")
        
        # Step 2: Generate blog content
        logger.info("Step 2: Generating blog content...")
        blog_writer = get_blog_writer_agent()
        
        # Generate blog post
        blog_content = blog_writer.generate_blog_post(
            topic=request.topic,
            research_results=research_results
        )
        
        if not blog_content or not blog_content.get("markdown"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate blog content"
            )
        
        # Extract data from blog result  
        metadata = blog_content.get("metadata", {})
        markdown_content = blog_content.get("markdown", "")
        used_sources = blog_content.get("used_sources", [])
        images_data = blog_content.get("images", [])
        
        logger.info(f"Blog generated: {metadata.get('word_count', 0)} words")
        logger.info(f"Sources used: {len(used_sources)}")
        logger.info(f"Images fetched: {len(images_data)}")
        
        # Convert images data to ImageMetadata format  
        images = []
        for img in images_data:
            images.append(ImageMetadata(
                url=img.get('image_url', ''),
                alt_text=img.get('alt_description', ''),
                photographer=img.get('photographer', ''),
                source_url=img.get('source_url', ''),
                width=img.get('width', 0),
                height=img.get('height', 0)
            ))
        
        # Step 4: Store in database
        post_id = blog_storage.save_blog_post(
            topic=request.topic,
            markdown=markdown_content,
            references=research_results,  # Store full research results
            images=[img.dict() for img in images],  # Store image metadata
            metadata={
                "word_count": metadata.get('word_count', 0),
                "sources_count": len(used_sources),
                "images_count": len(images),
                "provider": request.provider,
                "model": request.model or metadata.get('model', 'auto'),
                "generated_at": datetime.now().isoformat()
            }
        )
        logger.info(f"Blog post saved to database with ID: {post_id}")
        
        # Prepare response
        response = BlogResponse(
            id=str(post_id),  # Convert int ID to string for API compatibility
            markdown=markdown_content,
            references=research_results,
            images=images,
            metadata={
                "word_count": metadata.get('word_count', 0),
                "sources_count": len(used_sources),
                "images_count": len(images),
                "provider": request.provider,
                "model": request.model or metadata.get('model', 'auto'),
                "generated_at": datetime.now().isoformat()
            }
        )
        
        logger.info(f"Blog generation completed successfully for topic: {request.topic}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Blog generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blog generation failed: {str(e)}"
        )

@app.post("/edit", response_model=EditResponse)
async def edit_blog_post(request: EnhancedEditRequest):
    """
    Edit an existing blog post using natural language instructions with advanced features
    
    Uses the Enhanced Editing Agent with features like:
    - Diff tracking and change summaries
    - Version history management
    - Configurable editing parameters
    - Multiple LLM provider support
    """
    logger.info(f"Starting enhanced blog edit with instruction: {request.instruction}")
    
    try:
        editing_agent = get_editing_agent()
        
        # Apply the edit using the enhanced editing agent
        edit_result = editing_agent.apply_edit(
            markdown_text=request.markdown,
            instruction=request.instruction,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            track_version=request.track_version
        )
        
        # Prepare response based on edit result
        response = EditResponse(
            markdown=edit_result.edited_content,
            instruction_applied=edit_result.instruction,
            edited_at=edit_result.timestamp.isoformat(),
            success=edit_result.success,
            model_used=edit_result.model_used,
            provider_used=edit_result.provider_used,
            error_message=edit_result.error_message
        )
        
        # Include diff information if requested
        if request.export_diff and edit_result.success:
            response.changes_summary = edit_result.changes_summary
            response.diff_text = edit_result.diff_text
        
        if not edit_result.success:
            logger.warning(f"Edit failed: {edit_result.error_message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=edit_result.error_message or "Failed to edit blog content"
            )
        
        logger.info("Enhanced blog edit completed successfully")
        return response
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Enhanced blog edit failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blog edit failed: {str(e)}"
        )

@app.post("/edit/simple", response_model=Dict[str, str])
async def edit_blog_post_simple(request: EditRequest):
    """
    Simple edit endpoint for backward compatibility
    
    This endpoint maintains compatibility with existing frontend while using
    the enhanced editing agent internally
    """
    logger.info(f"Starting simple blog edit with instruction: {request.instruction}")
    
    try:
        editing_agent = get_editing_agent()
        
        # Apply the edit with default parameters
        edit_result = editing_agent.apply_edit(
            markdown_text=request.markdown,
            instruction=request.instruction,
            temperature=0.3,
            max_tokens=4000,
            track_version=False  # Don't track versions for simple edits
        )
        
        if not edit_result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=edit_result.error_message or "Failed to edit blog content"
            )
        
        logger.info("Simple blog edit completed successfully")
        
        return {
            "markdown": edit_result.edited_content,
            "instruction_applied": edit_result.instruction,
            "edited_at": edit_result.timestamp.isoformat()
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Simple blog edit failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blog edit failed: {str(e)}"
        )

@app.get("/posts/search")
async def search_blog_posts(query: str, limit: int = 10):
    """
    Search blog posts by topic or content
    """
    logger.info(f"Searching blog posts for: {query}")
    
    try:
        posts = blog_storage.search_blog_posts(query, limit)
        
        # Return summary information
        posts_summary = []
        for post in posts:
            posts_summary.append({
                "id": post["id"],
                "topic": post["topic"],
                "word_count": len(post["markdown"].split()) if post.get("markdown") else 0,
                "sources_count": len(post.get("references", [])),
                "images_count": len(post.get("images", [])),
                "created_at": post["created_at"],
                "updated_at": post["updated_at"]
            })
        
        logger.info(f"Found {len(posts_summary)} blog posts matching '{query}'")
        return {
            "query": query,
            "results": posts_summary,
            "total": len(posts_summary)
        }
        
    except Exception as e:
        logger.error(f"Failed to search blog posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search blog posts: {str(e)}"
        )

@app.get("/posts/stats")
async def get_blog_stats():
    """
    Get blog database statistics
    """
    logger.info("Retrieving blog statistics")
    
    try:
        stats = blog_storage.get_stats()
        logger.info("Blog statistics retrieved successfully")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get blog statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get blog statistics: {str(e)}"
        )

@app.get("/post/{post_id}")
async def get_blog_post(post_id: int):
    """
    Retrieve a specific blog post by ID
    """
    logger.info(f"Retrieving blog post: {post_id}")
    
    try:
        blog_data = blog_storage.get_blog_post(post_id)
        
        if not blog_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blog post {post_id} not found"
            )
        
        # Convert the database result to API format
        blog_post = {
            "id": str(blog_data["id"]),
            "topic": blog_data["topic"],
            "content": blog_data["markdown"],
            "word_count": len(blog_data["markdown"].split()),
            "references": blog_data.get("references", []),
            "images": blog_data.get("images", []),
            "metadata": blog_data.get("metadata", {}),
            "created_at": blog_data["created_at"],
            "updated_at": blog_data["updated_at"]
        }
        
        logger.info(f"Blog post {post_id} retrieved successfully")
        return blog_post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve blog post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve blog post: {str(e)}"
        )

@app.get("/posts", response_model=List[Dict[str, Any]])
async def list_blog_posts(limit: int = 10, offset: int = 0):
    """
    List all blog posts with pagination
    """
    logger.info(f"Listing blog posts (limit: {limit}, offset: {offset})")
    
    try:
        posts = blog_storage.list_blog_posts(limit=limit, offset=offset)
        
        # Return summary information
        posts_summary = []
        for post in posts:
            posts_summary.append({
                "id": post["id"],
                "topic": post["topic"],
                "word_count": len(post["markdown"].split()) if post.get("markdown") else 0,
                "sources_count": len(post.get("references", [])),
                "images_count": len(post.get("images", [])),
                "created_at": post["created_at"],
                "updated_at": post["updated_at"]
            })
        
        logger.info(f"Retrieved {len(posts_summary)} blog posts")
        return posts_summary
        
    except Exception as e:
        logger.error(f"Failed to list blog posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list blog posts: {str(e)}"
        )

@app.delete("/post/{post_id}")
async def delete_blog_post(post_id: int):
    """
    Delete a specific blog post
    """
    logger.info(f"Deleting blog post: {post_id}")
    
    try:
        success = blog_storage.delete_blog_post(post_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blog post {post_id} not found"
            )
        
        logger.info(f"Blog post {post_id} deleted successfully")
        return {"message": f"Blog post {post_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete blog post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete blog post: {str(e)}"
        )


@app.get("/edit/history", response_model=VersionHistoryResponse)
async def get_edit_history():
    """
    Get the version history for the current editing session
    """
    logger.info("Retrieving edit version history")
    
    try:
        editing_agent = get_editing_agent()
        history = editing_agent.get_version_history()
        
        current_version = None
        if history:
            current_version = history[-1].get("version_id")
        
        return VersionHistoryResponse(
            versions=history,
            current_version=current_version
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve version history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve version history: {str(e)}"
        )

@app.post("/edit/undo/{version_id}")
async def undo_to_version(version_id: str):
    """
    Undo editing changes to a specific version
    """
    logger.info(f"Undoing to version: {version_id}")
    
    try:
        editing_agent = get_editing_agent()
        content = editing_agent.undo_to_version(version_id)
        
        if content is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version_id} not found"
            )
        
        return {
            "markdown": content,
            "version_restored": version_id,
            "restored_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Failed to undo to version {version_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to undo to version: {str(e)}"
        )

@app.delete("/edit/history")
async def clear_edit_history():
    """
    Clear the edit version history
    """
    logger.info("Clearing edit version history")
    
    try:
        editing_agent = get_editing_agent()
        editing_agent.clear_history()
        
        return {
            "message": "Version history cleared successfully",
            "cleared_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to clear version history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear version history: {str(e)}"
        )

@app.get("/post/{post_id}/versions")
async def get_post_versions(post_id: int):
    """
    Get all versions of a blog post
    """
    logger.info(f"Retrieving versions for blog post: {post_id}")
    
    try:
        versions = blog_storage.get_post_versions(post_id)
        
        # Convert versions to API format
        version_list = []
        for version in versions:
            version_list.append({
                "id": version["id"],
                "version_number": version["version_number"],
                "edit_instruction": version["edit_instruction"],
                "created_at": version["created_at"],
                "word_count": len(version["markdown"].split()) if version.get("markdown") else 0
            })
        
        logger.info(f"Retrieved {len(version_list)} versions for post {post_id}")
        return {
            "post_id": post_id,
            "versions": version_list,
            "total_versions": len(version_list)
        }
        
    except Exception as e:
        logger.error(f"Failed to get versions for post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get versions for post: {str(e)}"
        )

@app.post("/post/{post_id}/edit")
async def edit_saved_blog_post(post_id: int, request: EditRequest):
    """
    Edit a saved blog post and create a new version
    """
    logger.info(f"Editing saved blog post: {post_id}")
    
    try:
        # Get the existing post
        existing_post = blog_storage.get_blog_post(post_id)
        if not existing_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blog post {post_id} not found"
            )
        
        # Apply the edit using the editing agent
        editing_agent = get_editing_agent()
        edit_result = editing_agent.apply_edit(
            markdown_text=existing_post["markdown"],
            instruction=request.instruction,
            temperature=0.3,
            max_tokens=4000
        )
        
        if not edit_result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=edit_result.error_message or "Failed to edit blog post"
            )
        
        # Update the post with the new content
        success = blog_storage.update_blog_post(
            post_id=post_id,
            markdown=edit_result.edited_content,
            edit_instruction=request.instruction
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save edited content"
            )
        
        logger.info(f"Blog post {post_id} edited successfully")
        
        return {
            "post_id": post_id,
            "markdown": edit_result.edited_content,
            "instruction_applied": request.instruction,
            "edited_at": edit_result.timestamp.isoformat(),
            "model_used": edit_result.model_used,
            "provider_used": edit_result.provider_used
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to edit saved blog post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to edit blog post: {str(e)}"
        )

if __name__ == "__main__":
    # Load environment variables
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("python-dotenv not installed, skipping .env loading")
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
