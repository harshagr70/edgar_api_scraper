# Financial Data API - Quick Start

## What's Been Created

✅ **API Server** (`api_server.py`) - FastAPI endpoints for frontend integration
✅ **Docker Setup** (Dockerfile, docker-compose.yml) - Containerization
✅ **API Documentation** (`pipeline_detail.md`) - JSON payload structure
✅ **Deployment Guide** (`DEPLOYMENT.md`) - Step-by-step deployment instructions

## Quick Start

### 1. Test Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python api_server.py

# API will be available at http://localhost:8000
```

### 2. Build Docker Image
```bash
# Build
docker build -t financial-data-api .

# Run
docker run -p 8000:8000 financial-data-api
```

### 3. Using Docker Compose (Easiest)
```bash
docker-compose up -d
```

## API Endpoints

### Check Available Years
```bash
POST http://localhost:8000/check-availability
Body: {"ticker": "AAPL"}
```

### Fetch Financial Data
```bash
POST http://localhost:8000/fetch-financials
Body: {"ticker": "AAPL", "years_back": 3}
```

### Health Check
```bash
GET http://localhost:8000/health
```

### Interactive Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Response Structure

See `pipeline_detail.md` for complete JSON payload structure and field descriptions.

## For Frontend Developer

The API returns structured financial data with:
- **Income Statement**: Revenue, expenses, net income by year
- **Balance Sheet**: Assets, liabilities, equity by year  
- **Cash Flow**: Operating, investing, financing activities by year
- **Source URLs**: Direct links to SEC filings for verification

All values are in millions (e.g., 383285 = $383.285 billion).

## Next Steps

1. **Test the API** with different tickers (AAPL, MSFT, GOOGL)
2. **Review the response structure** in `pipeline_detail.md`
3. **Deploy to cloud** using instructions in `DEPLOYMENT.md`
4. **Integrate with frontend** using the API endpoints

For detailed deployment options (AWS, GCP, Azure, Kubernetes), see `DEPLOYMENT.md`.

