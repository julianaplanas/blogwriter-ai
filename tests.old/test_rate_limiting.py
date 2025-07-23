"""
Enhanced Test for Research Agent with Rate Limiting

This script tests the research agent's rate limiting and retry functionality.
"""

import time
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from research_agent import ResearchAgent


def test_rate_limiting():
    """Test rate limiting with multiple rapid requests."""
    
    print("🚦 Testing Rate Limiting and Retry Logic")
    print("=" * 60)
    
    # Test topics for rapid succession
    topics = [
        "artificial intelligence 2024",
        "sustainable energy trends",
        "machine learning healthcare",
        "quantum computing advances",
        "renewable energy technology"
    ]
    
    print(f"🔄 Testing {len(topics)} consecutive requests with rate limiting...")
    print()
    
    # Initialize agent with specific rate limiting settings
    agent = ResearchAgent(
        request_delay=2.0,  # 2 seconds between requests
        max_retries=3       # 3 retry attempts
    )
    
    results = {}
    start_time = time.time()
    
    for i, topic in enumerate(topics, 1):
        print(f"📑 Request {i}/{len(topics)}: '{topic}'")
        print("-" * 40)
        
        request_start = time.time()
        
        try:
            articles = agent.search_articles(
                topic=topic, 
                count=3,  # Fewer results to be more respectful
                days_back=30
            )
            
            request_duration = time.time() - request_start
            
            if articles:
                print(f"✅ Success: Found {len(articles)} articles")
                print(f"⏱️  Request took {request_duration:.1f} seconds")
                results[topic] = {
                    'status': 'success',
                    'count': len(articles),
                    'duration': request_duration,
                    'titles': [article['title'][:50] + "..." for article in articles[:2]]
                }
            else:
                print(f"⚠️  No articles found or rate limited")
                results[topic] = {
                    'status': 'no_results',
                    'count': 0,
                    'duration': request_duration
                }
                
        except Exception as e:
            request_duration = time.time() - request_start
            print(f"❌ Error: {e}")
            results[topic] = {
                'status': 'error',
                'error': str(e),
                'duration': request_duration
            }
        
        print()
    
    total_duration = time.time() - start_time
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"Total test duration: {total_duration:.1f} seconds")
    print(f"Average time per request: {total_duration/len(topics):.1f} seconds")
    print()
    
    successful_requests = sum(1 for r in results.values() if r['status'] == 'success')
    failed_requests = len(results) - successful_requests
    
    print(f"✅ Successful requests: {successful_requests}/{len(topics)}")
    print(f"❌ Failed/limited requests: {failed_requests}/{len(topics)}")
    print()
    
    # Show successful results
    if successful_requests > 0:
        print("🎯 Successful Results:")
        for topic, result in results.items():
            if result['status'] == 'success':
                print(f"   • {topic}: {result['count']} articles ({result['duration']:.1f}s)")
                for title in result.get('titles', []):
                    print(f"     - {title}")
    
    return results


def test_different_delays():
    """Test different delay settings."""
    
    print("\n⚙️  Testing Different Rate Limiting Settings")
    print("=" * 60)
    
    delay_settings = [
        {"delay": 0.5, "name": "Fast (0.5s)"},
        {"delay": 1.0, "name": "Medium (1.0s)"},
        {"delay": 2.0, "name": "Conservative (2.0s)"}
    ]
    
    test_topic = "climate change solutions"
    
    for setting in delay_settings:
        print(f"\n🔧 Testing {setting['name']} delay setting:")
        print("-" * 30)
        
        try:
            agent = ResearchAgent(
                request_delay=setting['delay'],
                max_retries=2
            )
            
            start_time = time.time()
            articles = agent.search_articles(test_topic, count=2, days_back=30)
            duration = time.time() - start_time
            
            if articles:
                print(f"✅ Success: {len(articles)} articles in {duration:.1f}s")
            else:
                print(f"⚠️  No results in {duration:.1f}s")
                
        except Exception as e:
            print(f"❌ Failed: {e}")


def main():
    """Run the enhanced rate limiting tests."""
    
    print("🧪 Enhanced Research Agent Rate Limiting Test")
    print("=" * 70)
    print("📝 This test demonstrates intelligent rate limiting and retry logic.")
    print("⏰ The agent will automatically add delays between requests.")
    print("🔄 Failed requests will be retried with exponential backoff.")
    print()
    
    try:
        # Test 1: Rate limiting with multiple requests
        results = test_rate_limiting()
        
        # Test 2: Different delay settings
        test_different_delays()
        
        print("\n🎉 Enhanced Testing Completed!")
        print("\n💡 Key Features Demonstrated:")
        print("   • Automatic delays between requests")
        print("   • Intelligent retry logic on rate limits")
        print("   • Exponential backoff on failures")
        print("   • Configurable delay and retry settings")
        print("   • Graceful handling of API limits")
        
        print("\n🔧 Usage Tips:")
        print("   • Use 1-2 second delays for production")
        print("   • Increase delays if you get frequent rate limits")
        print("   • Adjust max_retries based on your use case")
        print("   • Monitor the logs for rate limiting events")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print("💡 Make sure your BRAVE_API_KEY is set in the .env file")


if __name__ == "__main__":
    main()
