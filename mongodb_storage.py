from pymongo import MongoClient
from datetime import datetime

class MongoDBStorage:
    def __init__(self, db_name="gen_eezes", mongo_uri="mongodb://localhost:27017/"): # connect to mongodb
        """Connect to MongoDB"""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.github_collection = self.db["github_repos"]
        self.arxiv_collection = self.db["arxiv_papers"]
        self.news_collection = self.db["tech_news"]
        self.users_collection = self.db["users"]
        print(f"Connected to MongoDB database: {db_name}")
    
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
    
    def save_tech_news(self, news_items): # save tech news to mongodb
        if not news_items:
            print("no news to save")
            return
        
        for news in news_items:
            news["scraped_at"] = datetime.utcnow()
            try:
                self.news_collection.insert_one(news)
            except Exception as e:
                print(f"error saving {news['title']}: {e}")
        
        print(f"saved {len(news_items)} news items to mongodb")
    
    def get_recent_news(self, limit=10): # get most recently scraped news
        news = list(self.news_collection.find().sort("scraped_at", -1).limit(limit))
        return news
    
    def get_news_by_score(self, min_score=100, limit=10): # get news by minimum score
        news = list(self.news_collection.find({"score": {"$gte": min_score}}).sort("score", -1).limit(limit))
        return news
    
    def get_collection_stats(self): # get stats about collections
        github_count = self.github_collection.count_documents({})
        arxiv_count = self.arxiv_collection.count_documents({})
        news_count = self.news_collection.count_documents({})
        print(f"\n{'='*60}")
        print(f"github repos stored: {github_count}")
        print(f"arxiv papers stored: {arxiv_count}")
        print(f"tech news items stored: {news_count}")
        print(f"{'='*60}\n")

    def save_user(self, first_name, email): # save newsletter signup to mongodb
        user = {
            "first_name": first_name,
            "email": email,
            "signup_date": datetime.utcnow()
        }
        
        try:
            result = self.users_collection.insert_one(user)
            print(f"Uuser saved: {email}")
            return result.inserted_id
        except Exception as e:
            print(f"error saving user: {e}")
            return None
    
    def get_all_users(self): # get all newsletter subscribers
        users = list(self.users_collection.find())
        return users