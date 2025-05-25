from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.schemas.message import (
    MessageCreate, MessageResponse, MessageUpdate, 
    MessageQuery, MessageSearchResponse
)
from app.services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["messages"])
message_service = MessageService()


@router.post("/", response_model=MessageResponse)
async def create_message(message: MessageCreate):
    """Create a new message"""
    result = await message_service.create_message(message)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create message")
    return result


@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    categories: Optional[List[str]] = Query(None),
    message_types: Optional[List[str]] = Query(None),
    sender_id: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None)
):
    """Get messages with optional filtering"""
    filters = {}
    if categories:
        filters['categories'] = categories
    if message_types:
        filters['message_types'] = message_types
    if sender_id:
        filters['sender_id'] = sender_id
    if date_from:
        filters['date_from'] = date_from
    if date_to:
        filters['date_to'] = date_to
    
    return await message_service.get_messages(skip=skip, limit=limit, filters=filters)


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(message_id: int):
    """Get a specific message by ID"""
    message = await message_service.get_message_by_id(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(message_id: int, update_data: MessageUpdate):
    """Update a message"""
    result = await message_service.update_message(message_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Message not found")
    return result


@router.delete("/{message_id}")
async def delete_message(message_id: int):
    """Delete a message"""
    success = await message_service.delete_message(message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message deleted successfully"}


@router.post("/search", response_model=Dict[str, Any])
async def search_messages(query: MessageQuery):
    """Search messages using AI and semantic similarity"""
    return await message_service.search_messages(query)


@router.post("/query")
async def query_ai(query: str, limit: int = Query(10, ge=1, le=50)):
    """Query AI with context from relevant messages"""
    response = await message_service.query_ai(query, limit)
    return {"query": query, "response": response}


@router.get("/stats/{user_id}")
async def get_user_stats(user_id: str):
    """Get user statistics"""
    stats = await message_service.get_user_stats(user_id)
    return stats 