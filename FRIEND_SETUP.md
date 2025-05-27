# 👋 Welcome to DataVault - Setup Guide for Collaborators

## 🚀 Getting Started with Cursor

This guide will walk you through setting up the DataVault project in Cursor IDE.

### Step 1: Clone the Repository

1. Open Cursor IDE
2. Click on "Clone Repository" (or press `Ctrl+Shift+P` and type "Clone")
3. Enter the repository URL: `https://github.com/MoNAi777/DATAVAULT.git`
4. Choose a local folder to clone to
5. Wait for the cloning process to complete

### Step 2: Set Up Environment Variables

1. Create a new `.env` file in the project root (copy from the example):

```bash
# In PowerShell
Copy-Item -Path "backend/env.example" -Destination ".env"
```

2. Edit the `.env` file to add your API keys:

```
# Required for AI processing (ask for the key or use your own)
OPENAI_API_KEY=your-openai-api-key-here

# Optional for Telegram bot (ask for the key or use your own)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

### Step 3: Set Up Python Environment

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate

# Install dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### Step 4: Run the Project with Docker

The easiest way to run the full project is with Docker:

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

This will start:
- Backend API (FastAPI): http://localhost:8080
- Frontend (Next.js): http://localhost:3000
- Database (PostgreSQL)
- Vector Database (ChromaDB)
- Redis Cache
- MinIO Object Storage
- Telegram Bot (if configured)

### Step 5: Development Workflow

#### Backend Development
```bash
cd backend
python -m app.main
# Access at http://localhost:8000
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
# Access at http://localhost:3000
```

### Step 6: Making Changes

1. Create a new branch for your features:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes

3. Commit and push:
```bash
git add .
git commit -m "Add your feature description"
git push origin feature/your-feature-name
```

4. Create a pull request on GitHub

## 📚 Important Files

- `README.md` - Project overview and documentation
- `GETTING_STARTED.md` - Detailed setup instructions
- `PROJECT_PLAN.md` - Architecture and development plan
- `docker-compose.yml` - Docker configuration

## 🤝 Need Help?

If you have any questions or run into issues, please reach out!

Happy coding! 🎉 