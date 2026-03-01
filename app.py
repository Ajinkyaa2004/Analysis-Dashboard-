import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


st.set_page_config(layout="wide")

# ========================================
# CONFIGURATION SECTION
# ========================================
# Initialize session state for configuration if not exists
if 'config' not in st.session_state:
    st.session_state.config = {
        'branches': ['NSW', 'QLD', 'WA'],
        'excel_sheet_names': ['WA', 'QLD', 'NSW'],
        'csv_columns': [
            "Entity Name", "Branch Region", "Branch", "Division", "Due Date", 
            "Top Level Customer ID", "Top Level Customer Name", "Customer ID", 
            "Customer", "Billing Group ID", "Billing Group", "Invoice ID", 
            "Invoice #", "Issue Date", "Total", "Outstanding", "Delivery", "Status"
        ],
        'date_format': 'dayfirst',  # 'dayfirst' or 'monthfirst'
        'currency_symbol': '$',
        'week_count': 52,
        'quarters': {
            'Q1': (1, 13),
            'Q2': (14, 26),
            'Q3': (27, 39),
            'Q4': (40, 52)
        },
        'year_comparison_window': 2,
        'csv_has_header': False,
        'excel_header_row': 0,
        'excel_data_start_row': 2,
        'chart_heights': {'default': 500, 'quarter': 400},
        'column_mappings': {
            'Customer': 'Customer',
            'Issue Date': 'Issue Date',
            'Total': 'Total',
            'Branch': 'Branch',
            'Invoice ID': 'Invoice ID',
            'Outstanding': 'Outstanding'
        }
    }

# Helper function for currency formatting
def format_currency(value, decimals=2):
    """Format a number as currency using the configured currency symbol"""
    currency_symbol = st.session_state.config['currency_symbol']
    return f"{currency_symbol}{value:,.{decimals}f}"

# ========================================
# AUTO-DETECTION FUNCTIONS
# ========================================

def smart_column_mapper(columns):
    """
    Intelligently map CSV columns to required fields.
    Returns a dictionary mapping required fields to actual column names.
    """
    columns_lower = [str(col).lower().strip() for col in columns]
    mapping = {}
    
    # Define patterns for each required field
    patterns = {
        'Customer': [
            'customer', 'customer name', 'cust', 'client', 
            'customer id', 'cust id', 'client name', 'account name'
        ],
        'Issue Date': [
            'issue date', 'date', 'invoice date', 'sale date', 
            'transaction date', 'order date', 'issuedate', 'inv date'
        ],
        'Total': [
            'total', 'amount', 'sales', 'revenue', 'value', 
            'total amount', 'sale amount', 'grand total', 'net total'
        ],
        'Branch': [
            'branch', 'location', 'store', 'region', 'office', 'site'
        ],
        'Invoice ID': [
            'invoice id', 'invoice #', 'invoice', 'inv id', 'bill id',
            'transaction id', 'order id', 'reference'
        ],
        'Outstanding': [
            'outstanding', 'balance', 'due', 'pending', 'unpaid'
        ]
    }
    
    # Try to find best match for each required field
    for required_field, search_patterns in patterns.items():
        best_match = None
        best_score = 0
        
        for i, col_lower in enumerate(columns_lower):
            for pattern in search_patterns:
                # Exact match (highest priority)
                if col_lower == pattern:
                    best_match = columns[i]
                    best_score = 100
                    break
                # Contains pattern
                elif pattern in col_lower:
                    score = 50 + (len(pattern) / len(col_lower)) * 50
                    if score > best_score:
                        best_match = columns[i]
                        best_score = score
            
            if best_score == 100:
                break
        
        if best_match:
            mapping[required_field] = best_match
    
    return mapping

def auto_detect_csv_structure(uploaded_files):
    """Auto-detect CSV structure from uploaded files"""
    detected_config = {}
    
    if not uploaded_files or len(uploaded_files) == 0:
        return detected_config
    
    # Get first non-None file for detection
    sample_file = next((f for f in uploaded_files if f is not None), None)
    if sample_file is None:
        return detected_config
    
    try:
        # Reset file pointer
        sample_file.seek(0)
        
        # Try to read with header first
        df_with_header = pd.read_csv(sample_file, nrows=5)
        sample_file.seek(0)
        
        # Check if first row looks like headers (mostly strings, no numbers)
        first_row_values = df_with_header.iloc[0] if len(df_with_header) > 0 else []
        numeric_count = sum(pd.to_numeric(first_row_values, errors='coerce').notna())
        has_header = numeric_count < len(first_row_values) * 0.3  # If less than 30% are numbers, likely headers
        
        if has_header:
            detected_config['csv_has_header'] = True
            detected_config['csv_columns'] = df_with_header.columns.tolist()
            # Perform intelligent column mapping
            detected_config['column_mappings'] = smart_column_mapper(df_with_header.columns.tolist())
        else:
            # No header - use default column count
            sample_file.seek(0)
            df_no_header = pd.read_csv(sample_file, header=None, nrows=1)
            num_cols = len(df_no_header.columns)
            detected_config['csv_has_header'] = False
            
            # Intelligently handle column mapping
            default_columns = st.session_state.config['csv_columns']
            if num_cols == len(default_columns):
                # Perfect match - use default columns
                detected_config['csv_columns'] = default_columns
                detected_config['column_mappings'] = smart_column_mapper(default_columns)
            elif num_cols == 18 and len(default_columns) == 19:
                # Common case: 18 vs 19 columns - use first 18 from defaults
                detected_config['csv_columns'] = default_columns[:18]
                detected_config['column_mappings'] = smart_column_mapper(default_columns[:18])
            elif abs(num_cols - len(default_columns)) <= 2:
                # Close match - adapt by truncating or using subset
                cols = default_columns[:num_cols] if num_cols < len(default_columns) else default_columns
                detected_config['csv_columns'] = cols
                detected_config['column_mappings'] = smart_column_mapper(cols)
            else:
                # Significant mismatch - use generic names
                detected_config['csv_columns'] = [f"Column_{i+1}" for i in range(num_cols)]
                detected_config['column_mappings'] = {}  # No mappings for generic columns
        
        sample_file.seek(0)
        
    except Exception as e:
        st.warning(f"⚠️ Could not auto-detect CSV structure: {str(e)}")
    
    return detected_config

