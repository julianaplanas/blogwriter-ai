#!/usr/bin/env python3
"""
AI-Powered Blog Writer - Research Agent

Main entry point for the research agent functionality.
This script provides a command-line interface for the research agent.
"""

import sys
import os
import argparse

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from research_agent import ResearchAgent, research_topic


def main():
    """Main entry point for the research agent CLI."""
    
    parser = argparse.ArgumentParser(
        description='AI-Powered Blog Writer - Research Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "artificial intelligence trends"
  python main.py "sustainable energy" --count 3 --days 14
  python main.py "quantum computing" --count 5 --days 30 --country US
        """
    )
    
    parser.add_argument('topic', help='Research topic to search for')
    parser.add_argument('--count', '-c', type=int, default=5, 
                       help='Number of articles to return (default: 5)')
    parser.add_argument('--days', '-d', type=int, default=30,
                       help='Number of days back to search (default: 30)')
    parser.add_argument('--country', default='US',
                       help='Country code for search results (default: US)')
    parser.add_argument('--output', '-o', 
                       help='Output file path (default: results/search_results.json)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    print(f"🔍 Researching topic: '{args.topic}'")
    print("=" * 50)
    
    try:
        # Initialize research agent
        agent = ResearchAgent()
        
        # Search for articles
        articles = agent.search_articles(
            topic=args.topic,
            count=args.count,
            days_back=args.days,
            country=args.country
        )
        
        if not articles:
            print("❌ No articles found or API error occurred.")
            return 1
        
        # Display results
        print(f"📰 Found {len(articles)} relevant articles:")
        print()
        
        for i, article in enumerate(articles, 1):
            print(f"{i}. **{article['title']}**")
            print(f"   🔗 {article['url']}")
            print(f"   📝 {article['snippet'][:150]}...")
            print()
        
        # Get detailed summary
        details = agent.get_article_details(articles)
        print(f"📊 Search Summary:")
        print(f"   • Total articles: {details['total_articles']}")
        print(f"   • Unique domains: {len(details['domains'])}")
        print(f"   • Domains: {', '.join(details['domains'])}")
        print(f"   • Search timestamp: {details['search_timestamp']}")
        
        # Save results
        output_file = args.output or 'results/search_results.json'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(details, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to {output_file}")
        return 0
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Make sure to set your BRAVE_API_KEY environment variable:")
        print("   export BRAVE_API_KEY='your-api-key-here'")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
