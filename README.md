# Edgar Financial Statement Analyzer

A Python tool that fetches multi-year financial statements from SEC EDGAR, normalizes inconsistent line-item labels across years, and provides a unified API for financial data analysis.

## Quick Start

```bash
# Setup secrets
cp .secrets.example .secrets
chmod 600 .secrets

# Run with Docker
docker-compose up -d

# Or run locally
pip install -r requirements.txt
python api_server.py
```

## Documentation Files

| File | Purpose | When to Use |
|------|---------|-------------|
| **QUICK_START.md** | Setup and testing guide | Getting started locally or with Docker |
| **pipeline_detail.md** | Complete API documentation with JSON structure | Integrating with frontend or building clients |
| **DEPLOYMENT.md** | Production deployment options (AWS, GCP, Azure) | Deploying to cloud environments |
| **README_API.md** | Quick API overview and endpoints | Quick reference for API usage |

## What This Does

- Fetches financial data from SEC Edgar API
- Merges multi-year statements with consistent line items
- Provides FastAPI endpoints for programmatic access
- Includes Streamlit UI for interactive analysis

## Key Features

- **Normalization**: Handles inconsistent label names across years
- **GAAP Alignment**: Uses official accounting codes for matching
- **Multi-year Analysis**: Supports 3+ years of historical data
- **Excel Export**: Clean formatted output for analysis

## Architecture

- **API Server**: `api_server.py` - FastAPI endpoints
- **Helper Functions**: `helper/api_helper_functions.py` - Data fetching logic
- **Data Merger**: `helper/financial_merger_helper.py` - Statement normalization
- **Streamlit UI**: `financial_viewer.py` - Interactive web interface

