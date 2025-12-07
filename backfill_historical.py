"""
Historical Data Backfiller
Backfills 8 weeks of historical snapshots by running collectors
with backdated timestamps
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from pymongo import MongoClient
from periodic_collector import PeriodicDataCollector
import time

def backfill_historical_data(weeks: int = 8):
    """
    Backfill historical snapshots by running collectors with past dates
    
    Args:
        weeks: Number of weeks of historical data to create (default 8)
    """
    
    print("="*80)
    print(f"HISTORICAL DATA BACKFILLER - Creating {weeks} weeks of snapshots")
    print("="*80)
    
    collector = PeriodicDataCollector()
    mongo_client = MongoClient('localhost', 27017)
    db = mongo_client['gen_eezes']
    
    # Clear previous snapshots if starting fresh
    existing_snapshots = db['data_collection_snapshots'].count_documents({})
    print(f"\nExisting snapshots in database: {existing_snapshots}")
    
    # Auto-clear for backfilling
    db['data_collection_snapshots'].delete_many({})
    print("✓ Cleared existing snapshots for backfill")
    
    print(f"\n📅 Starting backfill from {weeks} weeks ago...")
    print("-"*80)
    
    # Calculate start date
    start_date = datetime.now() - timedelta(weeks=weeks)
    
    # Generate snapshots for each week
    for week_num in range(weeks):
        # Calculate the date for this week (going backwards)
        snapshot_date = start_date + timedelta(weeks=week_num)
        collector.set_snapshot_date(snapshot_date)
        
        week_display = snapshot_date.strftime('%Y-%m-%d (Week %W)')
        print(f"\n[{week_num + 1}/{weeks}] {week_display}")
        
        try:
            # Run collection with backdated timestamp
            snapshot = collector.run()
            
            # Update the snapshot with the backdated timestamp
            db['data_collection_snapshots'].update_one(
                {'_id': snapshot['_id']},
                {'$set': {'timestamp': snapshot_date}}
            )
            
            print(f"  ✓ Created snapshot with {snapshot['total_documents']} documents")
            
        except Exception as e:
            print(f"  ⚠ Error creating snapshot: {e}")
        
        # Small delay between collections to avoid rate limiting
        if week_num < weeks - 1:
            time.sleep(1)
    
    print("\n" + "="*80)
    print("BACKFILL COMPLETE")
    print("="*80)
    
    # Print final statistics
    stats = collector.get_collection_stats()
    print(f"\nFinal Statistics:")
    print(f"  GitHub Repositories: {stats['github_repos']}")
    print(f"  arXiv Papers: {stats['arxiv_papers']}")
    print(f"  Tech News Articles: {stats['tech_news']}")
    print(f"  Total Snapshots: {stats['total_snapshots']}")
    
    # Show snapshot timeline
    print(f"\nSnapshot Timeline:")
    snapshots = db['data_collection_snapshots'].find().sort('timestamp', 1)
    for snap in snapshots:
        date_str = snap['timestamp'].strftime('%Y-%m-%d')
        total = snap['total_documents']
        print(f"  {date_str}: {total} documents (GitHub: {snap['github_count']}, arXiv: {snap['arxiv_count']}, News: {snap['news_count']})")
    
    print("="*80)


if __name__ == '__main__':
    backfill_historical_data(weeks=52)
