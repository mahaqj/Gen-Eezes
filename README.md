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
├── clustering_pipeline/          # Clustering & topic modeling
│   ├── cluster_all.py           # Main clustering pipeline
│   ├── clustering_handler.py    # Clustering algorithms (K-means, DBSCAN, HDBSCAN)
│   ├── verify_clusters.py       # Verify clustering results
│   └── __init__.py              # Module initialization
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

### 3. Clustering & Topic Modeling

```bash
# Cluster embeddings and extract topics
cd clustering_pipeline
python cluster_all.py

# Verify clustering results
python verify_clusters.py
```

### 4. Verify Embeddings

```bash
# Verify embeddings stored in Qdrant
python ../tests/verify_qdrant.py
```

### 5. View Collected Data

```bash
cd collector-mongodb
python mongo.py
```

### 6. Newsletter Signup Website

```bash
cd website
python run_server.py
```

Visit `http://localhost:8000` to access the website. Users can sign up for the newsletter by entering their first name and email - data is automatically stored in MongoDB.

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

## Clustering & Topic Modeling Pipeline

### Overview
Groups similar items into meaningful topic clusters using multiple clustering algorithms.

### Architecture
- **Algorithms:**
  - K-Means: Partitions embeddings into k clusters with dynamic k based on dataset size
  - DBSCAN: Density-based clustering (identifies noise points)
  - HDBSCAN: Hierarchical density-based clustering
- **Keyword Extraction:** TF-IDF vectorization to extract top keywords per cluster
- **Representative Samples:** Selects closest points to cluster centroids
- **Storage:** All results stored in MongoDB `clusters` collection

### Main Pipeline
```bash
cd clustering_pipeline
python cluster_all.py
```

Process includes:
1. Load embeddings from Qdrant collections
2. Perform K-means, DBSCAN, and HDBSCAN clustering
3. Extract keywords using TF-IDF
4. Select representative samples from each cluster
5. Compute cluster statistics (size, centroid, std_dev)
6. Store all results in MongoDB

### Verification
```bash
python verify_clusters.py
```

Displays clustering results for each collection with:
- Number of clusters per algorithm
- Cluster sizes
- Top keywords per cluster
- Representative sample items

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

## Newsletter Website

**File:** `website/run_server.py`

Interactive website for newsletter signups. Users enter their first name and email to subscribe.

**Usage:**

```bash
cd website
python run_server.py
```

Visit `http://localhost:8000`

**Features:**
- Clean, responsive UI with dark mode toggle
- Form validation for first name and email
- Real-time feedback on signup success/error
- Newsletter data stored in MongoDB `users` collection
- View all subscribers in data viewer (option 8-9 in mongo.py)

**View Subscribers:**

```bash
cd collector-mongodb
python mongo.py
# Select option 8: View newsletter subscribers
# Select option 9: View user statistics
```

## Key Features

- **Multi-Source Aggregation:** Combines GitHub, arXiv, and HackerNews in one place
- **Automatic Translation:** Non-English content automatically translated to English
- **Text Cleaning:** README files and content cleaned (HTML, badges, emojis, URLs removed)
- **Language Detection:** Automatic language detection via langdetect
- **Quality Filtering:** Score and activity thresholds ensure quality data
- **Vector Search:** Semantic search via Qdrant embeddings (384-dim)
- **Newsletter:** Web-based signup with MongoDB persistence
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

## Project Status

### Completed Modules ✅

**Module 1: Data Collection** ✅ 
- GitHub trending repositories collector
- arXiv research papers collector
- HackerNews tech news collector
- All data persisted to MongoDB

**Module 2: Embedding & Preprocessing** ✅
- Text cleaning (HTML, boilerplate removal)
- Embedding generation (all-MiniLM-L6-v2, 384-dim)
- Vector storage in Qdrant
- 47 documents embedded and ready for clustering

**Module 3: Clustering & Topic Modeling** ✅
- K-Means clustering (primary algorithm)
- DBSCAN clustering (for density-based analysis)
- HDBSCAN clustering (hierarchical density-based)
- Keyword extraction per cluster (TF-IDF)
- Representative sample selection
- Results stored in MongoDB

### In Progress / TODO ⏳

**Module 4: Email Generation**
- Extract top topics from clusters
- Generate daily/weekly summaries
- Create email templates with trends
- Aggregate insights across sources

**Module 5: Email Delivery**
- Email scheduling system
- Integration with SMTP server
- Newsletter subscription management
- Unsubscribe handling

### Sample Results

**Current Data:**
- 14 GitHub repositories
- 10 arXiv papers  
- 24 HackerNews stories
- **Total: 48 documents clustered**

**Clustering Results:**
- GitHub: 5 K-means clusters
- arXiv: 3 K-means clusters
- News: 5 K-means clusters

