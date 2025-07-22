"""
Tests for the Image Agent.

This module contains tests to verify the Image Agent functionality,
including Unsplash API integration and image fetching.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestImageAgent(unittest.TestCase):
    """Test cases for the Image Agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_unsplash_response = {
            'results': [
                {
                    'id': 'test-id-1',
                    'urls': {
                        'regular': 'https://example.com/image1.jpg',
                        'small': 'https://example.com/image1_small.jpg'
                    },
                    'alt_description': 'Artificial intelligence concept',
                    'description': 'AI visualization',
                    'user': {
                        'name': 'Test Photographer',
                        'links': {'html': 'https://unsplash.com/@photographer'}
                    },
                    'links': {'html': 'https://unsplash.com/photos/test-id-1'},
                    'width': 1920,
                    'height': 1080
                },
                {
                    'id': 'test-id-2', 
                    'urls': {
                        'regular': 'https://example.com/image2.jpg'
                    },
                    'alt_description': 'Machine learning visualization',
                    'user': {
                        'name': 'Another Photographer',
                        'links': {'html': 'https://unsplash.com/@another'}
                    },
                    'links': {'html': 'https://unsplash.com/photos/test-id-2'}
                }
            ]
        }
    
    def test_initialization_with_api_key(self):
        """Test Image Agent initialization with API key."""
        with patch.dict(os.environ, {'UNSPLASH_API_KEY': 'test-key'}):
            from image_agent import ImageAgent
            agent = ImageAgent()
            self.assertEqual(agent.api_key, 'test-key')
            self.assertIn('Client-ID test-key', agent.headers['Authorization'])
    
    def test_initialization_without_api_key(self):
        """Test that missing API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            from image_agent import ImageAgent
            with self.assertRaises(ValueError) as context:
                ImageAgent()
            self.assertIn("Unsplash API key is required", str(context.exception))
    
    @patch('image_agent.requests.get')
    def test_search_images_success(self, mock_get):
        """Test successful image search."""
        with patch.dict(os.environ, {'UNSPLASH_API_KEY': 'test-key'}):
            from image_agent import ImageAgent
            
            # Mock successful API response
            mock_response = MagicMock()
            mock_response.json.return_value = self.mock_unsplash_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            agent = ImageAgent()
            results = agent._search_images('artificial intelligence', count=2)
            
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]['id'], 'test-id-1')
            self.assertEqual(results[1]['id'], 'test-id-2')
            
            # Verify API call parameters
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            self.assertIn('query', call_args[1]['params'])
            self.assertEqual(call_args[1]['params']['query'], 'artificial intelligence')
    
    @patch('image_agent.requests.get')
    def test_search_images_api_error(self, mock_get):
        """Test handling of API errors."""
        with patch.dict(os.environ, {'UNSPLASH_API_KEY': 'test-key'}):
            from image_agent import ImageAgent
            
            # Mock API error
            mock_get.side_effect = Exception("API Error")
            
            agent = ImageAgent()
            results = agent._search_images('test query', count=2)
            
            self.assertEqual(results, [])  # Should return empty list on error
    
    def test_process_image_data(self):
        """Test image data processing."""
        with patch.dict(os.environ, {'UNSPLASH_API_KEY': 'test-key'}):
            from image_agent import ImageAgent
            
            agent = ImageAgent()
            raw_data = self.mock_unsplash_response['results'][0]
            processed = agent._process_image_data(raw_data)
            
            expected_keys = [
                'image_url', 'alt_description', 'source_url', 
                'photographer', 'photographer_url', 'width', 'height'
            ]
            
            for key in expected_keys:
                self.assertIn(key, processed)
            
            self.assertEqual(processed['image_url'], 'https://example.com/image1.jpg')
            self.assertEqual(processed['photographer'], 'Test Photographer')
            self.assertEqual(processed['alt_description'], 'Artificial intelligence concept')
    
    @patch('image_agent.requests.get')
    def test_fetch_images_with_topic_only(self, mock_get):
        """Test fetching images with topic only."""
        with patch.dict(os.environ, {'UNSPLASH_API_KEY': 'test-key'}):
            from image_agent import ImageAgent
            
            # Mock successful API response
            mock_response = MagicMock()
            mock_response.json.return_value = self.mock_unsplash_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            agent = ImageAgent()
            images = agent.fetch_images('artificial intelligence', count=2)
            
            self.assertEqual(len(images), 2)
            self.assertIn('search_query', images[0])
            self.assertEqual(images[0]['search_query'], 'artificial intelligence')
    
    @patch('image_agent.requests.get')
    def test_fetch_images_with_keywords(self, mock_get):
        """Test fetching images with additional keywords."""
        with patch.dict(os.environ, {'UNSPLASH_API_KEY': 'test-key'}):
            from image_agent import ImageAgent
            
            # Mock successful API response  
            mock_response = MagicMock()
            mock_response.json.return_value = self.mock_unsplash_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            agent = ImageAgent()
            images = agent.fetch_images(
                'AI', 
                keywords=['machine learning', 'neural networks'], 
                count=3
            )
            
            # Should have made API calls (exact number depends on response sizes)
            self.assertTrue(mock_get.called)
            self.assertTrue(len(images) <= 3)  # Should not exceed requested count
    
    def test_get_attribution_text(self):
        """Test attribution text generation."""
        with patch.dict(os.environ, {'UNSPLASH_API_KEY': 'test-key'}):
            from image_agent import ImageAgent
            
            agent = ImageAgent()
            image_data = {
                'photographer': 'Test Photographer',
                'source_url': 'https://unsplash.com/photos/test'
            }
            
            attribution = agent.get_attribution_text(image_data)
            
            self.assertIn('Test Photographer', attribution)
            self.assertIn('Unsplash', attribution)
            self.assertIn('https://unsplash.com/photos/test', attribution)
    
    def test_get_markdown_image(self):
        """Test Markdown image generation."""
        with patch.dict(os.environ, {'UNSPLASH_API_KEY': 'test-key'}):
            from image_agent import ImageAgent
            
            agent = ImageAgent()
            image_data = {
                'image_url': 'https://example.com/test.jpg',
                'alt_description': 'Test image'
            }
            
            markdown = agent.get_markdown_image(image_data)
            expected = '![Test image](https://example.com/test.jpg)'
            
            self.assertEqual(markdown, expected)
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        with patch.dict(os.environ, {'UNSPLASH_API_KEY': 'test-key'}):
            from image_agent import ImageAgent
            import time
            
            agent = ImageAgent()
            agent.min_delay = 0.1  # Short delay for testing
            
            start_time = time.time()
            agent._rate_limit()  # First call should be immediate
            agent._rate_limit()  # Second call should be delayed
            end_time = time.time()
            
            # Should take at least the minimum delay
            self.assertGreaterEqual(end_time - start_time, 0.05)


class TestImageIntegration(unittest.TestCase):
    """Test integration with blog writer system."""
    
    def test_convenience_function(self):
        """Test the convenience function."""
        with patch.dict(os.environ, {'UNSPLASH_API_KEY': 'test-key'}):
            with patch('image_agent.ImageAgent') as mock_agent_class:
                from image_agent import fetch_blog_images
                
                # Mock agent instance
                mock_agent = MagicMock()
                mock_agent.fetch_images.return_value = [{'test': 'data'}]
                mock_agent_class.return_value = mock_agent
                
                result = fetch_blog_images('test topic', ['keyword1'])
                
                self.assertEqual(result, [{'test': 'data'}])
                mock_agent.fetch_images.assert_called_once_with('test topic', ['keyword1'])


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
