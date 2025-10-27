# Financial Data Pipeline - API Documentation

## Overview
This pipeline fetches and processes financial statements from SEC EDGAR for a given stock ticker, returning structured JSON data ready for frontend integration.

## Endpoints Structure

### 1. Check Available Years
**Endpoint:** `/check-availability`
**Method:** `POST`
**Request:**
```json
{
  "ticker": "AAPL"
}
```

**Response:**
```json
{
  "ticker": "AAPL",
  "available_years_count": 10,
  "status": "success"
}
```

---

### 2. Fetch Financial Data
**Endpoint:** `/fetch-financials`
**Method:** `POST`
**Request:**
```json
{
  "ticker": "AAPL",
  "years_back": 3
}
```

**Response Structure:**
```json
{
  "ticker": "AAPL",
  "status": "success",
  "summary": {
    "requested_years": 3,
    "available_years": 10,
    "fetched_years": 3,
    "requested_years": 3
  },
  "source_urls": {
    "income_statement": [
      "https://www.sec.gov/Archives/edgar/data/320193/000032019323000123/aapl-20230930.htm",
      "https://www.sec.gov/Archives/edgar/data/320193/000032019322000009/aapl-20220930.htm",
      "https://www.sec.gov/Archives/edgar/data/320193/000032019321000010/aapl-20210930.htm"
    ],
    "balance_sheet": [
      "https://www.sec.gov/Archives/edgar/data/320193/000032019323000123/aapl-20230930.htm",
      "https://www.sec.gov/Archives/edgar/data/320193/000032019322000009/aapl-20220930.htm",
      "https://www.sec.gov/Archives/edgar/data/320193/000032019321000010/aapl-20210930.htm"
    ],
    "cash_flow_statement": [
      "https://www.sec.gov/Archives/edgar/data/320193/000032019323000123/aapl-20230930.htm",
      "https://www.sec.gov/Archives/edgar/data/320193/000032019322000009/aapl-20220930.htm",
      "https://www.sec.gov/Archives/edgar/data/320193/000032019321000010/aapl-20210930.htm"
    ]
  },
  "statements": {
    "income_statement": {
      "statement_type": "income_statement",
      "years": ["2023", "2022", "2021"],
      "sections": {
        "Revenue": [
          {
            "item_label": "Total Revenue",
            "values": {
              "2023": 383285.0,
              "2022": 394328.0,
              "2021": 365817.0
            },
            "gaap_code": "us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax"
          },
          {
            "item_label": "Cost of Goods Sold",
            "values": {
              "2023": 214137.0,
              "2022": 223546.0,
              "2021": 192266.0
            },
            "gaap_code": "us-gaap_CostOfRevenue"
          }
        ],
        "Operating Expenses": [
          {
            "item_label": "Research and Development",
            "values": {
              "2023": 29915.0,
              "2022": 26251.0,
              "2021": 21914.0
            },
            "gaap_code": "us-gaap_ResearchAndDevelopmentExpense"
          },
          {
            "item_label": "Selling, General and Administrative",
            "values": {
              "2023": 24948.0,
              "2022": 25094.0,
              "2021": 21973.0
            },
            "gaap_code": "us-gaap_SellingGeneralAndAdministrativeExpense"
          }
        ],
        "Income Statement": [
          {
            "item_label": "Net Income",
            "values": {
              "2023": 99803.0,
              "2022": 99803.0,
              "2021": 94680.0
            },
            "gaap_code": "us-gaap_ProfitLoss"
          }
        ]
      }
    },
    "balance_sheet": {
      "statement_type": "balance_sheet",
      "years": ["2023", "2022", "2021"],
      "sections": {
        "Assets": [
          {
            "item_label": "Cash and Cash Equivalents",
            "values": {
              "2023": 29965.0,
              "2022": 23646.0,
              "2021": 34940.0
            },
            "gaap_code": "us-gaap_CashAndCashEquivalentsAtCarryingValue"
          },
          {
            "item_label": "Accounts Receivable",
            "values": {
              "2023": 29508.0,
              "2022": 28184.0,
              "2021": 26278.0
            },
            "gaap_code": "us-gaap_AccountsReceivableNetCurrent"
          },
          {
            "item_label": "Inventories",
            "values": {
              "2023": 6331.0,
              "2022": 4946.0,
              "2021": 6580.0
            },
            "gaap_code": "us-gaap_InventoryNet"
          },
          {
            "item_label": "Property, Plant and Equipment",
            "values": {
              "2023": 43692.0,
              "2022": 42117.0,
              "2021": 39440.0
            },
            "gaap_code": "us-gaap_PropertyPlantAndEquipmentNet"
          }
        ],
        "Liabilities": [
          {
            "item_label": "Accounts Payable",
            "values": {
              "2023": 62391.0,
              "2022": 64115.0,
              "2021": 54763.0
            },
            "gaap_code": "us-gaap_AccountsPayableCurrent"
          },
          {
            "item_label": "Long-term Debt",
            "values": {
              "2023": 95081.0,
              "2022": 98959.0,
              "2021": 109106.0
            },
            "gaap_code": "us-gaap_LongTermDebtNoncurrent"
          }
        ],
        "Equity": [
          {
            "item_label": "Total Shareholder Equity",
            "values": {
              "2023": 62146.0,
              "2022": 50672.0,
              "2021": 57465.0
            },
            "gaap_code": "us-gaap_StockholdersEquity"
          }
        ]
      }
    },
    "cash_flow_statement": {
      "statement_type": "cash_flow_statement",
      "years": ["2023", "2022", "2021"],
      "sections": {
        "Operating Activities": [
          {
            "item_label": "Net Income",
            "values": {
              "2023": 99803.0,
              "2022": 99803.0,
              "2021": 94680.0
            },
            "gaap_code": "us-gaap_NetIncomeLoss"
          },
          {
            "item_label": "Depreciation and Amortization",
            "values": {
              "2023": 11130.0,
              "2022": 10963.0,
              "2021": 11284.0
            },
            "gaap_code": "us-gaap_DepreciationAndAmortization"
          }
        ],
        "Investing Activities": [
          {
            "item_label": "Capital Expenditures",
            "values": {
              "2023": -10956.0,
              "2022": -11085.0,
              "2021": -7309.0
            },
            "gaap_code": "us-gaap_PaymentsToAcquireProductiveAssets"
          }
        ],
        "Financing Activities": [
          {
            "item_label": "Stock Repurchases",
            "values": {
              "2023": -77500.0,
              "2022": -89807.0,
              "2021": -85940.0
            },
            "gaap_code": "us-gaap_PaymentsForRepurchaseOfCommonStock"
          }
        ]
      }
    }
  }
}
```

