## link constuctructued 
## types of statements present 
## Number of statements of filed 
## Table per statement 
## (to figure out) How to retrieve the quaterly files


import os
import pandas as pd
import numpy as np  # make sure to add
import requests
from bs4 import BeautifulSoup
import logging  # make sure to add
import calendar  # make sure to add
 # change to your own headers file or add variable in code
USER_EMAIL = os.getenv("USER_EMAIL")
headers = {"User-Agent": USER_EMAIL}


pd.options.display.float_format = (
    lambda x: "{:,.0f}".format(x) if int(x) == x else "{:,.2f}".format(x)
)


statement_keys_map = {
    "balance_sheet": [
        "balance sheet",
        "balance sheets",
        "statement of financial position",
        "consolidated balance sheets",
        "consolidated balance sheet",
        "consolidated financial position",
        "consolidated balance sheets - southern",
        "consolidated statements of financial position",
        "consolidated statement of financial position",
        "consolidated statements of financial condition",
        "combined and consolidated balance sheet",
        "condensed consolidated balance sheets",
        "consolidated balance sheets, as of december 31",
        "dow consolidated balance sheets",
        "consolidated balance sheets (unaudited)",
    ],
    "income_statement": [
        "income statement",
        "income statements",
        "statement of earnings (loss)",
        "statements of consolidated income",
        "consolidated statements of operations",
        "consolidated statement of operations",
        "consolidated statements of earnings",
        "consolidated statement of earnings",
        "consolidated statements of income",
        "consolidated statement of income",
        "consolidated income statements",
        "consolidated income statement",
        "condensed consolidated statements of earnings",
        "consolidated results of operations",
        "consolidated statements of income (loss)",
        "consolidated statements of income - southern",
        "consolidated statements of operations and comprehensive income",
        "consolidated statements of comprehensive income",
    ],
    "cash_flow_statement": [
        "cash flows statement",
        "cash flows statements",
        "statement of cash flows",
        "statements of consolidated cash flows",
        "consolidated statements of cash flows",
        "consolidated statement of cash flows",
        "consolidated statement of cash flow",
        "consolidated cash flows statements",
        "consolidated cash flow statements",
        "condensed consolidated statements of cash flows",
        "consolidated statements of cash flows (unaudited)",
        "consolidated statements of cash flows - southern",
    ],
}




## for retrieveing the cik for the company 

def cik_matching_ticker(ticker, headers=headers):
    try:
        ticker = ticker.upper().replace(".", "-")
        response = requests.get(
            "https://www.sec.gov/files/company_tickers.json", headers=headers, timeout=10
        )
        response.raise_for_status()
        ticker_json = response.json()

        for company in ticker_json.values():
            if company["ticker"] == ticker:
                cik = str(company["cik_str"]).zfill(10)
                return cik
        raise ValueError(f"Ticker {ticker} not found in SEC database")
    except requests.RequestException as e:
        logging.error(f"Network error fetching ticker data: {e}")
        raise ConnectionError(f"Could not connect to SEC database. Please check your internet connection.")
    except ValueError:
        raise
    except Exception as e:
        logging.error(f"Unexpected error in cik_matching_ticker: {e}")
        raise ValueError(f"Error processing ticker {ticker}: {str(e)}")


####################################################################################################


def get_submission_data_for_ticker(ticker, headers=headers, only_filings_df=False):
    """
    Get the data in json form for a given ticker. For example: 'cik', 'entityType', 'sic', 'sicDescription', 'insiderTransactionForOwnerExists', 'insiderTransactionForIssuerExists', 'name', 'tickers', 'exchanges', 'ein', 'description', 'website', 'investorWebsite', 'category', 'fiscalYearEnd', 'stateOfIncorporation', 'stateOfIncorporationDescription', 'addresses', 'phone', 'flags', 'formerNames', 'filings'

    Args:
        ticker (str): The ticker symbol of the company.

    Returns:
        json: The submissions for the company.
    """
    try:
        cik = cik_matching_ticker(ticker)
        headers = headers
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        company_json = response.json()
        if only_filings_df:
            return pd.DataFrame(company_json["filings"]["recent"])
        else:
            return company_json
    except requests.RequestException as e:
        logging.error(f"Error fetching submission data for {ticker}: {e}")
        raise ConnectionError(f"Could not fetch company data from SEC. Please try again later.")
    except (KeyError, TypeError) as e:
        logging.error(f"Error parsing submission data for {ticker}: {e}")
        raise ValueError(f"Invalid data structure received from SEC for {ticker}")
    except Exception as e:
        logging.error(f"Unexpected error in get_submission_data_for_ticker: {e}")
        raise ValueError(f"Error processing submission data for {ticker}: {str(e)}") 

####################################################################################################
# This will give back the accn number , and the number of filings present in the company

