"""
Demo Research Agent - Test Version

This is a demo version of the research agent that returns mock data
for testing purposes without requiring a real API key.
"""

import json
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))


class DemoResearchAgent:
    """
    Demo Research Agent that returns mock data for testing.
    """
    
    def __init__(self):
        """Initialize the demo research agent."""
        self.mock_data = {
            "artificial intelligence": [
                {
                    "title": "The Future of Artificial Intelligence in 2024: Trends and Predictions",
                    "url": "https://example.com/ai-future-2024",
                    "snippet": "Artificial intelligence continues to evolve rapidly, with new breakthroughs in machine learning, natural language processing, and computer vision shaping the future of technology."
                },
                {
                    "title": "AI Ethics and Responsible Development: A Comprehensive Guide",
                    "url": "https://example.com/ai-ethics-guide",
                    "snippet": "As AI systems become more sophisticated, the importance of ethical considerations and responsible development practices has never been more critical for ensuring beneficial outcomes."
                },
                {
                    "title": "Machine Learning Applications in Healthcare: Revolutionary Changes",
                    "url": "https://example.com/ml-healthcare",
                    "snippet": "Healthcare is being transformed by machine learning applications, from diagnostic imaging to drug discovery, improving patient outcomes and operational efficiency."
                },
                {
                    "title": "AI-Powered Automation: Transforming Industries Worldwide",
                    "url": "https://example.com/ai-automation",
                    "snippet": "Industries across the globe are adopting AI-powered automation solutions to streamline operations, reduce costs, and enhance productivity in unprecedented ways."
                },
                {
                    "title": "Natural Language Processing: Recent Advances and Applications",
                    "url": "https://example.com/nlp-advances",
                    "snippet": "Recent advances in natural language processing have enabled more sophisticated chatbots, translation services, and content generation tools that understand context better."
                }
            ],
            "climate change": [
                {
                    "title": "Climate Change Mitigation Strategies for 2024: A Global Perspective",
                    "url": "https://example.com/climate-strategies-2024",
                    "snippet": "Global efforts to combat climate change are intensifying, with new technologies and policies emerging to reduce greenhouse gas emissions and promote sustainability."
                },
                {
                    "title": "Renewable Energy Breakthrough: Solar and Wind Power Innovations",
                    "url": "https://example.com/renewable-energy-breakthrough",
                    "snippet": "Revolutionary advances in solar panel efficiency and wind turbine technology are making renewable energy more cost-effective and accessible worldwide."
                },
                {
                    "title": "Carbon Capture Technology: The Next Frontier in Climate Solutions",
                    "url": "https://example.com/carbon-capture-tech",
                    "snippet": "Cutting-edge carbon capture and storage technologies are showing promise as crucial tools in the fight against climate change and atmospheric CO2 reduction."
                }
            ],
            "sustainable energy": [
                {
                    "title": "Sustainable Energy Solutions: Powering the Future",
                    "url": "https://example.com/sustainable-energy-future",
                    "snippet": "Innovative sustainable energy solutions are revolutionizing how we generate, store, and distribute power, creating a cleaner and more efficient energy ecosystem."
                },
                {
                    "title": "Battery Technology Advances: Enabling the Clean Energy Transition",
                    "url": "https://example.com/battery-tech-advances",
                    "snippet": "Next-generation battery technologies are overcoming storage challenges, making renewable energy sources more reliable and grid-scale deployment more feasible."
                }
            ]
        }
    
    def search_articles(
        self, 
        topic: str, 
        count: int = 5, 
        days_back: int = 30,
        country: str = "US",
        safe_search: str = "moderate"
    ) -> List[Dict[str, str]]:
        """
        Mock search for articles on a given topic.
        
        Args:
            topic (str): The search topic/query
            count (int): Number of results to return (1-20, default: 5)
            days_back (int): Number of days back to search (default: 30)
            country (str): Country code for search results (default: "US")
            safe_search (str): Safe search setting
        
        Returns:
            List[Dict[str, str]]: List of mock articles
        """
        print(f"🔍 [DEMO MODE] Searching for articles on topic: '{topic}'")
        print(f"📅 Date range: Last {days_back} days")
        
        # Find the best matching mock data
        topic_lower = topic.lower()
        best_match = None
        
        for key in self.mock_data.keys():
            if key in topic_lower or any(word in topic_lower for word in key.split()):
                best_match = key
                break
        
        if best_match:
            articles = self.mock_data[best_match][:count]
            print(f"✅ Found {len(articles)} relevant articles (demo data)")
        else:
            # Generic fallback articles
            articles = [
                {
                    "title": f"Latest Developments in {topic.title()}: A Comprehensive Overview",
                    "url": f"https://example.com/{topic.lower().replace(' ', '-')}-overview",
                    "snippet": f"Explore the latest trends and developments in {topic}, covering key innovations, challenges, and future prospects in this rapidly evolving field."
                },
                {
                    "title": f"Understanding {topic.title()}: Key Concepts and Applications",
                    "url": f"https://example.com/{topic.lower().replace(' ', '-')}-concepts",
                    "snippet": f"A detailed analysis of {topic}, examining fundamental concepts, practical applications, and their impact on various industries and society."
                },
                {
                    "title": f"The Future of {topic.title()}: Trends and Predictions",
                    "url": f"https://example.com/{topic.lower().replace(' ', '-')}-future",
                    "snippet": f"Expert insights into the future of {topic}, highlighting emerging trends, potential challenges, and opportunities for innovation and growth."
                }
            ][:count]
            print(f"✅ Generated {len(articles)} generic demo articles")
        
        return articles
    
    def get_article_details(self, articles: List[Dict[str, str]]) -> Dict:
        """
        Get detailed information about the mock search results.
        
        Args:
            articles (List[Dict[str, str]]): List of articles
        
        Returns:
            Dict: Summary of the search results
        """
        return {
            'total_articles': len(articles),
            'articles': articles,
            'search_timestamp': datetime.now().isoformat(),
            'domains': ['example.com', 'demo.org', 'test.net'][:len(articles)]
        }


