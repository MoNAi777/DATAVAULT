from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Source information
    source_type = Column(String(20), nullable=False)  # telegram, whatsapp
    source_chat_id = Column(String(100))
    source_message_id = Column(String(100))
    
    # Message content
    content = Column(Text)
    message_type = Column(String(20), default="text")  # text, image, video, audio, document
    
    # Metadata
    sender_name = Column(String(200))
    sender_id = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=func.now())
    
    # AI processing
    categories = Column(JSON)  # Auto-detected categories
    tags = Column(JSON)       # AI-generated tags
    sentiment = Column(Float) # Sentiment score
    summary = Column(Text)    # AI-generated summary
    
    # Vector embedding info
    embedding_id = Column(String(100))  # ChromaDB document ID
    has_embedding = Column(Boolean, default=False)
    
    # File information (for media messages)
    file_path = Column(String(500))
    file_type = Column(String(50))
    file_size = Column(Integer)
    
    # Processing status
    processed = Column(Boolean, default=False)
    processing_error = Column(Text)
    
    def __repr__(self):
        return f"<Message(id={self.id}, type={self.message_type}, source={self.source_type})>" 