"""
Integration Example: Research Agent + Blog Writer

This example demonstrates how to integrate the research agent
with a blog writing workflow.
"""

import json
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
from research_agent import ResearchAgent


def generate_research_report(topic: str) -> dict:
    """
    Generate a comprehensive research report for a topic.
    
    Args:
        topic (str): The research topic
    
    Returns:
        dict: Comprehensive research report
    """
    print(f"🔍 Starting research on: {topic}")
    
    try:
        # Initialize research agent with rate limiting
        agent = ResearchAgent(
            request_delay=1.5,  # 1.5 seconds between requests
            max_retries=3       # Allow up to 3 retries
        )
        
        # Get recent articles
        articles = agent.search_articles(
            topic=topic,
            count=5,
            days_back=30
        )
        
        if not articles:
            return {
                'topic': topic,
                'status': 'failed',
                'error': 'No articles found',
                'timestamp': datetime.now().isoformat()
            }
        
        # Get additional details
        details = agent.get_article_details(articles)
        
        # Create comprehensive report
        report = {
            'topic': topic,
            'status': 'success',
            'research_summary': {
                'total_sources': len(articles),
                'unique_domains': len(details['domains']),
                'search_date_range': '30 days',
                'primary_domains': details['domains'][:3]  # Top 3 domains
            },
            'sources': articles,
            'metadata': {
                'timestamp': details['search_timestamp'],
                'agent_version': '1.0.0'
            }
        }
        
        return report
        
    except Exception as e:
        return {
            'topic': topic,
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def create_blog_outline_with_research(topic: str) -> dict:
    """
    Create a blog post outline enhanced with research data.
    
    Args:
        topic (str): Blog topic
    
    Returns:
        dict: Blog outline with research integration points
    """
    print(f"📝 Creating blog outline for: {topic}")
    
    # Get research data
    research = generate_research_report(topic)
    
    if research['status'] != 'success':
        return {
            'error': f"Research failed: {research.get('error', 'Unknown error')}",
            'topic': topic
        }
    
    # Create enhanced blog outline
    outline = {
        'title': f"The Complete Guide to {topic.title()}",
        'topic': topic,
        'research_backed': True,
        'sections': [
            {
                'title': 'Introduction',
                'content_hints': ['Hook the reader', 'Define the topic', 'Preview main points'],
                'research_integration': 'Use recent statistics from sources'
            },
            {
                'title': 'Current Landscape',
                'content_hints': ['Recent developments', 'Key trends', 'Market overview'],
                'research_integration': f"Reference {len(research['sources'])} recent sources",
                'primary_sources': research['sources'][:2]  # Top 2 most relevant
            },
            {
                'title': 'Key Insights and Analysis',
                'content_hints': ['Deep dive into main concepts', 'Expert perspectives', 'Data analysis'],
                'research_integration': 'Quote directly from research sources',
                'supporting_sources': research['sources'][2:4]  # Additional sources
            },
            {
                'title': 'Practical Applications',
                'content_hints': ['Real-world examples', 'How-to guidance', 'Best practices'],
                'research_integration': 'Use case studies from research'
            },
            {
                'title': 'Future Outlook',
                'content_hints': ['Emerging trends', 'Predictions', 'What to watch'],
                'research_integration': 'Reference forward-looking insights'
            },
            {
                'title': 'Conclusion',
                'content_hints': ['Summarize key points', 'Call to action', 'Final thoughts'],
                'research_integration': 'Reinforce with data points'
            }
        ],
        'research_data': research,
        'estimated_word_count': 1000,
        'target_audience': 'General readers interested in ' + topic,
        'creation_timestamp': datetime.now().isoformat()
    }
    
    return outline


def main():
    """
    Example usage of research-enhanced blog creation.
    """
    print("🚀 Research-Enhanced Blog Creation Demo")
    print("=" * 50)
    
    # Example topics
    topics = [
        "sustainable energy solutions",
        "artificial intelligence in education",
        "remote work productivity tools"
    ]
    
    for topic in topics:
        print(f"\n📑 Processing topic: {topic}")
        print("-" * 40)
        
        try:
            # Generate research report
            report = generate_research_report(topic)
            
            if report['status'] == 'success':
                print(f"✅ Research completed: {report['research_summary']['total_sources']} sources found")
                
                # Create blog outline
                outline = create_blog_outline_with_research(topic)
                
                if 'error' not in outline:
                    print(f"✅ Blog outline created: {len(outline['sections'])} sections")
                    
                    # Save the complete research and outline
                    filename = f"blog_research_{topic.replace(' ', '_')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump({
                            'research_report': report,
                            'blog_outline': outline
                        }, f, indent=2, ensure_ascii=False)
                    
                    print(f"💾 Saved to {filename}")
                else:
                    print(f"❌ Outline creation failed: {outline['error']}")
            else:
                print(f"❌ Research failed: {report.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error processing {topic}: {e}")
    
    print(f"\n🎉 Demo completed!")
    print(f"\n💡 Next steps:")
    print(f"   1. Review generated research files")
    print(f"   2. Use outline data to generate actual blog content")
    print(f"   3. Integrate with LLM for content generation")


if __name__ == "__main__":
    main()
