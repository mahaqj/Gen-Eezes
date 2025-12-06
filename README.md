# Gen-Eezes

<div align="center">
  <img src="https://github.com/user-attachments/assets/525b89dc-f20e-45a3-b91b-7d2045c4e581" width="200" alt="powerpuff">
</div>

## Overview

Multi-agent data collection pipeline that aggregates trending tech information from three sources: **GitHub repositories**, **arXiv research papers**, and **HackerNews tech stories**. All data is stored in MongoDB with vector embeddings in Qdrant for semantic search capabilities.

## Project Structure

```
Gen-Eezes/
├── github-trending-collector/    # GitHub trending repos scraper
├── arxiv-collector/              # arXiv research papers scraper
├── tech-news-collector/          # HackerNews tech news scraper
├── collector-mongodb/            # MongoDB data viewer
├── embedding_pipeline/           # Vector embedding & storage
│   ├── embed_all.py             # Main embedding pipeline
│   ├── embedding_handler.py     # Embedding generation (all-MiniLM-L6-v2)
│   ├── qdrant_storage.py        # Qdrant vector database interface
│   └── embed_all_*.py           # Alternative pipeline variants
├── tests/                        # Test & verification scripts
│   ├── verify_qdrant.py         # Verify stored embeddings
│   ├── test_embeddings.py       # Test embedding functionality
│   └── verify_embeddings.py     # Additional embedding checks
├── qdrant_storage/              # Persisted vector database
├── mongodb_storage.py           # MongoDB interface
├── requirements.txt             # Python dependencies
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

## Quick Start

### 1. Collect Data

```bash
# GitHub trending repos
cd github-trending-collector
python scrape.py

# arXiv research papers
cd ../arxiv-collector
python scrape.py

# HackerNews tech stories
cd ../tech-news-collector
python scrape.py
```

### 2. Generate Embeddings

```bash
# Process all MongoDB data and store embeddings in Qdrant
cd embedding_pipeline
python embed_all.py
```

### 3. Verify Embeddings

```bash
# Verify embeddings stored in Qdrant
python ../tests/verify_qdrant.py
```

### 4. View Collected Data

```bash
cd collector-mongodb
python mongo.py
```

## Data Collectors

### GitHub Trending Collector
- **File:** `github-trending-collector/scrape.py`
- **Collects:** Repository metadata, stars, language, topics, cleaned README text
- **Features:** Supports daily/weekly/monthly trending, language detection, auto-translation
- **Configuration:** Adjust period, active_days filter in code

### arXiv Paper Collector
- **File:** `arxiv-collector/scrape.py`
- **Collects:** Paper title, abstract, authors, categories, publication date
- **Categories:** cs.AI, cs.CL, cs.CV, cs.LG, cs.MA, cs.RO, cs.DC, cs.CR, cs.SY, stat.ML
- **Configuration:** Adjust max_results, days_back in code

### HackerNews Tech Collector
- **File:** `tech-news-collector/scrape.py`
- **Collects:** Story title, URL, score, comments, author, publication date
- **Features:** Tech keyword filtering, minimum score threshold
- **Configuration:** Adjust max_results, score_threshold in code

## Embedding Pipeline

### Architecture
- **Model:** all-MiniLM-L6-v2 (Sentence Transformers)
- **Dimensions:** 384-dimensional vectors
- **Database:** Qdrant (file-based persistence at `./qdrant_storage/`)
- **Collections:** github_embeddings, arxiv_embeddings, news_embeddings

### Main Pipeline
```bash
cd embedding_pipeline
python embed_all.py
```

Process includes:
1. Connect to MongoDB and load all collected data
2. Initialize Qdrant with file-based storage
3. Generate 384-dimensional embeddings for each document
4. Store embeddings with metadata for semantic search

## MongoDB Collections

### github_repos
```
owner, name, description, language, topics, stars_total, stars_trending,
readme_text, created_at, updated_at, repo_url, scraped_at
```

### arxiv_papers
```
arxiv_id, title, abstract, authors, categories, published, pdf_url, 
arxiv_url, scraped_at
```

### tech_news
```
hackernews_id, title, url, score, comments, author, published_at, source, scraped_at
```

## Testing & Verification

```bash
# Verify embeddings stored in Qdrant
python tests/verify_qdrant.py

# Test embedding functionality
python tests/test_embeddings.py

# Additional embedding verification
python tests/verify_embeddings.py
```

## Key Features

- **Multi-Source Aggregation:** Combines GitHub, arXiv, and HackerNews in one place
- **Automatic Translation:** Non-English content automatically translated to English
- **Text Cleaning:** README files and content cleaned (HTML, badges, emojis, URLs removed)
- **Language Detection:** Automatic language detection via langdetect
- **Quality Filtering:** Score and activity thresholds ensure quality data
- **Vector Search:** Semantic search via Qdrant embeddings (384-dim)
- **Historical Tracking:** Timestamps on all entries for trend analysis
- **No Data Loss:** Each run creates new entries, historical data preserved

## Why Three Data Sources?

- **GitHub:** What open-source developers are actively building
- **arXiv:** Cutting-edge AI/ML research breakthroughs
- **HackerNews:** What the tech community is discussing and excited about

Combined = Complete view of tech ecosystem trends

## Notes

- All data stored in MongoDB with timestamps for trend tracking
- Vector embeddings persisted to `./qdrant_storage/` (DO NOT DELETE)
- Scrapers automatically save to MongoDB when run
- Viewer connects to local MongoDB by default
- All content automatically translated to English for consistency
