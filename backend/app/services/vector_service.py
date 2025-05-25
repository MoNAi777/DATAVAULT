import chromadb
from typing import List, Dict, Any, Optional
from config.settings import settings
import uuid
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class VectorService:
    def __init__(self):
        self.client = None
        self.collection_name = settings.chroma_collection_name
        self.collection = None
        self._initialize_client()
        self._initialize_collection()
    
    def _initialize_client(self):
        """Initialize ChromaDB client with proper error handling"""
        try:
            logger.info(f"Connecting to ChromaDB at {settings.chroma_host}:{settings.chroma_port}")
            # Try to create the client
            self.client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
                ssl=False  # Explicitly set SSL to False for HTTP connections
            )
            
            # Test the connection by trying to heartbeat
            try:
                self.client.heartbeat()
                logger.info("ChromaDB client initialized successfully")
            except Exception as heartbeat_error:
                logger.warning(f"ChromaDB heartbeat failed: {heartbeat_error}")
                # Don't fail initialization, as heartbeat might not be available
                
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            self.client = None
    
    def _initialize_collection(self):
        """Initialize or get the ChromaDB collection"""
        if not self.client:
            logger.warning("ChromaDB client not available")
            self.collection = None
            return
            
        try:
            # In ChromaDB 1.0+, use get_or_create_collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "DataVault message embeddings"}
            )
            logger.info(f"Collection '{self.collection_name}' initialized successfully")
        except Exception as e:
            logger.error(f"ChromaDB collection initialization error: {e}")
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
            logger.warning("Collection not available or embedding is empty")
            return None
        
        try:
            doc_id = f"msg_{message_id}_{uuid.uuid4().hex[:8]}"
            
            # Prepare metadata - ensure all values are JSON serializable
            meta = {
                "message_id": str(message_id),
                "content_preview": content[:200],
            }
            
            # Add metadata if provided, ensuring values are serializable
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        meta[key] = value
                    elif isinstance(value, list):
                        # Convert list to string representation for ChromaDB
                        meta[key] = str(value)
                    else:
                        meta[key] = str(value)
            
            self.collection.add(
                documents=[content],
                embeddings=[embedding],
                metadatas=[meta],
                ids=[doc_id]
            )
            
            logger.debug(f"Added embedding with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding embedding: {e}")
            return None
    
    async def search_similar_messages(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar messages using vector similarity"""
        if not self.collection or not query_embedding:
            logger.warning("Collection not available or query embedding is empty")
            return []
        
        try:
            # Build where clause for filtering - ChromaDB 1.0+ syntax
            where_clause = None
            if filters:
                where_clause = {}
                if filters.get('categories'):
                    # Convert list to string for filtering since we store it as string
                    categories_str = str(filters['categories'])
                    where_clause['categories'] = {"$contains": categories_str}
                if filters.get('message_type'):
                    where_clause['message_type'] = filters['message_type']
                if filters.get('date_from'):
                    where_clause['timestamp'] = {"$gte": filters['date_from'].isoformat()}
            
            logger.debug(f"Searching with query embedding of length {len(query_embedding)}, limit {limit}")
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None,
                include=['documents', 'metadatas', 'distances']  # Explicitly specify what to include
            )
            
            # Format results - handle ChromaDB 1.0+ result structure
            formatted_results = []
            if results and 'documents' in results and results['documents']:
                documents = results['documents'][0] if results['documents'] else []
                metadatas = results['metadatas'][0] if results.get('metadatas') else []
                distances = results['distances'][0] if results.get('distances') else []
                ids = results['ids'][0] if results.get('ids') else []
                
                for i, doc in enumerate(documents):
                    result_item = {
                        'id': ids[i] if i < len(ids) else f"unknown_{i}",
                        'content': doc,
                        'metadata': metadatas[i] if i < len(metadatas) else {},
                        'distance': distances[i] if i < len(distances) else None
                    }
                    formatted_results.append(result_item)
            
            logger.debug(f"Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []
    
    async def delete_message_embedding(self, doc_id: str) -> bool:
        """Delete message embedding from vector database"""
        if not self.collection:
            logger.warning("Collection not available for deletion")
            return False
        
        try:
            self.collection.delete(ids=[doc_id])
            logger.debug(f"Deleted embedding with ID: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting embedding: {e}")
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
            logger.warning("Collection not available for update")
            return False
        
        try:
            # ChromaDB doesn't support direct updates, so we delete and recreate
            self.collection.delete(ids=[doc_id])
            
            if embedding and content:
                # Prepare metadata
                meta = metadata or {}
                
                self.collection.add(
                    documents=[content],
                    embeddings=[embedding],
                    metadatas=[meta],
                    ids=[doc_id]
                )
            
            logger.debug(f"Updated embedding with ID: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating embedding: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection"""
        if not self.collection:
            return {"error": "Collection not available"}
        
        try:
            count = self.collection.count()
            logger.debug(f"Collection has {count} embeddings")
            return {
                "total_embeddings": count,
                "collection_name": self.collection_name,
                "status": "connected"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
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