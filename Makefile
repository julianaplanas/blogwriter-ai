# Makefile for AI-Powered Blog Writer - Complete System

.PHONY: help install test clean run write research models structure

# Default target
help:
	@echo "🚀 AI-Powered Blog Writer - Complete System"
	@echo "=========================================="
	@echo ""
	@echo "📦 Setup Commands:"
	@echo "  install     - Install dependencies and setup environment"
	@echo "  deps        - Check dependency status"
	@echo ""
	@echo "🔍 Research Commands:"
	@echo "  research    - Research a topic (make research TOPIC='your topic')"
	@echo "  research-ai - Research AI trends (example)"
	@echo ""
	@echo "✍️  Blog Writing Commands:"
	@echo "  write       - Write blog post (make write TOPIC='your topic')"
	@echo "  write-ai    - Write AI trends blog (example)"
	@echo "  write-fast  - Write using faster model (8B instead of 70B)"
	@echo ""
	@echo "🤖 Model Management:"
	@echo "  models      - List available Groq models"
	@echo ""
	@echo "🖼️  Image Management:"
	@echo "  images TOPIC='topic'  - Test image fetching"
	@echo "  images-ai             - Test image fetching for AI (example)"
	@echo ""
	@echo "🧪 Testing Commands:"
	@echo "  test        - Run all tests"
	@echo "  test-basic  - Run basic functionality tests"
	@echo "  test-rate   - Run rate limiting tests"
	@echo ""
	@echo "🔧 Utility Commands:"
	@echo "  clean       - Clean up generated files"
	@echo "  structure   - Show project structure"
	@echo "  example     - Run integration example"
	@echo ""
	@echo "Usage examples:"
	@echo "  make install"
	@echo "  make research TOPIC='machine learning'"
	@echo "  make write TOPIC='sustainable energy'"
	@echo "  make write-fast TOPIC='AI trends'"

# Installation
install:
	@echo "📦 Installing dependencies..."
	python3 -m pip install -r requirements.txt
	@echo "✅ Installation completed!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Copy config/.env.example to .env"
	@echo "2. Add your BRAVE_API_KEY and GROQ_API_KEY to .env"
	@echo "3. Run 'make test' to verify installation"
	@echo "4. Run 'make models' to see available LLM models"

deps:
	@echo "📋 Checking dependencies..."
	@python3 -c "import sys; print(f'Python version: {sys.version}')"
	@pip list | grep -E "(requests|python-dotenv|groq)" || echo "⚠️  Some dependencies missing - run 'make install'"

# Research commands
research:
	@echo "🔍 Researching topic: $(TOPIC)"
	python3 blog_writer.py research "$(TOPIC)" --count 5

research-ai:
	@echo "🔍 Researching AI trends..."
	python3 blog_writer.py research "artificial intelligence trends and innovations 2024" --count 5

# Blog writing commands  
write:
	@echo "✍️  Writing blog post about: $(TOPIC)"
	python3 blog_writer.py write "$(TOPIC)" --provider groq

write-ai:
	@echo "✍️  Writing AI trends blog post..."
	python3 blog_writer.py write "artificial intelligence trends and future innovations in 2024" --provider groq

write-fast:
	@echo "✍️  Writing blog post with fast model: $(TOPIC)"
	python3 blog_writer.py write "$(TOPIC)" --provider groq --model llama-3.1-8b-instant

# Model management
models:
	@echo "🤖 Available Groq models:"
	python3 blog_writer.py models --provider groq

# Image management
images:
	@echo "🖼️  Testing image fetching for: $(TOPIC)"
	python3 blog_writer.py images "$(TOPIC)" --count 3

images-ai:
	@echo "🖼️  Testing image fetching for AI topics..."
	python3 blog_writer.py images "artificial intelligence machine learning" --keywords "neural networks,deep learning" --count 3

# Testing
test: test-basic test-rate
	@echo "🎉 All tests completed!"

test-basic:
	@echo "🧪 Running basic tests..."
	python3 -m pytest tests/test_research_agent.py -v

test-rate:
	@echo "🚦 Running rate limiting tests..."
	python3 -m pytest tests/test_rate_limiting.py -v

# Running (backwards compatibility)
run:
	@echo "🔍 Running legacy research agent..."
	python3 main.py $(if $(TOPIC),"$(TOPIC)","artificial intelligence trends")

example:
	@echo "📑 Running integration example..."
	python3 examples/integration_example.py

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	rm -rf results/*.json 2>/dev/null || true
	rm -rf results/*.md 2>/dev/null || true
	@echo "✅ Cleanup completed!"

# Project structure
structure:
	@echo "📁 Project Structure:"
	@echo "==================="
	@tree -I '__pycache__|*.pyc|.git|venv' || (find . -name "*.py" -o -name "*.md" -o -name "*.txt" | head -20)

# Legacy linting (optional)
lint:
	@echo "🔍 Running basic syntax check..."
	@python3 -m py_compile src/*.py config/*.py || echo "⚠️  Syntax errors found"
	@echo "✅ Basic syntax check complete"
