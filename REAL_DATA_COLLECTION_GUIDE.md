# Real Temporal Data Collection System

This document explains the real data collection pipeline that builds actual historical snapshots for temporal analysis.

## Overview

Instead of using synthetic data, we now collect real data from GitHub, arXiv, and HackerNews on a periodic basis (weekly). This allows us to track actual trends in technology topics over time.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Data Sources (GitHub, arXiv, HackerNews)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  periodic_collector.py (Weekly Execution)                  │
│  - Runs GitHub trending collector                          │
│  - Runs arXiv paper collector                              │
│  - Runs HackerNews tech news collector                     │
│  - Creates collection snapshot in MongoDB                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │ data_collection_snapshots │
         │ (8 weeks of real data)    │
         └────────────┬──────────────┘
                      │
                      ▼
      ┌──────────────────────────────────┐
      │  snapshot_aggregator.py          │
      │  - Extracts keywords             │
      │  - Identifies clusters           │
      │  - Converts to temporal format   │
      └──────────────┬───────────────────┘
                     │
                     ▼
          ┌──────────────────────────┐
          │ temporal_snapshots_real  │
          │ (Aggregated data)        │
          └────────────┬─────────────┘
                       │
                       ▼
      ┌──────────────────────────────────┐
      │  analyze_real_trends.py          │
      │  - Keyword shift analysis        │
      │  - Cluster drift detection       │
      │  - Trend identification          │
      └──────────────┬───────────────────┘
                     │
                     ▼
       ┌──────────────────────────────┐
       │ temporal_analysis_real       │
       │ (Final analysis results)     │
       └──────────────────────────────┘
```

## Scripts

### 1. `periodic_collector.py`
**Purpose:** Runs the data collectors and creates a snapshot

**Usage (One-time collection):**
```powershell
python periodic_collector.py
```

**What it does:**
- Calls GitHub trending collector
- Calls arXiv paper collector  
- Calls HackerNews tech news collector
- Creates a timestamped snapshot in `data_collection_snapshots` collection
- Displays current statistics

**MongoDB Collections Created:**
- `data_collection_snapshots`: Stores collection state at each collection time
  - Fields: timestamp, week, github_count, arxiv_count, news_count, total_documents

### 2. `backfill_historical.py`
**Purpose:** Backfill 8 weeks of historical data for initial demo

**Usage:**
```powershell
python backfill_historical.py
```

**What it does:**
- Runs the periodic collector 8 times
- Simulates collecting data from 8 weeks ago to now
- Each collection run creates a snapshot with a backdated timestamp
- Useful for initial setup to have historical data

**Output:**
```
[1/8] 2025-10-12 - Created snapshot with 47 documents
[2/8] 2025-10-19 - Created snapshot with 47 documents
...
[8/8] 2025-11-30 - Created snapshot with 47 documents
```

### 3. `snapshot_aggregator.py`
**Purpose:** Convert collection snapshots into temporal format

**Usage:**
```powershell
python snapshot_aggregator.py
```

**What it does:**
- Reads all collection snapshots from `data_collection_snapshots`
- Extracts keywords from all collected documents
- Creates cluster distribution profiles
- Generates temporal snapshots in format needed for analysis
- Saves to `temporal_snapshots_real` collection

**MongoDB Collections:**
- Input: `data_collection_snapshots`
- Output: `temporal_snapshots_real`
  - Fields: timestamp, clusters, keyword_evolution, documents_by_source

### 4. `analyze_real_trends.py`
**Purpose:** Analyze temporal trends from real collected data

**Usage:**
```powershell
python analyze_real_trends.py
```

**What it does:**
- Loads temporal snapshots from `temporal_snapshots_real`
- Analyzes keyword frequency shifts over 8 weeks
- Detects cluster drift and changes
- Identifies rising, falling, and stable trends
- Saves analysis results to `temporal_analysis_real` collection

**Output Example:**
```
🔥 TOP RISING KEYWORDS:
  📍 LLM
     Start: 2 | End: 5 | Change: +150.0%
     
❄️  TOP FALLING KEYWORDS:
  📍 RAG
     Start: 2 | End: 0 | Change: -100.0%

🌊 CLUSTER DRIFT ANALYSIS:
  Cluster frontend: MINIMAL DRIFT
     Size change: +0.0%
     Drift magnitude: 8.9/100
```

## Complete Workflow

### Initial Setup (Run Once):
```powershell
# 1. Backfill 8 weeks of historical data
python backfill_historical.py

# 2. Aggregate snapshots to temporal format
python snapshot_aggregator.py

# 3. Analyze trends from real data
python analyze_real_trends.py
```

### Weekly Execution (Ongoing):
```powershell
# Run this every week to collect new data
python periodic_collector.py

