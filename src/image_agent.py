"""
Image Agent for AI-Powered Blog Writer

This module implements an image fetching agent that retrieves relevant,
openly licensed images using the Pexels API for blog post illustration.
"""

import os
import requests
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageAgent:
    """
    Image Agent that fetches relevant images from Pexels API.
    """
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "pexels"):
        """
        Initialize the Image Agent.
        
        Args:
            api_key (str, optional): Pexels API key
            provider (str): Image provider ("pexels" or "unsplash")
        """
        self.provider = provider.lower()
        
        if self.provider == "pexels":
            self.api_key = api_key or os.getenv('PEXELS_API_KEY')
            if not self.api_key:
                raise ValueError("Pexels API key is required. Set PEXELS_API_KEY environment variable.")
            
            self.base_url = "https://api.pexels.com/v1"
            self.headers = {
                'Authorization': self.api_key
            }
        elif self.provider == "unsplash":
            self.api_key = api_key or os.getenv('UNSPLASH_API_KEY')
            if not self.api_key:
                raise ValueError("Unsplash API key is required. Set UNSPLASH_API_KEY environment variable.")
            
            self.base_url = "https://api.unsplash.com"
            self.headers = {
                'Authorization': f'Client-ID {self.api_key}',
                'Accept-Version': 'v1'
            }
        else:
            raise ValueError(f"Unsupported image provider: {provider}")
        
        # Rate limiting
        self.last_request_time = 0
        self.min_delay = 1.0  # Minimum delay between requests (1 second)
        
        logger.info(f"Initialized Image Agent with {self.provider.title()} API")
    
    def _rate_limit(self):
        """Apply rate limiting between API calls."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _search_images(self, query: str, count: int = 3) -> List[Dict]:
        """
        Search for images using Pexels or Unsplash API.
        
        Args:
            query (str): Search query
            count (int): Number of images to fetch (max 80 for Pexels, 30 for Unsplash)
        
        Returns:
            List[Dict]: List of image data
        """
        self._rate_limit()
        
        try:
            if self.provider == "pexels":
                url = f"{self.base_url}/search"
                params = {
                    'query': query,
                    'per_page': min(count, 80),
                    'orientation': 'landscape'
                }
            else:  # unsplash
                url = f"{self.base_url}/search/photos"
                params = {
                    'query': query,
                    'per_page': min(count, 30),
                    'orientation': 'landscape',
                    'content_filter': 'high',
                    'order_by': 'relevant'
                }
            
            logger.info(f"Searching {self.provider.title()} for: '{query}' (count: {count})")
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if self.provider == "pexels":
                results = data.get('photos', [])
            else:  # unsplash
                results = data.get('results', [])
            
            logger.info(f"Found {len(results)} images for query: '{query}'")
            return results
            
        except requests.RequestException as e:
            logger.error(f"{self.provider.title()} API request failed for query '{query}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching images: {e}")
            return []
    
    def _process_image_data(self, image_data: Dict) -> Dict:
        """
        Process raw image data into standardized format (works for both Pexels and Unsplash).
        
        Args:
            image_data (Dict): Raw image data from API
        
        Returns:
            Dict: Processed image metadata
        """
        try:
            if self.provider == "pexels":
                # Pexels API format
                image_url = image_data.get('src', {}).get('large') or image_data.get('src', {}).get('medium')
                alt_description = image_data.get('alt', 'Image')
                source_url = image_data.get('url', '')
                photographer_name = image_data.get('photographer', 'Unknown')
                photographer_url = image_data.get('photographer_url', '')
                image_id = image_data.get('id', '')
                
                processed_data = {
                    'image_url': image_url,
                    'alt_description': alt_description,
                    'source_url': source_url,
                    'photographer': photographer_name,
                    'photographer_url': photographer_url,
                    'width': image_data.get('width'),
                    'height': image_data.get('height'),
                    'download_url': image_data.get('src', {}).get('original'),
                    'provider_id': image_id,
                    'provider': 'pexels'
                }
                
            else:  # unsplash
                # Unsplash API format
                urls = image_data.get('urls', {})
                image_url = urls.get('regular') or urls.get('small') or urls.get('thumb')
                
                alt_description = (
                    image_data.get('alt_description') or 
                    image_data.get('description') or 
                    "Image"
                )
                
                user = image_data.get('user', {})
                photographer_name = user.get('name', 'Unknown')
                photographer_url = user.get('links', {}).get('html', '')
                source_url = image_data.get('links', {}).get('html', '')
                
                processed_data = {
                    'image_url': image_url,
                    'alt_description': alt_description,
                    'source_url': source_url,
                    'photographer': photographer_name,
                    'photographer_url': photographer_url,
                    'width': image_data.get('width'),
                    'height': image_data.get('height'),
                    'download_url': urls.get('download'),
                    'provider_id': image_data.get('id'),
                    'provider': 'unsplash'
                }
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing image data: {e}")
            return {}
    
    def fetch_images(self, topic: str, keywords: Optional[List[str]] = None, count: int = 3) -> List[Dict]:
        """
        Fetch relevant images for a blog topic.
        
        Args:
            topic (str): Main blog topic
            keywords (List[str], optional): Additional keywords from blog sections
            count (int): Number of images to fetch (2-3 recommended)
        
        Returns:
            List[Dict]: List of image metadata dictionaries
        """
        if count > 3:
            logger.warning(f"Requested {count} images, limiting to 3 for better performance")
            count = min(count, 3)
        
        all_images = []
        queries_used = set()
        
        # Primary search with main topic
        if topic and topic not in queries_used:
            images = self._search_images(topic, count)
            for img in images[:count]:
                processed = self._process_image_data(img)
                if processed and processed.get('image_url'):
                    processed['search_query'] = topic
                    all_images.append(processed)
            queries_used.add(topic.lower())
        
        # If we need more images and have keywords, search with them
        if len(all_images) < count and keywords:
            remaining_count = count - len(all_images)
            
            for keyword in keywords[:2]:  # Limit to 2 additional keyword searches
                if len(all_images) >= count:
                    break
                
                # Skip if we already searched this keyword
                keyword_lower = keyword.lower()
                if keyword_lower in queries_used:
                    continue
                
                logger.info(f"Searching with keyword: '{keyword}'")
                images = self._search_images(keyword, remaining_count)
                
                for img in images[:remaining_count]:
                    processed = self._process_image_data(img)
                    if processed and processed.get('image_url'):
                        # Avoid duplicates
                        if not any(existing['provider_id'] == processed['provider_id'] for existing in all_images):
                            processed['search_query'] = keyword
                            all_images.append(processed)
                            
                            if len(all_images) >= count:
                                break
                
                queries_used.add(keyword_lower)
        
        # Limit to requested count
        final_images = all_images[:count]
        
        logger.info(f"Successfully fetched {len(final_images)} images for topic: '{topic}'")
        
        # Log image details
        for i, img in enumerate(final_images, 1):
            logger.info(f"  {i}. {img['alt_description']} (by {img['photographer']})")
        
        return final_images
    
    def get_attribution_text(self, image_data: Dict) -> str:
        """
        Generate attribution text for an image.
        
        Args:
            image_data (Dict): Image metadata
        
        Returns:
            str: Attribution text
        """
        photographer = image_data.get('photographer', 'Unknown')
        source_url = image_data.get('source_url', '')
        provider = image_data.get('provider', 'unknown')
        
        if source_url:
            if provider == 'pexels':
                return f"Photo by [{photographer}]({source_url}) on [Pexels](https://www.pexels.com/)"
            else:  # unsplash
                return f"Photo by [{photographer}]({source_url}) on [Unsplash](https://unsplash.com/)"
        else:
            return f"Photo by {photographer} on {provider.title()}"
    
    def get_markdown_image(self, image_data: Dict, alt_override: Optional[str] = None) -> str:
        """
        Generate Markdown image syntax for an image.
        
        Args:
            image_data (Dict): Image metadata
            alt_override (str, optional): Override alt text
        
        Returns:
            str: Markdown image syntax
        """
        image_url = image_data.get('image_url', '')
        alt_text = alt_override or image_data.get('alt_description', 'Image')
        
        if not image_url:
            return f"<!-- IMAGE: {alt_text} -->"
        
        return f"![{alt_text}]({image_url})"


def fetch_blog_images(topic: str, keywords: Optional[List[str]] = None, provider: str = "pexels") -> List[Dict]:
    """
    Convenience function to fetch images for a blog topic.
    
    Args:
        topic (str): Main blog topic
        keywords (List[str], optional): Additional keywords
        provider (str): Image provider ("pexels" or "unsplash")
    
    Returns:
        List[Dict]: List of image metadata
    """
    try:
        agent = ImageAgent(provider=provider)
        return agent.fetch_images(topic, keywords)
    except Exception as e:
        logger.error(f"Failed to fetch blog images: {e}")
        return []


# Example usage and testing
if __name__ == "__main__":
    # Test the Image Agent
    print("🖼️  Testing Image Agent")
    print("=" * 40)
    
    try:
        # Test with environment variable
        agent = ImageAgent(provider="pexels")  # Default to Pexels
        
        # Test image fetching
        topic = "artificial intelligence"
        keywords = ["machine learning", "neural networks", "AI technology"]
        
        print(f"Fetching images for topic: '{topic}'")
        images = agent.fetch_images(topic, keywords, count=3)
        
        if images:
            print(f"\n✅ Successfully fetched {len(images)} images:")
            for i, img in enumerate(images, 1):
                print(f"\n{i}. **{img['alt_description']}**")
                print(f"   URL: {img['image_url']}")
                print(f"   Source: {img['source_url']}")
                print(f"   Photographer: {img['photographer']}")
                print(f"   Attribution: {agent.get_attribution_text(img)}")
                print(f"   Markdown: {agent.get_markdown_image(img)}")
        else:
            print("❌ No images found")
            
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Make sure to set your PEXELS_API_KEY environment variable")
        print("   Get your free API key at: https://www.pexels.com/api/")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
