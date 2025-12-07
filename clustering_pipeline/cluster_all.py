"""
Clustering & Topic Modeling Pipeline
Combines embeddings with clustering algorithms to identify topics and trends
"""

import sys
import json
import numpy as np
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from clustering_handler import ClusteringHandler
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import pymongo
from pymongo import MongoClient

class ClusteringPipeline:
    def __init__(self):
        print("="*80)
        print("CLUSTERING & TOPIC MODELING PIPELINE")
        print("="*80)
        
        # MongoDB connection
        self.mongo_client = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo_client['gen_eezes']
        
        # Qdrant connection
        qdrant_path = Path(__file__).parent.parent / "qdrant_storage"
        self.qdrant = QdrantClient(path=str(qdrant_path))
        
        # Clustering handler
        self.clustering_handler = ClusteringHandler()
        
        self.results = {}
        
    def load_embeddings_from_qdrant(self, collection_name: str):
        """Load all embeddings and metadata from Qdrant collection"""
        print(f"\n1. Loading embeddings from Qdrant collection: {collection_name}")
        print("-" * 80)
        
        collection_info = self.qdrant.get_collection(collection_name)
        n_points = collection_info.points_count
        print(f"  Found {n_points} items in {collection_name}")
        
        embeddings_list = []
        items = []
        
        # Scroll through all points
        offset = 0
        batch_size = 100
        
        while True:
            points, next_offset = self.qdrant.scroll(
                collection_name=collection_name,
                limit=batch_size,
                offset=offset,
                with_vectors=True,
                with_payload=True
            )
            
            for point in points:
                embeddings_list.append(point.vector)
                items.append({
                    'id': point.id,
                    'payload': point.payload
                })
            
            if next_offset is None or next_offset == 0:
                break
            offset = next_offset
        
        embeddings = np.array(embeddings_list)
        print(f"  ✓ Loaded {len(embeddings)} embeddings with shape {embeddings.shape}")
        
        return embeddings, items
    
    def cluster_collection(self, collection_name: str, source_type: str):
        """Cluster a single collection and store results"""
        print(f"\n\n{'='*80}")
        print(f"CLUSTERING: {collection_name}")
        print(f"{'='*80}")
        
        # Load embeddings
        embeddings, items = self.load_embeddings_from_qdrant(collection_name)
        
        if len(embeddings) < 3:
            print(f"  ⚠ Not enough items to cluster ({len(embeddings)} < 3)")
            return
        
        # Extract text for keyword extraction
        texts = []
        for item in items:
            payload = item['payload']
            if source_type == 'github':
                text = payload.get('readme_text', '') + ' ' + payload.get('description', '')
            elif source_type == 'arxiv':
                text = payload.get('title', '') + ' ' + payload.get('abstract', '')
            else:  # tech_news
                text = payload.get('title', '') + ' ' + payload.get('url', '')
            texts.append(text)
        
        cluster_results = {
            'collection': collection_name,
            'source_type': source_type,
            'n_items': len(embeddings),
            'timestamp': datetime.now().isoformat(),
            'algorithms': {}
        }
        
        # Determine optimal n_clusters for K-means
        n_clusters = max(2, min(5, len(embeddings) // 3))
        
        # K-means clustering
        print(f"\n2. K-Means Clustering")
        print("-" * 80)
        kmeans_labels = self.clustering_handler.kmeans_clustering(embeddings, n_clusters=n_clusters)
        kmeans_keywords = self.clustering_handler.extract_keywords(texts, kmeans_labels)
        kmeans_samples = self.clustering_handler.get_representative_samples(items, kmeans_labels, embeddings)
        kmeans_stats = self.clustering_handler.compute_cluster_stats(kmeans_labels, embeddings)
        
        cluster_results['algorithms']['kmeans'] = {
            'n_clusters': n_clusters,
            'clusters': {}
        }
        
        for cluster_id in sorted(kmeans_stats.keys()):
            cluster_results['algorithms']['kmeans']['clusters'][str(cluster_id)] = {
                'size': int(kmeans_stats[cluster_id]['size']),
                'keywords': kmeans_keywords.get(cluster_id, []),
                'representative_samples': [
                    {
                        'source_id': s['payload'].get(self._get_id_field(source_type)),
                        'title': self._get_title(s['payload'], source_type),
                        'source': source_type
                    }
                    for s in kmeans_samples.get(cluster_id, [])
                ]
            }
        
        # DBSCAN clustering
        print(f"\n3. DBSCAN Clustering")
        print("-" * 80)
        dbscan_labels = self.clustering_handler.dbscan_clustering(embeddings, eps=0.5, min_samples=3)
        dbscan_keywords = self.clustering_handler.extract_keywords(texts, dbscan_labels)
        dbscan_samples = self.clustering_handler.get_representative_samples(items, dbscan_labels, embeddings)
        dbscan_stats = self.clustering_handler.compute_cluster_stats(dbscan_labels, embeddings)
        
        cluster_results['algorithms']['dbscan'] = {
            'clusters': {}
        }
        
        for cluster_id in sorted(dbscan_stats.keys()):
            cluster_results['algorithms']['dbscan']['clusters'][str(cluster_id)] = {
                'size': int(dbscan_stats[cluster_id]['size']),
                'keywords': dbscan_keywords.get(cluster_id, []),
                'representative_samples': [
                    {
                        'source_id': s['payload'].get(self._get_id_field(source_type)),
                        'title': self._get_title(s['payload'], source_type),
                        'source': source_type
                    }
                    for s in dbscan_samples.get(cluster_id, [])
                ]
            }
        
        # HDBSCAN clustering
        print(f"\n4. HDBSCAN Clustering")
        print("-" * 80)
        hdbscan_labels = self.clustering_handler.hdbscan_clustering(embeddings, min_cluster_size=max(3, len(embeddings)//5))
        hdbscan_keywords = self.clustering_handler.extract_keywords(texts, hdbscan_labels)
        hdbscan_samples = self.clustering_handler.get_representative_samples(items, hdbscan_labels, embeddings)
        hdbscan_stats = self.clustering_handler.compute_cluster_stats(hdbscan_labels, embeddings)
        
        cluster_results['algorithms']['hdbscan'] = {
            'clusters': {}
        }
        
        for cluster_id in sorted(hdbscan_stats.keys()):
            cluster_results['algorithms']['hdbscan']['clusters'][str(cluster_id)] = {
                'size': int(hdbscan_stats[cluster_id]['size']),
                'keywords': hdbscan_keywords.get(cluster_id, []),
                'representative_samples': [
                    {
                        'source_id': s['payload'].get(self._get_id_field(source_type)),
                        'title': self._get_title(s['payload'], source_type),
                        'source': source_type
                    }
                    for s in hdbscan_samples.get(cluster_id, [])
                ]
            }
        
        # Store in MongoDB
        print(f"\n5. Storing Results to MongoDB")
        print("-" * 80)
        self._store_clusters_to_mongodb(collection_name, source_type, cluster_results,
                                       kmeans_labels, dbscan_labels, hdbscan_labels, items)
        
        print(f"  ✓ Stored clustering results for {collection_name}")
        
        self.results[collection_name] = cluster_results
        
        return cluster_results
    
    def _get_id_field(self, source_type: str) -> str:
        """Get the ID field name for each source type"""
        if source_type == 'github':
            return 'full_name'
        elif source_type == 'arxiv':
            return 'arxiv_id'
        else:
            return 'hackernews_id'
    
    def _get_title(self, payload: dict, source_type: str) -> str:
        """Extract title from payload"""
        if source_type == 'github':
            return payload.get('full_name', 'Unknown')
        elif source_type == 'arxiv':
            return payload.get('title', 'Unknown')
        else:
            return payload.get('title', 'Unknown')
    
    def _store_clusters_to_mongodb(self, collection_name: str, source_type: str, 
                                  cluster_results: dict, kmeans_labels: np.ndarray,
                                  dbscan_labels: np.ndarray, hdbscan_labels: np.ndarray,
                                  items: list):
        """Store clustering results to MongoDB"""
        mongo_collection = self.db['clusters']
        
        # Convert numpy types to Python native types
        def convert_numpy_types(obj):
            """Recursively convert numpy types to Python native types"""
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            else:
                return obj
        
        # Convert cluster results
        cluster_results = convert_numpy_types(cluster_results)
        
        # Create document with clustering results
        cluster_doc = {
            'collection_name': collection_name,
            'source_type': source_type,
            'timestamp': datetime.now(),
            'n_items': len(items),
            'kmeans_summary': cluster_results['algorithms'].get('kmeans', {}),
            'dbscan_summary': cluster_results['algorithms'].get('dbscan', {}),
            'hdbscan_summary': cluster_results['algorithms'].get('hdbscan', {}),
        }
        
        result = mongo_collection.insert_one(cluster_doc)
        print(f"    Stored document ID: {result.inserted_id}")
    
    def run(self):
        """Run the complete clustering pipeline"""
        try:
            # Cluster each collection
            self.cluster_collection('github_embeddings', 'github')
            self.cluster_collection('arxiv_embeddings', 'arxiv')
            self.cluster_collection('news_embeddings', 'tech_news')
            
            # Summary
            print(f"\n\n{'='*80}")
            print("CLUSTERING PIPELINE COMPLETED")
            print(f"{'='*80}")
            
            print("\n📊 SUMMARY:")
            for collection, results in self.results.items():
                print(f"\n  {collection}:")
                print(f"    Items: {results['n_items']}")
                if 'kmeans' in results['algorithms']:
                    print(f"    K-Means clusters: {len(results['algorithms']['kmeans']['clusters'])}")
                if 'dbscan' in results['algorithms']:
                    print(f"    DBSCAN clusters: {len(results['algorithms']['dbscan']['clusters'])}")
                if 'hdbscan' in results['algorithms']:
                    print(f"    HDBSCAN clusters: {len(results['algorithms']['hdbscan']['clusters'])}")
            
            print(f"\n✅ All clusters stored in MongoDB")
            print(f"{'='*80}")
            
        except Exception as e:
            print(f"❌ Error in clustering pipeline: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    pipeline = ClusteringPipeline()
    pipeline.run()
