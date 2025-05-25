# 🚀 DataVault - AI-Powered Message Intelligence System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)

DataVault is a cutting-edge AI-powered message intelligence system that transforms how you interact with your messaging data. It ingests, categorizes, and enables natural language querying of messages from Telegram and WhatsApp, providing deep insights through advanced AI analysis.

![DataVault Dashboard](https://via.placeholder.com/800x400/1a1a2e/ffffff?text=DataVault+Dashboard)

## ✨ Features

### 🤖 **AI-Powered Intelligence**
- **Smart Categorization**: Automatic message classification (crypto, AI tools, finance, etc.)
- **Sentiment Analysis**: Real-time emotion detection and scoring
- **Auto-Tagging**: Intelligent keyword extraction
- **AI Summaries**: Concise message summaries
- **Semantic Search**: Natural language querying with context understanding

### 📱 **Multi-Platform Support**
- **Telegram Integration**: Real-time message forwarding and processing
- **WhatsApp Support**: Message import and analysis
- **Media Handling**: Images, videos, audio, and documents
- **Hebrew & Multi-language**: Full Unicode support

### 🎨 **Beautiful Dashboard**
- **Glassmorphism Design**: Modern, stunning UI with blur effects
- **Real-time Updates**: Live message sync every 5 seconds
- **Interactive Analytics**: Charts, trends, and insights
- **Responsive Design**: Perfect on desktop and mobile
- **Dark Theme**: Easy on the eyes

### 🔍 **Advanced Search & Analytics**
- **Vector Search**: ChromaDB-powered semantic similarity
- **AI Chat Interface**: Ask questions about your messages
- **Category Filtering**: Visual category cards with counts
- **Sentiment Trends**: Emotion analysis over time
- **Tag Clouds**: Popular topics and keywords

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: High-performance Python web framework
- **PostgreSQL**: Robust relational database
- **ChromaDB**: Vector database for embeddings
- **Redis**: High-speed caching and sessions
- **MinIO**: S3-compatible object storage
- **OpenAI GPT-4**: Advanced AI processing

### Frontend Stack
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations
- **React Query**: Intelligent data fetching
- **Recharts**: Beautiful data visualizations

### Infrastructure
- **Docker Compose**: Multi-service orchestration
- **Standalone Services**: Microservices architecture
- **Health Monitoring**: Service status tracking
- **Auto-scaling**: Container-based deployment

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API Key
- Telegram Bot Token (optional)

### 1. Clone & Setup
```bash
git clone https://github.com/MoNAi777/DATAVAULT.git
cd DATAVAULT
```

### 2. Environment Configuration
Create a `.env` file:
```env
# Required: OpenAI API Key for AI processing
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Telegram Bot Token for message forwarding
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

### 3. Launch DataVault
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 4. Access Your Dashboard
- **🌐 Frontend Dashboard**: http://localhost:3000
- **🔧 Backend API**: http://localhost:8080
- **📚 API Documentation**: http://localhost:8080/docs

## 📊 Services Overview

| Service | Port | Description | Status |
|---------|------|-------------|--------|
| **Frontend** | 3000 | Next.js Dashboard | ✅ Running |
| **Backend API** | 8080 | FastAPI Server | ✅ Running |
| **Telegram Bot** | - | Message Processor | ✅ Active |
| **PostgreSQL** | 5432 | Primary Database | ✅ Healthy |
| **ChromaDB** | 8000 | Vector Database | ✅ Running |
| **Redis** | 6379 | Cache Layer | ✅ Healthy |
| **MinIO** | 9000-9001 | Object Storage | ✅ Healthy |

## 🔌 API Endpoints

### Core Endpoints
```http
GET    /health                    # System health check
GET    /api/messages             # List messages with filters
POST   /api/messages             # Create new message
POST   /api/messages/query       # AI-powered search
GET    /api/messages/{id}        # Get specific message
```

### Example API Usage
```bash
# Health check
curl http://localhost:8080/health

# Get recent messages
curl http://localhost:8080/api/messages?limit=10

# AI search
curl -X POST http://localhost:8080/api/messages/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What crypto investments were mentioned?"}'
```

## 🤖 Telegram Bot Setup

### 1. Create Bot
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command
3. Follow instructions to get your bot token

### 2. Configure Bot
Add your bot token to `.env`:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 3. Start Forwarding
1. Find your bot on Telegram
2. Send `/start` to activate
3. Forward any messages to your bot
4. Watch them appear in your dashboard!

## 🛠️ Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations
```bash
# Auto-create tables on startup
docker-compose restart backend
```

## 📈 Features in Action

### AI Categorization
```json
{
  "content": "Just bought Bitcoin and Ethereum!",
  "categories": ["crypto", "finance"],
  "tags": ["Bitcoin", "Ethereum", "investment"],
  "sentiment": 0.8,
  "summary": "Excited about cryptocurrency purchases"
}
```

### Semantic Search
```bash
Query: "What AI tools were discussed?"
Results: Messages about Claude, ChatGPT, and other AI platforms
```

### Real-time Analytics
- Message volume trends
- Sentiment analysis over time
- Category distribution
- Popular tags and topics

## 🔧 Configuration

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API key for AI processing |
| `TELEGRAM_BOT_TOKEN` | ❌ Optional | Telegram bot token for message forwarding |

### Docker Compose Override
Create `docker-compose.override.yml` for custom configurations:
```yaml
version: '3.8'
services:
  backend:
    environment:
      - DEBUG=true
    ports:
      - "8080:8000"
```

## 🚨 Troubleshooting

### Common Issues

**Services not starting?**
```bash
docker-compose down
docker-compose up -d
```

**Telegram bot not responding?**
```bash
docker-compose logs telegram-bot
```

**Frontend not loading?**
```bash
docker-compose restart frontend
```

**Database connection issues?**
```bash
docker-compose restart postgres backend
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines
- Follow Python PEP 8 style guide
- Use TypeScript for frontend development
- Write tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for powerful AI capabilities
- **Telegram** for excellent bot API
- **ChromaDB** for vector search
- **FastAPI** for the amazing web framework
- **Next.js** for the fantastic React framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/MoNAi777/DATAVAULT/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MoNAi777/DATAVAULT/discussions)

---

<div align="center">

**⭐ Star this repository if you find it useful!**

Made with ❤️ by [MoNAi777](https://github.com/MoNAi777)

</div> 