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

### 5. Temporal Analysis & Trend Detection (Module 4)

```bash
# Backfill 52 weeks of historical snapshots
python backfill_historical.py

# Aggregate snapshots to temporal format
python snapshot_aggregator.py

# Analyze trends from real data
python analyze_real_trends.py
```

**Output:** Trend analysis showing rising/falling keywords and cluster drift patterns
**Results:** Stored in MongoDB temporal_snapshots_real and temporal_analysis_real collections

### 6. Email Generation & Delivery (Module 5)

```bash
# Generate and send weekly newsletter to all subscribers
python email_pipeline/main_email_pipeline.py
```

**Features:**
- Generates ONE newsletter template using Gemini 2.5 LLM
- Personalizes with subscriber first names
- Sends via Gmail API with OAuth 2.0
- Logs delivery results to MongoDB
- Includes Module 4 trend data and analysis

**Setup:**
```bash
# Set environment variables
$env:GEMINI_API_KEY = "your-gemini-api-key"
$env:GMAIL_CREDENTIALS_FILE = "path/to/credentials.json"
$env:GMAIL_TOKEN_FILE = "path/to/token.json"
$env:SENDER_EMAIL = "your-email@gmail.com"

# Run pipeline
python email_pipeline/main_email_pipeline.py
```

**Output:** Personalized HTML emails with brand design, sent to all subscribed users

### 7. View Collected Data

```bash
cd collector-mongodb
python mongo.py
```

### 8. Newsletter Signup Website

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

## Temporal Analysis & Trend Detection (Module 4)

### Overview
Analyzes keyword frequency shifts and cluster drift over time using real collected data across 52 weeks.

### Architecture
- **Data Source:** Periodic data collection from GitHub, arXiv, and HackerNews
- **Analysis Period:** 52 weeks (configurable)
- **Algorithms:**
  - Keyword Shift Analysis: Tracks frequency changes (RISING/FALLING/STABLE)
  - Cluster Drift Detection: Measures size/cohesion changes (5 severity levels)
  - Time Series Modeling: Linear regression on temporal metrics
  - Trend Labeling: Automatic classification with confidence scoring

### Key Scripts

**periodic_collector.py**
- Runs data collectors on demand
- Creates timestamped collection snapshots
- Use: Daily/weekly collection of fresh data
```bash
python periodic_collector.py
```

**backfill_historical.py**
- Creates N weeks of historical snapshots
- Runs collectors with backdated timestamps
- Use: Initial setup with 52 weeks of data
```bash
python backfill_historical.py  # Creates 52 weeks
```

**snapshot_aggregator.py**
- Converts collection snapshots to temporal format
- Extracts keywords and cluster features
- Output: temporal_snapshots_real collection
```bash
python snapshot_aggregator.py
```

**analyze_real_trends.py**
- Main analysis pipeline
- Detects keyword shifts and cluster drift
- Generates comprehensive trend report
- Output: temporal_analysis_real collection
```bash
python analyze_real_trends.py
```

### 52-Week Results Example

**Data Period:** December 8, 2024 - November 30, 2025

**Cluster Evolution:**
- AI/LLM: +93.3% growth (EXTREME DRIFT)
- Frontend: 0.0% change (MINIMAL DRIFT)
- DevOps: -66.7% decline (EXTREME DRIFT)

**Keyword Trends:**
- Rising: embedding (+600%), transformer (+500%), llm (+350%)
- Falling: kubernetes (-100%), docker (-100%), devops (-100%)
- Stable: react (-11%), javascript (+14%)

**Storage:** 52 temporal snapshots analyzed → Results in MongoDB

## Testing & Verification

```bash
# Verify embeddings stored in Qdrant
python tests/verify_qdrant.py

# Test embedding functionality
python tests/test_embeddings.py

# Additional embedding verification
python tests/verify_embeddings.py
```

## Email Generation & Delivery Pipeline (Module 5)

### Overview
Generates personalized AI newsletters using Gemini 2.5 LLM and delivers via Gmail API with OAuth 2.0.

### Architecture
- **LLM:** Google Gemini 2.5 (gemini-2.5-flash) for newsletter generation
- **Email:** Gmail API with OAuth 2.0 authentication
- **Database:** MongoDB for user subscriptions and delivery logging
- **Template:** Single high-quality template with name variable replacement
- **Personalization:** Automatic first name extraction from email addresses

### Key Scripts

**main_email_pipeline.py**
- Main orchestrator for complete pipeline
- Retrieves Module 4 trend data
- Generates newsletter with Gemini 2.5
- Personalizes for each subscriber
- Sends via Gmail API
- Logs results to MongoDB

