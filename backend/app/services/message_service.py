from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageUpdate, MessageResponse, MessageQuery
from app.core.database import get_db
from app.services.ai_service import AIService
import asyncio

# Try to import ChromaDB vector service, fallback to simple one
try:
    from app.services.vector_service import VectorService
except ImportError:
    from app.services.vector_service_simple import SimpleVectorService as VectorService


class MessageService:
    def __init__(self):
        self.ai_service = AIService()
        # Use try-except to handle ChromaDB connection issues
        try:
            self.vector_service = VectorService()
        except Exception as e:
            print(f"ChromaDB not available, using simple fallback: {e}")
            from app.services.vector_service_simple import SimpleVectorService
            self.vector_service = SimpleVectorService()
    
    async def create_message(self, message_data: MessageCreate) -> Optional[MessageResponse]:
        """Create a new message and trigger AI processing"""
        db = next(get_db())
        try:
            # Create message record
            db_message = Message(**message_data.dict())
            db.add(db_message)
            db.commit()
            db.refresh(db_message)
            
            # Trigger async AI processing
            asyncio.create_task(self.process_message_ai(db_message.id))
            
            return MessageResponse.from_orm(db_message)
        
        except Exception as e:
            db.rollback()
            print(f"Error creating message: {e}")
            return None
        finally:
            db.close()
    
    async def process_message_ai(self, message_id: int):
        """Process message with AI services (async background task)"""
        db = next(get_db())
        try:
            message = db.query(Message).filter(Message.id == message_id).first()
            if not message or not message.content:
                return
            
            # AI analysis
            ai_result = await self.ai_service.analyze_message(
                message.content, 
                message.message_type
            )
            
            # Generate embedding
            embedding = await self.ai_service.generate_embedding(message.content)
            
            # Store in vector database
            embedding_id = None
            if embedding:
                embedding_id = await self.vector_service.add_message_embedding(
                    message_id=message.id,
                    content=message.content,
                    embedding=embedding,
                    metadata={
                        "categories": ai_result.get("categories", []),
                        "tags": ai_result.get("tags", []),
                        "message_type": message.message_type,
                        "sender_name": message.sender_name,
                        "timestamp": message.timestamp.isoformat() if message.timestamp else None
                    }
                )
            
            # Update message with AI results
            message.categories = ai_result.get("categories", [])
            message.tags = ai_result.get("tags", [])
            message.sentiment = ai_result.get("sentiment", 0.0)
            message.summary = ai_result.get("summary", "")
            message.embedding_id = embedding_id
            message.has_embedding = bool(embedding_id)
            message.processed = True
            
            db.commit()
            
        except Exception as e:
            print(f"Error processing message AI: {e}")
            # Mark as processed with error
            if 'message' in locals():
                message.processing_error = str(e)
                message.processed = True
                db.commit()
        finally:
            db.close()
    
    async def get_messages(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[MessageResponse]:
        """Get messages with optional filtering"""
        db = next(get_db())
        try:
            query = db.query(Message)
            
            # Apply filters
            if filters:
                if filters.get('categories'):
                    query = query.filter(Message.categories.overlap(filters['categories']))
                if filters.get('message_types'):
                    query = query.filter(Message.message_type.in_(filters['message_types']))
                if filters.get('sender_id'):
                    query = query.filter(Message.sender_id == filters['sender_id'])
                if filters.get('date_from'):
                    query = query.filter(Message.timestamp >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(Message.timestamp <= filters['date_to'])
            
            messages = query.order_by(desc(Message.created_at)).offset(skip).limit(limit).all()
            return [MessageResponse.from_orm(msg) for msg in messages]
        
        finally:
            db.close()
    
    async def search_messages(self, query_data: MessageQuery) -> Dict[str, Any]:
        """Search messages using AI and vector similarity"""
        try:
            # Generate embedding for query
            query_embedding = await self.ai_service.generate_embedding(query_data.query)
            
            # Semantic search
            vector_results = await self.vector_service.hybrid_search(
                query_text=query_data.query,
                query_embedding=query_embedding,
                keyword_filters={
                    'categories': query_data.categories,
                    'message_type': query_data.message_types,
                    'date_from': query_data.date_from,
                    'date_to': query_data.date_to
                },
                limit=query_data.limit
            )
            
            # Get message details from database
            db = next(get_db())
            message_ids = [int(result['metadata']['message_id']) for result in vector_results]
            
            if message_ids:
                messages = db.query(Message).filter(Message.id.in_(message_ids)).all()
                message_dict = {msg.id: msg for msg in messages}
                
                # Order messages by search relevance
                ordered_messages = []
                for result in vector_results:
                    msg_id = int(result['metadata']['message_id'])
                    if msg_id in message_dict:
                        ordered_messages.append(message_dict[msg_id])
            else:
                ordered_messages = []
            
            # Get suggested categories
            suggested_categories = await self.ai_service.suggest_categories(
                [{'categories': msg.categories} for msg in ordered_messages if msg.categories]
            )
            
            db.close()
            
            return {
                "messages": [MessageResponse.from_orm(msg) for msg in ordered_messages],
                "total": len(ordered_messages),
                "query": query_data.query,
                "suggested_categories": suggested_categories
            }
        
        except Exception as e:
            print(f"Search error: {e}")
            return {
                "messages": [],
                "total": 0,
                "query": query_data.query,
                "suggested_categories": []
            }
    
    async def query_ai(self, query: str, limit: int = 10) -> str:
        """Query AI with context from relevant messages"""
        try:
            # Find relevant messages
            query_embedding = await self.ai_service.generate_embedding(query)
            relevant_messages = await self.vector_service.search_similar_messages(
                query_embedding, 
                limit=limit
            )
            
            # Format messages for AI context
            context_messages = []
            for result in relevant_messages:
                context_messages.append({
                    'content': result['content'],
                    'metadata': result['metadata'],
                    'timestamp': result['metadata'].get('timestamp', 'unknown'),
                    'sender_name': result['metadata'].get('sender_name', 'Unknown')
                })
            
            # Generate AI response
            response = await self.ai_service.query_messages(query, context_messages)
            return response
        
        except Exception as e:
            print(f"AI query error: {e}")
            return "I'm sorry, I encountered an error while processing your query."
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        db = next(get_db())
        try:
            total_messages = db.query(Message).filter(Message.sender_id == user_id).count()
            
            # Get recent activity
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_messages = db.query(Message).filter(
                and_(Message.sender_id == user_id, Message.created_at >= week_ago)
            ).count()
            
            # Get top categories
            messages_with_categories = db.query(Message).filter(
                and_(Message.sender_id == user_id, Message.categories.isnot(None))
            ).all()
            
            all_categories = []
            for msg in messages_with_categories:
                if msg.categories:
                    all_categories.extend(msg.categories)
            
            category_counts = {}
            for cat in all_categories:
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            top_categories = sorted(category_counts.keys(), 
                                  key=lambda x: category_counts[x], 
                                  reverse=True)[:5]
            
            # Get last activity
            last_message = db.query(Message).filter(Message.sender_id == user_id)\
                            .order_by(desc(Message.created_at)).first()
            
            last_activity = last_message.created_at.strftime('%Y-%m-%d %H:%M') if last_message else 'Never'
            
            return {
                'total_messages': total_messages,
                'recent_messages': recent_messages,
                'top_categories': top_categories,
                'last_activity': last_activity,
                'storage_used': f'{total_messages * 0.5:.1f} MB'  # Rough estimate
            }
        
        finally:
            db.close()
    
    async def get_message_by_id(self, message_id: int) -> Optional[MessageResponse]:
        """Get a specific message by ID"""
        db = next(get_db())
        try:
            message = db.query(Message).filter(Message.id == message_id).first()
            return MessageResponse.from_orm(message) if message else None
        finally:
            db.close()
    
    async def update_message(self, message_id: int, update_data: MessageUpdate) -> Optional[MessageResponse]:
        """Update message"""
        db = next(get_db())
        try:
            message = db.query(Message).filter(Message.id == message_id).first()
            if not message:
                return None
            
            for field, value in update_data.dict(exclude_unset=True).items():
                setattr(message, field, value)
            
            db.commit()
            db.refresh(message)
            return MessageResponse.from_orm(message)
        
        except Exception as e:
            db.rollback()
            print(f"Error updating message: {e}")
            return None
        finally:
            db.close()
    
    async def delete_message(self, message_id: int) -> bool:
        """Delete message and its embedding"""
        db = next(get_db())
        try:
            message = db.query(Message).filter(Message.id == message_id).first()
            if not message:
                return False
            
            # Delete from vector database if exists
            if message.embedding_id:
                await self.vector_service.delete_message_embedding(message.embedding_id)
            
            db.delete(message)
            db.commit()
            return True
        
        except Exception as e:
            db.rollback()
            print(f"Error deleting message: {e}")
            return False
        finally:
            db.close() 