def auto_detect_date_format(uploaded_files):
    """Auto-detect date format from uploaded CSV files"""
    if not uploaded_files or len(uploaded_files) == 0:
        return None
    
    sample_file = next((f for f in uploaded_files if f is not None), None)
    if sample_file is None:
        return None
    
    try:
        sample_file.seek(0)
        df = pd.read_csv(sample_file, nrows=10)
        sample_file.seek(0)
        
        # Look for date columns (common names)
        date_columns = [col for col in df.columns if any(word in str(col).lower() for word in ['date', 'issue', 'due'])]
        
        if date_columns:
            date_col = date_columns[0]
            sample_dates = df[date_col].dropna().head(5)
            
            # Try both formats
            dayfirst_success = 0
            monthfirst_success = 0
            
            for date_str in sample_dates:
                try:
                    pd.to_datetime(date_str, dayfirst=True)
                    dayfirst_success += 1
                except:
                    pass
                
                try:
                    pd.to_datetime(date_str, dayfirst=False)
                    monthfirst_success += 1
                except:
                    pass
            
            # If dates have day > 12, they must be dayfirst
            for date_str in sample_dates:
                parts = str(date_str).split('/')
                if len(parts) >= 2:
                    try:
                        first_part = int(parts[0])
                        if first_part > 12:
                            return 'dayfirst'
                    except:
                        pass
            
            return 'dayfirst' if dayfirst_success >= monthfirst_success else 'monthfirst'
    
    except Exception as e:
        pass
    
    return None

def auto_detect_excel_sheets(uploaded_excel):
    """Auto-detect sheet names from uploaded Excel file"""
    if uploaded_excel is None:
        return None
    
    try:
        uploaded_excel.seek(0)
        excel_file = pd.ExcelFile(uploaded_excel)
        sheet_names = excel_file.sheet_names
        uploaded_excel.seek(0)
        return sheet_names
    except Exception as e:
        st.warning(f"⚠️ Could not read Excel sheets: {str(e)}")
        return None

def auto_detect_week_count(uploaded_excel, sheet_names):
    """Auto-detect week count from Excel historical data"""
    if uploaded_excel is None or not sheet_names:
        return None
    
    try:
        uploaded_excel.seek(0)
        # Read first sheet
        df = pd.read_excel(uploaded_excel, sheet_name=sheet_names[0], header=None)
        uploaded_excel.seek(0)
        
        # Look for rows containing "Week"
        week_rows = df[df.iloc[:, 0].astype(str).str.contains(r'Week\s*\d+', na=False, regex=True)]
        if len(week_rows) > 0:
            # Extract week numbers
            week_numbers = []
            for val in week_rows.iloc[:, 0]:
                match = pd.Series([val]).astype(str).str.extract(r'Week\s*(\d+)')[0]
                if not match.empty and not pd.isna(match[0]):
                    week_numbers.append(int(match[0]))
            
            if week_numbers:
                max_week = max(week_numbers)
                return max_week
    except Exception as e:
        pass
    
    return None

def auto_detect_currency(uploaded_files):
    """Auto-detect currency symbol from data"""
    if not uploaded_files or len(uploaded_files) == 0:
        return None
    
    sample_file = next((f for f in uploaded_files if f is not None), None)
    if sample_file is None:
        return None
    
    try:
        sample_file.seek(0)
        df = pd.read_csv(sample_file, nrows=10)
        sample_file.seek(0)
        
        # Look for currency columns
        currency_cols = [col for col in df.columns if any(word in str(col).lower() for word in ['total', 'amount', 'price', 'outstanding'])]
        
        if currency_cols:
            sample_values = df[currency_cols[0]].dropna().head(3).astype(str)
            for val in sample_values:
                # Check for currency symbols
                if '$' in val:
                    return '$'
                elif '£' in val:
                    return '£'
                elif '€' in val:
                    return '€'
                elif '₹' in val:
                    return '₹'
    except:
        pass
    
    return None

@st.cache_data
# ///

# ///


def load_data(branch_files, branch_names, columns, date_format='dayfirst', csv_has_header=False, column_mappings=None):
    """Load data from multiple branch CSV files with configurable structure and intelligent column mapping"""
    dfs = []
    
    # Default column mappings if not provided
    if column_mappings is None:
        column_mappings = {
            'Customer': 'Customer',
            'Issue Date': 'Issue Date',
            'Total': 'Total',
            'Branch': 'Branch'
        }
    
    for i, (file, branch_name) in enumerate(zip(branch_files, branch_names)):
        try:
            if csv_has_header:
                df = pd.read_csv(file)
                # Auto-detection succeeded - no warning needed
            else:
                # Read without header and check column count
                df = pd.read_csv(file, header=None)
                actual_cols = len(df.columns)
                
                # If column count matches, use predefined names
                if actual_cols == len(columns):
                    df.columns = columns
                else:
                    # Auto-adapt: generate column names based on actual structure
                    if actual_cols == 18 and len(columns) == 19:
                        # Use first 18 columns from the predefined list
                        df.columns = columns[:18]
                    else:
                        # Use generic column names and show info only
                        df.columns = [f"Column_{i+1}" for i in range(actual_cols)]
                        # Only warn if significant mismatch (not just off-by-one)
                        if abs(actual_cols - len(columns)) > 2:
                            st.warning(f"⚠️ {branch_name}: Detected {actual_cols} columns (expected {len(columns)}). Using auto-detected structure.")
            
            df['Branch'] = branch_name
            dfs.append(df)
        except Exception as e:
            st.error(f"❌ Error loading {branch_name} file: {str(e)}")
            return None
    
    if not dfs:
        return None
    
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    
    # Apply intelligent column mappings to create standardized column names
    # This ensures the dashboard works regardless of the original column names
    
    # Map Customer column
    if 'Customer' in column_mappings and column_mappings['Customer'] in df.columns:
        if column_mappings['Customer'] != 'Customer':
            df['Customer'] = df[column_mappings['Customer']].astype(str).str.strip()
        else:
            df['Customer'] = df['Customer'].astype(str).str.strip()
    elif 'Customer' in df.columns:
        df['Customer'] = df['Customer'].astype(str).str.strip()
    else:
        # Create dummy Customer column if not found
        df['Customer'] = 'Unknown Customer'
        st.warning("⚠️ Customer column not found. Using default value.")
    
    # Map Issue Date column
    if 'Issue Date' in column_mappings and column_mappings['Issue Date'] in df.columns:
        date_col = column_mappings['Issue Date']
        if date_format == 'dayfirst':
            df['Issue Date'] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
        else:
            df['Issue Date'] = pd.to_datetime(df[date_col], errors='coerce')
    elif 'Issue Date' in df.columns:
        if date_format == 'dayfirst':
            df['Issue Date'] = pd.to_datetime(df['Issue Date'], dayfirst=True, errors='coerce')
        else:
            df['Issue Date'] = pd.to_datetime(df['Issue Date'], errors='coerce')
    else:
        # Create dummy Issue Date if not found
        df['Issue Date'] = pd.Timestamp.now()
        st.error("❌ Issue Date column not found. Cannot proceed without date information.")
        return None
    
    # Map Total column
    if 'Total' in column_mappings and column_mappings['Total'] in df.columns:
        total_col = column_mappings['Total']
        df['Total'] = pd.to_numeric(df[total_col].astype(str).str.replace(',', ''), errors='coerce')
    elif 'Total' in df.columns:
        df['Total'] = pd.to_numeric(df['Total'].astype(str).str.replace(',', ''), errors='coerce')
    else:
        # Create dummy Total if not found
        df['Total'] = 0.0
        st.error("❌ Total/Amount column not found. Cannot proceed without sales data.")
        return None
    
    # Ensure Branch column exists and is properly formatted
    df['Branch'] = df['Branch'].astype(str).str.strip()
    
    # Create derived columns for analysis
    df['Year'] = df['Issue Date'].dt.year
    df['Month'] = df['Issue Date'].dt.to_period('M').astype(str)

    return df.dropna(subset=['Issue Date', 'Total', 'Branch'])