def get_filtered_filings(
    ticker, ten_k=True, just_accession_numbers=False, headers=None
):
    """
    Retrieves either 10-K or 10-Q filings for a given ticker and optionally returns just accession numbers.

    Args:
        ticker (str): Stock ticker symbol.
        ten_k (bool): If True, fetches 10-K filings; otherwise, fetches 10-Q filings.
        just_accession_numbers (bool): If True, returns only accession numbers; otherwise, returns full data.
        headers (dict): Headers for HTTP request.

    Returns:
        DataFrame or Series: DataFrame of filings or Series of accession numbers.
    """
    try:
        # Fetch submission data for the given ticker
        company_filings_df = get_submission_data_for_ticker(
            ticker, only_filings_df=True, headers=headers
        )
        
        if company_filings_df is None or company_filings_df.empty:
            logging.warning(f"No filings data received for {ticker}")
            return pd.DataFrame()  # Return empty DataFrame instead of None
        
        # Filter for 10-K or 10-Q forms
        form_type = "10-K" if ten_k else "10-Q"
        df = company_filings_df[company_filings_df["form"] == form_type]
        
        if df.empty:
            logging.warning(f"No {form_type} filings found for {ticker}")
            return pd.DataFrame()
        
        # Return accession numbers if specified
        if just_accession_numbers:
            df = df.set_index("reportDate")
            accession_df = df["accessionNumber"]
            return accession_df
        else:
            return df
    except Exception as e:
        logging.error(f"Error in get_filtered_filings for {ticker}: {e}")
        raise ValueError(f"Error retrieving filings for {ticker}: {str(e)}")
    
####################################################################################################
# this gets all the 
def get_statement_file_names_in_filing_summary(ticker, accession_number, headers=None):
    """
    Retrieves file names of financial statements from a filing summary.

    Args:
        ticker (str): Stock ticker symbol.
        accession_number (str): SEC filing accession number.
        headers (dict): Headers for HTTP request.

    Returns:
        dict: Dictionary mapping statement types to their file names.
    """
    try:
        # Set up request session and get filing summary
        session = requests.Session()
        cik = cik_matching_ticker(ticker)
        base_link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}"
        filing_summary_link = f"{base_link}/FilingSummary.xml"
        
        response = session.get(filing_summary_link, headers=headers, timeout=10)
        response.raise_for_status()
        filing_summary_response = response.content.decode("utf-8")

        # Parse the filing summary
        filing_summary_soup = BeautifulSoup(filing_summary_response, "lxml-xml")
        statement_file_names_dict = {}
        # Extract file names for statements
        for report in filing_summary_soup.find_all("Report"):
            file_name = _get_file_name(report)
            short_name, long_name = report.find("ShortName"), report.find("LongName")
            if _is_statement_file(short_name, long_name, file_name):
                statement_file_names_dict[short_name.text.lower()] = file_name
        return statement_file_names_dict 
    except requests.RequestException as e:
        logging.error(f"Network error fetching filing summary for {ticker}/{accession_number}: {e}")
        return {}
    except Exception as e:
        logging.error(f"Error parsing filing summary for {ticker}/{accession_number}: {e}")
        return {}
##
## helper function

def _get_file_name(report):
    """
    Extracts the file name from an XML report tag.

    Args:
        report (Tag): BeautifulSoup tag representing the report.

    Returns:
        str: File name extracted from the tag.
    """
    html_file_name_tag = report.find("HtmlFileName")
    xml_file_name_tag = report.find("XmlFileName")
    # Return the appropriate file name
    if html_file_name_tag:
        return html_file_name_tag.text
    elif xml_file_name_tag:
        return xml_file_name_tag.text
    else:
        return ""  

##


def _is_statement_file(short_name_tag, long_name_tag, file_name):
    """
    Determines if a given file is a financial statement file.

    Args:
        short_name_tag (Tag): BeautifulSoup tag for the short name.
        long_name_tag (Tag): BeautifulSoup tag for the long name.
        file_name (str): Name of the file.

    Returns:
        bool: True if it's a statement file, False otherwise.
    """
    return (
        short_name_tag is not None
        and long_name_tag is not None
        and file_name  # Ensure file_name is not an empty string
        and "Statement" in long_name_tag.text
    )

## 
# this will return the path to the file directly

