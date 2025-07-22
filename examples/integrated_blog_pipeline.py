"""
Integrated Blog Creation Pipeline

This example demonstrates the complete workflow:
Research Agent → Blog Writer Agent → Final Blog Post
"""

import sys
import os
import json
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from research_agent import ResearchAgent
    from blog_writer_agent import BlogWriterAgent, generate_blog_post
    from llm_config import get_optimal_settings
    
    # Import from config directory
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'))
    from rate_limit_config import create_research_agent
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure all source files are in the src directory")
    sys.exit(1)


def create_complete_blog_workflow(topic: str,
                                research_config: str = 'STANDARD',
                                llm_provider: str = 'openai',
                                llm_model: str = None,
                                use_case: str = 'balanced') -> dict:
    """
    Complete blog creation workflow combining research and writing agents.
    
    Args:
        topic (str): Blog topic
        research_config (str): Research agent rate limiting config
        llm_provider (str): LLM provider for blog writing
        llm_model (str): Specific model to use (optional)
        use_case (str): Use case for optimal LLM settings
    
    Returns:
        dict: Complete blog creation results
    """
    workflow_results = {
        'topic': topic,
        'workflow_start': datetime.now().isoformat(),
        'steps': {},
        'final_blog': {},
        'errors': []
    }
    
    print(f"🚀 Starting Complete Blog Creation Workflow")
    print(f"📑 Topic: '{topic}'")
    print(f"⚙️  Research Config: {research_config}")
    print(f"🤖 LLM Provider: {llm_provider} ({use_case})")
    print("=" * 60)
    
    # Step 1: Research Phase
    print(f"\n🔍 Step 1: Research Phase")
    print("-" * 30)
    
    try:
        # Create research agent with specified config
        research_agent = create_research_agent(research_config)
        
        # Perform research
        research_results = research_agent.search_articles(
            topic=topic,
            count=5,
            days_back=30
        )
        
        if research_results:
            print(f"✅ Research completed: {len(research_results)} sources found")
            workflow_results['steps']['research'] = {
                'status': 'success',
                'sources_found': len(research_results),
                'sources': research_results,
                'timestamp': datetime.now().isoformat()
            }
        else:
            print(f"⚠️  No research results found")
            workflow_results['steps']['research'] = {
                'status': 'no_results',
                'sources_found': 0,
                'timestamp': datetime.now().isoformat()
            }
            workflow_results['errors'].append("No research results found")
            
    except Exception as e:
        print(f"❌ Research phase failed: {e}")
        workflow_results['steps']['research'] = {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        workflow_results['errors'].append(f"Research failed: {e}")
        research_results = []
    
    # Step 2: Blog Writing Phase
    print(f"\n✍️  Step 2: Blog Writing Phase")
    print("-" * 30)
    
    try:
        if research_results:
            # Get optimal settings for the LLM
            llm_settings = get_optimal_settings(llm_provider, use_case)
            if llm_model:
                llm_settings['model'] = llm_model
            
            print(f"🔧 Using {llm_provider} with model: {llm_settings['model']}")
            
            # Generate blog post
            blog_result = generate_blog_post(
                topic=topic,
                research_results=research_results,
                llm_provider=llm_provider,
                model=llm_settings['model'],
                temperature=llm_settings['temperature'],
                max_tokens=llm_settings['max_tokens']
            )
            
            if blog_result.get('error'):
                print(f"⚠️  Blog generation failed: {blog_result['error']}")
                workflow_results['steps']['blog_writing'] = {
                    'status': 'failed',
                    'error': blog_result['error'],
                    'timestamp': datetime.now().isoformat()
                }
                workflow_results['errors'].append(f"Blog writing failed: {blog_result['error']}")
            else:
                print(f"✅ Blog post generated successfully!")
                print(f"   • Word count: {blog_result['metadata']['word_count']}")
                print(f"   • Sources used: {blog_result['metadata']['sources_used']}")
                print(f"   • Image placeholders: {blog_result['metadata']['image_placeholders']}")
                
                workflow_results['steps']['blog_writing'] = {
                    'status': 'success',
                    'metadata': blog_result['metadata'],
                    'timestamp': datetime.now().isoformat()
                }
                workflow_results['final_blog'] = blog_result
                
        else:
            # Create blog with mock data as fallback
            print(f"⚠️  Creating blog with limited information (no research data)")
            
            mock_research = [{
                'title': f'Information about {topic}',
                'url': 'https://example.com/mock-source',
                'snippet': f'General information and insights about {topic} and related concepts.'
            }]
            
            blog_result = generate_blog_post(
                topic=topic,
                research_results=mock_research,
                llm_provider=llm_provider,
                temperature=0.7,
                max_tokens=2000
            )
            
            workflow_results['steps']['blog_writing'] = {
                'status': 'fallback',
                'note': 'Used mock data due to research failure',
                'timestamp': datetime.now().isoformat()
            }
            workflow_results['final_blog'] = blog_result
            
    except Exception as e:
        print(f"❌ Blog writing phase failed: {e}")
        workflow_results['steps']['blog_writing'] = {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        workflow_results['errors'].append(f"Blog writing failed: {e}")
    
    # Step 3: Save Results
    print(f"\n💾 Step 3: Save Results")
    print("-" * 30)
    
    try:
        # Create results directory
        os.makedirs('../results', exist_ok=True)
        
        # Generate filename-safe topic name
        safe_topic = topic.lower().replace(' ', '_').replace('/', '_')[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save blog post if generated
        if workflow_results['final_blog'].get('markdown'):
            blog_filename = f"../results/complete_blog_{safe_topic}_{timestamp}.md"
            with open(blog_filename, 'w', encoding='utf-8') as f:
                f.write(workflow_results['final_blog']['markdown'])
            print(f"✅ Blog post saved: {blog_filename}")
        
        # Save complete workflow results
        workflow_filename = f"../results/workflow_{safe_topic}_{timestamp}.json"
        with open(workflow_filename, 'w', encoding='utf-8') as f:
            json.dump(workflow_results, f, indent=2, ensure_ascii=False)
        print(f"✅ Workflow results saved: {workflow_filename}")
        
        workflow_results['files_saved'] = {
            'blog_post': blog_filename if workflow_results['final_blog'].get('markdown') else None,
            'workflow_data': workflow_filename
        }
        
    except Exception as e:
        print(f"❌ Failed to save results: {e}")
        workflow_results['errors'].append(f"Save failed: {e}")
    
    # Final summary
    workflow_results['workflow_end'] = datetime.now().isoformat()
    workflow_results['success'] = len(workflow_results['errors']) == 0
    
    return workflow_results


def demo_workflow():
    """Demonstrate the complete workflow with different configurations."""
    
    print("🎬 Complete Blog Creation Workflow Demo")
    print("=" * 70)
    
    # Demo topics
    demo_topics = [
        "The Future of Renewable Energy",
        "Artificial Intelligence in Education",
        "Sustainable Urban Planning"
    ]
    
    # Demo configurations
    demo_configs = [
        {
            'research_config': 'STANDARD',
            'llm_provider': 'openai',
            'use_case': 'balanced'
        },
        {
            'research_config': 'CONSERVATIVE',
            'llm_provider': 'groq',
            'use_case': 'quality'
        }
    ]
    
    results_summary = []
    
    for i, topic in enumerate(demo_topics[:1], 1):  # Test with first topic
        config = demo_configs[0]  # Use first config
        
        print(f"\n🎯 Demo {i}: '{topic}'")
        print(f"Configuration: {config}")
        print("=" * 50)
        
        try:
            workflow_result = create_complete_blog_workflow(
                topic=topic,
                research_config=config['research_config'],
                llm_provider=config['llm_provider'],
                use_case=config['use_case']
            )
            
            results_summary.append({
                'topic': topic,
                'success': workflow_result['success'],
                'errors': len(workflow_result['errors']),
                'research_sources': workflow_result['steps'].get('research', {}).get('sources_found', 0),
                'blog_generated': bool(workflow_result['final_blog'].get('markdown'))
            })
            
        except Exception as e:
            print(f"❌ Demo {i} failed: {e}")
            results_summary.append({
                'topic': topic,
                'success': False,
                'error': str(e)
            })
    
    # Print summary
    print(f"\n📊 Demo Results Summary")
    print("=" * 70)
    
    for result in results_summary:
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"• {result['topic']}: {status}")
        if result['success']:
            print(f"  Research sources: {result.get('research_sources', 'N/A')}")
            print(f"  Blog generated: {'Yes' if result.get('blog_generated') else 'No'}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")


def main():
    """Main function for testing the integrated workflow."""
    
    if len(sys.argv) > 1:
        # Run with user-provided topic
        topic = " ".join(sys.argv[1:])
        
        print(f"🚀 Running integrated workflow for: '{topic}'")
        
        result = create_complete_blog_workflow(
            topic=topic,
            research_config='STANDARD',
            llm_provider='openai',
            use_case='balanced'
        )
        
        if result['success']:
            print(f"\n🎉 Workflow completed successfully!")
        else:
            print(f"\n⚠️  Workflow completed with {len(result['errors'])} errors:")
            for error in result['errors']:
                print(f"   • {error}")
    else:
        # Run demo
        demo_workflow()
    
    print(f"\n💡 Usage Tips:")
    print(f"   • Set BRAVE_API_KEY for research functionality")
    print(f"   • Set OPENAI_API_KEY or GROQ_API_KEY for blog generation")
    print(f"   • Run with topic: python integrated_blog_pipeline.py 'your topic'")


if __name__ == "__main__":
    main()
