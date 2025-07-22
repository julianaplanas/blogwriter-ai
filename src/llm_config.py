"""
LLM Provider Configuration for Blog Writer Agent

This module provides configuration settings and utilities for different LLM providers.
"""

from typing import Dict, Any, Optional
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GROQ = "groq"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"  # For local models


class LLMConfig:
    """Configuration settings for different LLM providers."""
    
    # OpenAI Configuration
    OPENAI = {
        'api_key_env': 'OPENAI_API_KEY',
        'base_url': 'https://api.openai.com/v1',
        'default_model': 'gpt-3.5-turbo',
        'models': [
            'gpt-3.5-turbo',
            'gpt-3.5-turbo-16k',
            'gpt-4',
            'gpt-4-turbo-preview',
            'gpt-4o',
            'gpt-4o-mini'
        ],
        'max_tokens_default': 2000,
        'temperature_default': 0.7,
        'supports_system_message': True
    }
    
    # Groq Configuration (OpenAI-compatible API)
    GROQ = {
        'api_key_env': 'GROQ_API_KEY',
        'base_url': 'https://api.groq.com/openai/v1',
        'default_model': 'mixtral-8x7b-32768',
        'models': [
            'mixtral-8x7b-32768',
            'llama2-70b-4096',
            'llama3-8b-8192',
            'llama3-70b-8192',
            'gemma-7b-it'
        ],
        'max_tokens_default': 2000,
        'temperature_default': 0.7,
        'supports_system_message': True
    }
    
    # Anthropic Configuration
    ANTHROPIC = {
        'api_key_env': 'ANTHROPIC_API_KEY',
        'base_url': 'https://api.anthropic.com',
        'default_model': 'claude-3-haiku-20240307',
        'models': [
            'claude-3-haiku-20240307',
            'claude-3-sonnet-20240229',
            'claude-3-opus-20240229',
            'claude-3-5-sonnet-20241022'
        ],
        'max_tokens_default': 2000,
        'temperature_default': 0.7,
        'supports_system_message': False  # Uses different message format
    }
    
    # Ollama Configuration (Local models)
    OLLAMA = {
        'api_key_env': None,  # No API key needed for local
        'base_url': 'http://localhost:11434',
        'default_model': 'llama3',
        'models': [
            'llama3',
            'llama3:8b',
            'llama3:70b',
            'mixtral',
            'codellama',
            'gemma'
        ],
        'max_tokens_default': 2000,
        'temperature_default': 0.7,
        'supports_system_message': True
    }


def get_provider_config(provider: str) -> Dict[str, Any]:
    """
    Get configuration for a specific LLM provider.
    
    Args:
        provider (str): Provider name (openai, groq, anthropic, ollama)
    
    Returns:
        Dict[str, Any]: Provider configuration
    
    Raises:
        ValueError: If provider is not supported
    """
    provider = provider.lower()
    
    if provider == 'openai':
        return LLMConfig.OPENAI
    elif provider == 'groq':
        return LLMConfig.GROQ
    elif provider == 'anthropic':
        return LLMConfig.ANTHROPIC
    elif provider == 'ollama':
        return LLMConfig.OLLAMA
    else:
        available = ['openai', 'groq', 'anthropic', 'ollama']
        raise ValueError(f"Unsupported provider '{provider}'. Available: {available}")


def get_model_suggestions(provider: str) -> Dict[str, str]:
    """
    Get model suggestions for different use cases.
    
    Args:
        provider (str): LLM provider name
    
    Returns:
        Dict[str, str]: Model suggestions by use case
    """
    config = get_provider_config(provider)
    models = config['models']
    
    suggestions = {
        'fast': models[0] if models else config['default_model'],
        'balanced': config['default_model'],
        'quality': models[-1] if len(models) > 1 else config['default_model'],
        'cost_effective': models[0] if models else config['default_model']
    }
    
    # Provider-specific optimizations
    if provider == 'openai':
        suggestions.update({
            'fast': 'gpt-3.5-turbo',
            'balanced': 'gpt-4o-mini',
            'quality': 'gpt-4o',
            'cost_effective': 'gpt-3.5-turbo'
        })
    elif provider == 'groq':
        suggestions.update({
            'fast': 'llama3-8b-8192',
            'balanced': 'mixtral-8x7b-32768',
            'quality': 'llama3-70b-8192',
            'cost_effective': 'llama3-8b-8192'
        })
    elif provider == 'anthropic':
        suggestions.update({
            'fast': 'claude-3-haiku-20240307',
            'balanced': 'claude-3-sonnet-20240229',
            'quality': 'claude-3-5-sonnet-20241022',
            'cost_effective': 'claude-3-haiku-20240307'
        })
    
    return suggestions


def validate_model_for_provider(provider: str, model: str) -> bool:
    """
    Validate if a model is available for a given provider.
    
    Args:
        provider (str): LLM provider name
        model (str): Model name to validate
    
    Returns:
        bool: True if model is supported
    """
    try:
        config = get_provider_config(provider)
        return model in config['models']
    except ValueError:
        return False


def get_optimal_settings(provider: str, use_case: str = 'balanced') -> Dict[str, Any]:
    """
    Get optimal settings for a provider and use case.
    
    Args:
        provider (str): LLM provider name
        use_case (str): Use case (fast, balanced, quality, cost_effective)
    
    Returns:
        Dict[str, Any]: Optimal settings
    """
    config = get_provider_config(provider)
    suggestions = get_model_suggestions(provider)
    
    # Base settings
    settings = {
        'model': suggestions.get(use_case, config['default_model']),
        'temperature': config['temperature_default'],
        'max_tokens': config['max_tokens_default']
    }
    
    # Use case specific adjustments
    if use_case == 'fast':
        settings['temperature'] = 0.5  # Lower temperature for faster, more focused output
        settings['max_tokens'] = 1500   # Shorter responses
    elif use_case == 'quality':
        settings['temperature'] = 0.8  # Higher creativity
        settings['max_tokens'] = 3000   # Longer, more detailed responses
    elif use_case == 'cost_effective':
        settings['temperature'] = 0.6
        settings['max_tokens'] = 1800
    
    return settings


def print_provider_info():
    """Print information about all available providers."""
    
    print("🤖 Available LLM Providers")
    print("=" * 50)
    
    for provider_name in ['openai', 'groq', 'anthropic', 'ollama']:
        try:
            config = get_provider_config(provider_name)
            suggestions = get_model_suggestions(provider_name)
            
            print(f"\n📡 {provider_name.upper()}")
            print(f"   API Key: {config.get('api_key_env', 'Not required')}")
            print(f"   Default Model: {config['default_model']}")
            print(f"   Available Models: {len(config['models'])}")
            
            print(f"   Model Suggestions:")
            for use_case, model in suggestions.items():
                print(f"     • {use_case.title()}: {model}")
                
        except Exception as e:
            print(f"\n❌ {provider_name.upper()}: Error loading config - {e}")


def main():
    """Demo the LLM configuration system."""
    
    print_provider_info()
    
    print(f"\n🔧 Example Configurations")
    print("=" * 50)
    
    # Show optimal settings for different use cases
    for provider in ['openai', 'groq']:
        for use_case in ['fast', 'balanced', 'quality']:
            try:
                settings = get_optimal_settings(provider, use_case)
                print(f"\n{provider.upper()} - {use_case.title()}:")
                print(f"   Model: {settings['model']}")
                print(f"   Temperature: {settings['temperature']}")
                print(f"   Max Tokens: {settings['max_tokens']}")
            except Exception as e:
                print(f"\n❌ {provider} - {use_case}: {e}")


if __name__ == "__main__":
    main()
