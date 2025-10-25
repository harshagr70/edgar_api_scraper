import streamlit as st
import pandas as pd
from helper.api_helper_functions import get_available_years_count, get_multi_year_financials_parallel
from helper.financial_merger_helper import build_unified_catalog_all_statements

# Page config
st.set_page_config(page_title="Financial Statement Viewer", layout="wide")

# Custom CSS for better table styling
st.markdown("""
    <style>
    .section-header {
        background-color: #1f4788;
        color: white;
        font-weight: bold;
        padding: 8px;
        font-size: 14px;
    }
    .dataframe {
        font-size: 13px;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #1f4788;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("📊 Financial Statement Viewer")

# Initialize session state
if 'available_years' not in st.session_state:
    st.session_state.available_years = None
if 'current_ticker' not in st.session_state:
    st.session_state.current_ticker = None
if 'years_checked' not in st.session_state:
    st.session_state.years_checked = False

# Sidebar inputs
with st.sidebar:
    st.header("Step 1: Check Availability")
    ticker = st.text_input("Company Ticker", value="AAPL", placeholder="e.g., AAPL, MSFT")
    
    check_button = st.button("🔍 Check Available Years", type="secondary", use_container_width=True)
    
    st.markdown("---")
    
    # ✅ Show Step 2 only after checking availability
    if st.session_state.years_checked and st.session_state.current_ticker == ticker.upper():
        st.header("Step 2: Fetch Data")
        
        if st.session_state.available_years and st.session_state.available_years > 0:
            st.markdown(f"""
            <div class="success-box">
                ✅ <strong>{st.session_state.available_years} years</strong> of data available for {ticker.upper()}
            </div>
            """, unsafe_allow_html=True)
            
            years_back = st.number_input(
                "Years to Fetch", 
                min_value=1, 
                max_value=st.session_state.available_years, 
                value=min(3, st.session_state.available_years),
                help=f"Choose between 1 and {st.session_state.available_years} years"
            )
            
            fetch_button = st.button("📥 Fetch Financial Data", type="primary", use_container_width=True)
        else:
            st.error(f"❌ No data available for {ticker.upper()}")
            fetch_button = False
            years_back = 3
    else:
        st.info("👆 Check available years first")
        fetch_button = False
        years_back = 3

# Helper function to format statement data into clean display with section headers
def format_statement(statement_dict, statement_name):
    if not statement_dict:
        st.warning(f"No data available for {statement_name}")
        return
    
    st.subheader(f"📄 {statement_name.upper()} (Scale: millions)")
    
    # Group items by section (preserving order from OrderedDict)
    sections = {}
    section_order = []
    for key, item in statement_dict.items():
        section_label = item.get("section_label", "Unknown Section")
        if section_label not in sections:
            sections[section_label] = []
            section_order.append(section_label)
        sections[section_label].append(item)
    
    # Get all years and sort descending
    all_years = set()
    for item in statement_dict.values():
        all_years.update(item.get("values", {}).keys())
    years_sorted = sorted(all_years, reverse=True)
    
    # Build complete table with section headers as rows
    all_rows = []
    
    for section_label in section_order:
        items = sections[section_label]
        
        # Add section header row (with empty values for year columns)
        section_row = {"Label": f"**{section_label}**", "_is_section": True}
        for year in years_sorted:
            section_row[year] = ""
        all_rows.append(section_row)
        
        # Add line items under this section
        for item in items:
            row = {"Label": f"  {item.get('item_label', 'N/A')}", "_is_section": False}
            for year in years_sorted:
                value = item.get("values", {}).get(year, 0)
                # Format: show "-" for 0, otherwise format with commas
                
            if value is None or value == 0:
                row[year] = "-"
            else:
                row[year] = f"{value:,.2f}" if abs(value) < 1 else f"{value:,.0f}"
            all_rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(all_rows)
    
    # Remove the helper column before display
    is_section_flags = df["_is_section"].tolist()
    df_display = df.drop(columns=["_is_section"])
    
    # Apply styling to highlight section rows
    def highlight_sections(row):
        row_idx = row.name
        if is_section_flags[row_idx]:
            return ['background-color: #1f4788; color: white; font-weight: bold'] * len(row)
        return [''] * len(row)
    
    # Style and display
    styled_df = df_display.style.apply(highlight_sections, axis=1)
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Label": st.column_config.TextColumn("Label", width="large"),
            **{year: st.column_config.TextColumn(year, width="medium") for year in years_sorted}
        }
    )

# ✅ Handle Step 1: Check Available Years
if check_button and ticker:
    with st.spinner(f"Checking available data for {ticker}..."):
        try:
            available_count = get_available_years_count(ticker)
            
            st.session_state.available_years = available_count
            st.session_state.current_ticker = ticker.upper()
            st.session_state.years_checked = True
            
            if available_count > 0:
                st.success(f"✅ Found {available_count} years of 10-K filings for {ticker.upper()}")
                st.info("👉 Now select how many years to fetch in the sidebar")
            else:
                st.error(f"❌ No 10-K filings found for {ticker.upper()}. Please verify the ticker symbol.")
                
        except Exception as e:
            st.error(f"❌ Error checking availability: {str(e)}")
            st.exception(e)

# ✅ Handle Step 2: Fetch Financial Data
elif fetch_button and ticker and st.session_state.years_checked:
    with st.spinner(f"Fetching {years_back} years of data for {ticker}..."):
        try:
            # Fetch raw data from Edgar API
            raw_data = get_multi_year_financials_parallel(ticker, years_back=years_back)
            
            # Debug: Check what we got
            if not raw_data:
                st.error("❌ No data received from API. Please check the ticker symbol and try again.")
                st.stop()
            
            # Extract counts
            available_years_count = raw_data.get('available_years_count', 0)
            requested_years = raw_data.get('requested_years', years_back)
            fetched_years = raw_data.get('fetched_years', 0)
            
            # Show fetch summary
            st.info(f"📊 Requested: {requested_years} years | Available: {available_years_count} years | Fetched: {fetched_years} years")
            
            if fetched_years == 0:
                st.error(f"❌ No financial statements could be retrieved for {ticker.upper()}")
                st.stop()
            
            # Check for errors in the response
            if isinstance(raw_data, dict) and 'error' in raw_data:
                st.error(f"❌ API Error: {raw_data['error']}")
                st.stop()
            
            # Check if we got years data
            if isinstance(raw_data, dict) and 'years' in raw_data:
                years_data = raw_data['years']
                
                if not years_data:
                    st.error(f"❌ No financial statements found for {ticker.upper()}")
                    st.stop()
                
                # Check if any year has errors
                error_found = False
                for year, statements in years_data.items():
                    for stmt_type, stmt_data in statements.items():
                        if isinstance(stmt_data, dict) and 'error' in stmt_data:
                            st.error(f"❌ Error in {year} - {stmt_type}: {stmt_data['error']}")
                            error_found = True
                
                if error_found:
                    st.warning("⚠️ Some statements encountered errors during fetching")
            
            st.write(f"✅ Received data for ticker: {raw_data.get('ticker', ticker)}")
            
            # Build unified catalogs for all statements
            unified_data = build_unified_catalog_all_statements(raw_data)
            
            if not unified_data:
                st.error("❌ Failed to process financial data. The data might be incomplete.")
                st.stop()
            
            st.success(f"✅ Data processed successfully for {ticker.upper()}")
            
            # Extract each statement type
            income_statement = unified_data.get("income_statement", {})
            balance_sheet = unified_data.get("balance_sheet", {})
            cash_flow = unified_data.get("cash_flow_statement", {})
            
            # Display in tabs
            tab1, tab2, tab3 = st.tabs(["📈 Income Statement", "💰 Balance Sheet", "💵 Cash Flow"])
            
            with tab1:
                format_statement(income_statement, "Income Statement")
            
            with tab2:
                format_statement(balance_sheet, "Balance Sheet")
            
            with tab3:
                format_statement(cash_flow, "Cash Flow Statement")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)
            
            # Additional debugging info
            with st.expander("🔍 Debug Information"):
                st.write("Error type:", type(e).__name__)
                st.write("Error details:", str(e))
                import traceback
                st.code(traceback.format_exc())

# Initial state message
elif not ticker:
    st.info("👈 Enter a ticker symbol in the sidebar and click 'Check Available Years' to begin")
elif not st.session_state.years_checked:
    st.info("👈 Click 'Check Available Years' to see how much data is available for this ticker")