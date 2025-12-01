# Gen-Eezes

<div align="center">
  <img src="https://github.com/user-attachments/assets/525b89dc-f20e-45a3-b91b-7d2045c4e581" width="200" alt="powerpuff">
</div>

## Overview

The data collection pipeline scrapes trending information from two sources:
1. **GitHub Trending Repositories** - Tracks popular open-source projects
2. **arXiv Research Papers** - Collects recent AI/ML academic papers

## Components

### 1. GitHub Trending Collector (`github-trending-collector/scrape.py`)

**What it does:**
- Scrapes GitHub's trending page (daily/weekly/monthly)
- Filters for **English-only** repositories using language detection
- Filters for **recently active** repos (configurable, default: last 60 days)
- Fetches detailed metadata via GitHub API (stars, forks, topics, etc.)
- Downloads and cleans README files (removes HTML, badges, emojis, URLs)
- Saves timestamped JSON files with all collected data

**Key Features:**
- GitHub API authentication support (5000 req/hour vs 60)
- README text preprocessing and cleaning
- Language detection to filter non-English repos
- Activity-based filtering (only recent repos)
- Rich metadata collection (topics, stars, creation date)

**Output:** `data/github_trending_YYYYMMDD_HHMMSS.json`

---

### 2. arXiv Paper Collector (`arxiv-collector/scrape.py`)

**What it does:**
- Queries arXiv API for papers in AI-related categories
- Filters papers by publication date (configurable, default: last 365 days)
- Collects paper metadata, abstracts, and author information
- Saves timestamped JSON files for downstream processing

**Categories Tracked:**
- `cs.CL` - Natural Language Processing, LLMs
- `cs.LG` - Machine Learning
- `stat.ML` - Statistical Machine Learning Theory
- `cs.AI` - Artificial Intelligence (General)
- `cs.CV` - Computer Vision
- `cs.RO` - Robotics
- `cs.MA` - Multi-Agent Systems
- `cs.DC` - Distributed Systems
- `cs.CR` - Security & Cryptography
- `cs.SY` - Systems & Control

**Key Features:**
- Multi-category search with OR logic
- Date-based filtering for recent papers
- Timezone-aware datetime handling
- Detailed console logging for progress tracking
- Author and category metadata extraction

**Output:** `data/arxiv_papers_YYYYMMDD_HHMMSS.json`

---

## Usage

### GitHub Trending Collector

```bash
cd github-trending-collector

# Set GitHub token (optional but recommended)
$env:GITHUB_TOKEN="ghp_your_token_here"

# Run scraper
python scrape.py
```

**Configuration:**
- `period`: "daily", "weekly", or "monthly"
- `active_days`: Filter repos updated in last N days (default: 60)
- `github_token`: GitHub API token for higher rate limits

### arXiv Paper Collector

```bash
cd arxiv-collector

# Run scraper
python scrape.py
```

**Configuration:**
- `max_results`: Maximum papers to fetch (default: 300)
- `days_back`: Only fetch papers from last N days (default: 365)
- `categories`: List of arXiv categories to search

---

## Data Structure

### GitHub Repo Schema
```json
{
  "owner": "username",
  "name": "repo-name",
  "full_name": "username/repo-name",
  "description": "Short description",
  "language": "Python",
  "topics": ["ai", "machine-learning"],
  "stars_trending": "1,234",
  "stars_total": 12345,
  "readme_text": "Cleaned README content...",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-12-01T00:00:00Z",
  "pushed_at": "2025-12-01T00:00:00Z",
  "repo_url": "https://github.com/username/repo-name"
}
```

### arXiv Paper Schema
```json
{
  "arxiv_id": "2501.12345",
  "title": "Paper Title",
  "abstract": "Full abstract text...",
  "authors": ["Author One", "Author Two"],
  "categories": ["cs.AI", "cs.LG"],
  "published": "2025-12-01",
  "pdf_url": "https://arxiv.org/pdf/2501.12345",
  "arxiv_url": "https://arxiv.org/abs/2501.12345"
}
```

---

## GitHub Token Setup

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scope: `public_repo`
4. Copy token and set environment variable:
   ```powershell
   $env:GITHUB_TOKEN="ghp_your_token_here"
   ```

**Rate Limits:**
- Without token: 60 requests/hour
- With token: 5,000 requests/hour (FREE!)

---

## Output

All data is saved in timestamped JSON files:
- `github-trending-collector/data/github_trending_YYYYMMDD_HHMMSS.json`
- `arxiv-collector-agent/data/arxiv_papers_YYYYMMDD_HHMMSS.json`

This allows tracking trends over time without overwriting previous runs.
