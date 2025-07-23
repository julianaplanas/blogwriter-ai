"""
Blog Writer Agent for AI-Powered Blog Writer

This module implements a blog writing agent that generates structured Markdown
blog posts using LLM providers based on research data and topics.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Add config directory to Python path for model configuration
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
sys.path.insert(0, config_path)

# Add src directory to Python path for image agent
src_path = os.path.dirname(__file__)
sys.path.insert(0, src_path)

try:
    from models import get_best_model_for_task, get_model_info, GROQ_MODELS
except ImportError:
    # Fallback if models.py not found
    def get_best_model_for_task(task: str, provider: str = "groq") -> str:
        return "llama-3.1-8b-instant"
    def get_model_info(model_id: str, provider: str = "groq") -> dict:
        return {}
    GROQ_MODELS = {}

try:
    from image_agent import ImageAgent
except ImportError:
    ImageAgent = None
    logging.warning("Image Agent not available - images will use placeholders only")

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlogWriterAgent:
    """
    Blog Writer Agent that generates structured blog posts using LLMs.
    """
    
    def __init__(self, 
                 llm_provider: str = "groq",
                 api_key: Optional[str] = None,
                 model: Optional[str] = None,
                 task: str = "blog_writing",
                 use_images: bool = True):
        """
        Initialize the Blog Writer Agent.
        
        Args:
            llm_provider (str): LLM provider ("groq", "openai", "anthropic") - defaults to "groq"
            api_key (str, optional): API key for the LLM provider
            model (str, optional): Model name to use (auto-selected if not provided)
            task (str): Task type for optimal model selection
            use_images (bool): Whether to fetch real images or use placeholders only
        """
        self.llm_provider = llm_provider.lower()
        self.use_images = use_images
        
        # Initialize image agent if available and requested
        self.image_agent = None
        if self.use_images and ImageAgent:
            try:
                self.image_agent = ImageAgent(provider="pexels")  # Use Pexels by default
                logger.info("Image Agent initialized with Pexels - will fetch real images")
            except Exception as e:
                logger.warning(f"Image Agent initialization failed: {e}")
                logger.warning("Will use image placeholders only")
        elif not self.use_images:
            logger.info("Image fetching disabled - will use placeholders only")
        
        # Auto-select best model for task if not provided
        if model is None:
            self.model = get_best_model_for_task(task, self.llm_provider)
        else:
            self.model = model
        
        # Get model info for optimization
        self.model_info = get_model_info(self.model, self.llm_provider)
        
        # Set up API key based on provider
        if api_key:
            self.api_key = api_key
        elif self.llm_provider == "groq":
            self.api_key = os.getenv('GROQ_API_KEY')
        elif self.llm_provider == "openai":
            self.api_key = os.getenv('OPENAI_API_KEY')
        elif self.llm_provider == "anthropic":
            self.api_key = os.getenv('ANTHROPIC_API_KEY')
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
        
        if not self.api_key:
            raise ValueError(f"API key for {llm_provider} is required. Set {llm_provider.upper()}_API_KEY environment variable.")
        
        # Initialize the LLM client
        self._init_llm_client()
        
        logger.info(f"Initialized Blog Writer Agent with {llm_provider} provider")
        logger.info(f"Using model: {self.model} ({self.model_info.get('name', 'Unknown')})")
        if self.model_info.get('description'):
            logger.info(f"Model description: {self.model_info['description']}")
    
    def _init_llm_client(self):
        """Initialize the appropriate LLM client based on provider."""
        try:
            if self.llm_provider == "openai":
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            elif self.llm_provider == "groq":
                import groq
                self.client = groq.Groq(api_key=self.api_key)
            elif self.llm_provider == "anthropic":
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError as e:
            raise ImportError(f"Required package for {self.llm_provider} not installed: {e}")
    
    def _create_blog_prompt(self, topic: str, research_results: List[Dict]) -> str:
        """
        Create a comprehensive prompt for blog generation.
        
        Args:
            topic (str): The blog topic
            research_results (List[Dict]): Research data from Research Agent
        
        Returns:
            str: Formatted prompt for the LLM
        """
        # Extract research information
        sources_info = []
        for i, source in enumerate(research_results[:5], 1):  # Limit to top 5 sources
            sources_info.append(
                f"{i}. **{source.get('title', 'No title')}**\n"
                f"   URL: {source.get('url', 'No URL')}\n"
                f"   Summary: {source.get('snippet', 'No summary')}\n"
            )
        
        sources_text = "\n".join(sources_info)
        
        prompt = f"""You are an expert technical writer creating a comprehensive blog post. Your task is to write a well-structured, informative, and engaging ~1000-word blog post in Markdown format.

