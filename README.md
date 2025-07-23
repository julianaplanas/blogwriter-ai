# AI-Powered Blog Writer

A modern, production-ready AI blog writing system that generates high-quality, well-researched blog posts with real images and sources. Built with FastAPI and Next.js, deployed on Heroku and Vercel.

## Overview

This system uses direct API calls to create comprehensive blog posts:
- **Research**: Finds relevant articles using Brave Search API
- **Content Generation**: Creates structured content using Groq LLM
- **Image Integration**: Fetches relevant images from Pexels API
- **Natural Language Editing**: Edit posts with simple instructions
- **Version Control**: Complete edit history with rollback capability

The system includes both a FastAPI backend and a modern Next.js frontend for a complete blogging solution.

## Tech Stack

### Backend
- **FastAPI**: Python web framework for REST API
- **SQLite**: Database for blog storage and versioning
- **Uvicorn**: ASGI server for production deployment
- **Direct API Calls**: Simple, reliable integration with AI services

### Frontend
- **Next.js 14**: React framework with TypeScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Markdown**: Markdown rendering and preview
- **Shadcn/ui**: Modern UI components and design system

### AI Services & APIs
- **Groq**: Fast LLM API with Llama models 
- **Brave Search**: Web search and research API 
- **Pexels**: High-quality stock images API 

### Development Tools
- **Cursor**: AI-powered code editor for development and debugging
- **Copilot (Claude Sonnet 4)**: Advanced code completion and refactoring in the editor
- **ChatGPT 4o**: Used for project strategy, architecture, and prompt engineering
- **Vercel v0**: Frontend component design and rapid UI prototyping
- **GitHub**: Version control and collaboration
- **Heroku**: Backend deployment and hosting
- **Vercel**: Frontend deployment and hosting

## Features

### Core Functionality
- **Automated Research**: Fetches and analyzes recent articles on any topic
- **AI Writing**: Generates 800-1000 word blog posts with proper structure
- **Image Integration**: Automatically includes relevant stock photos with proper attribution
- **Natural Language Editing**: Edit posts with simple instructions like "make it shorter" or "add a conclusion"
- **Version History**: Track all edits with detailed diff and rollback capability
- **Blog Management**: Save, load, search, and organize blog posts with metadata

### Technical Features
- **Direct API Integration**: Simple, reliable calls to AI services
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

1. **Clone the repository**
```bash
git clone https://github.com/julianaplanas/blogwriter-ai
cd blogwriter-ai
```

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
```
The backend will start on `http://localhost:8000`

2. **Start Frontend**
```bash
cd frontend
npm run dev
```
The frontend will start on `http://localhost:3000`

## API Keys

### Required APIs

#### Groq API
- **Purpose**: Content generation and editing
- **Get Key**: [https://console.groq.com/](https://console.groq.com/)
- **Cost**: Free tier available
- **Usage**: Generates blog content and handles edits

#### Brave Search API
- **Purpose**: Research and finding sources
- **Get Key**: [https://api.search.brave.com/](https://api.search.brave.com/)
- **Cost**: Free tier available
- **Usage**: Finds recent articles and research sources

### Optional APIs

#### Pexels API
- **Purpose**: High-quality stock images
- **Get Key**: [https://www.pexels.com/api/](https://www.pexels.com/api/)
- **Cost**: Free tier available
- **Usage**: Adds relevant images to blog posts

## Deployment

### Backend (Heroku)

1. **Create Heroku App**
```bash
heroku create your-app-name
```

2. **Set Environment Variables**
```bash
heroku config:set BRAVE_API_KEY=your_key
heroku config:set GROQ_API_KEY=your_key
heroku config:set PEXELS_API_KEY=your_key
```

3. **Deploy**
```bash
git push heroku main
```

### Frontend (Vercel)

1. **Connect Repository**
- Connect your GitHub repository to Vercel
- Set build command: `npm run build`
- Set output directory: `.next`

2. **Set Environment Variables**
- `NEXT_PUBLIC_API_URL`: Your Heroku backend URL

3. **Deploy**
- Vercel will automatically deploy on push to main branch

## Usage

### Generating a Blog Post

1. **Enter a topic** in the main input field
2. **Click "Generate"** to create a blog post
3. **Review the content** with sources and images
4. **Edit if needed** using natural language instructions

### Editing Content

1. **Type edit instructions** in the edit panel
2. **Examples**:
   - "Make the introduction more engaging"
   - "Add more details about the benefits"
   - "Shorten the conclusion"
   - "Add a section about future trends"

### Version Control

- **View all versions** in the version history
- **Revert to any version** with one click
- **See edit instructions** for each version
- **Track changes** with timestamps

## Architecture

### Backend Structure
```
backend/
├── main.py              # FastAPI application with all endpoints
├── requirements.txt     # Python dependencies
├── venv/               # Virtual environment
└── blog_posts.db       # SQLite database
```

### Frontend Structure
```
frontend/
├── app/                # Next.js app directory
├── components/         # Reusable UI components
├── hooks/             # Custom React hooks
├── lib/               # Utility functions
└── public/            # Static assets
```

## Future Enhancements & Reflection

This project demonstrates what's possible with free-tier APIs and open-source tools, but there are several exciting directions for expansion:

- **Advanced AI Model Integration**: Multi-model orchestration, premium LLMs, and fine-tuning for specialized content.
- **Enhanced Research Capabilities**: Multi-source research, real-time data, and advanced filtering for credibility.
- **Professional Media Services**: Premium stock photos, AI-generated images, and video/media integration.
- **Production-Scale Features**: Authentication, analytics, editorial workflows, and advanced content management.
- **Technical Architecture Improvements**: Microservices, real-time collaboration, advanced caching, and CDN integration.
