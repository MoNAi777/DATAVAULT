import chromadb
from typing import List, Dict, Any, Optional
from config.settings import settings
import uuid


class VectorService:
    def __init__(self):
        self.client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port
        )
        self.collection_name = settings.chroma_collection_name
        self.collection = None
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or get the ChromaDB collection"""
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "DataVault message embeddings"}
            )
        except Exception as e:
            print(f"ChromaDB connection error: {e}")
            self.collection = None
    
    async def add_message_embedding(
        self, 
        message_id: int, 
        content: str, 
        embedding: List[float],
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Add message embedding to vector database"""
        if not self.collection or not embedding:
            return None
        
        try:
            doc_id = f"msg_{message_id}_{uuid.uuid4().hex[:8]}"
            
            # Prepare metadata
            meta = {
                "message_id": message_id,
                "content_preview": content[:200],
                **(metadata or {})
            }
            
            self.collection.add(
                documents=[content],
                embeddings=[embedding],
                metadatas=[meta],
                ids=[doc_id]
            )
            
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
        """Search for similar messages using vector similarity"""
        if not self.collection or not query_embedding:
            return []
        
        try:
            # Build where clause for filtering
            where_clause = {}
            if filters:
                if filters.get('categories'):
                    where_clause['categories'] = {"$in": filters['categories']}
                if filters.get('message_type'):
                    where_clause['message_type'] = filters['message_type']
                if filters.get('date_from'):
                    where_clause['timestamp'] = {"$gte": filters['date_from'].isoformat()}
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'content': doc,
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if results.get('distances') else None
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Vector search error: {e}")
            return []
    
    async def delete_message_embedding(self, doc_id: str) -> bool:
        """Delete message embedding from vector database"""
        if not self.collection:
            return False
        
        try:
            self.collection.delete(ids=[doc_id])
            return True
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
        """Update message embedding in vector database"""
        if not self.collection:
            return False
        
        try:
            # ChromaDB doesn't support direct updates, so we delete and recreate
            self.collection.delete(ids=[doc_id])
            
            if embedding and content:
                self.collection.add(
                    documents=[content],
                    embeddings=[embedding],
                    metadatas=[metadata or {}],
                    ids=[doc_id]
                )
            
            return True
        except Exception as e:
            print(f"Error updating embedding: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection"""
        if not self.collection:
            return {"error": "Collection not available"}
        
        try:
            count = self.collection.count()
            return {
                "total_embeddings": count,
                "collection_name": self.collection_name
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"error": str(e)}
    
    async def hybrid_search(
        self, 
        query_text: str,
        query_embedding: List[float],
        keyword_filters: Dict[str, Any] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search combining vector similarity and keyword matching"""
        vector_results = await self.search_similar_messages(
            query_embedding, 
            limit=limit * 2,  # Get more results for filtering
            filters=keyword_filters
        )
        
        # Simple keyword matching for hybrid results
        query_words = set(query_text.lower().split())
        
        scored_results = []
        for result in vector_results:
            content_words = set(result['content'].lower().split())
            keyword_score = len(query_words.intersection(content_words)) / len(query_words)
            
            # Combine vector similarity and keyword matching
            vector_score = 1 - (result.get('distance', 1) if result.get('distance') else 1)
            combined_score = (vector_score * 0.7) + (keyword_score * 0.3)
            
            result['combined_score'] = combined_score
            scored_results.append(result)
        
        # Sort by combined score and return top results
        scored_results.sort(key=lambda x: x['combined_score'], reverse=True)
        return scored_results[:limit] 