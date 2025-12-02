import requests
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException
from datetime import datetime, timedelta
import re
import os
from googletrans import Translator
import sys
sys.path.insert(0, '..')
from mongodb_storage import MongoDBStorage

class GitHubTrendingCollector:
    def __init__(self, period="daily", github_token=None, active_days=60):
        self.period = period
        self.base_url = f"https://github.com/trending?since={period}"
        self.github_token = github_token
        self.active_days = active_days
        self.translator = Translator()

    def github_headers(self):
        headers = {"Accept": "application/vnd.github.mercy-preview+json"} # topics
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"
        return headers

    def is_english(self, text): # since there are a lot of chinese, korean, etc. repos
        if not text or len(text) < 20:
            return True
        try:
            return detect(text) == "en"
        except LangDetectException:
            return False

    def fetch_repo_metadata(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        r = requests.get(url, headers=self.github_headers())
        if r.status_code != 200:
            return None
        data = r.json()
        return {
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "pushed_at": data.get("pushed_at"),
            "stars_total": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "open_issues": data.get("open_issues_count"),
            "topics": data.get("topics", [])
        }
    
    def clean_readme(self, text):
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text) # remove html tags
        text = re.sub(r'!\[.*?\]\(https?://.*?\)', '', text) # remove badge/shield urls
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text) # remove img markdown
        emoji_pattern = re.compile( # remove emojis
            "["
            "\U0001F600-\U0001F64F" # emoticons
            "\U0001F300-\U0001F5FF" # symbols & pictographs
            "\U0001F680-\U0001F6FF" # transport & map
            "\U0001F1E0-\U0001F1FF" # flags
            "\U00002500-\U00002BEF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2600-\u2B55"
            "\u200d"
            "\ufe0f"
            "]+",
            flags=re.UNICODE
        )
        text = emoji_pattern.sub('', text)
        text = re.sub(r'https?://\S+', '', text) # read urls
        # remove multiple spaces/newlines:
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()
    
    def fetch_readme(self, owner, repo):
        urls = [
            f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
            f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
        ]
        for url in urls:
            r = requests.get(url)
            if r.status_code == 200:
                return self.clean_readme(r.text) # clean before returning
        return ""

    def translate_to_english(self, text): # translate text to eng if not
        if not text or len(text) < 20:
            return text
        try:
            lang = detect(text)
            if lang != "en":
                print(f"    translating from {lang} to english...")
                translated = self.translator.translate(text, src_lang=lang, dest_language='en')
                return translated.text
            return text
        except Exception as e:
            print(f"    translation failed: {e}")
            return text

    def fetch_trending(self):
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, "html.parser")
        repos = []
        repo_list = soup.find_all("article", class_="Box-row")
        cutoff_date = datetime.utcnow() - timedelta(days=self.active_days)
        print(f"found {len(repo_list)} trending repos")

        for repo in repo_list:
            full_name = repo.h2.a.text.strip().replace("\n", "").replace(" ", "")
            owner, name = full_name.split("/")
            print(f"\nprocessing: {owner}/{name}")
            desc_tag = repo.find("p", class_="col-9 color-fg-muted my-1 pr-4")
            description = desc_tag.text.strip() if desc_tag else ""
            lang_tag = repo.find("span", itemprop="programmingLanguage")
            language = lang_tag.text.strip() if lang_tag else None
            stars_tag = repo.find("span", class_="d-inline-block float-sm-right")
            stars_today = stars_tag.text.strip().split(" ")[0] if stars_tag else None
            meta = self.fetch_repo_metadata(owner, name)
            if not meta:
                print(f"  failed to fetch metadata")
                continue
            if meta["updated_at"]:
                updated_date = datetime.fromisoformat(meta["updated_at"].replace("Z", ""))
                if updated_date < cutoff_date:
                    print(f"  too old: updated {updated_date.date()}")
                    continue
                print(f"  recent: updated {updated_date.date()}")
            readme_text = self.fetch_readme(owner, name)
            combined_text = description + " " + readme_text
            if not self.is_english(combined_text): # translate if not eng
                print(f"  translating to english...")
                description = self.translate_to_english(description)
                readme_text = self.translate_to_english(readme_text)
                combined_text = description + " " + readme_text
            print(f"  english content")

            repos.append({
                "owner": owner,
                "name": name,
                "full_name": f"{owner}/{name}",
                "description": description,
                "language": language,
                "topics": meta["topics"],
                "stars_trending": stars_today,
                "stars_total": meta["stars_total"],
                "readme_text": readme_text,
                "created_at": meta["created_at"],
                "updated_at": meta["updated_at"],
                "pushed_at": meta["pushed_at"],
                "repo_url": f"https://github.com/{owner}/{name}"
            })
            print(f"  added to results")
        return repos

# generate github authentication token
# $env:GITHUB_TOKEN="ghp_your_token_here"
# python scrape.py
# if __name__ == "__main__":
#     github_token = os.getenv("GITHUB_TOKEN") # read from environment
#     collector = GitHubTrendingCollector(period="daily", active_days=60,github_token=github_token) # period can be daily, weekly, or monthly
#     data = collector.fetch_trending()
#     print(f"active repos found: {len(data)}")
#     if data:
#         print("example repo:")
#         print(data[0])

if __name__ == "__main__":
    github_token = os.getenv("GITHUB_TOKEN") # read from environment
    collector = GitHubTrendingCollector(period="daily", active_days=60, github_token=github_token) # period can be daily, weekly, or mo
    data = collector.fetch_trending()
    print(f"\n{'='*60}")
    print(f"active repos found: {len(data)}")
    print(f"{'='*60}")
    if data:
        print("\nexample repo:")
        print(data[0])
        print(f"\nsaving to MongoDB...")
        db = MongoDBStorage()
        db.save_github_repos(data)
        db.get_collection_stats()