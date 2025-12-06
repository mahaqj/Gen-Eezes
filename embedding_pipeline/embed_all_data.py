"""
Embedding Pipeline: Process MongoDB data and store embeddings in Qdrant.

This script:
1. Reads data from MongoDB collections
2. Combines relevant text fields for each document
3. Generates embeddings using Sentence Transformers
4. Stores embeddings in Qdrant with metadata for hybrid search
5. Provides utilities for querying and managing embeddings
"""

from mongodb_storage import MongoDBStorage
from embedding_handler import EmbeddingHandler
from qdrant_storage import QdrantStorage
from typing import List, Tuple
import numpy as np
from datetime import datetime
import json

class EmbeddingPipeline:
    """
    Complete pipeline for embedding data from MongoDB and storing in Qdrant.
    """
    
    def __init__(self, mongodb_db_name: str = "gen_eezes",
                 qdrant_path: str = "./qdrant_storage",
                 embedder_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding pipeline.
        
        Args:
            mongodb_db_name: MongoDB database name
            qdrant_path: Path for Qdrant local storage
            embedder_model: Name of the embedding model to use
        """
        print("\n" + "="*80)
        print("INITIALIZING EMBEDDING PIPELINE")
        print("="*80)
        
        # Initialize MongoDB storage
        print("\n1. connecting to mongodb...")
        self.db = MongoDBStorage(db_name=mongodb_db_name)
        
        # Initialize embedding handler
        print("\n2. loading embedding model...")
        self.embedder = EmbeddingHandler(model_name=embedder_model)
        embedding_dim = self.embedder.embedding_dim
        
        # Initialize Qdrant storage (3 collections, one per data source)
        print("\n3. initializing qdrant collections...")
        self.qdrant_github = QdrantStorage(
            collection_name="github_embeddings",
            vector_size=embedding_dim,
            use_memory=True  # Use memory to avoid file locking issues during batch insertion
        )
        self.qdrant_arxiv = QdrantStorage(
            collection_name="arxiv_embeddings",
            vector_size=embedding_dim,
            use_memory=True
        )
        self.qdrant_news = QdrantStorage(
            collection_name="news_embeddings",
            vector_size=embedding_dim,
            use_memory=True
        )
        
        self.processed_count = {
            "github": 0,
            "arxiv": 0,
            "news": 0
        }
    
    def embed_github_repos(self) -> int:
        """
        Process GitHub repos from MongoDB and store embeddings.
        
        Returns:
            Number of repos processed
        """
        print("\n" + "-"*80)
        print("PROCESSING GITHUB REPOS")
        print("-"*80)
        
        repos = list(self.db.github_collection.find())
        print(f"found {len(repos)} repos in mongodb")
        
        if not repos:
            print("no repos to process")
            return 0
        
        points = []
        for idx, repo in enumerate(repos, 1):
            # Combine relevant text fields
            combined_text = self.embedder.combine_fields({
                "owner": repo.get("owner", ""),
                "name": repo.get("name", ""),
                "description": repo.get("description", ""),
                "readme": repo.get("readme_text", "")[:500],  # Limit readme length
                "topics": " ".join(repo.get("topics", []))
            }, weights={
                "owner": 0.5,
                "name": 1.5,
                "description": 2,
                "readme": 1,
                "topics": 1
            })
            
            # Generate embedding
            embedding = self.embedder.embed_text(combined_text)
            
            # Prepare payload (metadata)
            payload = {
                "source": "github",
                "owner": repo.get("owner", ""),
                "name": repo.get("name", ""),
                "full_name": repo.get("full_name", ""),
                "title": repo.get("full_name", ""),
                "description": repo.get("description", ""),
                "language": repo.get("language", ""),
                "topics": json.dumps(repo.get("topics", [])),
                "stars_total": repo.get("stars_total", 0),
                "stars_trending": str(repo.get("stars_trending", "0")).rstrip("+"),
                "repo_url": repo.get("repo_url", ""),
                "created_at": repo.get("created_at", ""),
                "updated_at": repo.get("updated_at", ""),
                "scraped_at": repo.get("scraped_at", "").isoformat() if repo.get("scraped_at") else ""
            }
            
            # Use MongoDB ObjectId as Qdrant point ID (convert to int)
            point_id = hash(str(repo["_id"])) % (2**31)
            
            points.append((point_id, embedding, payload))
            
            if idx % 5 == 0:
                print(f"  processed {idx}/{len(repos)} repos...")
        
        # Batch insert to Qdrant
        added = self.qdrant_github.add_points_batch(points)
        print(f"✓ added {added} embeddings to qdrant")
        
        self.processed_count["github"] = added
        return added
    
    def embed_arxiv_papers(self) -> int:
        """
        Process arXiv papers from MongoDB and store embeddings.
        
        Returns:
            Number of papers processed
        """
        print("\n" + "-"*80)
        print("PROCESSING ARXIV PAPERS")
        print("-"*80)
        
        papers = list(self.db.arxiv_collection.find())
        print(f"found {len(papers)} papers in mongodb")
        
        if not papers:
            print("no papers to process")
            return 0
        
        points = []
        for idx, paper in enumerate(papers, 1):
            # Combine relevant text fields
            combined_text = self.embedder.combine_fields({
                "title": paper.get("title", ""),
                "abstract": paper.get("abstract", ""),
                "categories": " ".join(paper.get("categories", []))
            }, weights={
                "title": 2,
                "abstract": 2,
                "categories": 0.5
            })
            
            # Generate embedding
            embedding = self.embedder.embed_text(combined_text)
            
            # Prepare payload
            payload = {
                "source": "arxiv",
                "arxiv_id": paper.get("arxiv_id", ""),
                "title": paper.get("title", ""),
                "abstract": paper.get("abstract", ""),
                "authors": json.dumps(paper.get("authors", [])),
                "categories": json.dumps(paper.get("categories", [])),
                "published": paper.get("published", ""),
                "pdf_url": paper.get("pdf_url", ""),
                "arxiv_url": paper.get("arxiv_url", ""),
                "scraped_at": paper.get("scraped_at", "").isoformat() if paper.get("scraped_at") else ""
            }
            
            point_id = hash(str(paper["_id"])) % (2**31)
            points.append((point_id, embedding, payload))
            
            if idx % 5 == 0:
                print(f"  processed {idx}/{len(papers)} papers...")
        
        # Batch insert to Qdrant
        added = self.qdrant_arxiv.add_points_batch(points)
        print(f"✓ added {added} embeddings to qdrant")
        
        self.processed_count["arxiv"] = added
        return added
    
    def embed_tech_news(self) -> int:
        """
        Process tech news from MongoDB and store embeddings.
        
        Returns:
            Number of news items processed
        """
        print("\n" + "-"*80)
        print("PROCESSING TECH NEWS")
        print("-"*80)
        
        news_items = list(self.db.news_collection.find())
        print(f"found {len(news_items)} news items in mongodb")
        
        if not news_items:
            print("no news to process")
            return 0
        
        points = []
        for idx, news in enumerate(news_items, 1):
            # Combine relevant text fields
            combined_text = self.embedder.combine_fields({
                "title": news.get("title", ""),
                "url": news.get("url", ""),
                "author": news.get("author", "")
            }, weights={
                "title": 3,
                "url": 0.5,
                "author": 0.5
            })
            
            # Generate embedding
            embedding = self.embedder.embed_text(combined_text)
            
            # Prepare payload
            payload = {
                "source": "news",
                "hackernews_id": news.get("hackernews_id", 0),
                "title": news.get("title", ""),
                "url": news.get("url", ""),
                "score": news.get("score", 0),
                "comments": news.get("comments", 0),
                "author": news.get("author", ""),
                "published_at": news.get("published_at", ""),
                "story_type": news.get("story_type", ""),
                "scraped_at": news.get("scraped_at", "").isoformat() if news.get("scraped_at") else ""
            }
            
            point_id = hash(str(news["_id"])) % (2**31)
            points.append((point_id, embedding, payload))
            
            if idx % 5 == 0:
                print(f"  processed {idx}/{len(news_items)} news items...")
        
        # Batch insert to Qdrant
        added = self.qdrant_news.add_points_batch(points)
        print(f"✓ added {added} embeddings to qdrant")
        
        self.processed_count["news"] = added
        return added
    
    def process_all(self) -> dict:
        """
        Process all data sources (GitHub, arXiv, Tech News).
        
        Returns:
            Dictionary with processing statistics
        """
        print("\n" + "="*80)
        print("STARTING FULL EMBEDDING PIPELINE")
        print("="*80)
        
        start_time = datetime.now()
        
        self.embed_github_repos()
        self.embed_arxiv_papers()
        self.embed_tech_news()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Print final statistics
        self._print_statistics(duration)
        
        return self.processed_count
    
    def _print_statistics(self, duration: float):
        """Print processing statistics."""
        print("\n" + "="*80)
        print("EMBEDDING PIPELINE COMPLETED")
        print("="*80)
        
        print("\n📊 STATISTICS:")
        print(f"\nprocessed documents:")
        print(f"  github repos:    {self.processed_count['github']} ✓")
        print(f"  arxiv papers:    {self.processed_count['arxiv']} ✓")
        print(f"  tech news:       {self.processed_count['news']} ✓")
        print(f"  total:           {sum(self.processed_count.values())} ✓")
        
        print(f"\n⏱️  processing time: {duration:.2f} seconds")
        print(f"   average: {duration / max(sum(self.processed_count.values()), 1):.3f}s per document")
        
        print("\n📦 QDRANT COLLECTIONS:")
        github_stats = self.qdrant_github.get_collection_stats()
        arxiv_stats = self.qdrant_arxiv.get_collection_stats()
        news_stats = self.qdrant_news.get_collection_stats()
        
        if github_stats:
            print(f"  github_embeddings: {github_stats['points_count']} points")
        if arxiv_stats:
            print(f"  arxiv_embeddings:  {arxiv_stats['points_count']} points")
        if news_stats:
            print(f"  news_embeddings:   {news_stats['points_count']} points")
        
        print("\n" + "="*80)
        print("embeddings ready for semantic search and hybrid queries!")
        print("="*80 + "\n")


if __name__ == "__main__":
    pipeline = EmbeddingPipeline()
    stats = pipeline.process_all()
