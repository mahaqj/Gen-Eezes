# Gen-Eezes

<div align="center">
  <img src="https://github.com/user-attachments/assets/525b89dc-f20e-45a3-b91b-7d2045c4e581" width="200" alt="powerpuff">
</div>

## Overview

This data collection pipeline aggregates trending tech information from three sources: GitHub repositories, arXiv research papers, and HackerNews tech stories. All data is automatically stored in MongoDB for easy querying and trend analysis.

## Project Structure

```
Gen-Eezes/
├── github-trending-collector/
│   └── scrape.py              # GitHub trending scraper
├── arxiv-collector/
│   └── scrape.py              # arXiv paper scraper
├── tech-news-collector/
│   └── scrape.py              # HackerNews tech news scraper
├── collector-mongodb/
│   └── mongo.py               # Interactive data viewer
├── mongodb_storage.py         # MongoDB storage class
├── requirements.txt
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

**Requirements:**
- Python 3.8+
- MongoDB running on localhost:27017
- Internet connection

## GitHub Trending Collector

**File:** `github-trending-collector/scrape.py`

Scrapes GitHub's trending page and collects repository metadata.

**Collected Data:**
- Repository metadata (owner, name, stars, language, topics)
- Cleaned README text
- Activity dates (created, updated, pushed)
- GitHub API data (forks, issues)

**Features:**
- Supports daily, weekly, monthly trending periods
- Filters repos by activity (only updated in last N days)
- Auto-detects language and translates non-English to English
- Cleans README files (removes HTML, badges, emojis, URLs)
- GitHub API authentication support for higher rate limits

**Usage:**

```bash
# Set GitHub token (optional, increases rate limits from 60 to 5000 req/hour)
$env:GITHUB_TOKEN="ghp_your_token_here"

cd github-trending-collector
python scrape.py
```

**Configuration (in code):**
- `period`: "daily", "weekly", "monthly"
- `active_days`: Filter repos updated in last N days (default: 60)

## arXiv Paper Collector

**File:** `arxiv-collector/scrape.py`

Scrapes arXiv API for recent research papers in AI/ML categories.

**Collected Data:**
- Paper title, abstract, authors
- Publication date and arXiv ID
- Paper categories
- PDF and abstract URLs

**Categories Tracked:**
cs.AI, cs.CL, cs.CV, cs.LG, cs.MA, cs.RO, cs.DC, cs.CR, cs.SY, stat.ML

**Usage:**

```bash
cd arxiv-collector
python scrape.py
```

**Configuration (in code):**
- `max_results`: Maximum papers to fetch (default: 300)
- `days_back`: Fetch papers from last N days (default: 365)

## Tech News Collector

**File:** `tech-news-collector/scrape.py`

Scrapes HackerNews for trending tech news and discussions.

**Collected Data:**
- Story title and URL
- Upvote score
- Number of comments/discussion
- Author and publication date
- Story source

**Features:**
- Filters for tech-related stories (AI, ML, Python, Kubernetes, Docker, Cloud, etc.)
- Minimum score threshold to ensure quality (default: 100 upvotes)
- No API key required
- Real-time trending tech industry news

**Usage:**

```bash
cd tech-news-collector
python scrape.py
```

**Configuration (in code):**
- `max_results`: Number of stories to fetch (default: 50)
- `score_threshold`: Minimum upvotes to include (default: 100)

## Data Viewer

**File:** `collector-mongodb/mongo.py`

Interactive command-line tool to query and explore stored data.

**Usage:**

```bash
cd collector-mongodb
python mongo.py
```

**Menu Options:**
1. View recent GitHub repos (last 10 with stars, language, description)
2. Filter repos by programming language
3. View recent arXiv papers (last 10 with authors, publish date)
4. Filter papers by arXiv category
5. View recent tech news (last 10 with scores and comments)
6. Filter tech news by minimum score
7. View collection statistics (total items stored)
8. Exit

## MongoDB Storage

**Database:** `gen_eezes`

**Collections:**

### github_repos

```json
{
  "owner": "username",
  "name": "repo-name",
  "full_name": "username/repo-name",
  "description": "Repository description",
  "language": "Python",
  "topics": ["ai", "ml"],
  "stars_trending": "1,234",
  "stars_total": 12345,
  "forks": 500,
  "open_issues": 45,
  "readme_text": "Cleaned README content",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-12-01T00:00:00Z",
  "pushed_at": "2025-12-01T00:00:00Z",
  "repo_url": "https://github.com/username/repo-name",
  "scraped_at": "2025-12-01T14:30:00Z"
}
```

### arxiv_papers

```json
{
  "arxiv_id": "2501.12345",
  "title": "Paper Title",
  "abstract": "Full abstract text",
  "authors": ["Author One", "Author Two"],
  "categories": ["cs.AI", "cs.LG"],
  "published": "2025-12-01",
  "pdf_url": "https://arxiv.org/pdf/2501.12345",
  "arxiv_url": "https://arxiv.org/abs/2501.12345",
  "scraped_at": "2025-12-01T14:30:00Z"
}
```

### tech_news

```json
{
  "hackernews_id": 12345,
  "title": "New AI Framework Released",
  "url": "https://example.com/article",
  "score": 2500,
  "comments": 342,
  "author": "username",
  "published_at": "2025-12-01T14:30:00Z",
  "source": "HackerNews",
  "story_type": "story",
  "scraped_at": "2025-12-01T14:35:00Z"
}
```

## Complete Workflow

```bash
# 1. Set GitHub token (optional but recommended)
$env:GITHUB_TOKEN="ghp_your_token_here"

# 2. Scrape GitHub trending repos
cd github-trending-collector
python scrape.py

# 3. Scrape arXiv papers
cd ../arxiv-collector
python scrape.py

# 4. Scrape HackerNews tech stories
cd ../tech-news-collector
python scrape.py

# 5. View all collected data
cd ../collector-mongodb
python mongo.py
```

## Key Features

- **Multi-Source Aggregation:** Combines GitHub, arXiv, and HackerNews in one place
- **Automatic Translation:** Non-English content automatically translated to English
- **Text Cleaning:** README files and content cleaned (HTML, badges, emojis, URLs removed)
- **Language Detection:** Automatic language detection via langdetect
- **Quality Filtering:** Scores and activity thresholds ensure quality data
- **Historical Tracking:** Timestamps on all entries for trend analysis
- **Optimized Queries:** MongoDB indexes on unique fields for fast lookups
- **No Data Loss:** Each run creates new entries, historical data preserved
- **Interactive Viewer:** Easy-to-use CLI tool for querying data

## Why Three Data Sources?

- **GitHub:** What open-source developers are building
- **arXiv:** Cutting-edge AI/ML research breakthroughs
- **HackerNews:** What the tech community is discussing and excited about

Combined = Complete view of tech ecosystem trends

## Notes

- All data stored in MongoDB with timestamps for trend tracking
- Duplicate prevention via unique indexes
- Scrapers automatically save to MongoDB when run
- Viewer connects to local MongoDB by default
- All content automatically translated to English for consistency