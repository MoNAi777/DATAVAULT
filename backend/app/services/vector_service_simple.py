from typing import List, Dict, Any, Optional
import json
import os


class SimpleVectorService:
    """Simple in-memory vector service for testing without ChromaDB"""
    
    def __init__(self):
        self.embeddings = {}  # Store embeddings in memory
        self.documents = {}   # Store documents in memory
        self.metadata = {}    # Store metadata in memory
        self.counter = 0
    
    async def add_message_embedding(
        self, 
        message_id: int, 
        content: str, 
        embedding: List[float],
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Add message embedding to in-memory storage"""
        if not embedding:
            return None
        
        try:
            doc_id = f"msg_{message_id}_{self.counter}"
            self.counter += 1
            
            self.embeddings[doc_id] = embedding
            self.documents[doc_id] = content
            self.metadata[doc_id] = {
                "message_id": message_id,
                "content_preview": content[:200],
                **(metadata or {})
            }
            
            return doc_id
            
        except Exception as e:
            print(f"Error adding embedding: {e}")
            return None
    
    async def search_similar_messages(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Simple keyword-based search (fallback without vector similarity)"""
        if not query_embedding:
            return []
        
        try:
            # Simple implementation: return all documents (for testing)
            results = []
            for doc_id, content in list(self.documents.items())[:limit]:
                results.append({
                    'id': doc_id,
                    'content': content,
                    'metadata': self.metadata.get(doc_id, {}),
                    'distance': 0.5  # Dummy distance
                })
            
            return results
            
        except Exception as e:
            print(f"Vector search error: {e}")
            return []
    
    async def delete_message_embedding(self, doc_id: str) -> bool:
        """Delete message embedding from storage"""
        try:
            if doc_id in self.embeddings:
                del self.embeddings[doc_id]
                del self.documents[doc_id]
                del self.metadata[doc_id]
                return True
            return False
        except Exception as e:
            print(f"Error deleting embedding: {e}")
            return False
    
    async def update_message_embedding(
        self, 
        doc_id: str, 
        content: str = None,
        embedding: List[float] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Update message embedding"""
        try:
            if doc_id in self.embeddings:
                if embedding:
                    self.embeddings[doc_id] = embedding
                if content:
                    self.documents[doc_id] = content
                if metadata:
                    self.metadata[doc_id] = metadata
                return True
            return False
        except Exception as e:
            print(f"Error updating embedding: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        return {
            "total_embeddings": len(self.embeddings),
            "collection_name": "simple_memory_store"
        }
    
    async def hybrid_search(
        self, 
        query_text: str,
        query_embedding: List[float],
        keyword_filters: Dict[str, Any] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Simple keyword-based hybrid search"""
        # Simple keyword matching
        query_words = set(query_text.lower().split())
        
        scored_results = []
        for doc_id, content in self.documents.items():
            content_words = set(content.lower().split())
            keyword_score = len(query_words.intersection(content_words)) / max(len(query_words), 1)
            
            if keyword_score > 0:  # Only include results with keyword matches
                scored_results.append({
                    'id': doc_id,
                    'content': content,
                    'metadata': self.metadata.get(doc_id, {}),
                    'distance': 1 - keyword_score,
                    'combined_score': keyword_score
                })
        
        # Sort by score and return top results
        scored_results.sort(key=lambda x: x['combined_score'], reverse=True)
        return scored_results[:limit] 