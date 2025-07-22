"""
Advanced Editing Agent for AI-Powered Blog Writer

This module implements an advanced blog editing agent with features like:
- Natural language editing instructions
- Diff tracking and change summaries
- Version history and undo functionality
- Multiple LLM provider support
- Configurable editing parameters
"""

import os
import json
import logging
import difflib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EditResult:
    """Result of an editing operation with diff tracking."""
    original_content: str
    edited_content: str
    instruction: str
    changes_summary: str
    diff_html: str
    diff_text: str
    timestamp: datetime
    model_used: str
    provider_used: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class EditVersion:
    """Version information for content history."""
    version_id: str
    content: str
    instruction: str
    timestamp: datetime
    parent_version: Optional[str] = None


class EditingAgent:
    """
    Advanced Blog Editing Agent with diff tracking, versioning, and multi-provider support.
    """
    
    def __init__(self, 
                 llm_provider: str = "groq",
                 api_key: Optional[str] = None,
                 model: Optional[str] = None,
                 max_versions: int = 10):
        """
        Initialize the Editing Agent.
        
        Args:
            llm_provider (str): LLM provider ("groq", "openai", "anthropic")
            api_key (str, optional): API key for the LLM provider
            model (str, optional): Model name to use
            max_versions (int): Maximum number of versions to keep in history
        """
        self.llm_provider = llm_provider.lower()
        self.max_versions = max_versions
        self.version_history: List[EditVersion] = []
        
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
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        
        if not self.api_key:
            raise ValueError(f"API key not found for provider {self.llm_provider}")
        
        # Set default model based on provider
        if model is None:
            if self.llm_provider == "groq":
                self.model = "llama-3.1-8b-instant"  # Fast and capable
            elif self.llm_provider == "openai":
                self.model = "gpt-3.5-turbo"
            elif self.llm_provider == "anthropic":
                self.model = "claude-3-haiku-20240307"
        else:
            self.model = model
        
        logger.info(f"Editing Agent initialized with {self.llm_provider} provider using {self.model}")

    def apply_edit(self, 
                   markdown_text: str, 
                   instruction: str,
                   temperature: float = 0.3,
                   max_tokens: int = 4000,
                   track_version: bool = True) -> EditResult:
        """
        Apply natural language editing instruction to markdown content.
        
        Args:
            markdown_text (str): Original blog post content in Markdown
            instruction (str): Natural language edit instruction
            temperature (float): LLM temperature (0.0-1.0)
            max_tokens (int): Maximum tokens to generate
            track_version (bool): Whether to track this edit in version history
            
        Returns:
            EditResult: Result with edited content and diff information
        """
        logger.info(f"Applying edit with instruction: '{instruction[:100]}...'")
        
        try:
            # Generate edited content using LLM
            edited_content = self._generate_edit(
                markdown_text, instruction, temperature, max_tokens
            )
            
            # Generate diff and change summary
            diff_text, diff_html = self._generate_diff(markdown_text, edited_content)
            changes_summary = self._generate_changes_summary(
                markdown_text, edited_content, instruction
            )
            
            # Create edit result
            result = EditResult(
                original_content=markdown_text,
                edited_content=edited_content,
                instruction=instruction,
                changes_summary=changes_summary,
                diff_html=diff_html,
                diff_text=diff_text,
                timestamp=datetime.now(),
                model_used=self.model,
                provider_used=self.llm_provider,
                success=True
            )
            
            # Track version if requested
            if track_version:
                self._add_version(edited_content, instruction)
            
            logger.info("Edit applied successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error applying edit: {e}")
            return EditResult(
                original_content=markdown_text,
                edited_content=markdown_text,  # Return original on error
                instruction=instruction,
                changes_summary="Edit failed",
                diff_html="",
                diff_text="",
                timestamp=datetime.now(),
                model_used=self.model,
                provider_used=self.llm_provider,
                success=False,
                error_message=str(e)
            )

    def _generate_edit(self, 
                       content: str, 
                       instruction: str,
                       temperature: float,
                       max_tokens: int) -> str:
        """Generate edited content using the specified LLM provider."""
        
        # Create structured prompt for better editing results
        edit_prompt = f"""You are a professional blog editor with expertise in improving written content. Your task is to edit the given blog post according to the specific instruction provided.

**ORIGINAL BLOG POST:**
{content}

**EDITING INSTRUCTION:**
{instruction}

**EDITING GUIDELINES:**
1. Follow the instruction precisely while maintaining content quality
2. Preserve the Markdown formatting and structure
3. Keep the original tone and style unless specifically asked to change it
4. Maintain any existing references, links, and citations
5. Ensure smooth transitions and logical flow after edits
6. If adding content, make it consistent with existing content
7. If removing content, ensure remaining content flows naturally

**IMPORTANT:** Return ONLY the fully edited blog post in Markdown format. Do not include explanations, comments, or metadata.

**EDITED BLOG POST:**"""

        if self.llm_provider == "groq":
            return self._edit_with_groq(edit_prompt, temperature, max_tokens)
        elif self.llm_provider == "openai":
            return self._edit_with_openai(edit_prompt, temperature, max_tokens)
        elif self.llm_provider == "anthropic":
            return self._edit_with_anthropic(edit_prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.llm_provider}")

    def _edit_with_groq(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Edit content using Groq API."""
        try:
            import groq
            client = groq.Groq(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional blog editor skilled at improving and modifying content based on specific instructions. Always return clean Markdown content without additional commentary."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise

    def _edit_with_openai(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Edit content using OpenAI API."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional blog editor skilled at improving and modifying content based on specific instructions. Always return clean Markdown content without additional commentary."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _edit_with_anthropic(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Edit content using Anthropic API."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def _generate_diff(self, original: str, edited: str) -> Tuple[str, str]:
        """Generate text and HTML diff between original and edited content."""
        
        # Generate unified diff
        diff_lines = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            edited.splitlines(keepends=True),
            fromfile='original',
            tofile='edited',
            n=3
        ))
        diff_text = ''.join(diff_lines)
        
        # Generate HTML diff
        differ = difflib.HtmlDiff()
        diff_html = differ.make_file(
            original.splitlines(),
            edited.splitlines(),
            fromdesc='Original',
            todesc='Edited'
        )
        
        return diff_text, diff_html

    def _generate_changes_summary(self, original: str, edited: str, instruction: str) -> str:
        """Generate a summary of changes made during editing."""
        
        original_lines = original.splitlines()
        edited_lines = edited.splitlines()
        
        # Count changes
        diff = list(difflib.unified_diff(original_lines, edited_lines, n=0))
        additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        
        # Calculate word count change
        original_words = len(original.split())
        edited_words = len(edited.split())
        word_change = edited_words - original_words
        
        # Create summary
        summary = f"Applied instruction: '{instruction}'\n"
        summary += f"Lines added: {additions}, Lines removed: {deletions}\n"
        summary += f"Word count change: {word_change:+d} words ({original_words} → {edited_words})"
        
        return summary

    def _add_version(self, content: str, instruction: str) -> None:
        """Add a new version to the history."""
        
        # Generate version ID
        version_id = f"v{len(self.version_history) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get parent version
        parent_version = self.version_history[-1].version_id if self.version_history else None
        
        # Create version
        version = EditVersion(
            version_id=version_id,
            content=content,
            instruction=instruction,
            timestamp=datetime.now(),
            parent_version=parent_version
        )
        
        self.version_history.append(version)
        
        # Trim history if it exceeds max versions
        if len(self.version_history) > self.max_versions:
            self.version_history = self.version_history[-self.max_versions:]
        
        logger.info(f"Added version {version_id} to history")

    def get_version_history(self) -> List[Dict[str, Any]]:
        """Get the version history as a list of dictionaries."""
        return [asdict(version) for version in self.version_history]

    def undo_to_version(self, version_id: str) -> Optional[str]:
        """Undo to a specific version and return the content."""
        
        for version in self.version_history:
            if version.version_id == version_id:
                logger.info(f"Reverted to version {version_id}")
                return version.content
        
        logger.warning(f"Version {version_id} not found in history")
        return None

    def get_latest_version(self) -> Optional[str]:
        """Get the content of the latest version."""
        
        if self.version_history:
            return self.version_history[-1].content
        return None

    def clear_history(self) -> None:
        """Clear the version history."""
        self.version_history.clear()
        logger.info("Version history cleared")

    def export_edit_report(self, edit_result: EditResult, filename: Optional[str] = None) -> str:
        """Export a detailed edit report to a file."""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"edit_report_{timestamp}.html"
        
        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Blog Edit Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .diff {{ background-color: #f9f9f9; padding: 10px; border-left: 3px solid #007cba; }}
                pre {{ white-space: pre-wrap; word-wrap: break-word; }}
                .success {{ color: #28a745; }}
                .error {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Blog Edit Report</h1>
                <p><strong>Timestamp:</strong> {edit_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Provider:</strong> {edit_result.provider_used}</p>
                <p><strong>Model:</strong> {edit_result.model_used}</p>
                <p><strong>Status:</strong> <span class="{'success' if edit_result.success else 'error'}">
                    {'SUCCESS' if edit_result.success else 'FAILED'}
                </span></p>
                {f'<p><strong>Error:</strong> {edit_result.error_message}</p>' if edit_result.error_message else ''}
            </div>
            
            <div class="section">
                <h2>Edit Instruction</h2>
                <div class="diff">
                    <p>{edit_result.instruction}</p>
                </div>
            </div>
            
            <div class="section">
                <h2>Changes Summary</h2>
                <div class="diff">
                    <pre>{edit_result.changes_summary}</pre>
                </div>
            </div>
            
            <div class="section">
                <h2>Diff Visualization</h2>
                <div class="diff">
                    {edit_result.diff_html}
                </div>
            </div>
        </body>
        </html>
        """
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Edit report exported to {filename}")
        return filename


# Convenience function for standalone use
def apply_edit(markdown_text: str, 
               instruction: str,
               provider: str = "groq",
               api_key: Optional[str] = None,
               model: Optional[str] = None,
               temperature: float = 0.3,
               max_tokens: int = 4000) -> EditResult:
    """
    Standalone function to apply an edit to markdown text.
    
    Args:
        markdown_text (str): Original blog post content in Markdown
        instruction (str): Natural language edit instruction
        provider (str): LLM provider ("groq", "openai", "anthropic")
        api_key (str, optional): API key for the provider
        model (str, optional): Model name to use
        temperature (float): LLM temperature (0.0-1.0)
        max_tokens (int): Maximum tokens to generate
        
    Returns:
        EditResult: Result with edited content and diff information
    """
    agent = EditingAgent(llm_provider=provider, api_key=api_key, model=model)
    return agent.apply_edit(markdown_text, instruction, temperature, max_tokens)


def main():
    """Example usage and testing."""
    
    # Example markdown content
    sample_content = """# The Future of AI in Healthcare

Artificial Intelligence is revolutionizing healthcare in unprecedented ways. From diagnostic imaging to drug discovery, AI technologies are improving patient outcomes and operational efficiency.

## Current Applications

AI is currently being used in:
- Medical imaging analysis
- Drug discovery and development
- Electronic health records management
- Predictive analytics for patient care

## Challenges and Opportunities

While AI offers tremendous potential, there are challenges to consider including data privacy, regulatory compliance, and the need for clinical validation.

## Conclusion

The future of AI in healthcare looks promising, with continued innovation expected to drive better patient care and reduced costs."""
    
    try:
        # Create editing agent
        agent = EditingAgent(llm_provider="groq")  # Change as needed
        
        # Test edit instructions
        instructions = [
            "Add a section about ethical considerations in AI healthcare",
            "Make the writing more casual and conversational",
            "Add specific examples of AI tools currently used in hospitals"
        ]
        
        current_content = sample_content
        
        for i, instruction in enumerate(instructions, 1):
            print(f"\n{'='*60}")
            print(f"Edit #{i}: {instruction}")
            print('='*60)
            
            result = agent.apply_edit(current_content, instruction)
            
            if result.success:
                print(f"✅ Edit applied successfully!")
                print(f"\nChanges Summary:")
                print(result.changes_summary)
                
                # Use edited content for next iteration
                current_content = result.edited_content
                
                # Export report
                report_file = agent.export_edit_report(result, f"edit_report_{i}.html")
                print(f"📄 Report exported to: {report_file}")
                
            else:
                print(f"❌ Edit failed: {result.error_message}")
        
        # Show version history
        print(f"\n{'='*60}")
        print("Version History")
        print('='*60)
        history = agent.get_version_history()
        for version in history:
            print(f"• {version['version_id']}: {version['instruction'][:50]}...")
        
        print(f"\n✅ Final edited content length: {len(current_content)} characters")
        
        # Save final result
        with open("edited_blog_post.md", "w", encoding="utf-8") as f:
            f.write(current_content)
        print("💾 Final content saved to edited_blog_post.md")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have:")
        print("   1. Set up API key: export GROQ_API_KEY='your-key'")
        print("   2. Installed dependencies: pip install groq")


if __name__ == "__main__":
    main()