def get_statement_soup(
    ticker, accession_number, statement_name, headers, statement_keys_map
):
    """
    Retrieves the BeautifulSoup object for a specific financial statement.

    Args:
        ticker (str): Stock ticker symbol.
        accession_number (str): SEC filing accession number.
        statement_name (str): has to be 'balance_sheet', 'income_statement', 'cash_flow_statement'
        headers (dict): Headers for HTTP request.
        statement_keys_map (dict): Mapping of statement names to keys.

    Returns:
        BeautifulSoup: Parsed HTML/XML content of the financial statement.

    Raises:
        ValueError: If the statement file name is not found or if there is an error fetching the statement.
    """
    try:
        session = requests.Session()
        cik = cik_matching_ticker(ticker)
        base_link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}"
        # Get statement file names
        statement_file_name_dict = get_statement_file_names_in_filing_summary(
            ticker, accession_number, headers
        )
        
        if not statement_file_name_dict:
            raise ValueError(f"Could not fetch filing summary for {ticker}/{accession_number}")
        
        statement_link = None
        # Find the specific statement link
        for possible_key in statement_keys_map.get(statement_name.lower(), []):
            file_name = statement_file_name_dict.get(possible_key.lower())
            if file_name:
                statement_link = f"{base_link}/{file_name}"
                return statement_link
        
        if not statement_link:
            raise ValueError(f"Could not find statement file name for {statement_name}")
    except ValueError:
        raise
    except Exception as e:
        logging.error(f"Error in get_statement_soup for {ticker}/{accession_number}/{statement_name}: {e}")
        raise ValueError(f"Could not retrieve statement link: {str(e)}")






#### main parsing logic : 

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


def clean_value(txt: str):
    """Normalize SEC table values to float or None."""
    if not txt:
        return None

    # Remove non-breaking spaces
    txt = txt.replace("\u00a0", "").strip()

    # Handle blanks and dashes early
    if txt in ("", "—", "-", "— —"):
        return None

    # ✅ Handle cases like "$ (2,722)" or "$(2,722)" or "$((2,722))"
    # Remove $ and commas but keep parentheses for now
    txt = txt.replace("$", "").replace(",", "").strip()

    # ✅ Detect negatives in multiple formats
    # Examples that should become negative:
    # "(2722)", "( 2722 )", "-2722", "(2722.0)"
    neg_pattern = re.compile(r"^\(?\s*-?\d+(\.\d+)?\s*\)?$")
    if "(" in txt and ")" in txt:
        # If parentheses exist, strip them and mark negative
        number = txt.replace("(", "").replace(")", "").strip()
        try:
            return -float(number)
        except:
            return None

    # ✅ If no parentheses, just parse normally if numeric
    txt = txt.strip()
    try:
        return float(txt)
    except:
        return None
    

