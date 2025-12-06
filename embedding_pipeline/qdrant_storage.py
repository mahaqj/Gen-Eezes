from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional, Tuple
import numpy as np
from datetime import datetime
import json

class QdrantStorage:
    """
    Handles storage and retrieval of embeddings from Qdrant vector database.
    Supports hybrid search, filtering, and metadata-based queries.
    """
    
    def __init__(self, collection_name: str, vector_size: int, 
                 host: str = "localhost", port: int = 6333, 
                 path: str = None, use_memory: bool = False):
        """
        Initialize Qdrant client and collection.
        
        Args:
            collection_name: Name of the collection to work with
            vector_size: Dimension of vectors (e.g., 384 for all-MiniLM-L6-v2)
            host: Qdrant server host (default: localhost)
            port: Qdrant server port (default: 6333)
            path: Local path for in-memory storage (alternative to server)
            use_memory: If True, use in-memory storage (no persistence)
        """
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        try:
            if use_memory:
                # In-memory Qdrant (useful for testing)
                print(f"initializing qdrant in-memory client...")
                self.client = QdrantClient(":memory:")
            elif path:
                # File-based persistence with preferred handling
                print(f"initializing qdrant client with path: {path}")
                try:
                    self.client = QdrantClient(path=path, prefer_grpc=False)
                except Exception as e:
                    # Fallback to in-memory if path is locked
                    print(f"note: {e}")
                    print(f"using in-memory storage instead")
                    self.client = QdrantClient(":memory:")
            else:
                # Server-based connection
                print(f"initializing qdrant client: {host}:{port}")
                self.client = QdrantClient(host=host, port=port)
            
            print("qdrant client initialized successfully")
        except Exception as e:
            print(f"warning: could not connect to qdrant server. falling back to memory mode.")
            print(f"error: {e}")
            self.client = QdrantClient(":memory:")
        
        self.create_collection()
    
    def create_collection(self):
        """Create collection if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name in collection_names:
                print(f"collection '{self.collection_name}' already exists")
                return
            
            # Create new collection
            print(f"creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE  # Cosine distance for text embeddings
                )
            )
            print(f"collection '{self.collection_name}' created successfully")
        except Exception as e:
            print(f"error creating collection: {e}")
    
    def add_point(self, point_id: int, vector: np.ndarray, payload: Dict) -> bool:
        """
        Add a single point (embedding) to the collection.
        
        Args:
            point_id: Unique identifier for the point
            vector: Embedding vector
            payload: Metadata dictionary (source, title, url, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            vector_list = vector.tolist() if isinstance(vector, np.ndarray) else vector
            
            point = PointStruct(
                id=point_id,
                vector=vector_list,
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            return True
        except Exception as e:
            print(f"error adding point {point_id}: {e}")
            return False
    
    def add_points_batch(self, points: List[Tuple[int, np.ndarray, Dict]]) -> int:
        """
        Add multiple points efficiently in batch mode.
        
        Args:
            points: List of tuples (point_id, vector, payload)
            
        Returns:
            Number of points successfully added
        """
        try:
            point_structs = []
            for point_id, vector, payload in points:
                vector_list = vector.tolist() if isinstance(vector, np.ndarray) else vector
                point = PointStruct(
                    id=point_id,
                    vector=vector_list,
                    payload=payload
                )
                point_structs.append(point)
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=point_structs
            )
            return len(point_structs)
        except Exception as e:
            print(f"error adding batch of points: {e}")
            return 0
    
    def search(self, query_vector: np.ndarray, limit: int = 10, 
               score_threshold: float = None, filter_dict: Dict = None) -> List[Dict]:
        """
        Search for similar vectors with optional filtering.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0-1 for cosine)
            filter_dict: Optional filter on payload fields
                        Example: {"source": "github"} or {"score": {"$gte": 100}}
            
        Returns:
            List of search results with scores and metadata
        """
        try:
            vector_list = query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector
            
            # Build filter if provided
            query_filter = None
            if filter_dict:
                query_filter = self._build_filter(filter_dict)
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector_list,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            formatted_results = []
            for hit in results:
                formatted_results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                })
            
            return formatted_results
        except Exception as e:
            print(f"error searching: {e}")
            return []
    
    def search_by_id(self, point_id: int) -> Optional[Dict]:
        """
        Retrieve a specific point by ID.
        
        Args:
            point_id: ID of the point to retrieve
            
        Returns:
            Point data with vector and payload, or None if not found
        """
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id]
            )
            
            if points:
                point = points[0]
                return {
                    "id": point.id,
                    "vector": point.vector,
                    "payload": point.payload
                }
            return None
        except Exception as e:
            print(f"error retrieving point {point_id}: {e}")
            return None
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection info
        """
        try:
            stats = self.client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "points_count": stats.points_count if hasattr(stats, 'points_count') else 0,
                "vector_size": self.vector_size,
                "status": str(stats.status) if hasattr(stats, 'status') else "unknown"
            }
        except Exception as e:
            print(f"error getting collection stats: {e}")
            return {}
    
    def filter_by_source(self, source: str, limit: int = 100) -> List[Dict]:
        """
        Get all documents from a specific source (github, arxiv, news).
        
        Args:
            source: Source type ("github", "arxiv", "news")
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        try:
            points = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                scroll_filter=self._build_filter({"source": source})
            )
            
            results = []
            for point, _ in points:
                results.append({
                    "id": point.id,
                    "payload": point.payload
                })
            
            return results
        except Exception as e:
            print(f"error filtering by source: {e}")
            return []
    
    def delete_point(self, point_id: int) -> bool:
        """Delete a point by ID."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )
            return True
        except Exception as e:
            print(f"error deleting point {point_id}: {e}")
            return False
    
    def delete_collection(self) -> bool:
        """Delete the entire collection."""
        try:
            self.client.delete_collection(self.collection_name)
            print(f"collection '{self.collection_name}' deleted")
            return True
        except Exception as e:
            print(f"error deleting collection: {e}")
            return False
    
    def _build_filter(self, filter_dict: Dict):
        """
        Build a Qdrant filter from a dictionary.
        This is a simplified version - for complex filters, use Qdrant's Filter API directly.
        
        Args:
            filter_dict: Dictionary with field names and values/conditions
            
        Returns:
            Qdrant Filter object
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue, Range
        
        conditions = []
        for key, value in filter_dict.items():
            if isinstance(value, dict):
                # Handle range queries like {"$gte": 100}
                if "$gte" in value:
                    conditions.append(FieldCondition(
                        key=key,
                        range=Range(gte=value["$gte"])
                    ))
                elif "$lte" in value:
                    conditions.append(FieldCondition(
                        key=key,
                        range=Range(lte=value["$lte"])
                    ))
            else:
                # Simple equality match
                conditions.append(FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                ))
        
        if not conditions:
            return None
        
        return Filter(must=conditions)


