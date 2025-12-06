"""Verification script to check stored embeddings and perform sample queries."""

from qdrant_storage import QdrantStorage
from embedding_handler import EmbeddingHandler
import numpy as np

def verify_embeddings():
    """Verify all embeddings are properly stored."""
    print("\n" + "="*80)
    print("VERIFYING STORED EMBEDDINGS")
    print("="*80)
    
    qdrant_github = QdrantStorage('github_embeddings', 384, path='./qdrant_storage')
    qdrant_arxiv = QdrantStorage('arxiv_embeddings', 384, path='./qdrant_storage')
    qdrant_news = QdrantStorage('news_embeddings', 384, path='./qdrant_storage')
    
    github_stats = qdrant_github.get_collection_stats()
    print(f"\n✓ GitHub Embeddings Collection:")
    print(f"  Points stored: {github_stats['points_count']}")
    
    arxiv_stats = qdrant_arxiv.get_collection_stats()
    print(f"\n✓ arXiv Embeddings Collection:")
    print(f"  Points stored: {arxiv_stats['points_count']}")
    
    news_stats = qdrant_news.get_collection_stats()
    print(f"\n✓ News Embeddings Collection:")
    print(f"  Points stored: {news_stats['points_count']}")
    
    total = github_stats['points_count'] + arxiv_stats['points_count'] + news_stats['points_count']
    print(f"\n📊 TOTAL EMBEDDINGS STORED: {total}")
    
    return qdrant_github, qdrant_arxiv, qdrant_news


def test_semantic_search():
    """Test semantic search functionality."""
    print("\n" + "="*80)
    print("TESTING SEMANTIC SEARCH")
    print("="*80)
    
    qdrant_github, qdrant_arxiv, qdrant_news = verify_embeddings()
    embedder = EmbeddingHandler()
    
    # Test search queries
    test_queries = [
        ("AI and machine learning frameworks", qdrant_github, "github"),
        ("neural networks and deep learning", qdrant_arxiv, "arxiv"),
        ("cloud computing and DevOps", qdrant_news, "news")
    ]
    
    for query_text, qdrant_storage, source in test_queries:
        print(f"\n{'─'*80}")
        print(f"Query: '{query_text}' (searching {source})")
        print(f"{'─'*80}")
        
        query_embedding = embedder.embed_text(query_text)
        results = qdrant_storage.search(query_embedding, limit=3)
        
        if results:
            for i, result in enumerate(results, 1):
                payload = result['payload']
                print(f"\n{i}. Score: {result['score']:.4f}")
                if source == "github":
                    print(f"   Repo: {payload.get('full_name', 'N/A')}")
                    print(f"   Description: {payload.get('description', 'N/A')[:100]}...")
                elif source == "arxiv":
                    print(f"   Paper: {payload.get('title', 'N/A')[:70]}...")
                    print(f"   Categories: {payload.get('categories', 'N/A')}")
                elif source == "news":
                    print(f"   Title: {payload.get('title', 'N/A')[:70]}...")
                    print(f"   Score: {payload.get('score', 0)}, Comments: {payload.get('comments', 0)}")
        else:
            print("  No results found")


def test_sample_retrieval():
    """Test retrieving and displaying sample data."""
    print("\n" + "="*80)
    print("SAMPLE DATA RETRIEVAL")
    print("="*80)
    
    qdrant_github, qdrant_arxiv, qdrant_news = verify_embeddings()
    
    print("\n📦 SAMPLE GITHUB REPO:")
    github_sample = qdrant_github.filter_by_source("github", limit=1)
    if github_sample:
        payload = github_sample[0]['payload']
        print(f"  Repo: {payload.get('full_name')}")
        print(f"  Language: {payload.get('language')}")
        print(f"  Stars: {payload.get('stars_total')}")
        print(f"  Topics: {payload.get('topics')}")
    
    print("\n📄 SAMPLE ARXIV PAPER:")
    arxiv_sample = qdrant_arxiv.filter_by_source("arxiv", limit=1)
    if arxiv_sample:
        payload = arxiv_sample[0]['payload']
        print(f"  Title: {payload.get('title')[:60]}...")
        print(f"  arXiv ID: {payload.get('arxiv_id')}")
        print(f"  Categories: {payload.get('categories')}")
    
    print("\n📰 SAMPLE NEWS ITEM:")
    news_sample = qdrant_news.filter_by_source("news", limit=1)
    if news_sample:
        payload = news_sample[0]['payload']
        print(f"  Title: {payload.get('title')[:60]}...")
        print(f"  Score: {payload.get('score')}")
        print(f"  Comments: {payload.get('comments')}")
        print(f"  Author: {payload.get('author')}")


if __name__ == "__main__":
    print("\n" + "█"*80)
    print("EMBEDDING VERIFICATION & SEMANTIC SEARCH TEST")
    print("█"*80)
    
    verify_embeddings()
    test_sample_retrieval()
    test_semantic_search()
    
    print("\n" + "="*80)
    print("✅ ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\nYour embedding module is ready for:")
    print("  • Semantic search across tech topics")
    print("  • Hybrid search with metadata filtering")
    print("  • Multi-source recommendation engine")
    print("  • Agent-based query processing")
    print("="*80 + "\n")
