import arxiv
from datetime import datetime, timedelta, timezone
import sys
sys.path.insert(0, '..')
from mongodb_storage import MongoDBStorage

class ArxivCollector:
    def __init__(self, max_results=300, days_back=365,categories=None):
        if categories is None: # default AI-related arXiv categories
            categories = [
                "cat:cs.CL", # nlp, llms
                "cat:cs.LG", # machine learning
                "cat:stat.ML", # statistics + ml theory
                "cat:cs.AI", # artificial intelligence (general)
                "cat:cs.CV", # computer vision
                "cat:cs.RO", # robotics
                "cat:cs.MA", # multi-agent systems
                "cat:cs.DC", # distributed systems
                "cat:cs.CR", # security
                "cat:cs.SY" # systems
            ] 
        self.max_results = max_results
        self.days_back = days_back
        self.categories = categories
        self.query = " OR ".join(categories) # build query string

    def fetch_recent_papers(self):
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.days_back) # goes back x days (set from main + timezone aware)
        client = arxiv.Client()
        search = arxiv.Search(query=self.query, max_results=self.max_results, sort_by=arxiv.SortCriterion.SubmittedDate)
        collected = []
        print(f"searching for papers in categories: {', '.join(self.categories)}")
        print(f"cutoff date: {cutoff_date.strftime('%Y-%m-%d')}\n")
        for result in client.results(search):
            print(f"\nprocessing: {result.get_short_id()}")
            print(f"  title: {result.title[:60]}...")
            print(f"  published: {result.published.strftime('%Y-%m-%d')}")
            
            if result.published < cutoff_date:
                print(f"  too old (before {cutoff_date.strftime('%Y-%m-%d')})")
                continue
            
            print(f"  recent paper")
            
            paper = {
                "arxiv_id": result.get_short_id(),
                "title": result.title.strip(),
                "abstract": result.summary.strip(),
                "authors": [a.name for a in result.authors],
                "categories": result.categories,
                "published": result.published.strftime('%Y-%m-%d'),
                "pdf_url": result.pdf_url,
                "arxiv_url": result.entry_id
            }
            collected.append(paper)
            print(f"  added to results")
            
        return collected

if __name__ == "__main__":
    collector = ArxivCollector(max_results=10, days_back=365) # set max_results and days_back here
    papers = collector.fetch_recent_papers()
    print(f"\n{'='*60}")
    print(f"fetched {len(papers)} papers from the last {collector.days_back} days!")
    print(f"{'='*60}")
    if papers:
        print("\nexample:")
        print(papers[0])
        print(f"\nsaving to MongoDB...")
        db = MongoDBStorage()
        db.save_arxiv_papers(papers)
        db.get_collection_stats()