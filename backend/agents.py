import os
import requests
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ResearchAgent:
    """Agent for researching topics using Brave Search API."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")

    def search(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        params = {
            "q": query,
            "count": count,
            "search_lang": "en",
            "country": "US",
            "safesearch": "moderate",
            "freshness": "pw"
        }
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            articles = []
            if "web" in result and "results" in result["web"]:
                for item in result["web"]["results"]:
                    articles.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("description", ""),
                        "age": item.get("age", "")
                    })
            return articles
        except Exception as e:
            logger.warning(f"Brave Search API failed: {e}")
            return []

class WritingAgent:
    """Agent for generating blog content using Groq LLM API."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

    def generate(self, topic: str, research_context: str = "") -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        prompt = f"""Write a comprehensive blog post about {topic} in clean markdown format.{research_context}\n\nRequirements:\n- Start directly with the title (e.g., \"# Title\")\n- Include an introduction, main content with key points, and a conclusion\n- Make it engaging and informative\n- Use proper markdown formatting\n- Do NOT add any explanatory text like \"Here is the blog post:\" or \"Main Content:\"\n- Return ONLY the markdown content, no metadata or commentary\n\nWrite the blog post:"""
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2500,
            "temperature": 0.7
        }
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

class ImageAgent:
    """Agent for searching images using Pexels API."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PEXELS_API_KEY")

    def search(self, query: str, per_page: int = 3) -> List[Dict[str, Any]]:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": self.api_key}
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": "landscape"
        }
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            images = []
            if "photos" in result:
                for photo in result["photos"]:
                    images.append({
                        "id": photo.get("id"),
                        "url": photo["src"]["original"],
                        "medium_url": photo["src"]["medium"],
                        "photographer": photo.get("photographer", ""),
                        "alt": photo.get("alt", query)
                    })
            return images
        except Exception as e:
            logger.warning(f"Pexels API failed: {e}")
            return []

class EditingAgent:
    """Agent for editing blog content using Groq LLM API."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

    def edit(self, content: str, instruction: str) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        prompt = f"""Edit the following content according to the instruction provided. Return ONLY the edited markdown content.\n\nOriginal content:\n{content}\n\nInstruction: {instruction}\n\nRequirements:\n- Return ONLY the edited markdown content\n- Maintain the same style and format\n- Only make changes that align with the instruction\n- Do NOT add any explanatory text like \"Here is the edited content:\" or \"Main Content:\"\n- Do NOT add any metadata or commentary\n- Start directly with the content\n\nEdited content:"""
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2500,
            "temperature": 0.7
        }
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"] 