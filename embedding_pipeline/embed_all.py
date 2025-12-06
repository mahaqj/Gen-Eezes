"""
Main embedding pipeline with single-client file-based storage.
Processes all MongoDB data and stores embeddings in Qdrant.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mongodb_storage import MongoDBStorage
from embedding_handler import EmbeddingHandler
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import json

def create_collection(client, collection_name, vector_size):
    """Create collection if it doesn't exist."""
    try:
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if collection_name not in collection_names:
            print(f"creating collection: {collection_name}")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
        else:
            print(f"collection '{collection_name}' already exists")
    except Exception as e:
        print(f"error with collection {collection_name}: {e}")

def main():
    """Main embedding pipeline."""
    print("\n" + "="*80)
    print("EMBEDDING PIPELINE - FILE-BASED STORAGE")
    print("="*80)
    
    print("\n1. connecting to mongodb...")
    db = MongoDBStorage()
    
    print("\n2. loading embedding model...")
    embedder = EmbeddingHandler()
    embedding_dim = embedder.embedding_dim
    
    print("\n3. initializing qdrant with file-based storage...")
    client = QdrantClient(path="./qdrant_storage", prefer_grpc=False)
    print("qdrant client initialized")
    
    print("\n4. setting up collections...")
    create_collection(client, "github_embeddings", embedding_dim)
    create_collection(client, "arxiv_embeddings", embedding_dim)
    create_collection(client, "news_embeddings", embedding_dim)
    
    # Process GitHub repos
    print("\n" + "-"*80)
    print("PROCESSING GITHUB REPOS")
    print("-"*80)
    
    repos = list(db.github_collection.find())
    print(f"found {len(repos)} repos in mongodb")
    
    github_points = []
    for idx, repo in enumerate(repos, 1):
        combined_text = embedder.combine_fields({
            "owner": repo.get("owner", ""),
            "name": repo.get("name", ""),
            "description": repo.get("description", ""),
            "readme": repo.get("readme_text", "")[:500],
            "topics": " ".join(repo.get("topics", []))
        }, weights={"owner": 0.5, "name": 1.5, "description": 2, "readme": 1, "topics": 1})
        
        embedding = embedder.embed_text(combined_text)
        
        payload = {
            "source": "github",
            "owner": repo.get("owner", ""),
            "name": repo.get("name", ""),
            "full_name": repo.get("full_name", ""),
            "title": repo.get("full_name", ""),
            "language": repo.get("language", ""),
            "stars_total": repo.get("stars_total", 0),
            "stars_trending": str(repo.get("stars_trending", "0")).rstrip("+"),
            "repo_url": repo.get("repo_url", ""),
        }
        
        point_id = idx
        github_points.append(PointStruct(
            id=point_id,
            vector=embedding.tolist(),
            payload=payload
        ))
        
        if idx % 5 == 0:
            print(f"  processed {idx}/{len(repos)} repos...")
    
    client.upsert(collection_name="github_embeddings", points=github_points)
    print(f"[OK] stored {len(github_points)} github embeddings")
    
    # Process arXiv papers
    print("\n" + "-"*80)
    print("PROCESSING ARXIV PAPERS")
    print("-"*80)
    
    papers = list(db.arxiv_collection.find())
    print(f"found {len(papers)} papers in mongodb")
    
    arxiv_points = []
    for idx, paper in enumerate(papers, 1):
        combined_text = embedder.combine_fields({
            "title": paper.get("title", ""),
            "abstract": paper.get("abstract", ""),
            "categories": " ".join(paper.get("categories", []))
        }, weights={"title": 2, "abstract": 2, "categories": 0.5})
        
        embedding = embedder.embed_text(combined_text)
        
        payload = {
            "source": "arxiv",
            "arxiv_id": paper.get("arxiv_id", ""),
            "title": paper.get("title", ""),
            "authors": json.dumps(paper.get("authors", [])),
            "categories": json.dumps(paper.get("categories", [])),
            "published": paper.get("published", ""),
            "pdf_url": paper.get("pdf_url", ""),
            "arxiv_url": paper.get("arxiv_url", ""),
        }
        
        point_id = idx
        arxiv_points.append(PointStruct(
            id=point_id,
            vector=embedding.tolist(),
            payload=payload
        ))
        
        if idx % 5 == 0:
            print(f"  processed {idx}/{len(papers)} papers...")
    
    client.upsert(collection_name="arxiv_embeddings", points=arxiv_points)
    print(f"[OK] stored {len(arxiv_points)} arxiv embeddings")
    
    # Process tech news
    print("\n" + "-"*80)
    print("PROCESSING TECH NEWS")
    print("-"*80)
    
    news_items = list(db.news_collection.find())
    print(f"found {len(news_items)} news items in mongodb")
    
    news_points = []
    for idx, news in enumerate(news_items, 1):
        combined_text = embedder.combine_fields({
            "title": news.get("title", ""),
            "url": news.get("url", ""),
            "author": news.get("author", "")
        }, weights={"title": 3, "url": 0.5, "author": 0.5})
        
        embedding = embedder.embed_text(combined_text)
        
        payload = {
            "source": "news",
            "hackernews_id": news.get("hackernews_id", 0),
            "title": news.get("title", ""),
            "url": news.get("url", ""),
            "score": news.get("score", 0),
            "comments": news.get("comments", 0),
            "author": news.get("author", ""),
        }
        
        point_id = idx
        news_points.append(PointStruct(
            id=point_id,
            vector=embedding.tolist(),
            payload=payload
        ))
        
        if idx % 5 == 0:
            print(f"  processed {idx}/{len(news_items)} news items...")
    
    client.upsert(collection_name="news_embeddings", points=news_points)
    print(f"[OK] stored {len(news_points)} news embeddings")
    
    # Print summary
    print("\n" + "="*80)
    print("EMBEDDING PIPELINE COMPLETED")
    print("="*80)
    
    print("\nSTATISTICS:")
    total = len(github_points) + len(arxiv_points) + len(news_points)
    print(f"\nEmbeddings created:")
    print(f"  github repos:    {len(github_points)}")
    print(f"  arxiv papers:    {len(arxiv_points)}")
    print(f"  tech news:       {len(news_points)}")
    print(f"  total:           {total}")
    
    print(f"\nQdrant collections (persisted to disk):")
    github_stats = client.get_collection("github_embeddings")
    arxiv_stats = client.get_collection("arxiv_embeddings")
    news_stats = client.get_collection("news_embeddings")
    
    print(f"  github_embeddings: {github_stats.points_count} points")
    print(f"  arxiv_embeddings:  {arxiv_stats.points_count} points")
    print(f"  news_embeddings:   {news_stats.points_count} points")
    print(f"  storage location:  ./qdrant_storage/")
    
    print("\n" + "="*80)
    print("[SUCCESS] EMBEDDING PIPELINE COMPLETED!")
    print("="*80)
    print("\nNext steps:")
    print("  1. Use tests/verify_qdrant.py for verification")
    print("  2. Implement semantic search agent")
    print("  3. Build hybrid search with keyword matching")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
