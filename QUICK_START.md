# Quick Start Guide

## Prerequisites
- Docker Desktop installed and running
- Python 3.11+ (for local testing)

## Setup

```bash
# 1. Create .secrets file
cp .secrets.example .secrets

# 2. Edit .secrets and add your SEC credentials
# Example: SEC_USER_AGENT=your-email@example.com

# 3. Secure the file
chmod 600 .secrets
```

## Option 1: Run with Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

## Option 2: Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
python api_server.py
```

## Test the API

```bash
# Health check
curl http://localhost:8000/health

# Check availability
curl -X POST http://localhost:8000/check-availability \
     -H "Content-Type: application/json" \
     -d '{"ticker": "AAPL"}'

# Fetch financial data
curl -X POST http://localhost:8000/fetch-financials \
     -H "Content-Type: application/json" \
     -d '{"ticker": "AAPL", "years_back": 3}'
```

## API Endpoints

1. **Health Check**: `GET http://localhost:8000/health`
2. **Check Availability**: `POST http://localhost:8000/check-availability`
3. **Fetch Financials**: `POST http://localhost:8000/fetch-financials`
4. **API Docs**: `http://localhost:8000/docs`

## Streamlit UI (Optional)

```bash
streamlit run financial_viewer.py
```

## Documentation

- **API Structure**: See `pipeline_detail.md`
- **Deployment**: See `DEPLOYMENT.md`

