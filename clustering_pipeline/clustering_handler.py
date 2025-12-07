"""
Clustering Handler Module
Performs K-means, DBSCAN, and HDBSCAN clustering on embeddings
Extracts keywords and representative samples per cluster
"""

import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import hdbscan
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class ClusteringHandler:
    """Handles clustering of embeddings using multiple algorithms"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        
    def kmeans_clustering(self, embeddings: np.ndarray, n_clusters: int = 5) -> np.ndarray:
        """
        Perform K-means clustering
        
        Args:
            embeddings: Array of shape (n_samples, embedding_dim)
            n_clusters: Number of clusters
            
        Returns:
            Cluster labels for each embedding
        """
        print(f"  Running K-means clustering with k={n_clusters}...")
        embeddings_scaled = self.scaler.fit_transform(embeddings)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings_scaled)
        print(f"    ✓ K-means completed: {len(np.unique(labels))} clusters found")
        return labels
    
    def dbscan_clustering(self, embeddings: np.ndarray, eps: float = 0.5, 
                         min_samples: int = 3) -> np.ndarray:
        """
        Perform DBSCAN clustering
        
        Args:
            embeddings: Array of shape (n_samples, embedding_dim)
            eps: Maximum distance between samples
            min_samples: Minimum number of samples in a neighborhood
            
        Returns:
            Cluster labels for each embedding (-1 for noise points)
        """
        print(f"  Running DBSCAN clustering (eps={eps}, min_samples={min_samples})...")
        embeddings_scaled = self.scaler.fit_transform(embeddings)
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(embeddings_scaled)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)
        print(f"    ✓ DBSCAN completed: {n_clusters} clusters, {n_noise} noise points")
        return labels
    
    def hdbscan_clustering(self, embeddings: np.ndarray, min_cluster_size: int = 5) -> np.ndarray:
        """
        Perform HDBSCAN clustering
        
        Args:
            embeddings: Array of shape (n_samples, embedding_dim)
            min_cluster_size: Minimum number of samples in a cluster
            
        Returns:
            Cluster labels for each embedding (-1 for noise points)
        """
        print(f"  Running HDBSCAN clustering (min_cluster_size={min_cluster_size})...")
        embeddings_scaled = self.scaler.fit_transform(embeddings)
        clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, gen_min_span_tree=True)
        labels = clusterer.fit_predict(embeddings_scaled)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)
        print(f"    ✓ HDBSCAN completed: {n_clusters} clusters, {n_noise} noise points")
        return labels
    
    def extract_keywords(self, texts: List[str], cluster_labels: np.ndarray, 
                        n_keywords: int = 5) -> Dict[int, List[str]]:
        """
        Extract top keywords for each cluster using TF-IDF
        
        Args:
            texts: List of documents/text snippets
            cluster_labels: Cluster assignment for each text
            n_keywords: Number of top keywords to extract per cluster
            
        Returns:
            Dictionary mapping cluster_id to list of keywords
        """
        print(f"  Extracting keywords from clusters...")
        cluster_keywords = {}
        unique_clusters = set(cluster_labels)
        
        for cluster_id in sorted(unique_clusters):
            if cluster_id == -1:  # Skip noise cluster
                continue
            
            # Get texts in this cluster
            cluster_mask = cluster_labels == cluster_id
            cluster_texts = [texts[i] for i in range(len(texts)) if cluster_mask[i]]
            
            if len(cluster_texts) < 2:
                cluster_keywords[cluster_id] = []
                continue
            
            # TF-IDF vectorization
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english', 
                                        ngram_range=(1, 2), max_df=0.9, min_df=1)
            try:
                tfidf_matrix = vectorizer.fit_transform(cluster_texts)
                feature_names = vectorizer.get_feature_names_out()
                
                # Get mean TF-IDF scores
                mean_tfidf = np.array(tfidf_matrix.mean(axis=0)).flatten()
                top_indices = mean_tfidf.argsort()[-n_keywords:][::-1]
                keywords = [feature_names[i] for i in top_indices if mean_tfidf[i] > 0]
                cluster_keywords[cluster_id] = keywords
            except:
                cluster_keywords[cluster_id] = []
        
        print(f"    ✓ Keywords extracted for {len(cluster_keywords)} clusters")
        return cluster_keywords
    
    def get_representative_samples(self, items: List[Dict], cluster_labels: np.ndarray,
                                  embeddings: np.ndarray, n_samples: int = 3) -> Dict[int, List[Dict]]:
        """
        Get representative samples from each cluster (closest to centroid)
        
        Args:
            items: List of items (dicts with metadata)
            cluster_labels: Cluster assignment for each item
            embeddings: Embedding vectors
            n_samples: Number of representative samples per cluster
            
        Returns:
            Dictionary mapping cluster_id to list of representative items
        """
        print(f"  Selecting representative samples...")
        representative_samples = {}
        unique_clusters = set(cluster_labels)
        
        embeddings_scaled = self.scaler.fit_transform(embeddings)
        
        for cluster_id in sorted(unique_clusters):
            if cluster_id == -1:  # Skip noise cluster
                continue
            
            cluster_mask = cluster_labels == cluster_id
            cluster_indices = np.where(cluster_mask)[0]
            
            if len(cluster_indices) == 0:
                representative_samples[cluster_id] = []
                continue
            
            # Calculate centroid
            cluster_embeddings = embeddings_scaled[cluster_indices]
            centroid = cluster_embeddings.mean(axis=0)
            
            # Find closest points to centroid
            distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
            closest_indices = np.argsort(distances)[:min(n_samples, len(cluster_indices))]
            
            # Get items
            samples = [items[cluster_indices[i]] for i in closest_indices]
            representative_samples[cluster_id] = samples
        
        print(f"    ✓ Selected representative samples for {len(representative_samples)} clusters")
        return representative_samples
    
    def compute_cluster_stats(self, cluster_labels: np.ndarray, 
                             embeddings: np.ndarray) -> Dict[int, Dict]:
        """
        Compute statistics for each cluster
        
        Args:
            cluster_labels: Cluster assignment for each item
            embeddings: Embedding vectors
            
        Returns:
            Dictionary mapping cluster_id to stats (size, centroid, silhouette_score)
        """
        print(f"  Computing cluster statistics...")
        cluster_stats = {}
        unique_clusters = set(cluster_labels)
        
        embeddings_scaled = self.scaler.fit_transform(embeddings)
        
        for cluster_id in sorted(unique_clusters):
            if cluster_id == -1:  # Skip noise cluster
                continue
            
            cluster_mask = cluster_labels == cluster_id
            cluster_embeddings = embeddings_scaled[cluster_mask]
            
            stats = {
                'size': np.sum(cluster_mask),
                'centroid': cluster_embeddings.mean(axis=0).tolist(),
                'std_dev': float(np.std(cluster_embeddings))
            }
            cluster_stats[cluster_id] = stats
        
        print(f"    ✓ Statistics computed for {len(cluster_stats)} clusters")
        return cluster_stats
