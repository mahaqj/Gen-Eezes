"""
Periodic Data Collector (Module 1 - Extended)
Runs weekly to collect new data and create temporal snapshots
Maintains historical snapshots for temporal analysis
"""

import sys
from pathlib import Path
import importlib.util
from datetime import datetime, timedelta
from pymongo import MongoClient
import json

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / "github-trending-collector"))
sys.path.insert(0, str(Path(__file__).parent / "arxiv-collector"))
sys.path.insert(0, str(Path(__file__).parent / "tech-news-collector"))


class PeriodicDataCollector:
    """Collects data periodically and maintains temporal snapshots"""
    
    def __init__(self):
        """Initialize collector and database connection"""
        self.mongo_client = MongoClient('localhost', 27017)
        self.db = self.mongo_client['gen_eezes']
        self.snapshot_date = datetime.now()
        
    def run_github_collector(self):
        """Run GitHub trending collector"""
        print("  📦 Collecting GitHub trending repositories...")
        try:
            # Import the GitHub scraper
            spec = importlib.util.spec_from_file_location(
                "github_scraper",
                Path(__file__).parent / "github-trending-collector" / "scrape.py"
            )
            github_module = importlib.util.module_from_spec(spec)
            
            # Capture the scraper's output
            initial_count = self.db['github_repos'].count_documents({})
            spec.loader.exec_module(github_module)
            final_count = self.db['github_repos'].count_documents({})
            
            collected = final_count - initial_count
            print(f"    ✓ GitHub: {collected} new repos (total: {final_count})")
            return collected
        except Exception as e:
            print(f"    ⚠ GitHub collector error: {e}")
            return 0
    
    def run_arxiv_collector(self):
        """Run arXiv papers collector"""
        print("  📚 Collecting arXiv papers...")
        try:
            spec = importlib.util.spec_from_file_location(
                "arxiv_scraper",
                Path(__file__).parent / "arxiv-collector" / "scrape.py"
            )
            arxiv_module = importlib.util.module_from_spec(spec)
            
            initial_count = self.db['arxiv_papers'].count_documents({})
            spec.loader.exec_module(arxiv_module)
            final_count = self.db['arxiv_papers'].count_documents({})
            
            collected = final_count - initial_count
            print(f"    ✓ arXiv: {collected} new papers (total: {final_count})")
            return collected
        except Exception as e:
            print(f"    ⚠ arXiv collector error: {e}")
            return 0
    
    def run_news_collector(self):
        """Run tech news collector"""
        print("  📰 Collecting tech news...")
        try:
            spec = importlib.util.spec_from_file_location(
                "news_scraper",
                Path(__file__).parent / "tech-news-collector" / "scrape.py"
            )
            news_module = importlib.util.module_from_spec(spec)
            
            initial_count = self.db['tech_news'].count_documents({})
            spec.loader.exec_module(news_module)
            final_count = self.db['tech_news'].count_documents({})
            
            collected = final_count - initial_count
            print(f"    ✓ Tech News: {collected} new articles (total: {final_count})")
            return collected
        except Exception as e:
            print(f"    ⚠ News collector error: {e}")
            return 0
    
    def collect_all_data(self):
        """Run all collectors and aggregate into a snapshot"""
        print("\n" + "="*80)
        print(f"PERIODIC DATA COLLECTION - {self.snapshot_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        print("\n📥 Running data collectors...")
        github_count = self.run_github_collector()
        arxiv_count = self.run_arxiv_collector()
        news_count = self.run_news_collector()
        
        total_collected = github_count + arxiv_count + news_count
        
        print(f"\n✅ Collection complete: {total_collected} new documents collected")
        
        return total_collected
    
    def create_snapshot(self):
        """Create a temporal snapshot of current data state"""
        print("\n💾 Creating temporal snapshot...")
        
        # Get current state from collections
        github_data = list(self.db['github_repos'].find({}, {'_id': 1, 'title': 1, 'stars': 1}))
        arxiv_data = list(self.db['arxiv_papers'].find({}, {'_id': 1, 'title': 1}))
        news_data = list(self.db['tech_news'].find({}, {'_id': 1, 'title': 1}))
        
        snapshot = {
            'timestamp': self.snapshot_date,
            'week': self._get_week_number(),
            'github_count': len(github_data),
            'arxiv_count': len(arxiv_data),
            'news_count': len(news_data),
            'total_documents': len(github_data) + len(arxiv_data) + len(news_data),
            'data_summary': {
                'github': [{'id': str(doc.get('_id', '')), 'title': doc.get('title', '')} for doc in github_data[:5]],
                'arxiv': [{'id': str(doc.get('_id', '')), 'title': doc.get('title', '')} for doc in arxiv_data[:5]],
                'news': [{'id': str(doc.get('_id', '')), 'title': doc.get('title', '')} for doc in news_data[:5]]
            }
        }
        
        # Save to MongoDB
        result = self.db['data_collection_snapshots'].insert_one(snapshot)
        print(f"  ✓ Snapshot saved (ID: {result.inserted_id})")
        
        return snapshot
    
    def _get_week_number(self):
        """Get the ISO week number for the snapshot"""
        return self.snapshot_date.isocalendar()[1]
    
    def set_snapshot_date(self, date):
        """Set the snapshot date for historical data collection"""
        self.snapshot_date = date
    
    def run(self):
        """Run collection and create snapshot"""
        self.collect_all_data()
        snapshot = self.create_snapshot()
        return snapshot
    
    def get_collection_stats(self):
        """Get statistics about all collected data"""
        stats = {
            'github_repos': self.db['github_repos'].count_documents({}),
            'arxiv_papers': self.db['arxiv_papers'].count_documents({}),
            'tech_news': self.db['tech_news'].count_documents({}),
            'total_snapshots': self.db['data_collection_snapshots'].count_documents({})
        }
        return stats


def main():
    """Main entry point for periodic collector"""
    collector = PeriodicDataCollector()
    collector.run()
    
    stats = collector.get_collection_stats()
    print("\n" + "="*80)
    print("COLLECTION STATISTICS")
    print("="*80)
    print(f"  GitHub Repositories: {stats['github_repos']}")
    print(f"  arXiv Papers: {stats['arxiv_papers']}")
    print(f"  Tech News Articles: {stats['tech_news']}")
    print(f"  Total Snapshots: {stats['total_snapshots']}")
    print("="*80)


if __name__ == '__main__':
    main()
