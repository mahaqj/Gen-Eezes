"""
Real Temporal Analysis Pipeline (Module 4 - Extended)
Analyzes actual trends from 8 weeks of real collected data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from temporal_analysis.temporal_analysis_handler import TemporalAnalysisHandler
from pymongo import MongoClient
from datetime import datetime


class RealTemporalAnalysisPipeline:
    """Pipeline for analyzing real temporal data from collections"""
    
    def __init__(self):
        self.mongo_client = MongoClient('localhost', 27017)
        self.db = self.mongo_client['gen_eezes']
        self.analysis_handler = TemporalAnalysisHandler()
    
    def load_temporal_data(self):
        """Load temporal snapshots from real collections"""
        print("📅 Loading temporal data from collection snapshots...")
        
        snapshots = list(self.db['temporal_snapshots_real'].find().sort('timestamp', 1))
        
        if not snapshots:
            print("⚠ No temporal snapshots found. Run snapshot_aggregator.py first.")
            return None, None
        
        print(f"  ✓ Loaded {len(snapshots)} temporal snapshots")
        
        # Extract data for analysis
        keyword_timeline = {}
        cluster_timeline = {}
        
        for snapshot in snapshots:
            timestamp = snapshot['timestamp']
            
            # Collect keyword frequencies
            for keyword, data in snapshot.get('keyword_evolution', {}).items():
                if keyword not in keyword_timeline:
                    keyword_timeline[keyword] = []
                keyword_timeline[keyword].append({
                    'timestamp': timestamp,
                    'frequency': data.get('frequency', 0)
                })
            
            # Collect cluster information
            for cluster_name, cluster_data in snapshot.get('clusters', {}).items():
                if cluster_name not in cluster_timeline:
                    cluster_timeline[cluster_name] = []
                cluster_timeline[cluster_name].append({
                    'timestamp': timestamp,
                    'size': cluster_data.get('size', 0),
                    'std_dev': cluster_data.get('std_dev', 0)
                })
        
        return keyword_timeline, cluster_timeline
    
    def analyze_real_data(self):
        """Run full analysis on real temporal data"""
        print("\n" + "="*80)
        print("REAL TEMPORAL ANALYSIS PIPELINE - MODULE 4")
        snapshots = list(self.db['temporal_snapshots_real'].find().sort('timestamp', 1))
        weeks_analyzed = len(snapshots)
        print(f"Analysis of {weeks_analyzed} weeks of collected data")
        print("="*80)
        
        # Load data
        keyword_timeline, cluster_timeline = self.load_temporal_data()
        
        if keyword_timeline is None:
            return
        
        print(f"\n📊 Analyzing {len(keyword_timeline)} keywords...")
        print(f"   Tracking {len(cluster_timeline)} clusters...")
        
        # Analyze keyword shifts
        print("\n3️⃣  ANALYZING KEYWORD SHIFTS")
        print("-"*80)
        
        keyword_shifts = {}
        for keyword, timeline in keyword_timeline.items():
            if len(timeline) >= 2:
                first_freq = timeline[0]['frequency']
                last_freq = timeline[-1]['frequency']
                
                if first_freq > 0:
                    percent_change = ((last_freq - first_freq) / first_freq) * 100
                else:
                    percent_change = 100 if last_freq > 0 else 0
                
                keyword_shifts[keyword] = {
                    'start_frequency': first_freq,
                    'end_frequency': last_freq,
                    'percent_change': percent_change,
                    'trend_direction': 'RISING' if percent_change > 5 else ('FALLING' if percent_change < -5 else 'STABLE')
                }
        
        # Display top shifts
        sorted_shifts = sorted(keyword_shifts.items(), key=lambda x: x[1]['percent_change'], reverse=True)
        
        print("\n🔥 TOP RISING KEYWORDS:")
        for keyword, shift in sorted_shifts[:5]:
            if shift['trend_direction'] == 'RISING':
                print(f"  📍 {keyword.upper()}")
                print(f"     Start: {shift['start_frequency']} | End: {shift['end_frequency']} | Change: {shift['percent_change']:+.1f}%")
        
        print("\n❄️  TOP FALLING KEYWORDS:")
        falling = [s for s in sorted_shifts if s[1]['trend_direction'] == 'FALLING']
        for keyword, shift in falling[:5]:
            print(f"  📍 {keyword.upper()}")
            print(f"     Start: {shift['start_frequency']} | End: {shift['end_frequency']} | Change: {shift['percent_change']:+.1f}%")
        
        # Detect cluster drift
        print("\n4️⃣  DETECTING CLUSTER DRIFT")
        print("-"*80)
        
        cluster_stats = {}
        for cluster_name, timeline in cluster_timeline.items():
            if len(timeline) >= 2:
                sizes = [t['size'] for t in timeline]
                std_devs = [t['std_dev'] for t in timeline]
                
                size_change = ((sizes[-1] - sizes[0]) / sizes[0] * 100) if sizes[0] > 0 else 0
                std_dev_change = ((std_devs[-1] - std_devs[0]) / std_devs[0] * 100) if std_devs[0] > 0 else 0
                
                drift_magnitude = abs(size_change) + abs(std_dev_change)
                
                if drift_magnitude < 10:
                    drift_severity = 'MINIMAL'
                elif drift_magnitude < 25:
                    drift_severity = 'LOW'
                elif drift_magnitude < 50:
                    drift_severity = 'MEDIUM'
                elif drift_magnitude < 75:
                    drift_severity = 'HIGH'
                else:
                    drift_severity = 'EXTREME'
                
                cluster_stats[cluster_name] = {
                    'size_change_percent': size_change,
                    'std_dev_change_percent': std_dev_change,
                    'drift_magnitude': drift_magnitude,
                    'drift_severity': drift_severity
                }
        
        print("\n🌊 CLUSTER DRIFT ANALYSIS:")
        for cluster, stats in sorted(cluster_stats.items(), key=lambda x: x[1]['drift_magnitude'], reverse=True):
            print(f"  Cluster {cluster}: {stats['drift_severity']} DRIFT")
            print(f"     Size change: {stats['size_change_percent']:+.1f}%")
            print(f"     Drift magnitude: {stats['drift_magnitude']:.1f}/100")
        
        # Store analysis results
        analysis_result = {
            'timestamp': datetime.now(),
            'analysis_type': 'REAL_DATA_TEMPORAL_ANALYSIS',
            'weeks_analyzed': 8,
            'keywords_analyzed': len(keyword_timeline),
            'clusters_analyzed': len(cluster_timeline),
            'keyword_shifts': keyword_shifts,
            'cluster_stats': cluster_stats
        }
        
        # Save to MongoDB
        result = self.db['temporal_analysis_real'].insert_one(analysis_result)
        print(f"\n💾 Analysis stored to MongoDB (ID: {result.inserted_id})")
        
        # Final summary
        print("\n" + "="*80)
        print("ANALYSIS SUMMARY")
        print("="*80)
        print(f"✅ Analyzed {len(keyword_timeline)} keywords across {weeks_analyzed} weeks")
        print(f"✅ Tracked {len(cluster_timeline)} clusters for drift")
        print(f"✅ Keyword trends: {len([s for s in keyword_shifts.values() if s['trend_direction'] == 'RISING'])} rising, {len([s for s in keyword_shifts.values() if s['trend_direction'] == 'FALLING'])} falling, {len([s for s in keyword_shifts.values() if s['trend_direction'] == 'STABLE'])} stable")
        print(f"✅ Results saved to temporal_analysis_real collection")
        print("="*80)


def main():
    """Main entry point"""
    pipeline = RealTemporalAnalysisPipeline()
    pipeline.analyze_real_data()


if __name__ == '__main__':
    main()
