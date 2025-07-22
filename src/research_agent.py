"""
Research Agent for AI-Powered Blog Writer

This module implements a research agent that queries the Brave Search API
to retrieve recent and relevant articles for a given topic.
"""

import os
import requests
import json
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Research Agent that fetches relevant articles using Brave Search API.
    Includes intelligent rate limiting and delay management.
    """
    
    def __init__(self, api_key: Optional[str] = None, request_delay: float = 1.0, max_retries: int = 3):
        """
        Initialize the Research Agent.
        
        Args:
            api_key (str, optional): Brave Search API key. If not provided,
                                   will attempt to load from BRAVE_API_KEY environment variable.
            request_delay (float): Delay in seconds between API requests (default: 1.0)
            max_retries (int): Maximum number of retries on rate limit errors (default: 3)
        """
        self.api_key = api_key or os.getenv('BRAVE_API_KEY')
        if not self.api_key:
            raise ValueError("Brave Search API key is required. Set BRAVE_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.last_request_time = 0.0
        
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'X-Subscription-Token': self.api_key
        })
    
    def _wait_for_rate_limit(self):
        """
        Implement intelligent delay between API requests to respect rate limits.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.request_delay:
            sleep_time = self.request_delay - time_since_last_request
            logger.info(f"Rate limiting: waiting {sleep_time:.1f} seconds before next request")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request_with_retry(self, params: dict) -> Optional[dict]:
        """
        Make API request with retry logic for rate limiting.
        
        Args:
            params (dict): Request parameters
        
        Returns:
            Optional[dict]: API response data or None if failed
        """
        for attempt in range(self.max_retries + 1):
            try:
                # Wait before making request
                self._wait_for_rate_limit()
                
                # Make the API request
                response = self.session.get(self.base_url, params=params, timeout=15)
                
                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('retry-after', 5))
                    logger.warning(f"Rate limited (attempt {attempt + 1}/{self.max_retries + 1}). Waiting {retry_after} seconds...")
                    
                    if attempt < self.max_retries:
                        time.sleep(retry_after)
                        continue
                    else:
                        logger.error("Max retries exceeded for rate limiting")
                        return None
                
                # Check for other HTTP errors
                response.raise_for_status()
                
                # Parse and return JSON response
                return response.json()
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries + 1})")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    logger.error("Max retries exceeded for timeouts")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"HTTP request failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                if attempt < self.max_retries and "429" in str(e):
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    return None
        
        return None
    
    def search_articles(
        self, 
        topic: str, 
        count: int = 5, 
        days_back: int = 30,
        country: str = "US",
        safe_search: str = "moderate"
    ) -> List[Dict[str, str]]:
        """
        Search for recent articles on a given topic.
        
        Args:
            topic (str): The search topic/query
            count (int): Number of results to return (1-20, default: 5)
            days_back (int): Number of days back to search (default: 30)
            country (str): Country code for search results (default: "US")
            safe_search (str): Safe search setting ("strict", "moderate", "off")
        
        Returns:
            List[Dict[str, str]]: List of articles with title, url, and snippet
        """
        try:
            # Calculate date range for recent articles
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Prepare search parameters
            params = {
                'q': topic,
                'count': min(count, 20),  # Brave API limits to 20 results
                'country': country,
                'safesearch': safe_search,
                'freshness': f"{start_date.strftime('%Y-%m-%d')}to{end_date.strftime('%Y-%m-%d')}"
            }
            
            logger.info(f"Searching for articles on topic: '{topic}'")
            logger.info(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            # Make the API request with retry logic
            data = self._make_request_with_retry(params)
            
            if not data:
                logger.error("Failed to retrieve data from API")
                return []
            
            # Extract articles from the response
            articles = self._extract_articles(data)
            
            # Deduplicate and rank by relevance
            articles = self._deduplicate_articles(articles)
            
            logger.info(f"Found {len(articles)} relevant articles")
            return articles[:count]  # Return only the requested number
            
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            return []
    
    def _extract_articles(self, data: dict) -> List[Dict[str, str]]:
        """
        Extract article information from Brave Search API response.
        
        Args:
            data (dict): Raw API response data
        
        Returns:
            List[Dict[str, str]]: Extracted articles
        """
        articles = []
        
        # Check if we have web results
        if 'web' not in data or 'results' not in data['web']:
            logger.warning("No web results found in API response")
            return articles
        
        for result in data['web']['results']:
            try:
                article = {
                    'title': result.get('title', 'No title available'),
                    'url': result.get('url', ''),
                    'snippet': result.get('description', 'No description available')
                }
                
                # Only add articles with valid URLs
                if article['url']:
                    articles.append(article)
                    
            except Exception as e:
                logger.warning(f"Failed to extract article data: {e}")
                continue
        
        return articles
    
    def _deduplicate_articles(self, articles: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Remove duplicate articles based on URL and title similarity.
        
        Args:
            articles (List[Dict[str, str]]): List of articles
        
        Returns:
            List[Dict[str, str]]: Deduplicated articles
        """
        seen_urls = set()
        seen_titles = set()
        deduplicated = []
        
        for article in articles:
            url = article['url'].lower()
            title = article['title'].lower()
            
            # Check for duplicate URLs
            if url in seen_urls:
                continue
            
            # Check for very similar titles (simple approach)
            is_similar_title = any(
                self._is_similar_string(title, seen_title) 
                for seen_title in seen_titles
            )
            
            if not is_similar_title:
                deduplicated.append(article)
                seen_urls.add(url)
                seen_titles.add(title)
        
        return deduplicated
    
    def _is_similar_string(self, s1: str, s2: str, threshold: float = 0.8) -> bool:
        """
        Check if two strings are similar based on common words.
        
        Args:
            s1 (str): First string
            s2 (str): Second string
            threshold (float): Similarity threshold (0.0 to 1.0)
        
        Returns:
            bool: True if strings are similar
        """
        words1 = set(s1.lower().split())
        words2 = set(s2.lower().split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union)
        return similarity >= threshold
    
    def get_article_details(self, articles: List[Dict[str, str]]) -> Dict:
        """
        Get detailed information about the search results.
        
        Args:
            articles (List[Dict[str, str]]): List of articles
        
        Returns:
            Dict: Summary of the search results
        """
        return {
            'total_articles': len(articles),
            'articles': articles,
            'search_timestamp': datetime.now().isoformat(),
            'domains': list(set(self._extract_domain(article['url']) for article in articles))
        }
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url (str): Full URL
        
        Returns:
            str: Domain name
        """
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return 'unknown'


def research_topic(topic: str, count: int = 5, days_back: int = 30) -> List[Dict[str, str]]:
    """
    Convenience function to research a topic.
    
    Args:
        topic (str): The research topic
        count (int): Number of articles to return
        days_back (int): Number of days back to search
    
    Returns:
        List[Dict[str, str]]: List of relevant articles
    """
    try:
        agent = ResearchAgent()
        return agent.search_articles(topic, count, days_back)
    except Exception as e:
        logger.error(f"Research failed: {e}")
        return []


def main():
    """
    Example usage and testing function.
    """
    import sys
    
    # Check if topic is provided as command line argument
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "artificial intelligence in healthcare"
    
    print(f"🔍 Researching topic: '{topic}'")
    print("=" * 50)
    
    try:
        # Initialize research agent
        agent = ResearchAgent()
        
        # Search for articles
        articles = agent.search_articles(topic, count=5, days_back=30)
        
        if not articles:
            print("❌ No articles found or API error occurred.")
            return
        
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
        
        # Export to JSON for testing
        with open('research_results.json', 'w', encoding='utf-8') as f:
            json.dump(details, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to research_results.json")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Make sure to set your BRAVE_API_KEY environment variable:")
        print("   export BRAVE_API_KEY='your-api-key-here'")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
