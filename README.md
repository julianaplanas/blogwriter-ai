# AI-Powered Blog Writer

A sophisticated, production-ready multi-agent AI system that automatically generates high-quality, well-researched blog posts with real images and sources. Built with modern web technologies and powered by AI APIs.

## Overview

This system combines multiple specialized AI agents to create comprehensive blog posts:
- **Research Agent**: Finds relevant articles using Brave Search API
- **Blog Writer Agent**: Generates structured content using Groq LLM
- **Image Agent**: Fetches relevant images from Pexels API
- **Editing Agent**: Provides natural language editing with version control

The system includes both a FastAPI backend and a modern React frontend for a complete blogging solution with advanced features like versioning, natural language editing, and blog management.

## Tech Stack

### Backend
- **FastAPI**: Python web framework for REST API
- **SQLite**: Database for blog storage and versioning
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and serialization

### Frontend
- **Next.js 14**: React framework with TypeScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Markdown**: Markdown rendering and preview
- **Shadcn/ui**: Modern UI components and design system

### AI Services & APIs
- **Groq**: Free LLM API with Llama models 
- **Brave Search**: Web search and research API 
- **Pexels**: High-quality stock images API 

### Development Tools
- **ChatGPT 4o**: Project structuring, architecture design, and prompt engineering
- **GitHub Copilot with Claude Sonnet 3.5**: Primary code generation and development assistant
- **v0 by Vercel**: Frontend component design and rapid UI prototyping

## Features

### Core Functionality
- **Automated Research**: Fetches and analyzes recent articles on any topic
- **AI Writing**: Generates 800-1000 word blog posts with proper structure
- **Image Integration**: Automatically includes relevant stock photos with proper attribution
- **Natural Language Editing**: Edit posts with simple instructions like "make it shorter" or "add a conclusion"
- **Version History**: Track all edits with detailed diff and rollback capability
- **Blog Management**: Save, load, search, and organize blog posts with metadata

### Technical Features
- **Multi-Agent Architecture**: Modular design with separate agents for different tasks
- **Rate Limiting**: Production-ready rate limiting with exponential backoff
- **Error Handling**: Comprehensive error recovery and graceful degradation
- **Real-time Preview**: Live markdown preview in the frontend
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **API Documentation**: Interactive OpenAPI/Swagger documentation
- **Database Versioning**: Complete edit history with diff tracking
- **Search & Stats**: Full-text search and analytics dashboard

## Quick Start

### Prerequisites
- Python 3.8+ and pip
- Node.js 16+ and npm
- API keys (see API Keys section below)

### Installation

1. **Clone the repository (if necessary)**

2. **Setup Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Setup Frontend**
```bash
cd ../frontend
npm install
```

4. **Configure Environment Variables**
Create a `.env` file in the backend directory:
```bash
# Required APIs
BRAVE_API_KEY=your_brave_search_api_key
GROQ_API_KEY=your_groq_api_key

# Optional - for real images (otherwise uses placeholders)
PEXELS_API_KEY=your_pexels_api_key
```

### Running the Application

1. **Start Backend**
```bash
cd backend
source venv/bin/activate
python main.py
# Server runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

2. **Start Frontend**
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:3000
```

## API Keys Setup

### Required APIs