# ========================================
# SIDEBAR - CONFIGURATION SETTINGS
# ========================================
st.sidebar.title("⚙️ Configuration")
with st.sidebar.expander("🔧 Advanced Settings (Optional)", expanded=False):
    st.markdown("**Customize these settings if your data has a different structure**")
    
    # Branch configuration
    st.markdown("##### Branch Names")
    branch_input = st.text_input(
        "Enter branch names (comma-separated)", 
        value=", ".join(st.session_state.config['branches']),
        help="Default: NSW, QLD, WA"
    )
    config_branches = [b.strip() for b in branch_input.split(',') if b.strip()]
    
    # Excel sheet names
    st.markdown("##### Excel Sheet Names")
    sheet_input = st.text_input(
        "Enter sheet names (comma-separated)", 
        value=", ".join(st.session_state.config['excel_sheet_names']),
        help="Sheet names in your historical Excel file"
    )
    config_sheet_names = [s.strip() for s in sheet_input.split(',') if s.strip()]
    
    # Date format
    st.markdown("##### Date Format")
    date_format_option = st.selectbox(
        "Date format in CSV files",
        options=['DD/MM/YYYY (Day First)', 'MM/DD/YYYY (Month First)'],
        index=0,
        help="Select the date format used in your CSV files"
    )
    config_date_format = 'dayfirst' if 'Day First' in date_format_option else 'monthfirst'
    
    # Currency
    st.markdown("##### Currency Settings")
    config_currency = st.text_input(
        "Currency Symbol", 
        value=st.session_state.config['currency_symbol'],
        help="Default: $"
    )
    
    # Week count and quarters
    st.markdown("##### Week & Quarter Settings")
    config_week_count = st.number_input(
        "Total Weeks in Year", 
        min_value=1, 
        max_value=53, 
        value=st.session_state.config['week_count'],
        help="Default: 52"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        q1_start = st.number_input("Q1 Start", min_value=1, value=1, key='q1s')
        q1_end = st.number_input("Q1 End", min_value=1, value=13, key='q1e')
        q2_start = st.number_input("Q2 Start", min_value=1, value=14, key='q2s')
        q2_end = st.number_input("Q2 End", min_value=1, value=26, key='q2e')
    with col2:
        q3_start = st.number_input("Q3 Start", min_value=1, value=27, key='q3s')
        q3_end = st.number_input("Q3 End", min_value=1, value=39, key='q3e')
        q4_start = st.number_input("Q4 Start", min_value=1, value=40, key='q4s')
        q4_end = st.number_input("Q4 End", min_value=1, value=52, key='q4e')
    
    config_quarters = {
        'Q1': (q1_start, q1_end),
        'Q2': (q2_start, q2_end),
        'Q3': (q3_start, q3_end),
        'Q4': (q4_start, q4_end)
    }
    
    # Year comparison window
    config_year_window = st.number_input(
        "Year Comparison Window", 
        min_value=2, 
        max_value=10, 
        value=st.session_state.config['year_comparison_window'],
        help="Number of years to compare for customer trends (default: 2)"
    )
    
    # CSV header option
    config_csv_has_header = st.checkbox(
        "CSV files have header row", 
        value=st.session_state.config['csv_has_header'],
        help="Check if your CSV files include column names in the first row"
    )
    
    # Apply button
    if st.button("💾 Apply Configuration"):
        st.session_state.config.update({
            'branches': config_branches,
            'excel_sheet_names': config_sheet_names,
            'date_format': config_date_format,
            'currency_symbol': config_currency,
            'week_count': config_week_count,
            'quarters': config_quarters,
            'year_comparison_window': config_year_window,
            'csv_has_header': config_csv_has_header
        })
        st.success("✅ Configuration updated!")
        st.rerun()

st.sidebar.markdown("---")

# ========================================
# SIDEBAR - FILE UPLOAD
# ========================================
st.sidebar.title("⬆ Upload Sales Data")
st.sidebar.markdown("Upload CSV files for each branch:")

# Dynamic branch file uploaders
uploaded_branch_files = []
for branch in st.session_state.config['branches']:
    uploaded_file = st.sidebar.file_uploader(
        f"{branch} Branch CSV", 
        type=['csv'], 
        key=f'branch_{branch.lower().replace(" ", "_")}'
    )
    uploaded_branch_files.append(uploaded_file)

st.sidebar.markdown("---")

# Historical Data Upload
st.sidebar.title("📊 Upload Historical Sales Data")
st.sidebar.markdown("Upload Excel file for annual sales analysis:")
uploaded_historical = st.sidebar.file_uploader(
    f"Historical Sales Excel (with {', '.join(st.session_state.config['excel_sheet_names'])} sheets)", 
    type=['xlsx', 'xls'], 
    key='historical',
    help=f"Upload an Excel file containing sheets named {', '.join(st.session_state.config['excel_sheet_names'])} with historical sales data"
)

st.sidebar.markdown("---")

# ========================================
# AUTO-DETECTION & CONFIGURATION UPDATE
# ========================================
# Reset auto-detection flags when files are removed
if not all(f is not None for f in uploaded_branch_files):
    if 'auto_detected' in st.session_state:
        del st.session_state.auto_detected
        
if uploaded_historical is None:
    if 'excel_auto_detected' in st.session_state:
        del st.session_state.excel_auto_detected

# Check if files are uploaded and trigger auto-detection
all_files_uploaded = all(f is not None for f in uploaded_branch_files)

if all_files_uploaded and 'auto_detected' not in st.session_state:
    st.session_state.auto_detected = True
    
    # Auto-detect configuration from uploaded files
    detected_updates = {}
    
    # Detect CSV structure
    csv_config = auto_detect_csv_structure(uploaded_branch_files)
    if csv_config:
        detected_updates.update(csv_config)
    
    # Detect date format
    date_format = auto_detect_date_format(uploaded_branch_files)
    if date_format:
        detected_updates['date_format'] = date_format
    
    # Detect currency
    currency = auto_detect_currency(uploaded_branch_files)
    if currency:
        detected_updates['currency_symbol'] = currency
    
    # Apply detected updates
    if detected_updates:
        st.session_state.config.update(detected_updates)
        st.sidebar.success("✨ Auto-detected file structure!")

# Auto-detect Excel sheets when historical file is uploaded
if uploaded_historical is not None and 'excel_auto_detected' not in st.session_state:
    st.session_state.excel_auto_detected = True
    
    detected_sheets = auto_detect_excel_sheets(uploaded_historical)
    if detected_sheets and len(detected_sheets) > 0:
        # Update both sheet names and branch names if they match
        st.session_state.config['excel_sheet_names'] = detected_sheets
        
        # Auto-detect week count from historical data
        week_count = auto_detect_week_count(uploaded_historical, detected_sheets)
        if week_count and week_count != 52:
            st.session_state.config['week_count'] = week_count
            # Auto-adjust quarters for different week counts
            if week_count == 53:
                st.session_state.config['quarters'] = {
                    'Q1': (1, 13),
                    'Q2': (14, 27),
                    'Q3': (28, 40),
                    'Q4': (41, 53)
                }
            st.sidebar.info(f"📊 Detected {week_count} weeks in historical data")
        
        # If detected sheets look like branch names (2-4 chars, all caps), use them as branches too
        if all(len(s) <= 4 and s.isupper() for s in detected_sheets):
            old_branches = st.session_state.config['branches']
            st.session_state.config['branches'] = detected_sheets
            
            # Only show message if branches actually changed
            if old_branches != detected_sheets:
                st.sidebar.success(f"✨ Auto-detected branches: {', '.join(detected_sheets)}")
                st.sidebar.info("⬆️ Scroll up to upload CSV files for each branch")
        else:
            st.sidebar.info(f"📊 Detected Excel sheets: {', '.join(detected_sheets)}")

# Show auto-detected configuration in sidebar
if all_files_uploaded or uploaded_historical is not None:
    with st.sidebar.expander("🔍 Auto-Detected Configuration", expanded=False):
        if all_files_uploaded:
            st.markdown(f"""
            **CSV Structure:**
            - Has Header: {'Yes' if st.session_state.config['csv_has_header'] else 'No'}
            - Columns: {len(st.session_state.config['csv_columns'])}
            
            **Date Format:** {'DD/MM/YYYY' if st.session_state.config['date_format'] == 'dayfirst' else 'MM/DD/YYYY'}
            
            **Currency Symbol:** {st.session_state.config['currency_symbol']}
            """)
            
            # Show intelligent column mappings
            mappings = st.session_state.config.get('column_mappings', {})
            if mappings:
                st.markdown("**Column Mappings:**")
                for required_field, mapped_column in mappings.items():
                    if mapped_column:
                        st.markdown(f"✅ `{required_field}` ← `{mapped_column}`")
                if len(mappings) < 3:
                    st.warning("⚠️ Some required columns not mapped. Check your data structure.")
        
        st.markdown(f"""
        **Branches:** {', '.join(st.session_state.config['branches'])}
        """)
        
        if uploaded_historical is not None:
            quarters_str = ", ".join([f"{q}: {r[0]}-{r[1]}" for q, r in st.session_state.config['quarters'].items()])
            st.markdown(f"""
            **Historical Data:**
            - Excel Sheets: {', '.join(st.session_state.config['excel_sheet_names'])}
            - Week Count: {st.session_state.config['week_count']}
            - Quarters: {quarters_str}
            """)
        
        st.markdown("*If anything looks wrong, adjust in Advanced Settings above*")

st.sidebar.markdown("---")

if all_files_uploaded:
    df = load_data(
        uploaded_branch_files, 
        st.session_state.config['branches'],
        st.session_state.config['csv_columns'],
        st.session_state.config['date_format'],
        st.session_state.config['csv_has_header'],
        st.session_state.config.get('column_mappings', {})
    )
else:
    required_count = len(st.session_state.config['branches'])
    st.sidebar.warning(f"⚠ Please upload all {required_count} CSV files to proceed")
    df = None

@st.cache_data
def load_historical_sales_data(excel_file=None, sheet_names=None, excel_header_row=0, excel_data_start_row=2):
    """Loads and preprocesses the historical weekly sales data from Excel sheets,
    handling the two-row header structure and selecting relevant columns."""
    if excel_file is None:
        excel_file_path = 'HISTORICAL_REPORT.xlsx' # Fallback to default file
    else:
        excel_file_path = excel_file
    
    if sheet_names is None:
        sheet_names = ['WA', 'QLD', 'NSW']  # Default sheet names

    all_historical_df = []

    try:
        for sheet_name in sheet_names:
            # Read the specific sheet from the Excel file with no header initially
            df_raw = pd.read_excel(excel_file_path, sheet_name=sheet_name, header=None)

            # Extract the relevant header information from the specified header row
            header_row_0 = df_raw.iloc[excel_header_row]  # Configurable header row

            # Identify the indices of the actual sales year columns in header_row_0
            # These are columns like '18/19', '19/20', etc., which are strings containing '/'
            sales_year_indices = [i for i, val in enumerate(header_row_0) if isinstance(val, str) and '/' in val]

            # Construct the list of new column names for the DataFrame
            # The first column will be 'Week' (from 'Week No' in row 1, which is df_raw.iloc[1,0])
            new_column_names = ['Week']
            for idx in sales_year_indices:
                new_column_names.append(str(header_row_0[idx]))

            # Select the actual data rows (starting from configurable data start row)
            # and only the columns that correspond to our new_column_names
            data_columns_to_select = [0] + sales_year_indices

            df_processed = df_raw.iloc[excel_data_start_row:, data_columns_to_select].copy()
            df_processed.columns = new_column_names # Assign the new, clean column names

            # Filter out summary rows (Q1 Total, Totals, etc.)
            df_processed = df_processed[df_processed['Week'].astype(str).str.contains(r'Week\s\d+', na=False)]

            # Melt the DataFrame to unpivot the year columns
            id_vars_for_melt = ['Week']
            value_vars_for_melt = [col for col in new_column_names if col != 'Week']

            df_melted = df_processed.melt(id_vars=id_vars_for_melt, value_vars=value_vars_for_melt,
                                           var_name='Financial Year', value_name='Total')

            # Add Branch column
            df_melted['Branch'] = sheet_name

            # Convert 'Week' to numeric
            df_melted['Week'] = df_melted['Week'].astype(str).str.replace('Week ', '').astype(int)

            # Convert 'Total' to numeric, handling commas and errors, then to float
            df_melted['Total'] = pd.to_numeric(df_melted['Total'].astype(str).str.replace(',', ''), errors='coerce').astype(float)

            all_historical_df.append(df_melted)

    except FileNotFoundError:
        st.error(f"Error: Excel file '{excel_file_path}' not found. Please ensure it's in the same directory as the script.")
    except Exception as e:
        st.error(f"An error occurred while processing Excel file '{excel_file_path}' for sheet '{sheet_name}': {e}")

    if all_historical_df:
        return pd.concat(all_historical_df, ignore_index=True).dropna(subset=['Total'])
    else:
        return pd.DataFrame(columns=['Week', 'Financial Year', 'Total', 'Branch'])

# Main app - only runs if files are uploaded
if all_files_uploaded:
    # Load historical dataframes
    if uploaded_historical is not None:
        historical_df = load_historical_sales_data(
            uploaded_historical, 
            st.session_state.config['excel_sheet_names'],
            st.session_state.config['excel_header_row'],
            st.session_state.config['excel_data_start_row']
        )
    else:
        # Try to load from default file if it exists
        try:
            historical_df = load_historical_sales_data(
                None,
                st.session_state.config['excel_sheet_names'],
                st.session_state.config['excel_header_row'],
                st.session_state.config['excel_data_start_row']
            )
        except:
            historical_df = pd.DataFrame()

    st.title("▸ Invoice & Customer Analysis Dashboard")

    # ---- Filters ---- #
    branch_options = df['Branch'].dropna().unique().tolist()
    branch = st.sidebar.multiselect("Select Branch(es)", options=branch_options, default=branch_options)

    # Historical data filters
    if not historical_df.empty:
        financial_year_options = sorted(historical_df['Financial Year'].dropna().unique().tolist())

        # Add a "Select All" checkbox
        select_all_years = st.sidebar.checkbox("Select All Financial Years", value=True)

        if select_all_years:
            selected_financial_years = financial_year_options
        else:
            # Default to the first year if "Select All" is not checked and no years are selected
            # Or you can choose to default to an empty list or specific years as per preference
            default_selection = [financial_year_options[0]] if financial_year_options else []
            selected_financial_years = st.sidebar.multiselect(
                "Select Financial Year(s) (Historical Data)",
                options=financial_year_options,
                default=default_selection # Default to only the first year when "Select All" is off
            )
            # Handle case where user deselects all after unchecking "Select All"
            if not selected_financial_years and not select_all_years:
                st.sidebar.warning("Please select at least one financial year or 'Select All'.")
                selected_financial_years = [] # Ensure it's an empty list to filter nothing

        # Apply branch filter to historical data
        filtered_historical_df = historical_df[
            historical_df['Branch'].isin(branch) &
            historical_df['Financial Year'].isin(selected_financial_years)
        ].copy() # Ensure filtered_historical_df is a copy
    else:
        st.info("📁 Historical sales data not loaded. Upload an Excel file in the sidebar for Annual Sales Analysis.")
        filtered_historical_df = pd.DataFrame()


    customer_options = df['Customer'].dropna().unique().tolist()
    customer_options = sorted(customer_options)
    customer = st.sidebar.multiselect("Select Customer(s)", options=customer_options)

    year_min, year_max = int(df['Year'].min()), int(df['Year'].max())
    year_range = st.sidebar.slider("Select Year Range", year_min, year_max, (year_min, year_max))

    date_range = st.sidebar.date_input("Filter by Issue Date Range", [df['Issue Date'].min(), df['Issue Date'].max()])
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    # ---- Apply filters ---- #
    filtered_df = df[
        df['Branch'].isin(branch) &
        df['Year'].between(*year_range) &
        df['Issue Date'].between(start_date, end_date)
    ]
    if customer:
        filtered_df = filtered_df[filtered_df['Customer'].isin(customer)]



    # ---- Annual Sales ---- #
    # import plotly.express as px
    # import pandas as pd
    # import streamlit as st

    # st.header("📈 Annual Sales Report")

    # # Grouping data by Year and Branch
    # annual_sales = filtered_df.groupby(['Year', 'Branch'])['Total'].sum().reset_index()

    # # Create pivot table for display
    # pivot_table = annual_sales.pivot(index='Year', columns='Branch', values='Total')

    # # Add a row at the bottom for total sales across all years
    # total_row = pivot_table.sum().rename("Total")
    # pivot_table_with_total = pd.concat([pivot_table, pd.DataFrame([total_row])])

    # # Show DataFrame
    # st.dataframe(pivot_table_with_total, use_container_width=True)

    # # Plotly Bar Chart
    # fig = px.bar(
    #     annual_sales,
    #     x='Year',
    #     y='Total',
    #     color='Branch',
    #     barmode='group',
    #     title='Annual Branch Sales Comparison',
    #     text_auto=True,
    #     hover_data={'Total': ':.2f', 'Branch': True, 'Year': True}
    # )

    # fig.update_layout(
    #     xaxis_title='Year',
    #     yaxis_title='Total Sales',
    #     hovermode='x unified'
    # )

    # st.plotly_chart(fig, use_container_width=True)

    # --- Annual Sales Analysis Dashboard ---
    st.header("📊 Annual Sales Analysis Dashboard")

    if not filtered_historical_df.empty:
        # Create tabs for better organization
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📊 Quarter Analysis", "📅 Week Analysis", "📉 Comparative Analysis"])
        
        with tab1:
            st.subheader("Annual Sales Overview")
            
            # Key metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            total_sales = filtered_historical_df['Total'].sum()
            avg_weekly_sales = filtered_historical_df['Total'].mean()
            total_weeks = filtered_historical_df['Week'].nunique()
            total_years = filtered_historical_df['Financial Year'].nunique()
            
            with col1:
                st.metric("Total Sales", format_currency(total_sales))
            with col2:
                st.metric("Avg Weekly Sales", format_currency(avg_weekly_sales))
            with col3:
                st.metric("Total Weeks", total_weeks)
            with col4:
                st.metric("Financial Years", total_years)
            
            st.markdown("---")
            
            # Financial Year Total Sales Comparison
            st.subheader("Financial Year Total Sales Comparison")
            annual_historical_sales = filtered_historical_df.groupby(['Financial Year', 'Branch'])['Total'].sum().reset_index()
            
            if not annual_historical_sales.empty:
                # Create pivot table for display
                pivot_annual = annual_historical_sales.pivot(index='Financial Year', columns='Branch', values='Total').fillna(0)
                pivot_annual['Total'] = pivot_annual.sum(axis=1)
                
                # Format as currency
                currency_format = f"{st.session_state.config['currency_symbol']}{{:,.2f}}"
                st.dataframe(
                    pivot_annual.style.format(currency_format),
                    use_container_width=True
                )
                
                # Bar chart
                fig_annual_hist = px.bar(
                    annual_historical_sales,
                    x='Financial Year',
                    y='Total',
                    color='Branch',
                    barmode='group',
                    title='Total Sales per Financial Year by Branch',
                    text_auto='.2s',
                    hover_data={'Total': ':,.2f', 'Branch': True, 'Financial Year': True}
                )
                fig_annual_hist.update_layout(
                    xaxis_title='Financial Year',
                    yaxis_title='Total Sales ($)',
                    hovermode='x unified',
                    height=500
                )
                st.plotly_chart(fig_annual_hist, use_container_width=True)
                
                # Year-over-Year Growth Analysis
                st.subheader("Year-over-Year Growth Analysis")
                yoy_growth = annual_historical_sales.pivot(index='Financial Year', columns='Branch', values='Total')
                yoy_growth_pct = yoy_growth.pct_change() * 100
                
                if len(yoy_growth_pct) > 1:
                    st.dataframe(
                        yoy_growth_pct.style.format("{:.2f}%").highlight_max(axis=0, color='lightgreen').highlight_min(axis=0, color='lightcoral'),
                        use_container_width=True
                    )
            
            # Branch comparison
            st.subheader("Branch Performance Comparison")
            branch_totals = filtered_historical_df.groupby('Branch')['Total'].sum().reset_index()
            fig_branch_pie = px.pie(
                branch_totals,
                values='Total',
                names='Branch',
                title='Sales Distribution by Branch',
                hole=0.4,
                hover_data={'Total': ':,.2f'}
            )
            fig_branch_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_branch_pie, use_container_width=True)
        
        with tab2:
            st.subheader("Quarter Analysis")
            
            # Add Quarter column to dataframe using configurable quarter definitions
            def get_quarter(week, quarters_config):
                for quarter_name, (start, end) in quarters_config.items():
                    if start <= week <= end:
                        return quarter_name
                return 'Q4'  # Default fallback
            
            quarter_df = filtered_historical_df.copy()
            quarter_df['Quarter'] = quarter_df['Week'].apply(lambda w: get_quarter(w, st.session_state.config['quarters']))
            
            # Quarter summary table
            quarter_summary = quarter_df.groupby(['Financial Year', 'Quarter', 'Branch'])['Total'].sum().reset_index()
            quarter_pivot = quarter_summary.pivot_table(
                index=['Financial Year', 'Quarter'], 
                columns='Branch', 
                values='Total', 
                fill_value=0
            )
            quarter_pivot['Total'] = quarter_pivot.sum(axis=1)
            
            currency_format = f"{st.session_state.config['currency_symbol']}{{:,.2f}}"
            st.dataframe(
                quarter_pivot.style.format(currency_format),
                use_container_width=True
            )
            
            # Quarter comparison chart
            fig_quarter = px.bar(
                quarter_summary,
                x='Quarter',
                y='Total',
                color='Branch',
                facet_col='Financial Year',
                barmode='group',
                title='Quarterly Sales Comparison Across Years',
                text_auto='.2s'
            )
            fig_quarter.update_layout(height=400)
            st.plotly_chart(fig_quarter, use_container_width=True)
        
        with tab3:
            st.subheader("Week-wise Analysis")
            
    if not filtered_historical_df.empty:
        # --- 2. Enhanced Quarter/Week Range Analysis ---
        st.subheader("Quarter/Week Range Analysis")

        # Dynamically generate quarter options from configuration
        quarters_config = st.session_state.config['quarters']
        quarter_options = ["All Quarters"]
        quarter_mapping = {}
        for q_name, (start, end) in quarters_config.items():
            display_name = f"{q_name} (Weeks {start}-{end})"
            quarter_options.append(display_name)
            quarter_mapping[display_name] = (start, end)
        
        selected_quarters_display = st.multiselect("Select Quarter(s)", quarter_options, default=["All Quarters"])

        # Option to select specific week ranges
        all_weeks = sorted(filtered_historical_df['Week'].unique().tolist())
        selected_weeks = st.multiselect("Or, Select Specific Week(s)", all_weeks)

        # Filter data based on quarter or week range selection
        quarter_week_filtered_df = filtered_historical_df.copy()

        # Apply quarter filter if selected
        if "All Quarters" not in selected_quarters_display:
            quarter_weeks = []
            for q_display in selected_quarters_display:
                start_week, end_week = quarter_mapping[q_display]
                quarter_weeks.extend(range(start_week, end_week + 1))
            quarter_week_filtered_df = quarter_week_filtered_df[quarter_week_filtered_df['Week'].isin(quarter_weeks)]

        # Apply specific week filter if selected (overrides quarter if both selected)
        if selected_weeks:
            quarter_week_filtered_df = quarter_week_filtered_df[quarter_week_filtered_df['Week'].isin(selected_weeks)]

        if not quarter_week_filtered_df.empty:
            st.write(f"**Detailed Sales for Selected Range**")
            st.dataframe(quarter_week_filtered_df[['Branch', 'Financial Year', 'Week', 'Total']].sort_values(['Branch', 'Financial Year', 'Week']), use_container_width=True)

            total_sales_for_range = quarter_week_filtered_df['Total'].sum()
            st.metric(label=f"Total Sales for Selected Range", value=format_currency(total_sales_for_range))

            # Line chart for selected week range/quarter
            st.subheader("Sales Trend for Selected Range")
            fig_quarter_week_trend = px.line(
                quarter_week_filtered_df,
                x='Week',
                y='Total',
                color='Branch',
                line_dash='Financial Year',
                markers=True,
                title='Sales Trend by Week for Selected Range',
                hover_data={'Total': ':.2f', 'Week': True, 'Financial Year': True, 'Branch': True}
            )
            fig_quarter_week_trend.update_layout(
                xaxis_title='Week Number',
                yaxis_title='Total Sales',
                hovermode='x unified'
            )
            fig_quarter_week_trend.update_xaxes(dtick=1)
            st.plotly_chart(fig_quarter_week_trend, use_container_width=True)

        else:
            st.info("No sales data available for the selected quarter(s) or week range based on current filters.")

        st.markdown("---") # Separator

        with tab4:
            st.subheader("Comparative Analysis")
            
            # Compare selected years
            available_years = sorted(filtered_historical_df['Financial Year'].unique())
            
            if len(available_years) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    compare_year_1 = st.selectbox("Select First Year", available_years, index=0, key='year1')
                with col2:
                    compare_year_2 = st.selectbox("Select Second Year", available_years, index=min(1, len(available_years)-1), key='year2')
                
                if compare_year_1 != compare_year_2:
                    year1_data = filtered_historical_df[filtered_historical_df['Financial Year'] == compare_year_1]
                    year2_data = filtered_historical_df[filtered_historical_df['Financial Year'] == compare_year_2]
                    
                    # Summary comparison
                    col1, col2, col3 = st.columns(3)
                    
                    year1_total = year1_data['Total'].sum()
                    year2_total = year2_data['Total'].sum()
                    difference = year2_total - year1_total
                    pct_change = (difference / year1_total * 100) if year1_total > 0 else 0
                    
                    with col1:
                        st.metric(f"{compare_year_1} Total", format_currency(year1_total))
                    with col2:
                        st.metric(f"{compare_year_2} Total", format_currency(year2_total))
                    with col3:
                        st.metric("Change", format_currency(difference), f"{pct_change:+.2f}%")
                    
                    # Week-by-week comparison
                    st.subheader(f"Week-by-Week Comparison: {compare_year_1} vs {compare_year_2}")
                    
                    comparison_df = pd.merge(
                        year1_data.groupby(['Week', 'Branch'])['Total'].sum().reset_index().rename(columns={'Total': f'{compare_year_1}'}),
                        year2_data.groupby(['Week', 'Branch'])['Total'].sum().reset_index().rename(columns={'Total': f'{compare_year_2}'}),
                        on=['Week', 'Branch'],
                        how='outer'
                    ).fillna(0)
                    
                    comparison_df['Difference'] = comparison_df[f'{compare_year_2}'] - comparison_df[f'{compare_year_1}']
                    comparison_df['% Change'] = comparison_df.apply(
                        lambda row: (row['Difference'] / row[f'{compare_year_1}'] * 100) if row[f'{compare_year_1}'] > 0 else 0,
                        axis=1
                    )
                    
                    # Line chart comparison
                    fig_comparison = px.line(
                        comparison_df.melt(id_vars=['Week', 'Branch'], value_vars=[f'{compare_year_1}', f'{compare_year_2}'], 
                                          var_name='Year', value_name='Total'),
                        x='Week',
                        y='Total',
                        color='Branch',
                        line_dash='Year',
                        markers=True,
                        title=f'Sales Comparison: {compare_year_1} vs {compare_year_2}',
                        hover_data={'Total': ':,.2f'}
                    )
                    fig_comparison.update_layout(
                        xaxis_title='Week Number',
                        yaxis_title='Total Sales ($)',
                        hovermode='x unified',
                        height=500
                    )
                    st.plotly_chart(fig_comparison, use_container_width=True)
                    
                    # Show detailed comparison table
                    with st.expander("View Detailed Comparison Table"):
                        currency_format = f"{st.session_state.config['currency_symbol']}{{:,.2f}}"
                        st.dataframe(
                            comparison_df.style.format({
                                f'{compare_year_1}': currency_format,
                                f'{compare_year_2}': currency_format,
                                'Difference': currency_format,
                                '% Change': '{:+.2f}%'
                            }),
                            use_container_width=True
                        )
                else:
                    st.warning("Please select two different years for comparison.")
            else:
                st.info("Need at least 2 financial years for comparative analysis.")
    else:
        # Show message when no historical data is available
        st.info("""
        📁 **No Historical Sales Data Available**
        
        Upload an Excel file in the sidebar (under 'Upload Historical Sales Data') to view:
        - Annual sales overview with key metrics
        - Quarter-by-quarter analysis
        - Week-by-week sales trends
        - Year-over-year comparative analysis
        
        Your Excel file should contain sheets named 'WA', 'QLD', and 'NSW' with historical sales data.
        """)

    # ---- Monthly Sales ---- #
    # ---- Monthly Sales ---- #
    st.header("▸ Monthly Branch Sales")
    monthly_sales = filtered_df.groupby(['Month', 'Branch'])['Total'].sum().reset_index()

    fig_month = px.line(
        monthly_sales, x="Month", y="Total", color="Branch", markers=True,
        title="Monthly Sales by Branch", hover_data={"Total": True}
    )
    fig_month.update_traces(mode='lines+markers', hovertemplate='%{x}<br>Sales: %{y:.2f}')
    fig_month.update_layout(xaxis_title="Month", yaxis_title="Sales")
    st.plotly_chart(fig_month, use_container_width=True)


    # ---- Dropping & Rising Customers ---- #
    st.header(" Customer Trends (Drop vs Rise)")

    customer_sales = df[df['Branch'].isin(branch)].groupby(['Customer', 'Year'])['Total'].sum().reset_index()
    sales_pivot = customer_sales.pivot(index='Customer', columns='Year', values='Total').fillna(0)

    years = sorted(sales_pivot.columns)
    year_window = st.session_state.config['year_comparison_window']
    
    if len(years) >= year_window:
        # Compare the most recent year with the average of previous years based on window
        recent_years = years[-year_window:]
        current_year = recent_years[-1]
        previous_year = recent_years[-2]
        
        sales_pivot['Drop?'] = sales_pivot[current_year] < sales_pivot[previous_year]
        sales_pivot['Rise?'] = sales_pivot[current_year] > sales_pivot[previous_year]

        dropping_customers = sales_pivot[sales_pivot['Drop?']].reset_index()
        rising_customers = sales_pivot[sales_pivot['Rise?']].reset_index()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"⬇ Dropping Customers ({previous_year} → {current_year})")
            display_cols = ['Customer'] + [previous_year, current_year]
            st.dataframe(dropping_customers[display_cols])

        with col2:
            st.subheader(f"⬆ Rising Customers ({previous_year} → {current_year})")
            st.dataframe(rising_customers[display_cols])
    else:
        st.info(f"Not enough years for drop/rise analysis. Need at least {year_window} years of data.")

    # ---- Customer Purchase View ---- #
    st.header("▸ Customer-wise Purchase Detail")

    # Multiselect Customer
    cust_df = filtered_df.groupby(['Customer', 'Year'])['Total'].sum().reset_index()
    if not cust_df.empty:
        selected_customers = st.multiselect(
            "Select Customer(s) to Analyze",
            options=cust_df['Customer'].unique(),
            default=cust_df['Customer'].unique()[:1]
        )

        # Date Range Filter
        cust_date_range = st.date_input(
            "Select Date Range for Purchase Analysis",
            [filtered_df['Issue Date'].min(), filtered_df['Issue Date'].max()]
        )
        cust_start_date = pd.to_datetime(cust_date_range[0])
        cust_end_date = pd.to_datetime(cust_date_range[1])

        # Filter based on selection
        cust_purchase = filtered_df[
            (filtered_df['Customer'].isin(selected_customers)) &
            (filtered_df['Issue Date'].between(cust_start_date, cust_end_date))
        ]

        # Show drop warnings
        if 'dropping_customers' in locals() and 'previous_year' in locals() and 'current_year' in locals():
            for cust in selected_customers:
                if cust in dropping_customers['Customer'].values:
                    st.warning(f" {cust} is a **dropping customer** (sales declined from {previous_year} to {current_year}).")

        # Show raw purchase records
        # Show raw purchase records
        st.subheader("Filtered Purchase Records")
        st.dataframe(
            cust_purchase[['Customer', 'Issue Date', 'Branch', 'Invoice ID', 'Total']],
            use_container_width=True
        )

        # Calculate and display the total sum of purchases
        total_filtered_purchase = cust_purchase['Total'].sum()
        st.metric(label="Total Purchase for Filtered Records", value=format_currency(total_filtered_purchase))

        # Year-wise Total Purchases (Bar Chart)
        st.subheader("▸ Year-wise Purchase Totals")
        cust_yearly = cust_purchase.groupby(['Customer', 'Year'])['Total'].sum().reset_index()

        if not cust_yearly.empty:
            fig_year = px.bar(
                cust_yearly, x="Year", y="Total", color="Customer", barmode='group',
                title="Yearly Purchase Summary"
            )
            fig_year.update_traces(hovertemplate='Year: %{x}<br>Total: %{y:.2f}')
            fig_year.update_layout(xaxis_title="Year", yaxis_title="Total Purchase")
            st.plotly_chart(fig_year, use_container_width=True)
        else:
            st.info("No yearly data available for selected customers/date range.")

        # Monthly Trend (Line Chart)
        st.subheader("▸ Monthly Purchase Trend")
        cust_purchase['Month'] = cust_purchase['Issue Date'].dt.to_period('M').astype(str)
        cust_monthly = cust_purchase.groupby(['Customer', 'Month'])['Total'].sum().reset_index()

        if not cust_monthly.empty:
            fig_monthly = px.line(
                cust_monthly, x="Month", y="Total", color="Customer", markers=True,
                title="Monthly Purchase Trend"
            )
            fig_monthly.update_traces(hovertemplate='Month: %{x}<br>Total: %{y:.2f}')
            fig_monthly.update_layout(xaxis_title="Month", yaxis_title="Total Purchase")
            st.plotly_chart(fig_monthly, use_container_width=True)
        else:
            st.info("No monthly data available for selected customers/date range.")

    else:
        st.info("No customers found for the selected filters.")

