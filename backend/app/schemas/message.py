from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessageBase(BaseModel):
    content: Optional[str] = None
    message_type: str = "text"
    sender_name: Optional[str] = None
    sender_id: Optional[str] = None


class MessageCreate(MessageBase):
    source_type: str
    source_chat_id: Optional[str] = None
    source_message_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None


class MessageUpdate(BaseModel):
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    sentiment: Optional[float] = None
    summary: Optional[str] = None
    processed: Optional[bool] = None


class MessageResponse(MessageBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    source_type: str
    source_chat_id: Optional[str]
    source_message_id: Optional[str]
    timestamp: Optional[datetime]
    created_at: datetime
    categories: Optional[List[str]]
    tags: Optional[List[str]]
    sentiment: Optional[float]
    summary: Optional[str]
    file_path: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    processed: bool
    has_embedding: bool


class MessageQuery(BaseModel):
    query: str
    limit: int = 10
    categories: Optional[List[str]] = None
    message_types: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class MessageSearchResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    query: str
    suggested_categories: List[str] 