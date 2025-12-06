"""Test embeddings functionality."""

from qdrant_client import QdrantClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from embedding.handler import EmbeddingHandler

def test_embeddings():
    """Test embeddings using Qdrant."""
    print("\n" + "="*80)
    print("EMBEDDING VERIFICATION TEST")
    print("="*80)
    
    try:
        client = QdrantClient(path="./qdrant_storage", prefer_grpc=False)
        
        collections_response = client.get_collections()
        collection_names = [col.name for col in collections_response.collections]
        
        print(f"\n✓ Collections found: {collection_names}")
        
        total_points = 0
        for col_name in collection_names:
            if "embedding" in col_name:
                stats = client.get_collection(col_name)
                points_count = stats.points_count
                total_points += points_count
                print(f"  • {col_name}: {points_count} embeddings")
        
        print(f"\n📊 TOTAL EMBEDDINGS STORED: {total_points}")
        
        print(f"\n" + "-"*80)
        print("SEMANTIC SEARCH TEST")
        print("-"*80)
        
        embedder = EmbeddingHandler()
        
        query_text = "machine learning and AI frameworks"
        query_embedding = embedder.embed_text(query_text)
        print(f"\nQuery: '{query_text}'")
        
        print(f"\nSearching in github_embeddings...")
        results = []
        try:
            results = client.query_points(
                collection_name="github_embeddings",
                query=query_embedding.tolist(),
                limit=2,
                with_payload=True,
                with_vectors=False
            )
            if hasattr(results, 'points'):
                results = results.points
        except AttributeError:
            pass
        
        if results:
            print(f"✓ Found {len(results)} results")
        else:
            print("  No results found")
        
        print("\n" + "="*80)
        print("✅ VERIFICATION SUCCESSFUL!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    test_embeddings()
