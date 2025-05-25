from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import os

from config.settings import settings
from app.core.database import create_tables
from app.api.messages import router as messages_router
from app.api.whatsapp import router as whatsapp_router
# Telegram service removed - now runs as standalone service


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
    
    # Telegram bot runs as a separate Docker service
    print("ℹ️ Telegram bot runs as a separate Docker service")
    
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
app.include_router(whatsapp_router)

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
    """Health check endpoint with actual service status"""
    import httpx
    from sqlalchemy import text
    from app.core.database import get_db
    
    services_status = {
        "api": "running",
        "telegram_bot": "separate_docker_service",
        "database": "unknown",
        "vector_db": "unknown",
        "redis": "unknown"
    }
    
    # Check database
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        services_status["database"] = "connected"
        db.close()
    except Exception as e:
        services_status["database"] = f"error: {str(e)[:50]}"
    
    # Check ChromaDB
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{settings.chroma_host}:{settings.chroma_port}/api/v2/heartbeat", timeout=5)
            if response.status_code == 200:
                services_status["vector_db"] = "connected"
            else:
                services_status["vector_db"] = f"status_{response.status_code}"
    except Exception as e:
        services_status["vector_db"] = f"error: {str(e)[:50]}"
    
    # Check Redis
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
        services_status["redis"] = "connected"
    except Exception as e:
        services_status["redis"] = f"error: {str(e)[:50]}"
    
    return {
        "status": "healthy",
        "version": settings.app_version,
        "services": services_status
    }


@app.post("/api/telegram/test")
async def test_telegram_message(content: str, sender_name: str = "Test User"):
    """Test endpoint to simulate Telegram messages"""
    from app.services.message_service import MessageService
    from app.schemas.message import MessageCreate
    from datetime import datetime
    
    message_service = MessageService()
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
    
    result = await message_service.create_message(message_data)
    return {"status": "success", "message_id": result.id if result else None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.debug
    ) 