# DataVault - AI-Powered Message Intelligence System

## Project Overview
DataVault is an intelligent message management system that ingests, categorizes, and allows natural language querying of messages from WhatsApp and Telegram. It uses AI to understand context and provide insights about collected data.

## Architecture

### Core Components

1. **Message Ingestion Layer**
   - Telegram Bot for direct message forwarding
   - Web upload interface for WhatsApp exports
   - Email integration (optional future feature)

2. **Backend Services (Python/FastAPI)**
   - Message processing pipeline
   - AI categorization service
   - Vector embeddings for semantic search
   - RESTful API for frontend

3. **Data Storage**
   - PostgreSQL: Structured message data, metadata
   - ChromaDB: Vector embeddings for semantic search
   - MinIO/S3: Media file storage (images, videos)

4. **AI Processing**
   - OpenAI GPT-4 for content understanding
   - Embedding generation for semantic search
   - Automatic tagging and categorization
   - Context-aware querying

5. **Frontend (Next.js + TypeScript)**
   - Modern dashboard with analytics
   - Chat interface for querying
   - Message viewer with filtering
   - Search and discovery features

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy (ORM)
- ChromaDB (Vector DB)
- OpenAI API
- python-telegram-bot
- Celery (Background tasks)
- Redis (Queue/Cache)

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- React Query
- Recharts (Analytics)

### Infrastructure
- Docker & Docker Compose
- PostgreSQL
- Redis
- MinIO (Local S3)

## Features

### Phase 1 (MVP)
1. Telegram bot for message forwarding
2. Basic message storage and categorization
3. Simple search functionality
4. Web interface for viewing messages
5. Basic AI chat for querying

### Phase 2
1. WhatsApp chat import
2. Advanced categorization (crypto, AI tools, etc.)
3. Semantic search
4. Analytics dashboard
5. Export functionality

### Phase 3
1. Real-time notifications
2. Collaborative features
3. Custom AI models
4. Mobile app

## Data Flow

1. **Ingestion**: User forwards message → Telegram Bot → Backend API
2. **Processing**: Extract content → Generate embeddings → Categorize → Store
3. **Querying**: User asks question → Semantic search → Context retrieval → AI response

## Security Considerations
- End-to-end encryption for sensitive data
- User authentication (JWT)
- Rate limiting
- Data privacy compliance

## Development Roadmap

### Week 1: Backend Foundation
- Setup project structure
- Implement Telegram bot
- Basic message storage
- API endpoints

### Week 2: AI Integration
- OpenAI integration
- Embedding generation
- Categorization logic
- Vector search

### Week 3: Frontend Development
- Dashboard UI
- Message viewer
- Search interface
- Chat component

### Week 4: Polish & Deploy
- Testing
- Documentation
- Docker setup
- Deployment guide 