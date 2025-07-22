"""
AI-Powered Blog Writer - Research Agent Module

This package contains the core functionality for the AI-powered blog writing system,
including research agents, blog writers, and configuration utilities.
"""

"""
AI-Powered Blog Writer - Research Agent Module

This package contains the core functionality for the AI-powered blog writing system,
including research agents, blog writers, and configuration utilities.
"""

import sys
import os

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'))

from .research_agent import ResearchAgent, research_topic
from .blog_writer_agent import BlogWriterAgent, generate_blog_post
from .llm_config import LLMProvider, LLMConfig, get_optimal_settings, get_provider_config

# Import from config directory
try:
    from rate_limit_config import RateLimitConfig, create_research_agent, batch_research
except ImportError:
    # Fallback if config import fails
    RateLimitConfig = None
    create_research_agent = None
    batch_research = None

__version__ = "1.0.0"
__author__ = "AI Blog Writer Team"

__all__ = [
    # Research Agent
    'ResearchAgent',
    'research_topic',
    
    # Rate Limiting
    'RateLimitConfig',
    'create_research_agent',
    'batch_research',
    
    # Blog Writer Agent
    'BlogWriterAgent', 
    'generate_blog_post',
    
    # LLM Configuration
    'LLMProvider',
    'LLMConfig',
    'get_optimal_settings',
    'get_provider_config'
]