**newsletter_generator.py**
- Gemini 2.5 integration
- Prompt engineering for professional newsletters
- HTML and plain text output
- Brand design: Pink header (#c93e8b), black text
- Heart emoji accents

**email_sender_gmail.py**
- Gmail API OAuth 2.0 authentication
- Batch email sending with retry logic
- MIME message construction
- Token refresh handling
- Rate limiting (2-second delays)

**retrieval_context.py**
- Extracts trend data from Module 4
- Converts to natural language format
- Prepares context for LLM

**email_scheduler.py**
- Weekly scheduling (default: Sunday 8 AM)
- Cron-based execution
- Automatic pipeline triggering

### Performance

- **Newsletter Generation:** 20 seconds (single Gemini call)
- **Email Delivery:** 10 seconds (4 recipients with delays)
- **Total Pipeline:** 30 seconds
- **Cost Reduction:** 75% (single template vs 4 separate generations)
- **Success Rate:** 100%

### Design

**Newsletter Template:**
- Header: Brand pink (#c93e8b) with white text
- Body: Pure black text (#000000) on white background
- Content: Personalized greeting, trend analysis, insights
- Footer: "The Gen-Eezes Team" with pink heart emojis 💕💖💗
- Format: HTML with plain text fallback

**Personalization:**
- Automatic name extraction from email (nabeeha529@gmail.com → Nabeeha)
- Subject line includes recipient name
- Body greeting starts with first name

### Database Schema

**Collection: email_logs**
```
{
  "user_email": "nabeeha529@gmail.com",
  "recipient_name": "Nabeeha",
  "subject": "Nabeeha, AI Dominates, DevOps Retreats: Your Weekly Tech Shift!",
  "delivery_status": "success",
  "message_id": "19afaf863f7ce91a",
  "sent_timestamp": ISODate("2025-12-07T22:39:33.886Z"),
  "template_used": "[USER_NAME]",
  "pipeline_run_id": "2025-12-07T22:39:11.776002"
}
```

### Testing & Verification

```bash
# Run complete pipeline once
python email_pipeline/main_email_pipeline.py

# Run weekly scheduler
python email_pipeline/email_scheduler.py

# Check delivery logs
cd collector-mongodb
python mongo.py
# Select option 10: View email delivery logs
```

### Setup Checklist

- ✅ Gmail API credentials downloaded (credentials.json)
- ✅ First OAuth authentication completed (generates token.json)
- ✅ Gemini API key obtained
- ✅ MongoDB running with users collection
- ✅ Newsletter subscribers registered via website
- ✅ Environment variables configured



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

**Module 1: Data Collection** 
- GitHub trending repositories collector
- arXiv research papers collector
- HackerNews tech news collector
- All data persisted to MongoDB

**Module 2: Embedding & Preprocessing** 
- Text cleaning (HTML, boilerplate removal)
- Embedding generation (all-MiniLM-L6-v2, 384-dim)
- Vector storage in Qdrant
- 47 documents embedded and ready for clustering

**Module 3: Clustering & Topic Modeling** 
- K-Means clustering (primary algorithm)
- DBSCAN clustering (for density-based analysis)
- HDBSCAN clustering (hierarchical density-based)
- Keyword extraction per cluster (TF-IDF)
- Representative sample selection
- Results stored in MongoDB

**Module 4: Temporal Analysis & Trend Detection** 
- 52-week real data collection (periodic_collector.py)
- Historical data backfilling (backfill_historical.py)
- Temporal snapshot aggregation (snapshot_aggregator.py)
- Keyword shift analysis (rising/falling/stable trends)
- Cluster drift detection (5 severity levels)
- Time series modeling and forecasting
- Comprehensive trend reporting

**Module 5: Email Generation & Delivery** 
- Gemini 2.5 LLM integration for newsletter generation
- Gmail API OAuth 2.0 authentication and sending
- Single template generation with name personalization
- Automatic first name extraction from emails
- MongoDB delivery tracking and logging
- 4/4 successful test delivery (100% success rate)
- 48% performance improvement vs initial approach

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

**Trend Analysis (52 Weeks):**
- AI/LLM growth: +93.3% (EXTREME DRIFT)
- DevOps decline: -66.7% (EXTREME DRIFT)
- Frontend stability: 0.0% change (MINIMAL DRIFT)

**Email Delivery (Module 5):**
- Recipients: 4 subscribed users
- Success rate: 100% (4/4)
- Execution time: 30 seconds
- Template: Gemini 2.5 generated with personalization