else:
    # Show welcome message when no files are uploaded
    st.title("▸ Invoice & Customer Analysis Dashboard")
    
    branch_names = ", ".join(st.session_state.config['branches'])
    num_branches = len(st.session_state.config['branches'])
    
    st.info(f"↑ Please upload CSV files for all {num_branches} branches ({branch_names}) using the sidebar to begin analysis.")
    
    st.markdown(f"""
    ### ▸ Instructions:
    1. Use the sidebar on the left to upload your CSV files
    2. Upload one file for each branch: {branch_names}
    3. Ensure your CSV files have the same structure with the expected columns
    4. If your data structure is different, use the **⚙️ Configuration** → **🔧 Advanced Settings** in the sidebar to customize:
       - Branch names
       - Date format (DD/MM/YYYY or MM/DD/YYYY)
       - Currency symbol
       - Quarter definitions
       - Excel sheet names for historical data
    5. Once all files are uploaded, the dashboard will automatically display your analysis
    
    ### ▸ Available Visualizations:
    - Annual and Monthly Sales Analysis
    - Customer Trend Analysis (Rising vs Dropping Customers)
    - Customer-wise Purchase Details
    - Interactive Filters for Custom Analysis
    
    ### 🔧 Flexible Configuration:
    This dashboard supports customizable data structures. If you get any errors, check the Advanced Settings.
    """)