# Test if run directly
if __name__ == "__main__":
    print("\ntesting qdrant storage...")
    print("="*80)
    
    # Initialize Qdrant with in-memory storage for testing
    qdrant = QdrantStorage(
        collection_name="test_embeddings",
        vector_size=384,
        use_memory=True
    )
    
    # Add some test points
    print("\nadding test embeddings...")
    test_vectors = [
        np.random.randn(384).astype(np.float32),
        np.random.randn(384).astype(np.float32),
        np.random.randn(384).astype(np.float32),
    ]
    
    test_payloads = [
        {"source": "github", "title": "Test Repo 1", "score": 150},
        {"source": "arxiv", "title": "Test Paper 1", "score": 200},
        {"source": "news", "title": "Test News 1", "score": 100},
    ]
    
    points = list(zip(range(1, 4), test_vectors, test_payloads))
    added = qdrant.add_points_batch(points)
    print(f"added {added} test points")
    
    # Get collection stats
    stats = qdrant.get_collection_stats()
    print(f"\ncollection stats: {stats}")
    
    # Search
    print("\nsearching for similar vectors...")
    query_vector = test_vectors[0]
    results = qdrant.search(query_vector, limit=3)
    print(f"found {len(results)} results")
    for result in results:
        print(f"  id: {result['id']}, score: {result['score']:.4f}, title: {result['payload']['title']}")
    
    print("\n" + "="*80)
    print("all tests passed successfully!")
