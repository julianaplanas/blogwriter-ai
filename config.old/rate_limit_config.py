"""
Configuration helper for Research Agent rate limiting settings.

This module provides predefined configurations for different use cases.
"""

from typing import Dict, Any
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
from research_agent import ResearchAgent


class RateLimitConfig:
    """Predefined configurations for different usage scenarios."""
    
    # Conservative settings for heavy usage or strict API limits
    CONSERVATIVE = {
        'request_delay': 2.5,
        'max_retries': 5,
        'description': 'Conservative settings for heavy usage or strict API limits'
    }
    
    # Standard settings for normal usage
    STANDARD = {
        'request_delay': 1.0,
        'max_retries': 3,
        'description': 'Standard settings for normal usage'
    }
    
    # Fast settings for light usage or testing
    FAST = {
        'request_delay': 0.5,
        'max_retries': 2,
        'description': 'Fast settings for light usage or testing'
    }
    
    # Batch processing settings for multiple requests
    BATCH = {
        'request_delay': 3.0,
        'max_retries': 5,
        'description': 'Batch processing settings for multiple consecutive requests'
    }


def create_research_agent(config: str = 'STANDARD', api_key: str = None) -> ResearchAgent:
    """
    Create a research agent with predefined rate limiting configuration.
    
    Args:
        config (str): Configuration preset ('CONSERVATIVE', 'STANDARD', 'FAST', 'BATCH')
        api_key (str): Optional API key override
    
    Returns:
        ResearchAgent: Configured research agent
    
    Raises:
        ValueError: If invalid configuration is specified
    """
    configs = {
        'CONSERVATIVE': RateLimitConfig.CONSERVATIVE,
        'STANDARD': RateLimitConfig.STANDARD,
        'FAST': RateLimitConfig.FAST,
        'BATCH': RateLimitConfig.BATCH
    }
    
    if config not in configs:
        raise ValueError(f"Invalid config '{config}'. Available: {list(configs.keys())}")
    
    settings = configs[config]
    print(f"🔧 Creating research agent with {config} settings:")
    print(f"   • {settings['description']}")
    print(f"   • Request delay: {settings['request_delay']}s")
    print(f"   • Max retries: {settings['max_retries']}")
    
    return ResearchAgent(
        api_key=api_key,
        request_delay=settings['request_delay'],
        max_retries=settings['max_retries']
    )


def batch_research(topics: list, config: str = 'BATCH', articles_per_topic: int = 3) -> Dict[str, list]:
    """
    Perform batch research on multiple topics with appropriate rate limiting.
    
    Args:
        topics (list): List of research topics
        config (str): Rate limiting configuration to use
        articles_per_topic (int): Number of articles per topic
    
    Returns:
        Dict[str, list]: Results for each topic
    """
    print(f"🔍 Starting batch research for {len(topics)} topics")
    print(f"📊 Using {config} rate limiting configuration")
    print()
    
    # Create agent with batch processing settings
    agent = create_research_agent(config)
    results = {}
    
    for i, topic in enumerate(topics, 1):
        print(f"📑 Processing topic {i}/{len(topics)}: '{topic}'")
        
        try:
            articles = agent.search_articles(
                topic=topic,
                count=articles_per_topic,
                days_back=30
            )
            
            results[topic] = articles
            
            if articles:
                print(f"✅ Found {len(articles)} articles")
            else:
                print("⚠️  No articles found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results[topic] = []
        
        print()
    
    successful_topics = sum(1 for articles in results.values() if articles)
    total_articles = sum(len(articles) for articles in results.values())
    
    print(f"📊 Batch Research Summary:")
    print(f"   • Topics processed: {len(topics)}")
    print(f"   • Successful topics: {successful_topics}")
    print(f"   • Total articles found: {total_articles}")
    
    return results


def main():
    """Demonstrate the configuration helper."""
    
    print("⚙️  Research Agent Configuration Helper Demo")
    print("=" * 60)
    
    # Show available configurations
    configs = ['CONSERVATIVE', 'STANDARD', 'FAST', 'BATCH']
    
    print("📋 Available Configurations:")
    for config in configs:
        settings = getattr(RateLimitConfig, config)
        print(f"   • {config}: {settings['description']}")
        print(f"     - Delay: {settings['request_delay']}s, Retries: {settings['max_retries']}")
    print()
    
    # Demo single topic research with different configs
    test_topic = "sustainable technology innovations"
    
    print(f"🧪 Testing single topic research: '{test_topic}'")
    print("-" * 50)
    
    for config in ['FAST', 'STANDARD']:
        print(f"\n🔧 Testing {config} configuration:")
        try:
            agent = create_research_agent(config)
            articles = agent.search_articles(test_topic, count=2, days_back=30)
            
            if articles:
                print(f"✅ Success: Found {len(articles)} articles")
                for article in articles:
                    print(f"   - {article['title'][:60]}...")
            else:
                print("⚠️  No articles found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Demo batch research
    print(f"\n🚀 Testing batch research:")
    print("-" * 50)
    
    batch_topics = [
        "artificial intelligence ethics",
        "renewable energy storage",
        "quantum computing applications"
    ]
    
    try:
        results = batch_research(batch_topics, config='BATCH', articles_per_topic=2)
        
        print("\n📚 Batch Results Preview:")
        for topic, articles in results.items():
            if articles:
                print(f"   • {topic}: {len(articles)} articles")
            else:
                print(f"   • {topic}: No articles found")
                
    except Exception as e:
        print(f"❌ Batch research failed: {e}")
    
    print(f"\n🎉 Configuration helper demo completed!")
    print(f"\n💡 Usage examples:")
    print(f"   from rate_limit_config import create_research_agent, batch_research")
    print(f"   ")
    print(f"   # Create agent with conservative settings")
    print(f"   agent = create_research_agent('CONSERVATIVE')")
    print(f"   ")
    print(f"   # Batch process multiple topics")
    print(f"   results = batch_research(['topic1', 'topic2'], 'BATCH')")


if __name__ == "__main__":
    main()
