"""
Simple Blog Writer Agent Test

A basic test to verify the blog writer agent works with Groq models.
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_blog_writer_initialization():
    """Test that the Blog Writer Agent can be initialized."""
    try:
        from blog_writer_agent import BlogWriterAgent
        
        # Check if Groq API key is available
        if not os.getenv('GROQ_API_KEY'):
            print("⚠️  GROQ_API_KEY not found, skipping LLM tests")
            return True
        
        print("🤖 Testing Blog Writer Agent initialization...")
        
        # Test default Groq initialization
        agent = BlogWriterAgent()
        print(f"   ✅ Initialized with provider: {agent.llm_provider}")
        print(f"   ✅ Using model: {agent.model}")
        
        # Test custom model
        agent_custom = BlogWriterAgent(model="llama-3.1-8b-instant")
        print(f"   ✅ Custom model: {agent_custom.model}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return False


def test_prompt_generation():
    """Test blog prompt generation."""
    try:
        from blog_writer_agent import BlogWriterAgent
        
        if not os.getenv('GROQ_API_KEY'):
            print("⚠️  GROQ_API_KEY not found, skipping prompt test")
            return True
        
        print("📝 Testing prompt generation...")
        
        agent = BlogWriterAgent()
        
        # Mock research data
        research_data = [
            {
                "title": "AI Trends 2024",
                "url": "https://example.com/ai-trends",
                "snippet": "Latest developments in artificial intelligence..."
            }
        ]
        
        prompt = agent._create_blog_prompt("Artificial Intelligence", research_data)
        
        # Check prompt contains expected elements
        assert "Artificial Intelligence" in prompt
        assert "AI Trends 2024" in prompt
        assert "Markdown" in prompt
        assert "1000-word" in prompt
        
        print("   ✅ Prompt generation successful")
        return True
        
    except Exception as e:
        print(f"   ❌ Prompt generation failed: {e}")
        return False


def test_model_configuration():
    """Test model configuration loading."""
    try:
        # Test config import
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config')
        sys.path.insert(0, config_path)
        
        from models import get_best_model_for_task, list_available_models
        
        print("⚙️  Testing model configuration...")
        
        # Test model selection
        blog_model = get_best_model_for_task("blog_writing", "groq")
        print(f"   ✅ Best blog writing model: {blog_model}")
        
        # Test model listing
        models = list_available_models("groq")
        print(f"   ✅ Available models: {len(models)} found")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Model configuration failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Running Blog Writer Agent Tests")
    print("=" * 40)
    
    tests = [
        test_model_configuration,
        test_blog_writer_initialization,
        test_prompt_generation,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 Test Results:")
    print(f"   Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
