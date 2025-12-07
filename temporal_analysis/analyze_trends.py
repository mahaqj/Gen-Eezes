"""
Temporal Analysis Pipeline (Module 4)
Analyzes trends, keyword shifts, and cluster drift over time
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from temporal_analysis_handler import TemporalAnalysisHandler
from historical_data_generator import HistoricalDataGenerator
from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Dict


class TemporalAnalysisPipeline:
    """Main pipeline for temporal trend analysis"""
    
    def __init__(self):
        print("="*80)
        print("TEMPORAL ANALYSIS PIPELINE - MODULE 4")
        print("Trend Detection & Keyword Shift Analysis")
        print("="*80)
        
        # MongoDB connection
        self.mongo_client = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo_client['gen_eezes']
        
        # Initialize handlers
        self.temporal_handler = TemporalAnalysisHandler()
        self.data_generator = HistoricalDataGenerator(weeks=8)
        
    def run(self):
        """Execute the complete temporal analysis pipeline"""
        try:
            # Step 1: Generate historical snapshots (8 weeks of data)
            print("\n1. GENERATING HISTORICAL DATA SNAPSHOTS")
            print("-" * 80)
            self._generate_and_save_snapshots()
            
            # Step 2: Load snapshot data
            print("\n2. LOADING TEMPORAL DATA")
            print("-" * 80)
            snapshots_data = self.data_generator.get_all_snapshots()
            
            # Step 3: Analyze keyword frequency shifts
            print("\n3. ANALYZING KEYWORD SHIFTS")
            print("-" * 80)
            keyword_shifts = self.temporal_handler.analyze_keyword_shifts(
                snapshots_data['keywords']
            )
            
            # Step 4: Detect cluster drift
            print("\n4. DETECTING CLUSTER DRIFT")
            print("-" * 80)
            cluster_drifts = self.temporal_handler.detect_cluster_drift(
                snapshots_data['clusters']
            )
            
            # Step 5: Model time series for each metric
            print("\n5. MODELING TIME SERIES TRENDS")
            print("-" * 80)
            trend_models = self._build_time_series_models(snapshots_data)
            
            # Step 6: Label trends
            print("\n6. LABELING TRENDS")
            print("-" * 80)
            trend_labels = self.temporal_handler.label_trends(trend_models)
            
            # Step 7: Generate comprehensive report
            print("\n7. GENERATING TREND REPORT")
            print("-" * 80)
            report = self.temporal_handler.generate_trend_report(
                keyword_shifts,
                cluster_drifts,
                trend_labels
            )
            
            # Step 8: Store results in MongoDB
            print("\n8. STORING RESULTS TO MONGODB")
            print("-" * 80)
            self._store_analysis_results(keyword_shifts, cluster_drifts, trend_labels, report)
            
            # Display report
            print(report)
            
            print("\n✅ TEMPORAL ANALYSIS COMPLETED SUCCESSFULLY!")
            print("="*80)
            
        except Exception as e:
            print(f"\n❌ Error in temporal analysis: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _generate_and_save_snapshots(self):
        """Generate and save historical snapshots to MongoDB"""
        print("  Generating 8 weeks of historical snapshots...")
        self.data_generator.save_snapshots_to_mongodb(self.mongo_client)
        print("  ✓ Snapshots generated and saved")
    
    def _build_time_series_models(self, snapshots_data) -> Dict:
        """
        Build time series models for keywords and clusters
        
        Args:
            snapshots_data: Dictionary with keywords and clusters timeline
            
        Returns:
            Dictionary with time series models
        """
        trend_models = {}
        
        # Model keyword trends
        print("  Modeling keyword time series...")
        for keyword, timeline in snapshots_data['keywords'].items():
            model = self.temporal_handler.model_time_series(timeline)
            trend_models[f"keyword_{keyword}"] = model
        
        # Model cluster size trends
        print("  Modeling cluster size trends...")
        for cluster_id, timeline in snapshots_data['clusters'].items():
            # Extract size timeline
            size_timeline = [(cluster['date'], cluster['size']) for cluster in timeline]
            model = self.temporal_handler.model_time_series(size_timeline)
            trend_models[f"cluster_size_{cluster_id}"] = model
        
        print(f"  ✓ Built {len(trend_models)} time series models")
        return trend_models
    
    def _store_analysis_results(self, keyword_shifts, cluster_drifts, trend_labels, report):
        """Store all analysis results to MongoDB"""
        analysis_collection = self.db['temporal_analysis']
        
        # Prepare document for storage
        analysis_doc = {
            'timestamp': datetime.now(),
            'analysis_type': 'weekly_temporal_analysis',
            'keyword_shifts_summary': {
                keyword: {
                    'trend': data['trend'],
                    'change': data['change'],
                    'percent_change': data['percent_change'],
                }
                for keyword, data in keyword_shifts.items()
            },
            'cluster_drifts_summary': {
                cluster_id: {
                    'size_change': drift['size_change'],
                    'size_percent_change': drift['size_percent_change'],
                    'drift_severity': drift['drift_severity'],
                }
                for cluster_id, drift in cluster_drifts.items()
            },
            'trend_labels': trend_labels,
            'report': report,
            'key_insights': self._extract_key_insights(keyword_shifts, cluster_drifts, trend_labels)
        }
        
        result = analysis_collection.insert_one(analysis_doc)
        print(f"  ✓ Stored analysis document: {result.inserted_id}")
    
    def _extract_key_insights(self, keyword_shifts, cluster_drifts, trend_labels) -> Dict:
        """Extract key insights from analysis"""
        insights = {
            'rising_topics': [
                k for k, v in keyword_shifts.items() if v['trend'] == 'RISING'
            ][:5],
            'falling_topics': [
                k for k, v in keyword_shifts.items() if v['trend'] == 'FALLING'
            ][:5],
            'hottest_cluster': max(
                cluster_drifts.items(),
                key=lambda x: x[1]['size_percent_change']
            )[0] if cluster_drifts else None,
            'most_stable_cluster': min(
                cluster_drifts.items(),
                key=lambda x: x[1]['drift_magnitude']
            )[0] if cluster_drifts else None,
        }
        return insights


if __name__ == "__main__":
    pipeline = TemporalAnalysisPipeline()
    pipeline.run()
