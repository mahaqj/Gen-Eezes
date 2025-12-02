import requests
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')
from mongodb_storage import MongoDBStorage

class TechNewsCollector:
    def __init__(self, max_results=50, score_threshold=100): # collect tech news from hackernews
        self.max_results = max_results # num of stories to fetch
        self.score_threshold = score_threshold # min score to include story
        self.base_url = "https://hacker-news.firebaseio.com/v0"
    
    def fetch_top_stories(self): # fetch top story ids from HackerNews
        try:
            url = f"{self.base_url}/topstories.json"
            story_ids = requests.get(url).json()
            return story_ids[:self.max_results * 2] # fetch extra to filter
        except Exception as e:
            print(f"error fetching top stories: {e}")
            return []
    
    def fetch_story_details(self, story_id): # fetch details for a specific story
        try:
            url = f"{self.base_url}/item/{story_id}.json"
            story = requests.get(url).json()
            return story
        except Exception as e:
            print(f"error fetching story {story_id}: {e}")
            return None
    
    def is_tech_related(self, story): # filter for tech-related stories
        tech_keywords = [
            "ai", "machine learning", "python", "javascript", "rust", "golang",
            "kubernetes", "docker", "cloud", "aws", "azure", "gcp",
            "startup", "tech", "software", "app", "api", "database",
            "programming", "developer", "code", "open source", "github",
            "web3", "blockchain", "crypto", "llm", "gpt", "neural",
            "quantum", "5g", "iot", "automation", "framework",
            "library", "tool", "devops", "security", "cybersecurity"
        ]
        title = story.get("title", "").lower()
        url = story.get("url", "").lower()
        return any(keyword in title or keyword in url for keyword in tech_keywords)
    
    def fetch_news(self): # fetch and filter tech news from HackerNews
        print(f"\nfetching tech news from hackernews...")
        story_ids = self.fetch_top_stories()
        news = []
        fetched = 0
        for story_id in story_ids:
            if len(news) >= self.max_results:
                break
            story = self.fetch_story_details(story_id)
            if not story:
                continue
            fetched += 1
            print(f"  processing story {fetched}...", end="\r")
            if story.get("score", 0) < self.score_threshold: # filter by score and tech relevance
                continue
            if not self.is_tech_related(story):
                continue
            if not story.get("url"): # skip stories with no url
                continue
            try:
                timestamp = datetime.fromtimestamp(story.get("time", 0))
            except:
                timestamp = datetime.utcnow()
            news_item = {
                "hackernews_id": story.get("id"),
                "title": story.get("title"),
                "url": story.get("url"),
                "score": story.get("score", 0),
                "comments": story.get("descendants", 0),
                "author": story.get("by", "Unknown"),
                "published_at": timestamp.isoformat(),
                "source": "HackerNews",
                "story_type": story.get("type")
            }
            news.append(news_item)
            print(f"  added: {news_item['title'][:60]}...")
        print(f"\nProcessed {fetched} stories, found {len(news)} tech-related news items\n")
        return news

if __name__ == "__main__":
    collector = TechNewsCollector(max_results=50, score_threshold=100)
    news = collector.fetch_news()
    print(f"\n{'='*60}")
    print(f"fetched {len(news)} tech news items!")
    print(f"{'='*60}")
    if news:
        print("\nexample news item:")
        print(f"  title: {news[0]['title']}")
        print(f"  score: {news[0]['score']}")
        print(f"  url: {news[0]['url']}")
        print(f"\nsaving to mongodb...")
        db = MongoDBStorage()
        db.save_tech_news(news)
        db.get_collection_stats()