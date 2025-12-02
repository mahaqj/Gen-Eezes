from pymongo import MongoClient
from datetime import datetime

class MongoDBStorage:
    def __init__(self, db_name="gen_eezes", mongo_uri="mongodb://localhost:27017/"): # connect to mongodb
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.github_collection = self.db["github_repos"]
        self.arxiv_collection = self.db["arxiv_papers"]
        print(f" connected to mongodb database: {db_name}")
    
    def create_indexes(self): # create indexes for faster queries
        self.github_collection.create_index("full_name", unique=True)
        self.github_collection.create_index("scraped_at")
        self.arxiv_collection.create_index("arxiv_id", unique=True)
        self.arxiv_collection.create_index("scraped_at")
        print(" indexes created")
    
    def save_github_repos(self, repos): # save github repos to mongodb
        if not repos:
            print("no repos to save")
            return
        for repo in repos:
            repo["scraped_at"] = datetime.utcnow()
            try:
                self.github_collection.insert_one(repo)
            except Exception as e:
                print(f"error saving {repo['full_name']}: {e}")
        print(f" saved {len(repos)} repos to mongodb")
    
    def save_arxiv_papers(self, papers): # save arxiv papers to mongodb
        if not papers:
            print("no papers to save")
            return
        for paper in papers:
            paper["scraped_at"] = datetime.utcnow()
            try:
                self.arxiv_collection.insert_one(paper)
            except Exception as e:
                print(f"error saving {paper['arxiv_id']}: {e}")
        print(f" saved {len(papers)} papers to mongodb")
    
    def get_recent_repos(self, limit=10): # get most recently scraped repos
        repos = list(self.github_collection.find().sort("scraped_at", -1).limit(limit))
        return repos
    
    def get_repos_by_language(self, language): # get repos by programming language
        repos = list(self.github_collection.find({"language": language}))
        return repos
    
    def get_papers_by_category(self, category): # get papers by category
        papers = list(self.arxiv_collection.find({"categories": category}))
        return papers
    
    def get_collection_stats(self): # get stats about collections
        github_count = self.github_collection.count_documents({})
        arxiv_count = self.arxiv_collection.count_documents({})
        print(f"\n{'='*60}")
        print(f"github repos stored: {github_count}")
        print(f"arxiv papers stored: {arxiv_count}")
        print(f"{'='*60}\n")