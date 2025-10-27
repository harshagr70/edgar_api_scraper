from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
from helper.api_helper_functions import get_available_years_count, get_multi_year_financials_parallel
from helper.financial_merger_helper import build_unified_catalog_all_statements

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial Data API",
    description="API to fetch and process SEC EDGAR financial statements",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class CheckAvailabilityRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL, MSFT)")

class CheckAvailabilityResponse(BaseModel):
    ticker: str
    available_years_count: int
    status: str

class FetchFinancialsRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    years_back: int = Field(..., ge=1, le=15, description="Number of years to fetch (1-15)")

class FetchFinancialsResponse(BaseModel):
    ticker: str
    status: str
    summary: Dict[str, Any]
    source_urls: Dict[str, List[str]]
    statements: Dict[str, Any]
    error: Optional[str] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for container monitoring"""
    return {"status": "healthy", "service": "financial-data-api"}

# Check availability endpoint
@app.post("/check-availability", response_model=CheckAvailabilityResponse)
async def check_availability(request: CheckAvailabilityRequest):
    """
    Check how many years of 10-K filings are available for a ticker.
    
    Returns the count of available years without fetching actual data.
    """
    try:
        ticker = request.ticker.upper()
        logger.info(f"Checking availability for ticker: {ticker}")
        
        available_count = get_available_years_count(ticker)
        
        return {
            "ticker": ticker,
            "available_years_count": available_count,
            "status": "success"
        }
    except ValueError as e:
        logger.error(f"Value error for {request.ticker}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error checking availability: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking availability: {str(e)}")

# Fetch financial data endpoint
@app.post("/fetch-financials", response_model=Dict[str, Any])
async def fetch_financials(request: FetchFinancialsRequest):
    """
    Fetch and process financial statements for a ticker.
    
    Returns structured JSON with income statement, balance sheet, and cash flow statement
    across multiple years with source URLs for verification.
    """
    try:
        ticker = request.ticker.upper()
        years_back = request.years_back
        
        logger.info(f"Fetching {years_back} years of data for {ticker}")
        
        # Fetch raw data
        raw_data = get_multi_year_financials_parallel(ticker, years_back=years_back)
        
        if not raw_data or raw_data.get('fetched_years', 0) == 0:
            return {
                "ticker": ticker,
                "status": "error",
                "error": "No financial data could be retrieved",
                "summary": {},
                "source_urls": {},
                "statements": {}
            }
        
        # Build unified catalogs
        unified_data = build_unified_catalog_all_statements(raw_data)
        
        # Extract source URLs
        source_urls = {
            "income_statement": unified_data.get("income_statement_url", []),
            "balance_sheet": unified_data.get("balance_sheet_url", []),
            "cash_flow_statement": unified_data.get("cash_flow_statement_url", [])
        }
        
        # Format statements for API response
        statements = {}
        for stmt_type in ["income_statement", "balance_sheet", "cash_flow_statement"]:
            stmt_data = unified_data.get(stmt_type, {})
            if stmt_data:
                # Convert OrderedDict to regular dict with proper structure
                statements[stmt_type] = format_statement_for_api(stmt_data, stmt_type)
        
        return {
            "ticker": ticker,
            "status": "success",
            "summary": {
                "requested_years": years_back,
                "available_years": raw_data.get('available_years_count', 0),
                "fetched_years": raw_data.get('fetched_years', 0)
            },
            "source_urls": source_urls,
            "statements": statements
        }
        
    except ValueError as e:
        logger.error(f"Value error for {request.ticker}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        logger.error(f"Connection error for {request.ticker}: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error fetching financials: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching financial data: {str(e)}")

def format_statement_for_api(statement_dict: Dict, statement_type: str) -> Dict:
    """
    Format the statement OrderedDict into a clean API response structure.
    """
    result = {
        "statement_type": statement_type,
        "years": [],
        "sections": {}
    }
    
    # Collect all years
    all_years = set()
    sections = {}
    
    for key, item in statement_dict.items():
        if not isinstance(item, dict):
            continue
            
        section_label = item.get("section_label", "Unknown Section")
        
        # Get years from values
        values = item.get("values", {})
        all_years.update(values.keys())
        
        # Initialize section if needed
        if section_label not in sections:
            sections[section_label] = []
        
        # Add line item
        line_item = {
            "item_label": item.get("item_label", "N/A"),
            "values": values,
            "gaap_code": item.get("item_gaap")
        }
        sections[section_label].append(line_item)
    
    # Sort years descending
    result["years"] = sorted(all_years, reverse=True)
    result["sections"] = sections
    
    return result

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "Financial Data API",
        "version": "1.0.0",
        "endpoints": {
            "check_availability": "/check-availability",
            "fetch_financials": "/fetch-financials",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

