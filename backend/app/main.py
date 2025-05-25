from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import os

from config.settings import settings
from app.core.database import create_tables
from app.api.messages import router as messages_router
from app.services.telegram_service import TelegramService


# Global telegram service instance
telegram_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting DataVault...")
    
    # Create database tables
    create_tables()
    print("✅ Database tables created")
    
    # Create storage directories
    os.makedirs("storage/photos", exist_ok=True)
    os.makedirs("storage/videos", exist_ok=True)
    os.makedirs("storage/audio", exist_ok=True)
    os.makedirs("storage/documents", exist_ok=True)
    print("✅ Storage directories created")
    
    # Telegram bot now runs as a separate service
    print("ℹ️ Telegram bot runs as a separate service")
    
    print("🎉 DataVault started successfully!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down DataVault...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Message Intelligence System",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(messages_router, prefix="/api")

# Serve static files
if os.path.exists("storage"):
    app.mount("/storage", StaticFiles(directory="storage"), name="storage")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to DataVault API",
        "version": settings.app_version,
        "docs": "/docs",
        "telegram_bot_active": "separate_service"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "services": {
            "api": "running",
            "telegram_bot": "separate_service",
            "database": "connected",  # TODO: Add actual database health check
            "vector_db": "connected"  # TODO: Add ChromaDB health check
        }
    }


@app.post("/api/telegram/webhook")
async def telegram_webhook(update_data: dict):
    """Telegram webhook endpoint (alternative to polling)"""
    if telegram_service:
        await telegram_service.process_update(update_data)
    return {"status": "ok"}

@app.post("/api/telegram/test")
async def test_telegram_message(content: str, sender_name: str = "Test User"):
    """Test endpoint to simulate Telegram messages"""
    if telegram_service:
        from app.schemas.message import MessageCreate
        from datetime import datetime
        
        message_data = MessageCreate(
            content=content,
            source_type="telegram",
            source_chat_id="test_chat",
            source_message_id="test_msg",
            sender_name=sender_name,
            sender_id="test_user",
            timestamp=datetime.utcnow(),
            message_type="text"
        )
        
        result = await telegram_service.message_service.create_message(message_data)
        return {"status": "success", "message_id": result.id if result else None}
    return {"status": "error", "message": "Telegram service not available"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.debug
    ) 