TOPIC: {topic}

RESEARCH SOURCES:
{sources_text}

REQUIREMENTS:
1. **Structure**: Use proper Markdown formatting with:
   - Main title (# Title)
   - Section headings (## Section)
   - Subsections (### Subsection) as needed
   - Bullet points and numbered lists where appropriate
   - Bold and italic text for emphasis

2. **Content Guidelines**:
   - Write approximately 1000 words
   - Create an engaging introduction that hooks the reader
   - Develop 4-6 main sections with substantial content
   - Include specific examples and practical insights
   - Write a compelling conclusion with key takeaways
   - Maintain a professional yet accessible tone

3. **Source Integration**:
   - Naturally incorporate 2-3 of the provided sources into your content
   - Reference sources by embedding links in relevant sentences
   - Don't just list sources - weave them into the narrative
   - Use phrases like "According to [source]" or "Recent research shows"

4. **References Section**:
   - End with a "## References" section
   - List all sources you referenced in the content
   - Format as: "- [Title](URL) - Brief description"

5. **Image Placeholders**:
   - Include 2-3 image placeholder comments where relevant
   - Format as: `<!-- IMAGE: descriptive keyword for image search -->`
   - Place them strategically throughout the content

6. **SEO Optimization**:
   - Use the main topic keyword naturally throughout
   - Include related keywords and synonyms
   - Create descriptive headings

Write the complete blog post now, ensuring it's informative, well-researched, and professionally formatted in Markdown:"""

        return prompt
    
    def _call_llm(self, prompt: str, temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """
        Call the LLM with the given prompt.
        
        Args:
            prompt (str): The prompt to send to the LLM
            temperature (float): Temperature setting for creativity
            max_tokens (int, optional): Maximum tokens to generate (auto-selected if not provided)
        
        Returns:
            str: Generated content from the LLM
        """
        # Auto-select max_tokens based on model capabilities
        if max_tokens is None:
            max_tokens = min(self.model_info.get('max_tokens', 2000), 4000)  # Cap at 4000 for blog posts
        
        try:
            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif self.llm_provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif self.llm_provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"LLM call failed with {self.llm_provider} ({self.model}): {e}")
            raise
    
    def _extract_used_sources(self, markdown_content: str, research_results: List[Dict]) -> List[str]:
        """
        Extract which sources were actually used in the generated content.
        
        Args:
            markdown_content (str): Generated markdown content
            research_results (List[Dict]): Original research results
        
        Returns:
            List[str]: URLs of sources that were referenced
        """
        used_sources = []
        
        for source in research_results:
            url = source.get('url', '')
            if url and url in markdown_content:
                used_sources.append(url)
        
        return used_sources
    
    def _extract_image_keywords(self, markdown_content: str) -> List[str]:
        """
        Extract image keywords from the markdown content.
        
        Args:
            markdown_content (str): Generated markdown content
        
        Returns:
            List[str]: List of image keywords found
        """
        import re
        
        # Find all image placeholder comments
        pattern = r'<!-- IMAGE: (.*?) -->'
        matches = re.findall(pattern, markdown_content)
        
        return [match.strip() for match in matches]
    
    def _fetch_images_for_topic(self, topic: str, image_keywords: List[str]) -> List[Dict]:
        """
        Fetch real images for the blog topic.
        
        Args:
            topic (str): Blog topic
            image_keywords (List[str]): Keywords extracted from content
        
        Returns:
            List[Dict]: List of image metadata
        """
        if not self.image_agent:
            logger.info("Image agent not available, using placeholders only")
            return []
        
        try:
            logger.info(f"Fetching images for topic: '{topic}'")
            images = self.image_agent.fetch_images(
                topic=topic,
                keywords=image_keywords[:3],  # Limit keywords
                count=3  # Fetch up to 3 images
            )
            logger.info(f"Successfully fetched {len(images)} images")
            return images
        except Exception as e:
            logger.error(f"Failed to fetch images: {e}")
            return []
    
    def _integrate_images_into_content(self, markdown_content: str, images: List[Dict]) -> tuple[str, List[Dict]]:
        """
        Replace image placeholders with real images or improve placeholders.
        
        Args:
            markdown_content (str): Blog content with placeholders
            images (List[Dict]): Available images
        
        Returns:
            tuple[str, List[Dict]]: (Content with integrated images, List of actually used images)
        """
        if not images:
            return markdown_content, []
        
        import re
        
        # Find all image placeholder comments
        placeholder_pattern = r'<!-- IMAGE: ([^-->]+) -->'
        placeholders = re.findall(placeholder_pattern, markdown_content)
        
        logger.info(f"Found {len(placeholders)} image placeholders to replace")
        
        updated_content = markdown_content
        used_images = []
        
        # Replace placeholders with actual images
        for i, placeholder_text in enumerate(placeholders):
            if i >= len(images):
                break  # No more images available
            
            image = images[i]
            used_images.append(image)  # Track actually used images
            
            # Create markdown image with proper attribution
            alt_text = placeholder_text  # Use the placeholder text as alt text
            image_markdown = f"![{alt_text}]({image['image_url']})"
            
            # Add attribution
            attribution = self.image_agent.get_attribution_text(image) if self.image_agent else ""
            if attribution:
                image_markdown += f"\n\n*{attribution}*"
            
            # Replace the placeholder
            old_placeholder = f"<!-- IMAGE: {placeholder_text} -->"
            updated_content = updated_content.replace(old_placeholder, image_markdown, 1)
            
            logger.info(f"Replaced placeholder '{placeholder_text}' with image by {image.get('photographer', 'Unknown')}")
        
        return updated_content, used_images
    
    def _add_image_section_to_blog(self, markdown_content: str, images: List[Dict]) -> str:
        """
        Add an image credits section to the blog post if images were used.
        
        Args:
            markdown_content (str): Blog content
            images (List[Dict]): Used images
        
        Returns:
            str: Content with image credits section
        """
        if not images or not self.image_agent:
            return markdown_content
        
        # Add image credits section before references
        credits_section = "\n\n## Image Credits\n\n"
        
        for i, image in enumerate(images, 1):
            attribution = self.image_agent.get_attribution_text(image)
            credits_section += f"{i}. {attribution}\n"
        
        # Insert before the References section
        if "## References" in markdown_content:
            markdown_content = markdown_content.replace("## References", credits_section + "\n## References")
        else:
            # Add at the end
            markdown_content += credits_section
        
        return markdown_content
    
    def generate_blog_post(self, 
                          topic: str, 
                          research_results: List[Dict],
                          temperature: float = 0.7,
                          max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Generate a complete blog post based on topic and research.
        
        Args:
            topic (str): The blog post topic
            research_results (List[Dict]): Research data from Research Agent
            temperature (float): LLM temperature setting
            max_tokens (int): Maximum tokens to generate
        
        Returns:
            Dict[str, Any]: Generated blog post data
        """
        logger.info(f"Generating blog post for topic: '{topic}'")
        logger.info(f"Using {len(research_results)} research sources")
        
        try:
            # Create the prompt
            prompt = self._create_blog_prompt(topic, research_results)
            
            # Generate content using LLM
            markdown_content = self._call_llm(prompt, temperature, max_tokens)
            
            # Extract metadata
            used_sources = self._extract_used_sources(markdown_content, research_results)
            image_keywords = self._extract_image_keywords(markdown_content)
            
            # Fetch real images if enabled
            images = self._fetch_images_for_topic(topic, image_keywords)
            
            # Integrate images into content and get actually used images
            markdown_content, used_images = self._integrate_images_into_content(markdown_content, images)
            
            # Add image credits section only for actually used images
            markdown_content = self._add_image_section_to_blog(markdown_content, used_images)
            
            # Count words (approximate)
            word_count = len(markdown_content.split())
            
            result = {
                "topic": topic,
                "markdown": markdown_content,
                "used_sources": used_sources,
                "image_keywords": image_keywords,
                "images": used_images,  # Return only actually used images
                "metadata": {
                    "word_count": word_count,
                    "sources_available": len(research_results),
                    "sources_used": len(used_sources),
                    "image_placeholders": len(image_keywords),
                    "images_fetched": len(images),
                    "images_integrated": len(used_images),
                    "llm_provider": self.llm_provider,
                    "model": self.model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "generated_at": datetime.now().isoformat()
                }
            }
            
            logger.info(f"Blog post generated successfully:")
            logger.info(f"  • Word count: {word_count}")
            logger.info(f"  • Sources used: {len(used_sources)}/{len(research_results)}")
            logger.info(f"  • Image placeholders: {len(image_keywords)}")
            logger.info(f"  • Images fetched: {len(images)}")
            logger.info(f"  • Images integrated: {min(len(image_keywords), len(images))}")
            
            return result
            
        except Exception as e:
            logger.error(f"Blog generation failed: {e}")
            return {
                "topic": topic,
                "markdown": "",
                "used_sources": [],
                "image_keywords": [],
                "error": str(e),
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "status": "failed"
                }
            }
    
    def edit_content(self, content: str, instruction: str, provider: str = None, model: str = None) -> str:
        """
        Edit existing blog content using natural language instructions.
        
        Args:
            content (str): Existing blog content to edit
            instruction (str): Natural language editing instruction
            provider (str, optional): LLM provider to use
            model (str, optional): Specific model to use
            
        Returns:
            str: Edited content
        """
        logger.info(f"Editing content with instruction: {instruction}")
        
        # Use provided provider/model or default to instance settings
        edit_provider = provider or self.provider
        edit_model = model or self.model
        
        # Prepare the editing prompt
        edit_prompt = f"""You are a professional blog editor. Your task is to edit the given blog post according to the user's instruction.

**Original Blog Post:**
{content}

**Editing Instruction:**
{instruction}

**Important Guidelines:**
1. Keep the original tone and style unless specifically asked to change it
2. Maintain the Markdown formatting structure
3. Preserve any references, links, and citations
4. If adding content, make it consistent with the existing content
5. If shortening, maintain the key points and flow
6. Return ONLY the edited blog post content, no additional commentary

**Edited Blog Post:**"""

        try:
            if edit_provider == 'groq':
                import groq
                client = groq.Groq(api_key=self.api_key)
                
                response = client.chat.completions.create(
                    model=edit_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional blog editor skilled at improving and modifying content based on specific instructions."
                        },
                        {
                            "role": "user", 
                            "content": edit_prompt
                        }
                    ],
                    max_tokens=4000,
                    temperature=0.3,
                    stream=False
                )
                
                edited_content = response.choices[0].message.content.strip()
                logger.info(f"Content edited successfully using {edit_model}")
                return edited_content
                
            else:
                logger.error(f"Unsupported provider for editing: {edit_provider}")
                return content  # Return original if provider not supported
                
        except Exception as e:
            logger.error(f"Error editing content: {e}")
            # Return original content if editing fails
            return content

    # ...existing methods continue below...
def generate_blog_post(topic: str, 
                      research_results: List[Dict],
                      llm_provider: str = "openai",
                      model: str = "gpt-3.5-turbo",
                      temperature: float = 0.7,
                      max_tokens: int = 2000) -> Dict[str, Any]:
    """
    Convenience function to generate a blog post.
    
    Args:
        topic (str): Blog post topic
        research_results (List[Dict]): Research data
        llm_provider (str): LLM provider to use
        model (str): Model name
        temperature (float): Temperature setting
        max_tokens (int): Max tokens to generate
    
    Returns:
        Dict[str, Any]: Generated blog post
    """
    try:
        agent = BlogWriterAgent(llm_provider=llm_provider, model=model)
        return agent.generate_blog_post(topic, research_results, temperature, max_tokens)
    except Exception as e:
        logger.error(f"Blog generation failed: {e}")
        return {
            "topic": topic,
            "markdown": "",
            "used_sources": [],
            "image_keywords": [],
            "error": str(e),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "status": "failed"
            }
        }


def main():
    """
    Example usage and testing function.
    """
    import sys
    
    # Mock research data for testing
    mock_research = [
        {
            "title": "The Future of Artificial Intelligence: Trends and Predictions",
            "url": "https://example.com/ai-future",
            "snippet": "AI continues to evolve with breakthroughs in machine learning, natural language processing, and computer vision, reshaping industries worldwide."
        },
        {
            "title": "Machine Learning in Healthcare: Revolutionary Applications",
            "url": "https://example.com/ml-healthcare",
            "snippet": "Healthcare is being transformed by ML applications in diagnostics, drug discovery, and personalized medicine, improving patient outcomes."
        },
        {
            "title": "Ethical AI Development: Best Practices and Guidelines",
            "url": "https://example.com/ai-ethics",
            "snippet": "As AI systems become more powerful, ethical considerations and responsible development practices are crucial for beneficial outcomes."
        }
    ]
    
    # Get topic from command line or use default
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "The Future of Artificial Intelligence"
    
    print(f"✍️  Generating blog post for topic: '{topic}'")
    print("=" * 60)
    print("📝 Note: This demo uses mock research data")
    print()
    
    try:
        # Generate blog post (this will fail without API key, but shows the structure)
        result = generate_blog_post(
            topic=topic,
            research_results=mock_research,
            llm_provider="openai",  # Change as needed
            temperature=0.7,
            max_tokens=2000
        )
        
        if result.get('error'):
            print(f"❌ Generation failed: {result['error']}")
            print("💡 To use the blog writer agent:")
            print("   1. Set up an LLM provider API key:")
            print("      export OPENAI_API_KEY='your-key'  # for OpenAI")
            print("      export GROQ_API_KEY='your-key'    # for Groq")
            print("   2. Install required packages:")
            print("      pip install openai groq anthropic")
            print("   3. Run with real research data")
        else:
            print("✅ Blog post generated successfully!")
            print(f"📊 Statistics:")
            print(f"   • Word count: {result['metadata']['word_count']}")
            print(f"   • Sources used: {result['metadata']['sources_used']}")
            print(f"   • Image placeholders: {result['metadata']['image_placeholders']}")
            print()
            print("📄 Generated Content Preview:")
            print("-" * 40)
            print(result['markdown'][:500] + "..." if len(result['markdown']) > 500 else result['markdown'])
            
            # Save to file
            filename = f"results/blog_post_{topic.lower().replace(' ', '_')}.md"
            os.makedirs('results', exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result['markdown'])
            
            print(f"\n💾 Full blog post saved to: {filename}")
            
            # Save metadata
            metadata_filename = f"results/blog_metadata_{topic.lower().replace(' ', '_')}.json"
            with open(metadata_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Metadata saved to: {metadata_filename}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
