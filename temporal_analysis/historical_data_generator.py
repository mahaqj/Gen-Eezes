"""
Historical Data Generator
Creates 8 weeks of simulated snapshot data for temporal analysis demonstration
Simulates realistic trends over time (rising, falling, stable topics)
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List
import random


class HistoricalDataGenerator:
    """Generates realistic historical cluster and keyword data"""
    
    def __init__(self, weeks: int = 8):
        """
        Initialize data generator
        
        Args:
            weeks: Number of weeks of historical data to generate
        """
        self.weeks = weeks
        self.start_date = datetime.now() - timedelta(weeks=weeks)
        
    def generate_keyword_timeline(self) -> Dict[str, List]:
        """
        Generate keyword frequency timeline for 8 weeks
        
        Simulates:
        - LLM/AI keywords RISING (growing interest)
        - Frontend/React keywords STABLE (consistent)
        - DevOps keywords FALLING (declining interest)
        """
        print("📅 Generating keyword timeline (8 weeks)...")
        
        timeline = {}
        
        # RISING TREND: LLM/AI keywords
        rising_keywords = [
            ('llm', [2, 3, 5, 7, 10, 14, 18, 22]),
            ('agents', [0, 0, 1, 2, 4, 7, 11, 15]),
            ('rag', [0, 0, 0, 1, 2, 4, 7, 11]),
            ('transformer', [1, 2, 3, 4, 5, 6, 7, 8]),
            ('prompt_engineering', [0, 1, 2, 3, 5, 8, 12, 16]),
        ]
        
        # STABLE TREND: Frontend keywords
        stable_keywords = [
            ('react', [8, 8, 9, 8, 8, 9, 8, 8]),
            ('javascript', [7, 8, 7, 8, 7, 8, 7, 8]),
            ('frontend', [5, 5, 6, 5, 5, 6, 5, 5]),
            ('typescript', [4, 4, 5, 4, 4, 5, 4, 4]),
            ('web_development', [6, 6, 6, 6, 6, 6, 6, 6]),
        ]
        
        # FALLING TREND: DevOps/Infrastructure keywords
        falling_keywords = [
            ('kubernetes', [12, 11, 10, 9, 7, 5, 4, 2]),
            ('docker', [10, 10, 9, 8, 6, 5, 3, 2]),
            ('devops', [8, 8, 7, 6, 5, 3, 2, 1]),
            ('ci_cd', [6, 6, 5, 4, 3, 2, 1, 0]),
            ('infrastructure', [5, 5, 4, 3, 2, 1, 1, 0]),
        ]
        
        # EMERGING TREND: New keywords appearing
        emerging_keywords = [
            ('qlora', [0, 0, 0, 1, 1, 2, 3, 4]),
            ('vector_db', [0, 0, 0, 0, 1, 2, 3, 4]),
            ('embeddings', [1, 1, 2, 2, 3, 4, 5, 6]),
        ]
        
        # Add all keyword timelines
        for keyword, frequencies in rising_keywords + stable_keywords + falling_keywords + emerging_keywords:
            timeline[keyword] = [
                (self.start_date + timedelta(weeks=i), freq)
                for i, freq in enumerate(frequencies)
            ]
        
        print(f"  ✓ Generated timeline for {len(timeline)} keywords")
        return timeline
    
    def generate_cluster_timeline(self) -> Dict[str, List]:
        """
        Generate cluster evolution timeline for 8 weeks
        
        Simulates three clusters:
        - AI/LLM cluster: GROWING rapidly
        - Frontend cluster: STABLE size
        - DevOps cluster: SHRINKING
        """
        print("📅 Generating cluster timeline (8 weeks)...")
        
        timeline = {}
        
        # AI/LLM Cluster - GROWING (starts 5, grows to 15)
        ai_cluster_sizes = [5, 6, 8, 10, 12, 14, 16, 18]
        ai_cluster_cohesion = [0.6, 0.65, 0.7, 0.68, 0.65, 0.62, 0.6, 0.58]  # Getting looser as it grows
        
        timeline['ai_llm'] = [
            {
                'date': self.start_date + timedelta(weeks=i),
                'size': size,
                'std_dev': 1 / cohesion,  # Convert cohesion to std_dev
                'keywords': self._get_cluster_keywords('ai_llm', week=i),
                'centroid_shift': random.uniform(-0.1, 0.1)
            }
            for i, (size, cohesion) in enumerate(zip(ai_cluster_sizes, ai_cluster_cohesion))
        ]
        
        # Frontend Cluster - STABLE (stays around 8)
        frontend_cluster_sizes = [8, 8, 9, 8, 8, 9, 8, 8]
        frontend_cluster_cohesion = [0.8, 0.8, 0.78, 0.8, 0.8, 0.78, 0.8, 0.8]  # Very stable
        
        timeline['frontend'] = [
            {
                'date': self.start_date + timedelta(weeks=i),
                'size': size,
                'std_dev': 1 / cohesion,
                'keywords': self._get_cluster_keywords('frontend', week=i),
                'centroid_shift': random.uniform(-0.05, 0.05)
            }
            for i, (size, cohesion) in enumerate(zip(frontend_cluster_sizes, frontend_cluster_cohesion))
        ]
        
        # DevOps Cluster - SHRINKING (starts 12, shrinks to 2)
        devops_cluster_sizes = [12, 11, 10, 8, 6, 4, 3, 2]
        devops_cluster_cohesion = [0.7, 0.68, 0.65, 0.62, 0.6, 0.5, 0.4, 0.3]  # Gets much looser
        
        timeline['devops'] = [
            {
                'date': self.start_date + timedelta(weeks=i),
                'size': size,
                'std_dev': 1 / cohesion,
                'keywords': self._get_cluster_keywords('devops', week=i),
                'centroid_shift': random.uniform(-0.15, 0.15)
            }
            for i, (size, cohesion) in enumerate(zip(devops_cluster_sizes, devops_cluster_cohesion))
        ]
        
        print(f"  ✓ Generated timeline for {len(timeline)} clusters")
        return timeline
    
    def _get_cluster_keywords(self, cluster_type: str, week: int) -> List[str]:
        """Get keywords for a cluster at a specific week"""
        keywords_by_cluster = {
            'ai_llm': {
                0: ['llm', 'transformer'],
                1: ['llm', 'transformer', 'gpt'],
                2: ['llm', 'transformer', 'gpt', 'agents'],
                3: ['llm', 'agents', 'rag', 'prompt_engineering'],
                4: ['agents', 'rag', 'prompt_engineering', 'embeddings'],
                5: ['agents', 'rag', 'embeddings', 'vector_db'],
                6: ['rag', 'embeddings', 'vector_db', 'qlora'],
                7: ['embeddings', 'vector_db', 'qlora', 'fine_tune'],
            },
            'frontend': {
                i: ['react', 'javascript', 'frontend', 'typescript', 'web_development']
                for i in range(8)
            },
            'devops': {
                0: ['kubernetes', 'docker', 'devops', 'ci_cd', 'infrastructure'],
                1: ['kubernetes', 'docker', 'devops', 'ci_cd'],
                2: ['kubernetes', 'docker', 'devops'],
                3: ['docker', 'devops', 'ci_cd'],
                4: ['docker', 'devops'],
                5: ['docker'],
                6: ['docker'],
                7: [],
            }
        }
        
        return keywords_by_cluster.get(cluster_type, {}).get(week, [])
    
    def save_snapshots_to_mongodb(self, mongo_client):
        """
        Save all snapshots to MongoDB for later temporal analysis
        
        Args:
            mongo_client: MongoDB client connection
        """
        print("💾 Saving historical snapshots to MongoDB...")
        
        db = mongo_client['gen_eezes']
        snapshots_collection = db['temporal_snapshots']
        
        # Generate and save all snapshots
        for week in range(self.weeks):
            snapshot_date = self.start_date + timedelta(weeks=week)
            
            # Generate cluster snapshot
            cluster_snapshot = self._generate_cluster_snapshot(week)
            
            # Generate keyword snapshot
            keyword_snapshot = self._generate_keyword_snapshot(week)
            
            # Create combined snapshot document
            snapshot_doc = {
                'timestamp': snapshot_date,
                'week_number': week,
                'clusters': cluster_snapshot,
                'keywords': keyword_snapshot,
                'metadata': {
                    'total_documents': sum(c['size'] for c in cluster_snapshot.values()),
                    'active_clusters': len(cluster_snapshot),
                    'unique_keywords': len(keyword_snapshot)
                }
            }
            
            # Upsert (update or insert)
            snapshots_collection.update_one(
                {'timestamp': snapshot_date},
                {'$set': snapshot_doc},
                upsert=True
            )
        
        print(f"  ✓ Saved {self.weeks} weekly snapshots to MongoDB")
        return snapshots_collection
    
    def _generate_cluster_snapshot(self, week: int) -> Dict:
        """Generate cluster snapshot for a specific week"""
        ai_llm_sizes = [5, 6, 8, 10, 12, 14, 16, 18]
        frontend_sizes = [8, 8, 9, 8, 8, 9, 8, 8]
        devops_sizes = [12, 11, 10, 8, 6, 4, 3, 2]
        
        return {
            'ai_llm': {
                'size': ai_llm_sizes[week],
                'keywords': self._get_cluster_keywords('ai_llm', week),
                'growth_rate': (ai_llm_sizes[week] - ai_llm_sizes[week-1]) / ai_llm_sizes[week-1] * 100 if week > 0 else 0
            },
            'frontend': {
                'size': frontend_sizes[week],
                'keywords': self._get_cluster_keywords('frontend', week),
                'growth_rate': (frontend_sizes[week] - frontend_sizes[week-1]) / frontend_sizes[week-1] * 100 if week > 0 else 0
            },
            'devops': {
                'size': devops_sizes[week],
                'keywords': self._get_cluster_keywords('devops', week),
                'growth_rate': (devops_sizes[week] - devops_sizes[week-1]) / devops_sizes[week-1] * 100 if week > 0 else 0
            }
        }
    
    def _generate_keyword_snapshot(self, week: int) -> Dict:
        """Generate keyword snapshot for a specific week"""
        keyword_data = {
            'llm': [2, 3, 5, 7, 10, 14, 18, 22],
            'agents': [0, 0, 1, 2, 4, 7, 11, 15],
            'rag': [0, 0, 0, 1, 2, 4, 7, 11],
            'react': [8, 8, 9, 8, 8, 9, 8, 8],
            'javascript': [7, 8, 7, 8, 7, 8, 7, 8],
            'kubernetes': [12, 11, 10, 9, 7, 5, 4, 2],
            'docker': [10, 10, 9, 8, 6, 5, 3, 2],
            'embeddings': [1, 1, 2, 2, 3, 4, 5, 6],
        }
        
        return {
            keyword: freq_list[week]
            for keyword, freq_list in keyword_data.items()
        }
    
    def get_all_snapshots(self) -> Dict:
        """
        Get all generated snapshots as a dictionary
        
        Returns:
            Dictionary with keywords and clusters timeline
        """
        return {
            'keywords': self.generate_keyword_timeline(),
            'clusters': self.generate_cluster_timeline(),
            'period': {
                'start': self.start_date,
                'end': self.start_date + timedelta(weeks=self.weeks),
                'weeks': self.weeks
            }
        }