#### 1. Brave Search API (Required)
- **Purpose**: Web search and article discovery for research
- **Cost**: Free tier with 2,000 queries/month
- **How to get**: 
  1. Visit [Brave Search API](https://brave.com/search/api/)
  2. Sign up and create a free account
  3. Get your API key from the dashboard
  4. Add to `.env`: `BRAVE_API_KEY=your_key_here`

#### 2. Groq API (Required)
- **Purpose**: AI text generation using free Llama models
- **Cost**: Free tier with very generous limits
- **Models**: Llama 3.1 70B, Llama 3.1 8B, Mixtral, Gemma
- **How to get**:
  1. Visit [Groq Console](https://console.groq.com/)
  2. Create account and generate API key
  3. Add to `.env`: `GROQ_API_KEY=your_key_here`

#### 3. Pexels API (Optional)
- **Purpose**: High-quality stock images for blog posts
- **Cost**: Free with unlimited downloads (requires attribution)
- **How to get**:
  1. Visit [Pexels API](https://www.pexels.com/api/)
  2. Create account and get API key
  3. Add to `.env`: `PEXELS_API_KEY=your_key_here`
- **Note**: System works without this - uses image placeholders instead

## Usage Examples

### Frontend Usage
1. Open http://localhost:3000
2. Enter a blog topic (e.g., "artificial intelligence trends")
3. Click "Generate Blog Post" and wait 15-30 seconds
4. Review the generated blog with research, images, and sources
5. Use natural language editing: "Add a conclusion" or "Make it more technical"
6. Save, load, and manage your blog posts

## Architecture

### System Flow
1. **User Input**: Topic entered via frontend or API
2. **Research Phase**: Brave Search API finds relevant articles and sources
3. **Content Generation**: Groq LLM creates structured blog post with citations
4. **Image Enhancement**: Pexels API provides relevant professional images
5. **Storage**: Complete blog saved to SQLite with versioning
6. **Response**: Formatted blog post with metadata returned to user

### Database Schema
```sql
-- Main blog posts table
blog_posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  topic TEXT NOT NULL,
  markdown TEXT NOT NULL,
  source_refs TEXT,      -- JSON array of research references
  images TEXT,           -- JSON array of image metadata
  metadata TEXT,         -- JSON object with generation details
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Version history for edits with diff tracking
blog_post_versions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  version_number INTEGER NOT NULL,
  markdown TEXT NOT NULL,
  edit_instruction TEXT,
  edit_summary TEXT,
  diff_summary TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES blog_posts(id)
)
```

### API Endpoints

**Blog Management**
- `POST /generate` - Generate new blog post with research and images
- `GET /posts` - List all saved posts with pagination
- `GET /post/{id}` - Get specific post with full details
- `PUT /post/{id}` - Update existing post
- `DELETE /post/{id}` - Delete post and all versions

**Editing & Versioning**
- `POST /edit` - Edit blog with natural language instruction
- `POST /edit/simple` - Quick edit without versioning
- `POST /post/{id}/edit` - Edit saved post with version tracking
- `GET /post/{id}/versions` - Get complete version history
- `POST /edit/undo/{version_id}` - Rollback to specific version
- `GET /edit/history` - Get recent edit history

**Search & Analytics**
- `GET /posts/search` - Full-text search across all posts
- `GET /posts/stats` - Database statistics and analytics
- `DELETE /posts/clear` - Clear all posts (development only)

**Utility**
- `GET /health` - System health check and status
- `GET /docs` - Interactive API documentation

## Development Process

This project was built using a combination of AI tools and modern development practices, showcasing how AI can accelerate development while maintaining code quality.

### AI-Assisted Development Stack
- **ChatGPT 4o**: Used for initial project architecture, requirement analysis, API design, and prompt engineering for various AI agents
- **GitHub Copilot with Claude Sonnet 3.5**: Primary code writing assistant for both backend Python (FastAPI, SQLite) and frontend TypeScript/React
- **v0 by Vercel**: Frontend component design, UI/UX prototyping, and rapid iteration of the React interface

### Development Workflow
1. **Architecture Planning**: Used ChatGPT 4o to structure the multi-agent system, define API contracts, and plan the database schema
2. **Prompt Engineering**: Iteratively refined prompts for research, writing, and editing agents through testing and optimization
3. **Code Implementation**: Leveraged Copilot for accelerated development while maintaining code quality and best practices
4. **UI/UX Design**: Utilized v0 for rapid prototyping, modern component design, and responsive layout creation
5. **Integration Testing**: Manual and automated testing to ensure all agents work together seamlessly
6. **Production Readiness**: Added comprehensive error handling, rate limiting, and production considerations

## Performance Metrics

**Typical Performance**
- Blog Generation: 15-30 seconds (includes research + image fetching)
- Blog Editing: 5-10 seconds for natural language edits
- Blog Retrieval: <1 second from database
- Search: <2 seconds across all content
- Version History: <1 second to retrieve all versions

**Resource Usage**
- Memory: ~200MB base + ~50MB per concurrent request
- Storage: ~5KB per blog post + image metadata + version history
- Network: Varies based on research depth and image count
- CPU: Minimal (most processing done by external APIs)

**Rate Limits & Costs**
- Brave Search: 2,000 queries/month free (typical usage: 1-5 per blog)
- Groq LLM: Very generous free tier (thousands of requests)
- Pexels Images: Unlimited free downloads with attribution

## File Structure

```
ekona/
├── README.md              # This comprehensive guide
├── .env.example          # Environment variable template
├── Makefile              # Development commands and shortcuts
│
├── backend/              # FastAPI backend
│   ├── main.py          # Main FastAPI application with all endpoints
│   ├── db.py            # SQLite blog storage layer with versioning
│   ├── api_models.py    # Pydantic schemas for request/response
│   └── requirements.txt # Python dependencies
│
├── frontend/            # Next.js frontend
│   ├── app/
│   │   ├── page.tsx    # Main blog interface with all features
│   │   ├── layout.tsx  # App layout and metadata
│   │   └── globals.css # Global styles and Tailwind
│   ├── components/     # Reusable React components
│   ├── package.json    # Node.js dependencies
│   └── tailwind.config.js # Tailwind configuration
│
├── src/                # AI Agents (core intelligence)
│   ├── research_agent.py   # Brave Search integration
│   ├── blog_writer_agent.py # Groq LLM integration
│   ├── image_agent.py      # Pexels API integration
│   └── editing_agent.py    # Natural language editing with diff
│
├── tests/              # Test suites
│   ├── test_backend.py    # Backend API tests
│   ├── test_agents.py     # AI agent tests
│   └── test_integration.py # End-to-end tests
│
├── results/            # Generated blog posts (examples)
├── config/            # Configuration files
└── scripts/           # Utility scripts
```

## Production Considerations

### Current Status
- ✅ Fully functional development environment
- ✅ All APIs tested and working with error handling
- ✅ Complete frontend-backend integration
- ✅ SQLite database with versioning and rollback
- ✅ Production-ready rate limiting and error recovery
- ✅ Comprehensive API documentation
- ✅ Mobile-responsive frontend design

### Production Deployment Recommendations
- [ ] **Authentication**: Implement JWT tokens and user management
- [ ] **Database**: Migrate from SQLite to PostgreSQL for scalability
- [ ] **Caching**: Add Redis for API response caching
- [ ] **Monitoring**: Implement logging, metrics, and health checks
- [ ] **Security**: Enable HTTPS, input validation, and security headers
- [ ] **Scaling**: Add horizontal scaling and load balancing
- [ ] **Backups**: Implement automated database backups
- [ ] **CI/CD**: Add automated testing and deployment pipelines

## CLI Usage (Alternative Interface)

The system also includes a Makefile for command-line usage:

```bash
# Install dependencies
make install

# Research a topic
make research TOPIC="quantum computing"

# Write a complete blog post
make write TOPIC="sustainable energy solutions"

# Write with faster model (8B instead of 70B)
make write-fast TOPIC="AI trends"

# Test image fetching
make images TOPIC="machine learning"

# Run tests
make test

# Clean generated files
make clean
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
cd backend && python -m pytest tests/ -v

# Test specific functionality
python test_backend.py        # Backend API tests
python test_agents.py         # AI agent tests
python test_integration.py    # End-to-end tests
```

The test suite covers:
- All API endpoints with various inputs
- AI agent functionality and error handling
- Database operations and versioning
- Rate limiting and error recovery
- Frontend-backend integration

## Future Enhancements & Reflection

We value a forward-looking reflection on what could be accomplished with more time and resources. This project demonstrates what's possible with free-tier APIs and open-source tools, but there are several exciting directions for expansion:

### Advanced AI Model Integration
Currently, we're using Groq's free tier with primarily one model (Llama 3.1 70B). With more time and resources, we could:

- **Multi-Model Orchestration**: Integrate different models for different tasks - lightweight models for editing, specialized models for technical writing, creative models for marketing content
- **Model Selection Logic**: Implement intelligent model selection based on content type, complexity, and user preferences
- **Premium LLM Access**: Integrate GPT-4, Claude, or other premium models for higher quality output and specialized capabilities
- **Model Fine-tuning**: Train custom models on specific domains or writing styles for more targeted content generation

### Enhanced Search & Research Capabilities
We're currently limited to Brave Search's free tier. Future enhancements could include:

- **Multi-Source Research**: Combine multiple search APIs (Google Custom Search, Bing, academic databases) for more comprehensive research
- **Real-time Data**: Access to live social media feeds, news APIs, and trending topics for ultra-current content
- **Specialized Databases**: Integration with academic papers, industry reports, and professional databases
- **Advanced Filtering**: Implement sophisticated source credibility scoring and bias detection

### Professional Image & Media Services
Beyond Pexels' free tier, we could integrate:

- **Premium Stock Photos**: Getty Images, Shutterstock, Adobe Stock for professional-grade imagery
- **AI-Generated Images**: DALL-E, Midjourney, or Stable Diffusion for custom illustrations
- **Video Integration**: Automatic video sourcing and embedding for multimedia blog posts
- **Interactive Media**: Charts, graphs, and interactive elements generated from data

### Production-Scale Features
- **Enterprise Authentication**: SSO, team management, role-based access control
- **Advanced Analytics**: Content performance tracking, SEO optimization, reader engagement metrics
- **Content Management**: Editorial workflows, approval processes, scheduled publishing
- **API Rate Optimization**: Intelligent caching, request batching, and cost optimization across all external services

### Technical Architecture Improvements
- **Microservices Architecture**: Break agents into independent services for better scalability
- **Real-time Collaboration**: Multiple users editing simultaneously with live updates
- **Advanced Caching**: Redis-based caching for faster response times and reduced API costs
- **Content Distribution**: CDN integration for global performance optimization
