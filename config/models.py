"""
Model configuration for different LLM providers.
This module defines available models and their configurations.
"""

# Groq Models (Free tier with good performance) - Updated December 2024
GROQ_MODELS = {
    "llama-3.3-70b-versatile": {
        "name": "Llama 3.3 70B",
        "description": "Most capable model, best for complex writing tasks",
        "max_tokens": 8000,
        "recommended_for": ["blog_writing", "research_analysis", "complex_tasks"]
    },
    "llama-3.1-8b-instant": {
        "name": "Llama 3.1 8B", 
        "description": "Faster model, good for shorter content",
        "max_tokens": 8000,
        "recommended_for": ["quick_summaries", "simple_tasks"]
    },
    "mixtral-8x7b-32768": {
        "name": "Mixtral 8x7B",
        "description": "High quality model with large context window",
        "max_tokens": 32768,
        "recommended_for": ["blog_writing", "long_content", "research_analysis"]
    },
    "gemma2-9b-it": {
        "name": "Gemma 2 9B",
        "description": "Google's efficient model for various tasks",
        "max_tokens": 8192,
        "recommended_for": ["blog_writing", "general_tasks"]
    }
}

# Default model configurations
DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"  # Updated to available model
BLOG_WRITING_MODEL = "llama-3.1-8b-instant"   # Using available working model
RESEARCH_SUMMARY_MODEL = "llama-3.1-8b-instant"   # Using available working model

# Model selection helper
def get_best_model_for_task(task: str, provider: str = "groq") -> str:
    """
    Get the best model for a specific task.
    
    Args:
        task (str): Task type ('blog_writing', 'research_analysis', 'summary')
        provider (str): LLM provider (default: 'groq')
    
    Returns:
        str: Model identifier
    """
    if provider.lower() == "groq":
        if task == "blog_writing":
            return BLOG_WRITING_MODEL
        elif task == "research_analysis":
            return RESEARCH_SUMMARY_MODEL
        else:
            return DEFAULT_GROQ_MODEL
    
    return DEFAULT_GROQ_MODEL

def list_available_models(provider: str = "groq") -> dict:
    """
    List all available models for a provider.
    
    Args:
        provider (str): LLM provider
    
    Returns:
        dict: Available models and their info
    """
    if provider.lower() == "groq":
        return GROQ_MODELS
    
    return {}

def get_model_info(model_id: str, provider: str = "groq") -> dict:
    """
    Get information about a specific model.
    
    Args:
        model_id (str): Model identifier
        provider (str): LLM provider
    
    Returns:
        dict: Model information
    """
    if provider.lower() == "groq":
        return GROQ_MODELS.get(model_id, {})
    
    return {}
