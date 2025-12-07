"""
Clustering Verification Script
Verifies that clusters were created correctly and displays sample results
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pymongo import MongoClient


def verify_clusters():
    """Verify clustering results in MongoDB"""
    print("="*80)
    print("CLUSTERING VERIFICATION")
    print("="*80)
    
    # Connect to MongoDB
    mongo_client = MongoClient('mongodb://localhost:27017/')
    db = mongo_client['gen_eezes']
    clusters_collection = db['clusters']
    
    # Get all cluster documents
    cluster_docs = list(clusters_collection.find().sort('_id', -1).limit(3))
    
    if not cluster_docs:
        print("\nNo clustering results found in MongoDB")
        return
    
    print(f"\nFound {len(cluster_docs)} clustering results\n")
    
    for doc in cluster_docs:
        print("-" * 80)
        print(f"Collection: {doc['collection_name']}")
        print(f"Source Type: {doc['source_type']}")
        print(f"Number of Items: {doc['n_items']}")
        print(f"Timestamp: {doc['timestamp']}")
        
        if 'kmeans_summary' in doc and doc['kmeans_summary']:
            kmeans = doc['kmeans_summary']
            print(f"\nK-Means Clustering:")
            print(f"  Number of Clusters: {kmeans.get('n_clusters', 'N/A')}")
            if 'clusters' in kmeans:
                for cluster_id, cluster_info in list(kmeans['clusters'].items())[:2]:
                    print(f"\n  Cluster {cluster_id}:")
                    print(f"    Size: {cluster_info.get('size', 'N/A')}")
                    print(f"    Keywords: {', '.join(cluster_info.get('keywords', [])[:3])}")
                    print(f"    Sample Items:")
                    for sample in cluster_info.get('representative_samples', [])[:2]:
                        print(f"      - {sample.get('title', 'Unknown')}")
        
        print()
    
    print("="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    verify_clusters()
