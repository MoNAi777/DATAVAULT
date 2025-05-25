# 🚀 Getting Started with DataVault

## What You've Built

**DataVault** is now ready! You have a complete AI-powered message intelligence system that can:

- 📱 **Receive messages** via Telegram bot
- 🧠 **Analyze content** with AI (categorization, sentiment, tagging)
- 🔍 **Search semantically** using natural language
- 💬 **Answer questions** about your stored data
- 📊 **Track statistics** and insights

## 🏗️ Architecture Overview

```
Telegram Bot → FastAPI Backend → AI Processing → Database Storage
     ↓              ↓                ↓              ↓
  Messages    →  API Endpoints  →  OpenAI     →  PostgreSQL
                                   ↓              ↓
                              Vector Search  →  ChromaDB
```

## 📁 Project Structure

```
DATAVAULT/
├── backend/                 # Python/FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Database connection
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── config/             # Configuration
│   ├── requirements.txt    # Dependencies
│   └── Dockerfile         # Container setup
├── docker-compose.yml      # Full stack deployment
├── README.md              # Full documentation
└── PROJECT_PLAN.md        # Detailed architecture
```

## 🎯 Next Steps

### 1. **Set Up API Keys** (Required for AI features)

Edit `.env` file:
```bash
# Required for AI processing
OPENAI_API_KEY=your-openai-api-key-here

# Optional for Telegram bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

### 2. **Test Basic Functionality**

```bash
# Test backend without external dependencies
cd backend
python test_basic.py
```

### 3. **Start with Docker** (Recommended)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 4. **Test API Endpoints**

```bash
# Health check
curl http://localhost:8080/health

# API documentation
open http://localhost:8080/docs

# Create a test message
curl -X POST "http://localhost:8080/api/messages/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Bitcoin is showing strong momentum today",
    "source_type": "test",
    "sender_name": "Test User"
  }'
```

### 5. **Set Up Telegram Bot** (Optional)

1. **Create Bot:**
   - Message @BotFather on Telegram
   - Send `/newbot` and follow instructions
   - Copy token to `.env` file

2. **Test Bot:**
   - Find your bot on Telegram
   - Send `/start`
   - Forward any message to test

## 🔧 Development Workflow

### Local Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server
python -m app.main

# Access at http://localhost:8000
```

### Database Management
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U datavault -d datavault

# Reset database
docker-compose down -v postgres
docker-compose up -d postgres
```

### Monitoring
```bash
# View all logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f backend
docker-compose logs -f chromadb
```

## 🎨 Customization

### Add New Categories
Edit `backend/app/services/ai_service.py`:
```python
# Line ~20: Update categories list
categories = ["crypto", "ai-tools", "your-category", ...]
```

### Modify AI Prompts
Edit `backend/app/services/ai_service.py`:
```python
# Line ~30: Customize analysis prompt
prompt = f"""
Your custom analysis instructions...
"""
```

### Add New API Endpoints
Create new routes in `backend/app/api/`:
```python
@router.get("/your-endpoint")
async def your_function():
    return {"message": "Hello World"}
```

## 🚨 Troubleshooting

### Common Issues

**"No module named 'chromadb'"**
- ChromaDB is optional for basic functionality
- Use Docker setup for full features
- Or install: `pip install chromadb`

**"OpenAI API key not set"**
- Add your key to `.env` file
- Get key from: https://platform.openai.com/api-keys

**"Telegram bot not responding"**
- Check bot token in `.env`
- Verify bot is started: `docker-compose logs backend`

**"Database connection error"**
- Ensure PostgreSQL is running: `docker-compose ps`
- Check connection string in `.env`

### Performance Tips

**For large datasets:**
- Use Redis for caching
- Enable background processing with Celery
- Optimize database queries

**For high volume:**
- Scale with multiple workers
- Use message queues
- Implement rate limiting

## 🎉 Success! What's Working

✅ **Backend API** - FastAPI with automatic docs  
✅ **Database Models** - PostgreSQL with SQLAlchemy  
✅ **AI Integration** - OpenAI for analysis and embeddings  
✅ **Message Processing** - Automatic categorization and tagging  
✅ **Search System** - Semantic and keyword search  
✅ **Telegram Bot** - Message forwarding and commands  
✅ **Docker Setup** - Complete containerized deployment  
✅ **Documentation** - Comprehensive guides and examples  

## 📚 Learn More

- **API Documentation**: http://localhost:8080/docs
- **Full README**: [README.md](./README.md)
- **Architecture Details**: [PROJECT_PLAN.md](./PROJECT_PLAN.md)
- **Docker Compose**: [docker-compose.yml](./docker-compose.yml)

## 🤝 Need Help?

1. Check the logs: `docker-compose logs -f`
2. Test basic functionality: `python backend/test_basic.py`
3. Review the troubleshooting section above
4. Check API docs for endpoint details

---

**🎊 Congratulations!** You now have a fully functional AI-powered message intelligence system. Start by adding your API keys and testing with some messages! 