def parse_sec_statement(ticker, statement_name, year, user_agent: str = "harshagr838@gmail.com", header= headers):

    """Parse SEC R*.htm financial statement into structured JSON-like rows.
    
    Returns:
        dict: {"rows": [...], "source_url": url} or just rows list for backward compatibility
    """
    source_url = None  # Track the URL
    try:
        accn = get_filtered_filings(
            ticker, ten_k=True, just_accession_numbers=False, headers=header
        )
        
        if accn is None or accn.empty:
            raise ValueError(f"No filings found for {ticker}")
        
        if year >= len(accn):
            raise ValueError(f"Year index {year} is out of range for {ticker} (available: {len(accn)} filings)")
        
        acc_num = accn['accessionNumber'].iloc[year].replace("-", "")
        url = get_statement_soup(
                ticker,
                accession_number=acc_num,
                statement_name=statement_name,
                headers=header,
                statement_keys_map=statement_keys_map
        )
        source_url = url  # Store the URL

        # check for the URL : 
        logging.debug(f"Parsing URL: {url}")

        resp = requests.get(url, headers={"User-Agent": user_agent}, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
    except (IndexError, KeyError) as e:
        logging.error(f"Index error in parse_sec_statement for {ticker}, year {year}: {e}")
        raise ValueError(f"Invalid data structure for {ticker}, year {year}")
    except requests.RequestException as e:
        logging.error(f"Network error in parse_sec_statement for {ticker}, year {year}: {e}")
        raise ConnectionError(f"Could not fetch financial statement from SEC. Please try again.")
    except Exception as e:
        logging.error(f"Error in parse_sec_statement for {ticker}, year {year}: {e}")
        raise ValueError(f"Error parsing financial statement: {str(e)}")

    # Continue with parsing logic, but wrapped in error handling
    try:
        # ---- 1. Extract column headers (dates/periods) ----
        headers_list = [th.get_text(" ", strip=True) for th in soup.select("th")]
        periods = [h for h in headers_list if re.search(r"\d{4}", h)]
        if not periods:  # fallback: use all headers if no clean match
            periods = headers_list

        rows = []
        for tr in soup.select("tr"):
            label_cell = tr.select_one("td.pl, td.pl.custom")
            if not label_cell:
                continue

            link = label_cell.select_one("a")
            label = None
            gaap_code = None  # ✅ default

            if link:
                label = link.get_text(" ", strip=True)

                onclick_val = link.get("onclick", "")
                match = re.search(r"defref_([a-zA-Z0-9\-_]+)", onclick_val)
                gaap_code = match.group(1) if match else None

                is_section = False
                if gaap_code:
                    g = gaap_code.lower()
                    if g.endswith("abstract") or g.endswith("axis") or g.endswith("member"):
                        is_section = True

                # Fallback: no numeric values in row
                if not is_section:
                    numeric_vals = [
                        clean_value(td.get_text(" ", strip=True))
                        for td in tr.select("td.nump, td.num, td.text")
                    ]
                    if not any(v not in [None, "", "-"] for v in numeric_vals):
                        is_section = True
            else:
                label = label_cell.get_text(" ", strip=True)
                is_section = False

            if not label:
                continue

            # ---- 3. Extract values ----
            values = []
            for td in tr.select("td.nump, td.num, td.text"):
                val = clean_value(td.get_text(" ", strip=True))
                values.append(val)

            # ---- 4. Build row dict ----
            row_dict = {
                "label": label,
                "gaap": gaap_code,
                "is_section": is_section  # ✅ Add this
            }

            for i, v in enumerate(values):
                if i < len(periods):
                    row_dict[periods[i]] = v

            rows.append(row_dict)

        # Return dict with rows and source URL
        return {"rows": rows, "source_url": source_url}
    except (AttributeError, KeyError, TypeError) as e:
        logging.error(f"Error parsing HTML structure for {ticker}, year {year}, statement {statement_name}: {e}")
        raise ValueError(f"Could not parse financial statement HTML. The filing structure may be unusual.")
    except Exception as e:
        logging.error(f"Unexpected error parsing statement for {ticker}, year {year}, statement {statement_name}: {e}")
        raise ValueError(f"Error extracting data from financial statement: {str(e)}")





## json exporter 
def structure_statement_json(flat_rows, statement_name):
    """
    Convert flat list of row dicts into a nested JSON grouped by sections.
    Uses the 'is_section' flag to preserve hierarchy accurately.
    """
    try:
        if not flat_rows:
            return {"statement": statement_name, "sections": [], "periods": []}

        # ✅ Detect only actual periods (exclude label, is_section, gaap)
        sample_row = flat_rows[0]
        periods = [
            k for k in sample_row.keys()
            if k not in ("label", "gaap", "is_section")
        ]

        structured = {
            "statement": statement_name,
            "periods": periods,
            "sections": []
        }

        current_section = None

        for row in flat_rows:
            try:
                label = row.get("label", "").strip()
                gaap_code = row.get("gaap")
                is_section = row.get("is_section", False)

                # ✅ Extract only real values (exclude gaap & is_section)
                values = {
                    p: (None if row.get(p) in ("", None, "-", "—") else row[p])
                    for p in periods
                }

                # ✅ If it's a SECTION row
                if is_section:
                    current_section = {
                        "section": label,
                        "gaap": gaap_code,
                        "items": []
                    }
                    structured["sections"].append(current_section)

                else:
                    # ✅ It's a line item
                    item_entry = {
                        "label": label,
                        "gaap": gaap_code,
                        "values": values
                    }

                    # ✅ If no section has appeared yet → place in Uncategorized
                    if current_section is None:
                        current_section = {
                            "section": "Uncategorized",
                            "items": []
                        }
                        structured["sections"].append(current_section)

                    current_section["items"].append(item_entry)
            except (KeyError, TypeError) as e:
                logging.warning(f"Error processing row in structure_statement_json: {e}")
                continue

        return structured
    except Exception as e:
        logging.error(f"Error in structure_statement_json for {statement_name}: {e}")
        return {"statement": statement_name, "sections": [], "periods": [], "error": str(e)}


## function for multiple statement calls 
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

def get_available_years_count(ticker, header=headers):
    """
    Get the number of years of 10-K filings available for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        header: Request headers
        
    Returns:
        int: Number of years of 10-K filings available, or 0 if none found
    """
    try:
        filings_df = get_filtered_filings(
            ticker,
            ten_k=True,
            just_accession_numbers=False,
            headers=header
        )
        
        if filings_df is None or filings_df.empty:
            logging.warning(f"No filings found for {ticker}")
            return 0
        
        available_count = len(filings_df)
        logging.info(f"Found {available_count} years of filings for {ticker}")
        return available_count
        
    except Exception as e:
        logging.error(f"Error fetching filings count for {ticker}: {e}")
        return 0


def get_multi_year_financials_parallel(
    ticker,
    years_back=3,
    statements=("cash_flow_statement", "balance_sheet", "income_statement"),
    user_agent="harshagr838@gmail.com",
    header=headers,
    max_workers=5
):
    """
    Fetch multiple financial statements across multiple years in parallel.
    Uses ThreadPoolExecutor for speed.
    
    Args:
        ticker: Stock ticker symbol
        years_back: Number of years to fetch (default: 3)
        statements: Tuple of statement types to fetch
        user_agent: User agent for API requests
        header: Request headers
        max_workers: Maximum number of parallel workers
        
    Returns:
        dict: {
            "ticker": str,
            "years": dict of year data,
            "available_years_count": int,
            "requested_years": int,
            "fetched_years": int
        }
    """
    result = {
        "ticker": ticker.upper(),
        "years": {},
        "available_years_count": 0,
        "requested_years": years_back,
        "fetched_years": 0
    }
    
    # ✅ Fetch filings list
    try:
        filings_df = get_filtered_filings(
            ticker,
            ten_k=True,
            just_accession_numbers=False,
            headers=header
        )
    except Exception as e:
        logging.error(f"Error fetching filings for {ticker}: {e}")
        return result
    
    if filings_df is None or filings_df.empty:
        logging.error(f"No filings found for {ticker}")
        return result
    
    # ✅ Set available years count
    available = len(filings_df)
    result["available_years_count"] = available
    
    # ✅ Limit years_back to available filings
    years_to_fetch = min(years_back, available)
    
    if years_to_fetch == 0:
        logging.warning(f"No years available for {ticker}")
        return result
    
    # ✅ Submit tasks to thread pool
    tasks = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i in range(years_to_fetch):
            try:
                # Validate index
                if i >= len(filings_df):
                    logging.warning(f"Index {i} exceeds available filings for {ticker}")
                    break
                
                acc_num = filings_df["accessionNumber"].iloc[i].replace("-", "")
                report_date = filings_df["reportDate"].iloc[i]
                
                # Submit task for each statement type
                for stmt in statements:
                    tasks.append(
                        executor.submit(
                            _process_single_statement_task,
                            ticker,
                            stmt,
                            i,
                            report_date,
                            user_agent,
                            header
                        )
                    )
            except Exception as e:
                logging.error(f"Error preparing task for year index {i}: {e}")
                continue
        
        # ✅ Collect results from completed tasks
        for future in as_completed(tasks):
            try:
                report_date, stmt, json_struct = future.result()
                
                # Create year entry if it doesn't exist
                if report_date not in result["years"]:
                    result["years"][report_date] = {}
                
                result["years"][report_date][stmt] = json_struct
                
            except Exception as e:
                logging.error(f"Error reading thread result: {e}")
    
    # ✅ Set final counts
    result["fetched_years"] = len(result["years"])
    
    return result


def _process_single_statement_task(
    ticker, statement_name, year_index, report_date, user_agent, header
):
    """
    Helper function used by ThreadPoolExecutor to parse a single statement for a single year.
    
    Args:
        ticker: Stock ticker symbol
        statement_name: Type of financial statement
        year_index: Index of the year in filings
        report_date: Date of the report
        user_agent: User agent for API requests
        header: Request headers
        
    Returns:
        tuple: (report_date, statement_name, json_struct or error dict)
    """
    try:
        parse_result = parse_sec_statement(
            ticker=ticker,
            statement_name=statement_name,
            year=year_index,
            user_agent=user_agent,
            header=header
        )
        
        # Handle new dict format or legacy list format
        if isinstance(parse_result, dict):
            flat_rows = parse_result.get("rows", [])
            source_url = parse_result.get("source_url")
        else:
            flat_rows = parse_result
            source_url = None
        
        if not flat_rows:
            logging.warning(f"No rows extracted from {statement_name} for {ticker} at {report_date}")
            return report_date, statement_name, {"error": "No data extracted from statement"}
        
        json_struct = structure_statement_json(flat_rows, statement_name)
        
        if not json_struct or not json_struct.get("sections"):
            logging.warning(f"Empty structured data for {statement_name} for {ticker} at {report_date}")
            return report_date, statement_name, {"error": "Could not structure statement data"}
        
        # Add source URL to the structured data
        if source_url:
            json_struct["source_url"] = source_url
        
        return report_date, statement_name, json_struct
    except ValueError as e:
        logging.error(f"Value error processing {statement_name} for {ticker} at {report_date}: {e}")
        return report_date, statement_name, {"error": str(e)}
    except ConnectionError as e:
        logging.error(f"Connection error processing {statement_name} for {ticker} at {report_date}: {e}")
        return report_date, statement_name, {"error": str(e)}
    except Exception as e:
        logging.error(f"Unexpected error processing {statement_name} for {ticker} at {report_date}: {e}")
        return report_date, statement_name, {"error": str(e)}





## test merger 

def merge_statements(data):
    """
    Input: 
      data = {
        "ticker": "AAPL",
        "years": {
          "2024-09-28": {...},
          "2023-09-30": {...}
        }
      }

    Output:
      {
        "ticker": "...",
        "statements": {
          "balance_sheet": merged_json,
          "income_statement": merged_json,
          "cash_flow_statement": merged_json
        }
      }
    """

    from copy import deepcopy
    import re

    def extract_year(date_str):
        match = re.search(r'\d{4}', date_str)
        return match.group(0) if match else date_str

    final_output = {"ticker": data.get("ticker"), "statements": {}}

    # List all years sorted (latest first or oldest first - you decide)
    all_year_keys = sorted(data["years"].keys(), reverse=True)

    # We assume each year has the same top-level statements to merge
    if not all_year_keys:
        return final_output
    
    sample_year = data["years"][all_year_keys[0]]
    statement_types = sample_year.keys()  # e.g. ["balance_sheet", "income_statement", ...]

    # Process each statement type separately
    for stmt_type in statement_types:
        # We'll build merged data in a structure:
        # {
        #   "statement": stmt_type,
        #   "periods": [...unique years...],
        #   "sections": [
        #       {
        #         "section": name,
        #         "gaap": maybe_gaap,
        #         "items": [
        #            {
        #              "label": ...,
        #              "gaap": ...,
        #              "values": { '2024':..., '2023':..., ... }
        #            },
        #            ...
        #         ]
        #       },
        #       ...
        #   ]
        # }
        merged_statement = {
            "statement": stmt_type,
            "periods": [],
            "sections": []
        }

        # This dict helps us find existing line-items quickly by GAAP or by fallback
        # structure: sections_map[(section_name, section_gaap or None)] = reference to merged section
        # each section keeps an items_map keyed by (gaap, or fallback signature)
        sections_map = {}

        def get_or_create_section(sec_name, sec_gaap):
            key = (sec_name, sec_gaap)
            if key not in sections_map:
                new_sec = {
                    "section": sec_name,
                    "gaap": sec_gaap,
                    "items": [],
                    "items_map": {}  # to track by keys
                }
                sections_map[key] = new_sec
                merged_statement["sections"].append(new_sec)
            return sections_map[key]

        for year_key in all_year_keys:
            year_data = data["years"][year_key]
            if stmt_type not in year_data:
                # skip if for some reason no statement in that year
                continue

            stmt_obj = deepcopy(year_data[stmt_type])
            # periods from that year's statement
            # convert each to just year label
            local_periods = [extract_year(p) for p in stmt_obj["periods"]]

            # We'll add these to merged periods if not already
            for yp in local_periods:
                if yp not in merged_statement["periods"]:
                    merged_statement["periods"].append(yp)

            # Now process sections from that statement
            for sec in stmt_obj.get("sections", []):
                sec_name = sec.get("section")
                sec_gaap = sec.get("gaap")
                merged_sec = get_or_create_section(sec_name, sec_gaap)

                # For each item in this section
                for item in sec.get("items", []):
                    item_gaap = item.get("gaap")
                    item_label = item.get("label")

                    # get values & rename keys from full date -> year
                    new_values = {}
                    for k, val in item.get("values", {}).items():
                        new_values[extract_year(k)] = val

                    # 1) GAAP-based match
                    found_key = None
                    if item_gaap:
                        if item_gaap in merged_sec["items_map"]:
                            found_key = item_gaap

                    # 2) Fallback: match by identical values in overlapping years
                    if not found_key and item_gaap not in merged_sec["items_map"]:
                        for mk, existing_item in merged_sec["items_map"].items():
                            existing_values = existing_item["values"]
                            for yk, v in existing_values.items():
                                if yk in new_values and new_values[yk] == v and v is not None:
                                    found_key = mk
                                    break
                            if found_key:
                                break

                    # 3) Fallback: match by label
                    if not found_key:
                        for mk, existing_item in merged_sec["items_map"].items():
                            if existing_item["label"] == item_label:
                                found_key = mk
                                break

                    # If no match found, create new
                    if not found_key:
                        new_key = item_gaap if item_gaap else f"{item_label}_{len(merged_sec['items'])}"
                        new_item = {
                            "label": item_label,
                            "gaap": item_gaap,
                            "values": {}
                        }
                        # Add placeholder null for all existing periods
                        for p in merged_statement["periods"]:
                            new_item["values"][p] = None
                        # Overwrite with this row's actual data
                        for p, v in new_values.items():
                            new_item["values"][p] = v

                        merged_sec["items"].append(new_item)
                        merged_sec["items_map"][new_key] = new_item
                    else:
                        # Merge into existing
                        existing_item = merged_sec["items_map"][found_key]
                        for p, v in new_values.items():
                            existing_item["values"][p] = v

        # Now remove items_map keys
        for sec in merged_statement["sections"]:
            sec.pop("items_map", None)

        final_output["statements"][stmt_type] = merged_statement

    return final_output



#### merger v2 

def merge_statements_v2(data):
    """
    Input:
      data = {
        "ticker": "AAPL",
        "years": {
          "2024-09-28": {...},
          "2023-09-30": {...}
        }
      }

    Output:
      {
        "ticker": "...",
        "statements": {
          "balance_sheet": merged_json,
          "income_statement": merged_json,
          "cash_flow_statement": merged_json
        }
      }
    """
    from copy import deepcopy
    import re

    def extract_year(date_str):
        match = re.search(r'\d{4}', date_str)
        return match.group(0) if match else date_str

    final_output = {"ticker": data.get("ticker"), "statements": {}}

    all_year_keys = sorted(data["years"].keys(), reverse=True)
    if not all_year_keys:
        return final_output

    # Oldest year will define canonical hierarchy
    oldest_year = all_year_keys[-1]
    sample_year = data["years"][all_year_keys[0]]
    statement_types = sample_year.keys()

    for stmt_type in statement_types:
        merged_statement = {
            "statement": stmt_type,
            "periods": [],
            "sections": []
        }

        sections_map = {}

        def get_or_create_section(sec_name, sec_gaap):
            key = (sec_name, sec_gaap)
            if key not in sections_map:
                new_sec = {
                    "section": sec_name,
                    "gaap": sec_gaap,
                    "items": [],
                    "items_map": {}
                }
                sections_map[key] = new_sec
                merged_statement["sections"].append(new_sec)
            return sections_map[key]

        # ✅ Step 1: Pre-build structure from the OLDEST year
        if stmt_type in data["years"][oldest_year]:
            base_stmt = data["years"][oldest_year][stmt_type]
            base_periods = [extract_year(p) for p in base_stmt.get("periods", [])]
            for yp in base_periods:
                if yp not in merged_statement["periods"]:
                    merged_statement["periods"].append(yp)

            for sec in base_stmt.get("sections", []):
                sec_name = sec.get("section")
                sec_gaap = sec.get("gaap")
                merged_sec = get_or_create_section(sec_name, sec_gaap)

                for item in sec.get("items", []):
                    item_label = item.get("label")
                    item_gaap = item.get("gaap")
                    key = item_gaap if item_gaap else item_label

                    new_item = {
                        "label": item_label,
                        "gaap": item_gaap,
                        "values": {yp: None for yp in merged_statement["periods"]}
                    }
                    merged_sec["items"].append(new_item)
                    merged_sec["items_map"][key] = new_item

        # ✅ Step 2: Merge other years onto this structure
        for year_key in all_year_keys:
            year_data = data["years"][year_key]
            if stmt_type not in year_data:
                continue

            stmt_obj = deepcopy(year_data[stmt_type])
            local_periods = [extract_year(p) for p in stmt_obj["periods"]]

            for yp in local_periods:
                if yp not in merged_statement["periods"]:
                    merged_statement["periods"].append(yp)
                    for sec in merged_statement["sections"]:
                        for it in sec["items"]:
                            it["values"][yp] = None

            for sec in stmt_obj.get("sections", []):
                sec_name = sec.get("section")
                sec_gaap = sec.get("gaap")
                merged_sec = get_or_create_section(sec_name, sec_gaap)

                for item in sec.get("items", []):
                    item_gaap = item.get("gaap")
                    item_label = item.get("label")

                    new_values = {
                        extract_year(k): v
                        for k, v in item.get("values", {}).items()
                    }

                    found_key = None
                    if item_gaap and item_gaap in merged_sec["items_map"]:
                        found_key = item_gaap

                    if not found_key:
                        for mk, existing_item in merged_sec["items_map"].items():
                            ex_vals = existing_item["values"]
                            for yk, ev in ex_vals.items():
                                if yk in new_values and new_values[yk] == ev and ev is not None:
                                    found_key = mk
                                    break
                            if found_key:
                                break

                    if not found_key:
                        for mk, existing_item in merged_sec["items_map"].items():
                            if existing_item["label"] == item_label:
                                found_key = mk
                                break

                    if not found_key:
                        new_key = item_gaap if item_gaap else f"{item_label}_{len(merged_sec['items'])}"
                        new_item = {
                            "label": item_label,
                            "gaap": item_gaap,
                            "values": {
                                p: None for p in merged_statement["periods"]
                            }
                        }
                        for p, v in new_values.items():
                            new_item["values"][p] = v

                        merged_sec["items"].append(new_item)
                        merged_sec["items_map"][new_key] = new_item
                    else:
                        existing_item = merged_sec["items_map"][found_key]
                        for p, v in new_values.items():
                            existing_item["values"][p] = v

        for sec in merged_statement["sections"]:
            sec.pop("items_map", None)

        # ✅ Sort periods in ascending order
        merged_statement["periods"].sort(key=lambda x: int(x))

        # ✅ Reorder values inside each item to match sorted periods
        for sec in merged_statement["sections"]:
            for item in sec["items"]:
                ordered_values = {}
                for p in merged_statement["periods"]:
                    ordered_values[p] = item["values"].get(p)
                item["values"] = ordered_values

        final_output["statements"][stmt_type] = merged_statement

    return final_output




## merger version 4 
def merge_statements_flattened(data):
    """
    Merge multiple filings using oldest filing as anchor.
    - Preserve hierarchy & order from oldest filing.
    - Match new items globally by values → GAAP → label.
    - Rebuild hierarchy from anchor; unmatched new items are appended.
    """

    from copy import deepcopy
    import re

    # --- Helpers ---
    def normalize_year(date_str):
        if not date_str:
            return None
        m = re.search(r"(\d{4})", str(date_str))
        return m.group(1) if m else str(date_str)

    def normalize_value(v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip().replace(",", "")
            if v.startswith("(") and v.endswith(")"):
                v = "-" + v[1:-1]
        try:
            return float(v)
        except Exception:
            return None

    def normalize_label(label):
        if not label:
            return ""
        label = label.lower()
        label = re.sub(r"\s+", " ", label)
        return label.strip()

    # --- Collect all periods across filings ---
    all_periods = set()
    for filing in data["years"].values():
        for stmt in filing.values():
            for p in stmt.get("periods", []):
                all_periods.add(normalize_year(p))
    all_periods = sorted(all_periods)

    final_output = {"ticker": data.get("ticker"), "statements": {}}

    # --- Determine statement types from first filing ---
    any_filing = next(iter(data["years"].values()))
    statement_types = any_filing.keys()

    # --- Process each statement type ---
    for stmt_type in statement_types:
        merged_stmt = {
            "statement": stmt_type,
            "periods": all_periods,
            "sections": []
        }

        # Anchor = oldest filing
        oldest_year_key = sorted(data["years"].keys())[0]
        base_stmt = data["years"][oldest_year_key][stmt_type]

        # Build map of anchor items
        item_map = {}
        for sec in base_stmt.get("sections", []):
            new_sec = {
                "section": sec.get("section"),
                "gaap": sec.get("gaap"),
                "items": []
            }
            for item in sec.get("items", []):
                gaap = item.get("gaap")
                label = normalize_label(item.get("label"))
                key = gaap or label
                new_item = {
                    "label": item.get("label"),
                    "gaap": gaap,
                    "values": {p: None for p in all_periods}
                }
                for yp, v in item.get("values", {}).items():
                    new_item["values"][normalize_year(yp)] = normalize_value(v)
                new_sec["items"].append(new_item)
                item_map[key] = new_item
            merged_stmt["sections"].append(new_sec)

        # --- Merge newer filings ---
        for year_key, filing in data["years"].items():
            if stmt_type not in filing or year_key == oldest_year_key:
                continue

            stmt = filing[stmt_type]
            # flatten all items
            flat_items = []
            for sec in stmt.get("sections", []):
                for item in sec.get("items", []):
                    flat_items.append((sec.get("section"), item))

            # match each item globally
            for sec_name, item in flat_items:
                gaap = item.get("gaap")
                label = normalize_label(item.get("label"))
                new_vals = {normalize_year(k): normalize_value(v)
                            for k, v in item.get("values", {}).items()}

                matched = None
                overlap_needed = 2 if stmt_type in ["income_statement", "cash_flow_statement"] else 1

                # --- 1. Value matching ---
                for existing in item_map.values():
                    overlap = 0
                    for y, v in new_vals.items():
                        if v is not None and existing["values"].get(y) == v:
                            overlap += 1
                    if overlap >= overlap_needed:
                        matched = existing
                        break

                # --- 2. GAAP code ---
                if not matched and gaap and gaap in item_map:
                    matched = item_map[gaap]

                # --- 3. Label match ---
                if not matched:
                    for key, existing in item_map.items():
                        if normalize_label(existing["label"]) == label:
                            matched = existing
                            break

                # --- 4. If no match → create new item in correct section ---
                if not matched:
                    new_item = {
                        "label": item.get("label"),
                        "gaap": gaap,
                        "values": {p: None for p in all_periods}
                    }
                    for p, v in new_vals.items():
                        new_item["values"][p] = v
                    # find correct section (from this filing)
                    target_sec = None
                    for s in merged_stmt["sections"]:
                        if s["section"] == sec_name:
                            target_sec = s
                            break
                    if not target_sec:
                        target_sec = {"section": sec_name, "gaap": None, "items": []}
                        merged_stmt["sections"].append(target_sec)
                    target_sec["items"].append(new_item)
                    item_map[gaap or label + f"_{len(item_map)}"] = new_item
                    matched = new_item

                # merge values
                for p, v in new_vals.items():
                    if v is not None:
                        matched["values"][p] = v

        # order periods
        merged_stmt["periods"] = sorted(all_periods)

        # reorder values
        for sec in merged_stmt["sections"]:
            for item in sec["items"]:
                item["values"] = {p: item["values"].get(p) for p in merged_stmt["periods"]}

        final_output["statements"][stmt_type] = merged_stmt

    return final_output