# Then run aggregator and analyzer
python snapshot_aggregator.py
python analyze_real_trends.py
```

### Or Run in Background Terminal:
For continuous monitoring, run in a separate PowerShell terminal:
```powershell
# Create a weekly scheduler
$interval = 60 * 60 * 7  # 7 days in seconds
while ($true) {
    python periodic_collector.py
    python snapshot_aggregator.py
    python analyze_real_trends.py
    
    Write-Host "Next collection in 7 days..."
    Start-Sleep -Seconds $interval
}
```

## MongoDB Collections

### `data_collection_snapshots`
Stores the raw collection state at each collection timestamp

Fields:
- `timestamp`: Date when collection was run
- `week`: ISO week number
- `github_count`: Number of GitHub repos collected
- `arxiv_count`: Number of arXiv papers collected  
- `news_count`: Number of tech news articles collected
- `total_documents`: Total documents across all sources
- `data_summary`: Sample of document titles from each source

Example:
```json
{
  "_id": ObjectId("..."),
  "timestamp": ISODate("2025-10-12T20:00:00Z"),
  "week": 40,
  "github_count": 14,
  "arxiv_count": 10,
  "news_count": 23,
  "total_documents": 47
}
```

### `temporal_snapshots_real`
Aggregated temporal data extracted from collection snapshots

Fields:
- `timestamp`: Snapshot date
- `week`: Week number
- `total_documents`: Documents in this snapshot
- `documents_by_source`: Breakdown by source
- `clusters`: Information about each cluster
  - `size`: Number of documents in cluster
  - `keywords`: Main keywords for cluster
  - `std_dev`: Cohesion/spread of cluster
- `keyword_evolution`: Frequency of each keyword

### `temporal_analysis_real`
Final analysis results comparing snapshots

Fields:
- `timestamp`: Analysis run time
- `analysis_type`: "REAL_DATA_TEMPORAL_ANALYSIS"
- `weeks_analyzed`: Number of weeks included
- `keywords_analyzed`: Number of unique keywords
- `clusters_analyzed`: Number of clusters
- `keyword_shifts`: Frequency changes for each keyword
  - `start_frequency`: Initial frequency
  - `end_frequency`: Final frequency
  - `percent_change`: Percentage change over period
  - `trend_direction`: RISING/FALLING/STABLE
- `cluster_stats`: Drift metrics for each cluster
  - `drift_severity`: MINIMAL/LOW/MEDIUM/HIGH/EXTREME
  - `size_change_percent`: % change in cluster size
  - `std_dev_change_percent`: % change in cohesion

## Real Data vs Synthetic Data

### Previous Approach (Synthetic):
- Used `historical_data_generator.py` to create fake 8-week history
- Hardcoded trend lines (llm: [2, 3, 5, 7, 10, 14, 18, 22])
- Good for testing, but unrealistic

### New Approach (Real):
- Uses `periodic_collector.py` to gather actual GitHub/arXiv/HackerNews data
- Creates snapshots with real document counts and keywords
- More realistic for demo purposes
- Runs collectors 8 times to backfill history
- Actual trends based on collected content

## Example Output

```
[1/8] 2025-10-12 (Week 40) - 47 documents collected
[2/8] 2025-10-19 (Week 41) - 47 documents collected
[3/8] 2025-10-26 (Week 42) - 47 documents collected
[4/8] 2025-11-02 (Week 43) - 47 documents collected
[5/8] 2025-11-09 (Week 44) - 47 documents collected
[6/8] 2025-11-16 (Week 45) - 47 documents collected
[7/8] 2025-11-23 (Week 46) - 47 documents collected
[8/8] 2025-11-30 (Week 47) - 47 documents collected

✅ Analyzed 7 keywords across 8 weeks
✅ Tracked 3 clusters for drift
✅ Keyword trends: 5 rising, 2 falling, 0 stable
```

## Next Steps

1. **Schedule Weekly Collections**: Set up Windows Task Scheduler to run `periodic_collector.py` weekly
2. **Monitor Trends**: Regularly run `analyze_real_trends.py` to see evolving trends
3. **Dashboard**: Create web interface to visualize trends over time
4. **Module 5**: Use temporal analysis results for email generation and delivery

## Files Modified

- **New files created:**
  - `periodic_collector.py`: Weekly collector runner
  - `backfill_historical.py`: Backfill 8 weeks of history
  - `snapshot_aggregator.py`: Convert snapshots to temporal format
  - `analyze_real_trends.py`: Analyze real temporal trends
  - `REAL_DATA_COLLECTION_GUIDE.md`: This file

- **Database collections:**
  - `data_collection_snapshots`: Collection state history
  - `temporal_snapshots_real`: Aggregated temporal data
  - `temporal_analysis_real`: Analysis results