def demo_research_topic(topic: str, count: int = 5, days_back: int = 30) -> List[Dict[str, str]]:
    """
    Demo convenience function to research a topic using mock data.
    
    Args:
        topic (str): The research topic
        count (int): Number of articles to return
        days_back (int): Number of days back to search
    
    Returns:
        List[Dict[str, str]]: List of mock articles
    """
    agent = DemoResearchAgent()
    return agent.search_articles(topic, count, days_back)


def main():
    """
    Demo testing function.
    """
    import sys
    
    print("🎭 DEMO MODE - Research Agent Test")
    print("=" * 50)
    print("📝 Note: This is using mock data for demonstration purposes")
    print()
    
    # Check if topic is provided as command line argument
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "artificial intelligence healthcare"
    
    print(f"🔍 Researching topic: '{topic}'")
    print("=" * 50)
    
    # Initialize demo research agent
    agent = DemoResearchAgent()
    
    # Search for articles
    articles = agent.search_articles(topic, count=5, days_back=30)
    
    # Display results
    print(f"📰 Found {len(articles)} relevant articles:")
    print()
    
    for i, article in enumerate(articles, 1):
        print(f"{i}. **{article['title']}**")
        print(f"   🔗 {article['url']}")
        print(f"   📝 {article['snippet']}")
        print()
    
    # Get detailed summary
    details = agent.get_article_details(articles)
    print(f"📊 Search Summary:")
    print(f"   • Total articles: {details['total_articles']}")
    print(f"   • Unique domains: {len(details['domains'])}")
    print(f"   • Domains: {', '.join(details['domains'])}")
    print(f"   • Search timestamp: {details['search_timestamp']}")
    
    # Export to JSON for testing
    with open('demo_research_results.json', 'w', encoding='utf-8') as f:
        json.dump(details, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to demo_research_results.json")
    print(f"\n🎉 Demo completed successfully!")
    print(f"\n💡 To test with real API:")
    print(f"   1. Get a Brave Search API key from https://brave.com/search/api/")
    print(f"   2. Set environment variable: export BRAVE_API_KEY='your-key'")
    print(f"   3. Run: python research_agent.py '{topic}'")


if __name__ == "__main__":
    main()
