"""
Test script for the Research Agent

This script demonstrates how to use the research agent and provides
various test scenarios.
"""

import json
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from research_agent import ResearchAgent, research_topic


def test_research_agent():
    """Test the research agent with various topics."""
    
    test_topics = [
        "artificial intelligence trends 2024",
        "climate change renewable energy",
        "space exploration mars missions",
        "quantum computing breakthroughs",
        "sustainable agriculture technology"
    ]
    
    print("🧪 Testing Research Agent")
    print("=" * 50)
    
    for topic in test_topics:
        print(f"\n🔍 Testing topic: '{topic}'")
        print("-" * 40)
        
        try:
            # Use the convenience function
            articles = research_topic(topic, count=3, days_back=30)
            
            if articles:
                print(f"✅ Found {len(articles)} articles:")
                for i, article in enumerate(articles, 1):
                    print(f"  {i}. {article['title'][:60]}...")
                    print(f"     {article['url']}")
            else:
                print("❌ No articles found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")


def test_detailed_search():
    """Test detailed search functionality."""
    
    print("\n🔬 Testing Detailed Search")
    print("=" * 50)
    
    try:
        agent = ResearchAgent()
        
        # Test with specific parameters
        topic = "machine learning healthcare applications"
        articles = agent.search_articles(
            topic=topic,
            count=5,
            days_back=14,  # Last 2 weeks only
            country="US"
        )
        
        if articles:
            details = agent.get_article_details(articles)
            
            print(f"📊 Search Results for '{topic}':")
            print(f"   • Articles found: {details['total_articles']}")
            print(f"   • Unique domains: {len(details['domains'])}")
            print(f"   • Search timestamp: {details['search_timestamp']}")
            
            print(f"\n📰 Articles:")
            for i, article in enumerate(articles, 1):
                print(f"  {i}. **{article['title']}**")
                print(f"     🔗 {article['url']}")
                print(f"     📝 {article['snippet'][:100]}...")
                print()
            
            # Save detailed results
            with open('test_results.json', 'w', encoding='utf-8') as f:
                json.dump(details, f, indent=2, ensure_ascii=False)
            
            print("💾 Detailed results saved to test_results.json")
        
        else:
            print("❌ No articles found")
            
    except Exception as e:
        print(f"❌ Error during detailed search: {e}")


def test_error_handling():
    """Test error handling scenarios."""
    
    print("\n🛡️ Testing Error Handling")
    print("=" * 50)
    
    # Test with invalid API key
    try:
        agent = ResearchAgent(api_key="invalid_key")
        articles = agent.search_articles("test topic", count=1)
        print(f"Result with invalid key: {len(articles)} articles")
    except Exception as e:
        print(f"✅ Properly handled invalid API key: {type(e).__name__}")
    
    # Test with no API key
    try:
        import os
        old_key = os.environ.get('BRAVE_API_KEY')
        if 'BRAVE_API_KEY' in os.environ:
            del os.environ['BRAVE_API_KEY']
        
        agent = ResearchAgent()
        print("❌ Should have raised ValueError for missing API key")
        
    except ValueError as e:
        print(f"✅ Properly handled missing API key: {e}")
    
    finally:
        if old_key:
            os.environ['BRAVE_API_KEY'] = old_key


if __name__ == "__main__":
    # Run basic tests
    test_research_agent()
    
    # Run detailed tests
    test_detailed_search()
    
    # Test error handling
    test_error_handling()
    
    print("\n🎉 All tests completed!")
    print("\n💡 To run with your own API key:")
    print("   export BRAVE_API_KEY='your-api-key'")
    print("   python test_research_agent.py")
