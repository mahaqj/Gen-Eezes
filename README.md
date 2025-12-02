# Gen-Eezes

<div align="center">
  <img src="https://github.com/user-attachments/assets/525b89dc-f20e-45a3-b91b-7d2045c4e581" width="200" alt="powerpuff">
</div>

## Overview

This data collection pipeline scrapes trending GitHub repositories and arXiv research papers, automatically translates non-English content, and stores everything in MongoDB for easy querying and analysis.

## Project Structure

```
Gen-Eezes/
├── github-trending-collector/
│   └── scrape.py              # GitHub trending scraper
├── arxiv-collector/
│   └── scrape.py              # arXiv paper scraper
├── collector-mongodb/
│   └── mongo.py               # Data viewer tool
├── mongodb_storage.py         # MongoDB storage class
└── requirements.txt
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

Scrapes GitHub's trending page and collects:
- Repository metadata (owner, name, stars, language, topics)
- Cleaned README text
- Activity dates (created, updated, pushed)
- GitHub API data (forks, issues)

**Features:**
- Supports daily, weekly, monthly trending periods
- Filters repos by activity (only updated in last N days)
- Auto-detects language and translates non-English content to English
- Cleans README files (removes HTML, badges, emojis, URLs)
- GitHub API authentication for higher rate limits

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

Scrapes arXiv API for research papers and collects:
- Paper title, abstract, authors
- Publication date and arXiv ID
- Paper categories (cs.AI, cs.LG, etc.)
- PDF and abstract URLs

**Categories:**
cs.AI, cs.CL, cs.CV, cs.LG, cs.MA, cs.RO, cs.DC, cs.CR, cs.SY, stat.ML

**Usage:**

```bash
cd arxiv-collector
python scrape.py
```

**Configuration (in code):**
- `max_results`: Maximum papers to fetch (default: 300)
- `days_back`: Fetch papers from last N days (default: 365)

## Data Viewer

**File:** `collector-mongodb/mongo.py`

Interactive CLI tool to query and view stored data.

**Usage:**

```bash
cd collector-mongodb
python mongo.py
```

**Menu options:**
1. View recent GitHub repos (last 10 with stars, language, description)
2. Filter repos by programming language
3. View recent arXiv papers (last 10 with authors, publish date)
4. Filter papers by arXiv category
5. View collection statistics (total repos and papers stored)
6. Exit

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

## Workflow

```bash
# 1. Set GitHub token
$env:GITHUB_TOKEN="ghp_your_token_here"

# 2. Scrape GitHub trending
cd github-trending-collector
python scrape.py

# 3. Scrape arXiv papers
cd ../arxiv-collector
python scrape.py

# 4. View all data
cd ../collector-mongodb
python mongo.py
```

## Key Features

- **Automatic Translation:** Non-English repositories automatically translated to English using Google Translate
- **Text Cleaning:** README files cleaned of HTML, badges, emojis, and URLs
- **Language Detection:** langdetect used to identify content language
- **API Authentication:** GitHub token support for increased rate limits
- **Historical Tracking:** Timestamps on all entries to track trends over time
- **Optimized Queries:** MongoDB indexes on unique fields for fast lookups
- **No Data Loss:** Each run creates new entries, historical data preserved

## Notes

- All data persisted in MongoDB with timestamps
- Duplicate prevention via unique indexes
- Both scrapers automatically save to MongoDB when run
- Viewer tool connects to local MongoDB by default