## Data Structure Details

### Statement Object
Each statement contains:
- **statement_type**: Type of financial statement
- **years**: Array of years covered (most recent first)
- **sections**: Nested object containing line items by section

### Section Structure
Each section contains an array of line items.

### Line Item Object
Each line item has:
- **item_label**: Human-readable name (e.g., "Total Revenue")
- **values**: Object with year as key and value as float
- **gaap_code**: Official GAAP accounting code (or null if unavailable)

### Value Scale
All financial values are in **millions** (e.g., 383285.0 = $383.285 billion)

### Error Handling
If any error occurs during fetching, the response will include:
```json
{
  "status": "error",
  "error_type": "ConnectionError|ValueError|Exception",
  "message": "Error description",
  "partial_data": {} // If some data was successfully fetched
}
```

## Frontend Integration Notes

### Display Recommendations

1. **Table Structure:**
   - Create a table with columns for each year
   - Group rows by sections
   - Show section headers as highlighted rows
   - Display line items underneath each section

2. **Section Headers:**
   - Use distinct styling (e.g., bold, colored background)
   - Examples: "Revenue", "Operating Expenses", "Assets", "Liabilities"

3. **Line Items:**
   - Format numbers with commas (e.g., "383,285")
   - Show "-" or "N/A" for zero/empty values
   - Use proper indentation to show hierarchy

4. **Source Links:**
   - Display the source_urls array for each statement type
   - Provide clickable links to verify data against SEC filings
   - Label each link with the corresponding year

### Example Frontend Display

```html
<!-- Income Statement -->
<h2>📈 Income Statement</h2>
<p>
  <strong>Source Links:</strong>
  <a href="[2023_url]">2023</a> | 
  <a href="[2022_url]">2022</a> | 
  <a href="[2021_url]">2021</a>
</p>

<table>
  <tr class="section-header">
    <th>Revenue</th>
    <th>2023</th>
    <th>2022</th>
    <th>2021</th>
  </tr>
  <tr class="line-item">
    <td>Total Revenue</td>
    <td>383,285</td>
    <td>394,328</td>
    <td>365,817</td>
  </tr>
  <!-- More items... -->
</table>
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `ticker` | String | Stock ticker symbol (e.g., "AAPL") |
| `years` | Array | List of years available (strings) |
| `item_label` | String | Human-readable line item name |
| `values` | Object | Key-value pairs: year → financial value (float in millions) |
| `gaap_code` | String\|null | Official GAAP accounting standard code |
| `section_label` | String | Section/group name (e.g., "Revenue", "Assets") |

## Performance Notes

- Typical response time: 5-15 seconds for 3 years of data
- Parallel processing fetches multiple statements simultaneously
- Caching not implemented (each request fetches fresh data)

## Limitations

1. **Data Source:** Only 10-K annual filings (not quarterly 10-Q)
2. **Years Available:** Varies by company (typically 5-15 years)
3. **Statement Availability:** Not all companies have all three statement types in every year
4. **Data Scale:** Values are in millions, not raw numbers

## Testing Recommendations

Use these test tickers for development:
- **AAPL** (Apple) - Reliable data, multiple years
- **MSFT** (Microsoft) - Good coverage
- **GOOGL** (Alphabet) - Different structure
- **TSLA** (Tesla) - Varied financial patterns

