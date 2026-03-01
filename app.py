import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")

# Load Custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("assets/style.css")
# Inject FontAwesome 6 Free
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>', unsafe_allow_html=True)

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

# ========================================
# TOP-LEVEL CACHED HELPER FUNCTIONS
# (defined here so @st.cache_data persists across every rerun)
# ========================================

@st.cache_data(ttl=3600, show_spinner=False)
def filter_main_data(df, branches, years, start, end, customers):
    mask = (
        df['Branch'].isin(branches) &
        df['Year'].between(years[0], years[1]) &
        df['Issue Date'].between(start, end)
    )
    filtered = df[mask]
    if customers:
        filtered = filtered[filtered['Customer'].isin(customers)]
    return filtered

@st.cache_data(ttl=3600, show_spinner=False)
def filter_historical_data(hist_df, branches, financial_yrs):
    if hist_df.empty: return pd.DataFrame()
    return hist_df[
        hist_df['Branch'].isin(branches) &
        hist_df['Financial Year'].isin(financial_yrs)
    ].copy()

def get_quarter(week, quarters_config):
    """Map a week number to its quarter label using the current config."""
    for quarter_name, (start, end) in quarters_config.items():
        if start <= week <= end:
            return quarter_name
    return list(quarters_config.keys())[-1]  # default to last quarter

# ========================================
# UI COMPONENTS
# ========================================
def apply_chart_theme(fig, title=None, height=None):
    """Applies a professional consistent theme to Plotly charts"""
    fig.update_layout(
        template="plotly_white",
        font={'family': "Inter, sans-serif", 'color': "#2D3748"},
        title={'text': title, 'font': {'size': 18, 'color': '#1E293B'}, 'x': 0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20),
        height=height,
        # 'closest' prevents the huge stacked tooltip panel that overflows on multi-series charts
        hovermode='closest',
        hoverlabel=dict(
            bgcolor='white',
            bordercolor='#E2E8F0',
            font_size=13,
            font_family='Inter, sans-serif'
        ),
        xaxis=dict(showgrid=False, linecolor='#E2E8F0', tickfont={'color': '#64748B'}),
        yaxis=dict(showgrid=True, gridcolor='#F1F5F9', tickfont={'color': '#64748B'}),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def metric_card(title, value, description=None, icon=None):
    """
    Renders a professional metric card with optional FontAwesome icon.
    """
    desc_html = f'<div style="font-size: 0.8rem; color: #64748B; margin-top: 6px;">{description}</div>' if description else ""
    icon_html = (
        f'<div style="width: 38px; height: 38px; border-radius: 9px; '
        f'background: linear-gradient(135deg, #EFF6FF, #DBEAFE); '
        f'display: flex; align-items: center; justify-content: center; flex-shrink: 0;">'
        f'<i class="{icon}" style="color: #3B82F6; font-size: 1rem;"></i></div>'
    ) if icon else ""

    st.markdown(f"""
    <div class="css-card" style="padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between; height: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
            <span style="font-size: 0.875rem; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">{title}</span>
            {icon_html}
        </div>
        <div style="font-size: 1.75rem; font-weight: 700; color: #1E293B;">
            {value}
        </div>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)

# Helper function for currency formatting
def format_currency(value, decimals=2):
    """Format a number as currency using the configured currency symbol"""
    currency_symbol = st.session_state.config['currency_symbol']
    return f"{currency_symbol}{value:,.{decimals}f}"

# ========================================
# UI HELPERS
# ========================================

def apply_table_style(df, format_cols=None, date_cols=None):
    """
    Applies professional styling to a dataframe.
    """
    if df.empty:
        return df
    
    # Base Styler
    styler = df.style
    
    # 1. Hide Index if simpler
    styler.hide(axis='index')
    
    # 2. Format Currency Columns
    if format_cols is not None and len(format_cols) > 0:
        currency_fmt = f"{st.session_state.config.get('currency_symbol', '$')}{{:,.2f}}"
        styler.format({col: currency_fmt for col in format_cols if col in df.columns})
        
    # 3. Format Date Columns
    if date_cols is not None and len(date_cols) > 0:
        for col in date_cols:
            if col in df.columns:
                 styler.format({col: lambda x: x.strftime('%d-%b-%Y') if pd.notnull(x) else ""})

    # 4. Apply background gradient to numeric columns if relevant (optional)
    # styler.background_gradient(cmap="Blues", subset=format_cols)
    
    # 5. Set Table Properties (CSS)
    styler.set_table_styles([
        {'selector': 'thead th', 'props': [
            ('background-color', '#F8FAFC'),
            ('color', '#475569'),
            ('font-weight', '600'),
            ('border-bottom', '2px solid #E2E8F0'),
            ('text-align', 'left')
        ]},
        {'selector': 'tbody td', 'props': [
            ('padding', '12px 16px'),
            ('border-bottom', '1px solid #F1F5F9'),
            ('color', '#334155')
        ]},
        {'selector': 'tbody tr:hover', 'props': [
            ('background-color', '#F1F5F9')
        ]},
    ])
    
    return styler

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
                            st.warning(f"{branch_name}: Detected {actual_cols} columns (expected {len(columns)}). Using auto-detected structure.")
            
            df['Branch'] = branch_name
            dfs.append(df)
        except Exception as e:
            st.error(f"Error loading {branch_name} file: {str(e)}")
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
        st.warning("Customer column not found. Using default value.")
    
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
        st.error("Issue Date column not found. Cannot proceed without date information.")
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
        st.error("Total/Amount column not found. Cannot proceed without sales data.")
        return None
    
    # Ensure Branch column exists and is properly formatted
    df['Branch'] = df['Branch'].astype(str).str.strip()
    
    # Create derived columns for analysis
    df['Year'] = df['Issue Date'].dt.year
    df['Month'] = df['Issue Date'].dt.to_period('M').astype(str)

    return df.dropna(subset=['Issue Date', 'Total', 'Branch'])


def load_combined_data(combined_file, date_format='dayfirst', column_mappings=None):
    """Load data from a single combined CSV file that already has a Branch column."""
    if column_mappings is None:
        column_mappings = {}

    try:
        combined_file.seek(0)
        # utf-8-sig automatically strips the BOM (\ufeff) that Excel-exported CSVs often add
        df = pd.read_csv(combined_file, encoding='utf-8-sig')
        # Strip whitespace and BOM characters from column names
        df.columns = df.columns.str.strip().str.lstrip('\ufeff')
    except UnicodeDecodeError:
        try:
            combined_file.seek(0)
            df = pd.read_csv(combined_file, encoding='latin-1')
            df.columns = df.columns.str.strip().str.lstrip('\ufeff')
        except Exception as e:
            st.error(f"Error reading combined CSV: {str(e)}")
            return None
    except Exception as e:
        st.error(f"Error reading combined CSV: {str(e)}")
        return None

    # --- Branch detection ---
    # Priority 1: explicit Branch / Branch Region columns (if they actually have data)
    col_map_lower = {c.lower().strip(): c for c in df.columns}
    branch_col = None
    candidates = [
        column_mappings.get('Branch', 'Branch'),
        'Branch', 'branch', 'BRANCH',
        'Branch Region', 'branch region', 'BRANCH REGION',
    ]
    for candidate in candidates:
        actual = col_map_lower.get(candidate.lower().strip())
        if not actual:
            continue
        non_null = df[actual].dropna()
        real_values = non_null.astype(str).str.strip()
        real_values = real_values[~real_values.str.lower().isin(['nan', 'none', ''])]
        if len(real_values) > 0:
            branch_col = actual
            break

    if branch_col is not None:
        df['Branch'] = df[branch_col].astype(str).str.strip()
        df['Branch'] = df['Branch'].replace({'nan': None, 'None': None, '': None})
    else:
        # Priority 2: extract branch from Entity Name column
        # e.g. "Connect Resources (NSW) Pty Ltd" → "NSW"
        # e.g. "Connect Resources (QLD) Pty Ltd" → "QLD"
        # e.g. "Connect Resources Pty Ltd" (no state in parentheses) → "WA"
        entity_col = col_map_lower.get('entity name')
        if entity_col:
            known_branches = st.session_state.config.get('branches', ['NSW', 'QLD', 'WA'])
            import re

            def extract_branch(entity):
                if pd.isna(entity):
                    return None
                entity = str(entity).strip()
                
                # Priority 1: Check for state in parentheses like "(NSW)" or "(QLD)"
                m = re.search(r'\(([A-Z]{2,3})\)', entity, re.IGNORECASE)
                if m:
                    state = m.group(1).upper()
                    if state in known_branches:
                        return state
                
                # Priority 2: If no parentheses found, check if it's the base entity name
                # "Connect Resources Pty Ltd" (without state) should be WA
                base_patterns = [
                    r'^Connect Resources Pty Ltd$',
                    r'^Connect Resources$'
                ]
                for pattern in base_patterns:
                    if re.match(pattern, entity, re.IGNORECASE):
                        return 'WA'  # Default branch for base entity name
                
                # Priority 3: Check if any branch name appears directly in the text
                for b in known_branches:
                    if b.upper() in entity.upper():
                        return b.upper()
                
                return None

            df['Branch'] = df[entity_col].apply(extract_branch)
            
            # Show info about extraction
            if df['Branch'].isna().any():
                st.sidebar.warning(
                    f"Some rows could not be assigned a branch from Entity Name. "
                    f"They will be excluded."
                )
            else:
                st.sidebar.info("Branch extracted from 'Entity Name' column.")
        else:
            st.error(
                "Could not determine branch. CSV needs a 'Branch', 'Branch Region', or "
                "'Entity Name' column that identifies which branch each row belongs to. "
                f"Columns found: {', '.join(df.columns.tolist())}"
            )
            return None

    if df['Branch'].isna().all():
        st.error("Branch values could not be determined from the CSV. All rows have an empty branch.")
        return None

    # Show diagnostic info in sidebar
    with st.sidebar.expander("🔍 CSV Diagnostics", expanded=False):
        branch_src = branch_col if branch_col else 'Entity Name (auto-extracted)'
        st.write(f"**Branch source:** `{branch_src}`")
        st.write("**Unique Branches:**", sorted(df['Branch'].dropna().unique().tolist()))
        st.write("**Total rows:**", len(df))
        st.write("**Rows with branch:**", int(df['Branch'].notna().sum()))


    # --- Customer column ---
    customer_col = column_mappings.get('Customer', 'Customer')
    if customer_col in df.columns:
        df['Customer'] = df[customer_col].astype(str).str.strip()
    else:
        df['Customer'] = 'Unknown Customer'

    # --- Issue Date column ---
    date_col = column_mappings.get('Issue Date', 'Issue Date')
    if date_col in df.columns:
        df['Issue Date'] = pd.to_datetime(
            df[date_col], dayfirst=(date_format == 'dayfirst'), errors='coerce'
        )
    else:
        st.error("Issue Date column not found in combined CSV.")
        return None

    # --- Total column ---
    total_col = column_mappings.get('Total', 'Total')
    if total_col in df.columns:
        df['Total'] = pd.to_numeric(
            df[total_col].astype(str).str.replace(',', ''), errors='coerce'
        )
    else:
        st.error("Total column not found in combined CSV.")
        return None

    # --- Derived columns ---
    df['Year'] = df['Issue Date'].dt.year
    df['Month'] = df['Issue Date'].dt.to_period('M').astype(str)

    result = df.dropna(subset=['Issue Date', 'Total', 'Branch'])

    # Friendly summary
    branches_found = sorted(result['Branch'].unique().tolist())
    st.sidebar.success(f"Loaded combined file — branches detected: {', '.join(branches_found)}")
    return result


# ========================================
# SIDEBAR HEADER
# ========================================
st.sidebar.markdown("""
<div style="margin-bottom: 1.25rem; padding: 1rem 1rem 0.75rem; background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border-radius: 10px; border: 1px solid #BFDBFE;">
    <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.25rem;">
        <i class="fa-solid fa-chart-line" style="color: #3B82F6; font-size: 1.1rem;"></i>
        <span style="font-size: 1.05rem; font-weight: 700; color: #1E293B;">Sales Analytics</span>
    </div>
    <p style="font-size: 0.72rem; color: #64748B; margin: 0;">Professional Dashboard v1.0</p>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown('<p style="font-size: 0.8rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.07em; margin: 0.5rem 0 0.25rem;"><i class="fa-solid fa-gear" style="margin-right: 6px; color: #3B82F6;"></i>Settings</p>', unsafe_allow_html=True)

with st.sidebar.expander("Configuration", expanded=False):
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
    
    _q = st.session_state.config['quarters']
    col1, col2 = st.columns(2)
    with col1:
        q1_start = st.number_input("Q1 Start", min_value=1, value=_q['Q1'][0], key='q1s')
        q1_end = st.number_input("Q1 End", min_value=1, value=_q['Q1'][1], key='q1e')
        q2_start = st.number_input("Q2 Start", min_value=1, value=_q['Q2'][0], key='q2s')
        q2_end = st.number_input("Q2 End", min_value=1, value=_q['Q2'][1], key='q2e')
    with col2:
        q3_start = st.number_input("Q3 Start", min_value=1, value=_q['Q3'][0], key='q3s')
        q3_end = st.number_input("Q3 End", min_value=1, value=_q['Q3'][1], key='q3e')
        q4_start = st.number_input("Q4 Start", min_value=1, value=_q['Q4'][0], key='q4s')
        q4_end = st.number_input("Q4 End", min_value=1, value=_q['Q4'][1], key='q4e')
    
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
    if st.button("Apply Configuration"):
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
        st.success("Configuration updated!")
        st.rerun()

st.sidebar.markdown("---")

# ========================================
# SIDEBAR - FILE UPLOAD
# ========================================
st.sidebar.markdown("---")
st.sidebar.markdown("### Upload Sales Data")

# Upload mode toggle
upload_mode = st.sidebar.radio(
    "Upload mode",
    ["Separate CSVs (one per branch)", "Combined CSV (all branches in one file)"],
    key="upload_mode",
    horizontal=False
)

uploaded_combined_file = None
uploaded_branch_files = []

if upload_mode == "Separate CSVs (one per branch)":
    for branch in st.session_state.config['branches']:
        uploaded_file = st.sidebar.file_uploader(
            f"{branch} Branch CSV",
            type=['csv'],
            key=f'branch_{branch.lower().replace(" ", "_")}'
        )
        uploaded_branch_files.append(uploaded_file)
else:
    st.sidebar.markdown(
        '<p style="font-size:0.8rem;color:#475569;margin-bottom:0.25rem;">'  
        '<i class="fa-solid fa-file-csv" style="color:#3B82F6;margin-right:6px;"></i>'
        'Upload Combined CSV</p>',
        unsafe_allow_html=True
    )
    uploaded_combined_file = st.sidebar.file_uploader(
        "Combined CSV (must include a Branch column)",
        type=['csv'],
        key='combined_csv',
        help="Upload a single CSV file that contains rows for all branches. "
             "The file must have a 'Branch' column (e.g. NSW, QLD, WA)."
    )

st.sidebar.markdown("---")

st.sidebar.markdown('<p style="font-size: 0.8rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.07em; margin: 0.5rem 0 0.25rem;"><i class="fa-solid fa-file-excel" style="margin-right: 6px; color: #10B981;"></i>Upload Historical Data</p>', unsafe_allow_html=True)
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
_separate_all_uploaded = all(f is not None for f in uploaded_branch_files) if uploaded_branch_files else False
_combined_uploaded = uploaded_combined_file is not None

if not _separate_all_uploaded and not _combined_uploaded:
    if 'auto_detected' in st.session_state:
        del st.session_state.auto_detected
        
if uploaded_historical is None:
    if 'excel_auto_detected' in st.session_state:
        del st.session_state.excel_auto_detected

# Check if files are uploaded and trigger auto-detection
all_files_uploaded = _separate_all_uploaded or _combined_uploaded

if _separate_all_uploaded and 'auto_detected' not in st.session_state:
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
        st.sidebar.success("Auto-detected file structure!")

elif _combined_uploaded and 'auto_detected' not in st.session_state:
    st.session_state.auto_detected = True

    # Wrap single file in list so the same detection functions work unchanged
    _combined_as_list = [uploaded_combined_file]
    detected_updates = {}

    # Detect column structure and mappings
    csv_config = auto_detect_csv_structure(_combined_as_list)
    if csv_config:
        detected_updates.update(csv_config)

    # Detect date format
    date_format = auto_detect_date_format(_combined_as_list)
    if date_format:
        detected_updates['date_format'] = date_format

    # Detect currency
    currency = auto_detect_currency(_combined_as_list)
    if currency:
        detected_updates['currency_symbol'] = currency

    if detected_updates:
        st.session_state.config.update(detected_updates)
        st.sidebar.success("Auto-detected combined CSV structure!")

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
            st.sidebar.info(f"Detected {week_count} weeks in historical data")
        
        # If detected sheets look like branch names (2-4 chars, all caps), use them as branches too
        if all(len(s) <= 4 and s.isupper() for s in detected_sheets):
            old_branches = st.session_state.config['branches']
            st.session_state.config['branches'] = detected_sheets
            
            # Only show message if branches actually changed
            if old_branches != detected_sheets:
                st.sidebar.success(f"Auto-detected branches: {', '.join(detected_sheets)}")
                st.sidebar.info("Scroll up to upload CSV files for each branch")
        else:
            st.sidebar.info(f"Detected Excel sheets: {', '.join(detected_sheets)}")

# Show auto-detected configuration in sidebar
if all_files_uploaded or uploaded_historical is not None:
    with st.sidebar.expander("Auto-Detected Configuration", expanded=False):
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
                        st.markdown(f"`{required_field}` ← `{mapped_column}`")
                if len(mappings) < 3:
                    st.warning("Some required columns not mapped. Check your data structure.")
        
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
    if _combined_uploaded:
        df = load_combined_data(
            uploaded_combined_file,
            st.session_state.config['date_format'],
            st.session_state.config.get('column_mappings', {})
        )
    else:
        df = load_data(
            uploaded_branch_files,
            st.session_state.config['branches'],
            st.session_state.config['csv_columns'],
            st.session_state.config['date_format'],
            st.session_state.config['csv_has_header'],
            st.session_state.config.get('column_mappings', {})
        )
else:
    if upload_mode == "Separate CSVs (one per branch)":
        required_count = len(st.session_state.config['branches'])
        st.sidebar.info(f"Please upload all {required_count} branch CSV files to proceed")
    else:
        st.sidebar.info("Please upload the combined CSV file to proceed")
    df = None

def load_historical_sales_data(excel_file=None, sheet_names=None, excel_header_row=0, excel_data_start_row=2):
    """Loads and preprocesses the historical weekly sales data from Excel sheets,
    handling the two-row header structure and selecting relevant columns."""
    import io
    if excel_file is None:
        excel_file_path = 'HISTORICAL_REPORT.xlsx'
        try:
            open(excel_file_path)
        except FileNotFoundError:
            st.error(f"Error: Excel file '{excel_file_path}' not found. Please ensure it's in the same directory as the script.")
            return pd.DataFrame(columns=['Week', 'Financial Year', 'Total', 'Branch'])
    else:
        # Load entire file into BytesIO once — avoids file-pointer issues across multiple sheet reads
        excel_file.seek(0)
        excel_file_path = io.BytesIO(excel_file.read())

    if sheet_names is None:
        sheet_names = ['WA', 'QLD', 'NSW']

    # Only process sheets that look like branch names (≤4 uppercase chars, e.g. WA, NSW, QLD).
    # This automatically skips comparison/summary sheets like QLD-V-WA, NSW-V-WA, etc.
    branch_sheets = [s for s in sheet_names if len(s) <= 4 and s.replace(' ', '').isupper()]
    if not branch_sheets:
        branch_sheets = sheet_names

    all_historical_df = []

    try:
        # Open the workbook ONCE — pd.ExcelFile keeps the file handle open so every
        # sheet.parse() call works regardless of BytesIO position.
        xls = pd.ExcelFile(excel_file_path)
    except Exception as e:
        st.error(f"Could not open Excel file: {e}")
        return pd.DataFrame(columns=['Week', 'Financial Year', 'Total', 'Branch'])

    for sheet_name in branch_sheets:
        if sheet_name not in xls.sheet_names:
            continue
        try:
            df_raw = xls.parse(sheet_name, header=None)

            header_row_0 = df_raw.iloc[excel_header_row]

            sales_year_indices = [i for i, val in enumerate(header_row_0) if isinstance(val, str) and '/' in val]
            if not sales_year_indices:
                continue

            new_column_names = ['Week'] + [str(header_row_0[i]) for i in sales_year_indices]
            data_columns_to_select = [0] + sales_year_indices

            df_processed = df_raw.iloc[excel_data_start_row:, data_columns_to_select].copy()
            df_processed.columns = new_column_names

            df_processed = df_processed[df_processed['Week'].astype(str).str.contains(r'Week\s\d+', na=False)]
            if df_processed.empty:
                continue

            value_vars = [c for c in new_column_names if c != 'Week']
            df_melted = df_processed.melt(id_vars=['Week'], value_vars=value_vars,
                                          var_name='Financial Year', value_name='Total')
            df_melted['Branch'] = sheet_name
            df_melted['Week'] = df_melted['Week'].astype(str).str.replace('Week ', '').astype(int)
            df_melted['Total'] = pd.to_numeric(df_melted['Total'].astype(str).str.replace(',', ''), errors='coerce').astype(float)

            all_historical_df.append(df_melted)

        except Exception as e:
            st.warning(f"Skipped sheet '{sheet_name}': {e}")

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

    # Main Dashboard Title
    # st.markdown('<h1 style="margin-bottom: 0;">Invoice & Customer Analysis Dashboard</h1>', unsafe_allow_html=True) 
    # ^ Emojis removed from string literals if present earlier, but here it looks standard.
    
    # Check if there are other emojis in sidebar titles...
    # st.sidebar.markdown("### 📤 Upload Sales Data") -> st.sidebar.markdown("### Upload Sales Data")
    st.markdown('<p class="text-secondary" style="margin-bottom: 2rem;">Overview of sales performance across branches</p>', unsafe_allow_html=True)

    # Guard: if df failed to load (e.g. bad CSV), stop here with a clear message
    if df is None:
        st.error(
            "Could not load the sales data file. "
            "Please check the errors above and re-upload a valid CSV."
        )
        st.stop()

    # ---- Filters ---- #
    branch_options = df['Branch'].dropna().unique().tolist()
    branch = st.sidebar.multiselect("Select Branch(es)", options=branch_options, default=branch_options)


    # Historical data filters
    if not historical_df.empty:
        financial_year_options = sorted(historical_df['Financial Year'].dropna().unique().tolist())
        # Default to selecting all years initially without extra UI clutter if possible, or keep simple
        selected_financial_years = st.sidebar.multiselect(
            "Select Financial Year(s)",
            options=financial_year_options,
            default=financial_year_options # Default select all
        )
    else:
        st.sidebar.info("Upload historical data to enable year comparison")
        selected_financial_years = [] 

    with st.sidebar.expander("Data Filters", expanded=True):
        customer_options = sorted(df['Customer'].dropna().unique().tolist())
        # Performance: Limit initial options or use a search box effectively (multiselect does this well)
        customer = st.multiselect("Select Customer(s)", options=customer_options)

        year_min, year_max = int(df['Year'].min()), int(df['Year'].max())
        year_range = st.slider("Select Year Range", year_min, year_max, (year_min, year_max))

        # Date input can return a single date if not fully selected, handle carefully
        date_range_val = st.date_input("Filter by Issue Date Range", [df['Issue Date'].min(), df['Issue Date'].max()])
        
        if isinstance(date_range_val, list) and len(date_range_val) == 2:
            start_date = pd.to_datetime(date_range_val[0])
            end_date = pd.to_datetime(date_range_val[1])
        elif isinstance(date_range_val, list) and len(date_range_val) == 1:
            start_date = pd.to_datetime(date_range_val[0])
            end_date = pd.to_datetime(date_range_val[0]) # Start and end same day
        else: 
            # Fallback or single date selected without range
            start_date = pd.to_datetime(df['Issue Date'].min())
            end_date = pd.to_datetime(df['Issue Date'].max())
            
    filtered_df = filter_main_data(
        df, 
        tuple(branch), 
        tuple(year_range), 
        pd.to_datetime(start_date), 
        pd.to_datetime(end_date), 
        tuple(customer) if customer else None
    )

    filtered_historical_df = filter_historical_data(
        historical_df, 
        tuple(branch), 
        tuple(selected_financial_years)
    )



    # ---- Annual Sales ---- #
    # st.header("Annual Sales Report")

    # # Grouping data by Year and Branch
    annual_sales = filtered_df.groupby(['Year', 'Branch'])['Total'].sum().reset_index()

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

    if not filtered_historical_df.empty:
        # Create tabs for better organization
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Quarter Analysis", "Week Analysis", "Comparative Analysis", "Customer Analysis"])
        
        with tab1:
            st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-gauge-high" style="color:#3B82F6;"></i> Annual Sales Overview</h3>', unsafe_allow_html=True)
            
            total_sales = filtered_historical_df['Total'].sum()
            avg_weekly_sales = filtered_historical_df['Total'].mean()
            total_weeks = filtered_historical_df['Week'].nunique()
            total_years = filtered_historical_df['Financial Year'].nunique()

            # Custom Metric Cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                metric_card("Total Sales", format_currency(total_sales), description="All time revenue", icon="fa-solid fa-dollar-sign")
            with col2:
                metric_card("Weekly Avg", format_currency(avg_weekly_sales), description="Average sales per week", icon="fa-solid fa-chart-line")
            with col3:
                metric_card("Active Weeks", str(total_weeks), description="Total weeks of data", icon="fa-solid fa-calendar-days")
            with col4:
                metric_card("Financial Years", str(total_years), description="Years covered", icon="fa-solid fa-clock-rotate-left")
            
            st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
            
            # Financial Year Total Sales Comparison
            st.markdown("## Annual Performance")
            annual_historical_sales = filtered_historical_df.groupby(['Financial Year', 'Branch'])['Total'].sum().reset_index()
            
            if not annual_historical_sales.empty:
                # Create pivot table for display
                pivot_annual = annual_historical_sales.pivot(index='Financial Year', columns='Branch', values='Total').fillna(0)
                pivot_annual['Total'] = pivot_annual.sum(axis=1)
                
                # Format as currency and apply professional styling
                # Reset index to ensure Financial Year is visible as a column
                pivot_annual_display = pivot_annual.reset_index()
                st.dataframe(
                    apply_table_style(pivot_annual_display, format_cols=pivot_annual.columns),
                    use_container_width=True
                )
                
                # Bar chart
                fig_annual_hist = px.bar(
                    annual_historical_sales,
                    x='Financial Year',
                    y='Total',
                    color='Branch',
                    barmode='group',
                    title='Total Sales per Financial Year',
                    color_discrete_sequence=px.colors.qualitative.Prism
                )
                apply_chart_theme(fig_annual_hist, title="Total Sales per Financial Year", height=500)
                fig_annual_hist.update_traces(
                    hovertemplate='<b>%{x}</b><br>Branch: %{fullData.name}<br>Total: $%{y:,.0f}<extra></extra>'
                )
                st.plotly_chart(fig_annual_hist, use_container_width=True, key='annual_hist_overview')
                
                st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

                # Year-over-Year Growth Analysis
                st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-arrows-up-down" style="color:#3B82F6;"></i> Year-over-Year Growth Analysis</h3>', unsafe_allow_html=True)
                yoy_growth = annual_historical_sales.pivot(index='Financial Year', columns='Branch', values='Total')
                yoy_growth_pct = yoy_growth.pct_change() * 100
                
                if len(yoy_growth_pct) > 1:
                    def _style_yoy(df):
                        import math
                        def _nan_cell(v):
                            try:
                                if v is None or (isinstance(v, float) and math.isnan(v)):
                                    return 'background-color:#F8FAFC; color:#94A3B8; font-style:italic;'
                            except Exception:
                                pass
                            return ''
                        # axis=None + numpy gmap avoids the Series/DataFrame mismatch error
                        base = (
                            df.style
                            .format("{:.2f}%", na_rep="—")
                            .background_gradient(
                                cmap='RdYlGn',
                                axis=None,
                                vmin=-50,
                                vmax=50,
                                gmap=df.fillna(0).values
                            )
                        )
                        try:
                            return base.map(_nan_cell)        # pandas >= 2.1
                        except AttributeError:
                            return base.applymap(_nan_cell)   # pandas < 2.1
                    st.dataframe(_style_yoy(yoy_growth_pct), use_container_width=True)
            
            st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

            # Branch comparison
            st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-building" style="color:#3B82F6;"></i> Branch Performance Comparison</h3>', unsafe_allow_html=True)
            branch_totals = filtered_historical_df.groupby('Branch')['Total'].sum().reset_index()
            fig_branch_pie = px.pie(
                branch_totals,
                values='Total',
                names='Branch',
                title='Sales Distribution by Branch',
                hole=0.6,
                hover_data={'Total': ':,.2f'},
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            apply_chart_theme(fig_branch_pie, title="Sales Distribution by Branch")
            fig_branch_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Total: $%{value:,.2f}<br>Share: %{percent}<extra></extra>',
                insidetextorientation='auto'
            )
            st.plotly_chart(fig_branch_pie, use_container_width=True, key='branch_pie_overview')
            
            st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
            
            # --- Week Analysis in Overview ---
            st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-filter" style="color:#3B82F6;"></i> Quarter / Week Range Analysis</h3>', unsafe_allow_html=True)

            # Dynamically generate quarter options from configuration
            quarters_config = st.session_state.config['quarters']
            quarter_options = ["All Quarters"]
            quarter_mapping = {}
            for q_name, (start, end) in quarters_config.items():
                display_name = f"{q_name} (Weeks {start}-{end})"
                quarter_options.append(display_name)
                quarter_mapping[display_name] = (start, end)
            
            selected_quarters_display_overview = st.multiselect("Select Quarter(s)", quarter_options, default=["All Quarters"], key='quarters_overview')

            # Option to select specific week ranges
            all_weeks = sorted(filtered_historical_df['Week'].unique().tolist())
            selected_weeks_overview = st.multiselect("Or, Select Specific Week(s)", all_weeks, key='weeks_overview')

            # Filter data based on quarter or week range selection
            quarter_week_filtered_df_overview = filtered_historical_df.copy()

            # Apply quarter filter if selected
            if "All Quarters" not in selected_quarters_display_overview:
                quarter_weeks = []
                for q_display in selected_quarters_display_overview:
                    start_week, end_week = quarter_mapping[q_display]
                    quarter_weeks.extend(range(start_week, end_week + 1))
                quarter_week_filtered_df_overview = quarter_week_filtered_df_overview[quarter_week_filtered_df_overview['Week'].isin(quarter_weeks)]

            # Apply specific week filter if selected (overrides quarter if both selected)
            if selected_weeks_overview:
                quarter_week_filtered_df_overview = quarter_week_filtered_df_overview[quarter_week_filtered_df_overview['Week'].isin(selected_weeks_overview)]

            if not quarter_week_filtered_df_overview.empty:
                st.write(f"**Detailed Sales for Selected Range**")
                display_quarter_week_df = quarter_week_filtered_df_overview[['Branch', 'Financial Year', 'Week', 'Total']].sort_values(['Branch', 'Financial Year', 'Week'])
                
                # Optimized rendering for large dataframe
                st.dataframe(
                    display_quarter_week_df,
                    column_config={
                        "Total": st.column_config.NumberColumn(
                            "Total Sales",
                            format=f"{st.session_state.config['currency_symbol']}%.2f"
                        ),
                        "Week": st.column_config.NumberColumn("Week #", format="%d")
                    },
                    use_container_width=True,
                    height=400
                )

                total_sales_for_range = quarter_week_filtered_df_overview['Total'].sum()
                st.metric(label=f"Total Sales for Selected Range", value=format_currency(total_sales_for_range))

                # Line chart for selected week range/quarter
                st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-chart-area" style="color:#3B82F6;"></i> Sales Trend for Selected Range</h3>', unsafe_allow_html=True)
                fig_quarter_week_trend_overview = px.line(
                    quarter_week_filtered_df_overview,
                    x='Week',
                    y='Total',
                    color='Branch',
                    line_dash='Financial Year',
                    markers=True,
                    title='Sales Trend by Week for Selected Range',
                    color_discrete_sequence=px.colors.qualitative.Prism
                )
                apply_chart_theme(fig_quarter_week_trend_overview, title="Sales Trend by Week", height=450)
                fig_quarter_week_trend_overview.update_layout(
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.01,
                        font=dict(size=10),
                        title=dict(text="Branch, Financial Year", font=dict(size=11))
                    ),
                    margin=dict(r=220)
                )
                fig_quarter_week_trend_overview.update_traces(
                    hovertemplate='<b>Week %{x}</b><br>%{fullData.name}<br>$%{y:,.0f}<extra></extra>'
                )
                fig_quarter_week_trend_overview.update_xaxes(dtick=1)
                st.plotly_chart(fig_quarter_week_trend_overview, use_container_width=True, key='week_trend_overview')

            else:
                st.info("No sales data available for the selected quarter(s) or week range based on current filters.")
            
            st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
            
            # --- Monthly Sales in Overview ---
            st.markdown('<h2><i class="fa-solid fa-chart-area" style="color:#3B82F6;margin-right:0.4rem;"></i>Monthly Branch Sales</h2>', unsafe_allow_html=True)
            monthly_sales = filtered_df.groupby(['Month', 'Branch'])['Total'].sum().reset_index()

            fig_month = px.line(
                monthly_sales, x="Month", y="Total", color="Branch", markers=True,
                title="Monthly Sales by Branch",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_month.update_traces(
                mode='lines+markers',
                hovertemplate='<b>%{x}</b><br>Branch: %{fullData.name}<br>Sales: $%{y:,.0f}<extra></extra>'
            )
            apply_chart_theme(fig_month, title="Monthly Sales Trend", height=450)
            st.plotly_chart(fig_month, use_container_width=True, key='monthly_sales_overview')
            
            st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
            
            # --- Customer Analysis in Overview ---
            st.markdown('<h2><i class="fa-solid fa-users" style="color:#3B82F6;margin-right:0.4rem;"></i>Customer Trends <span style="font-size:0.9rem;color:#64748B;font-weight:500;">(Drop vs Rise)</span></h2>', unsafe_allow_html=True)

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
                    st.markdown(f'<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-arrow-trend-down" style="color:#EF4444;"></i> Dropping Customers ({previous_year} → {current_year})</h3>', unsafe_allow_html=True)
                    display_cols = ['Customer'] + [previous_year, current_year]
                    st.dataframe(
                        apply_table_style(dropping_customers[display_cols], format_cols=display_cols[1:]),
                        use_container_width=True
                    )

                with col2:
                    st.markdown(f'<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-arrow-trend-up" style="color:#10B981;"></i> Rising Customers ({previous_year} → {current_year})</h3>', unsafe_allow_html=True)
                    st.dataframe(
                        apply_table_style(rising_customers[display_cols], format_cols=display_cols[1:]),
                        use_container_width=True
                    )
            else:
                st.info(f"Not enough years for drop/rise analysis. Need at least {year_window} years of data.")

            # ---- Customer Purchase View ---- #
            st.markdown('<h2><i class="fa-solid fa-receipt" style="color:#3B82F6;margin-right:0.4rem;"></i>Customer-wise Purchase Detail</h2>', unsafe_allow_html=True)

            # Multiselect Customer - Check for Customer Name column
            # Find customer name column if it exists
            customer_name_col = None
            for col in filtered_df.columns:
                if 'customer' in col.lower() and 'name' in col.lower():
                    customer_name_col = col
                    break
            
            if customer_name_col and customer_name_col in filtered_df.columns:
                # Create a mapping between Customer ID and Customer Name
                customer_mapping = filtered_df[['Customer', customer_name_col]].drop_duplicates()
                customer_mapping = customer_mapping[customer_mapping[customer_name_col].notna()]
                
                # Create display options (Customer Name)
                display_options = sorted(customer_mapping[customer_name_col].unique())
                
                selected_customer_names = st.multiselect(
                    "Select Customer(s) to Analyze",
                    options=display_options,
                    default=display_options[:1] if len(display_options) > 0 else [],
                    key='customer_overview'
                )
                
                # Map selected names back to Customer IDs
                selected_customers_overview = customer_mapping[
                    customer_mapping[customer_name_col].isin(selected_customer_names)
                ]['Customer'].tolist()
            else:
                # Fallback to Customer ID if no Customer Name column exists
                cust_df = filtered_df.groupby(['Customer', 'Year'])['Total'].sum().reset_index()
                selected_customers_overview = st.multiselect(
                    "Select Customer(s) to Analyze",
                    options=sorted(cust_df['Customer'].unique()),
                    default=cust_df['Customer'].unique()[:1],
                    key='customer_overview'
                )
            
            if selected_customers_overview and len(selected_customers_overview) > 0:

                # Date Range Filter
                cust_date_range_overview = st.date_input(
                    "Select Date Range for Purchase Analysis",
                    [filtered_df['Issue Date'].min(), filtered_df['Issue Date'].max()],
                    key='date_range_overview'
                )
                cust_start_date = pd.to_datetime(cust_date_range_overview[0])
                cust_end_date = pd.to_datetime(cust_date_range_overview[1])

                # Filter based on selection
                cust_purchase = filtered_df[
                    (filtered_df['Customer'].isin(selected_customers_overview)) &
                    (filtered_df['Issue Date'].between(cust_start_date, cust_end_date))
                ]

                # Show drop warnings
                if 'dropping_customers' in locals() and 'previous_year' in locals() and 'current_year' in locals():
                    for cust in selected_customers_overview:
                        if cust in dropping_customers['Customer'].values:
                            # Optimized warning
                            st.warning(f"{cust} is a dropping customer (sales declined from {previous_year} to {current_year}).")

                # Show raw purchase records
                st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-table-list" style="color:#3B82F6;"></i> Filtered Purchase Records</h3>', unsafe_allow_html=True)
                display_cust_purchase = cust_purchase[['Customer', 'Issue Date', 'Branch', 'Invoice ID', 'Total']]
                
                # Optimized rendering: Using native column configuration for performance
                st.dataframe(
                    display_cust_purchase,
                    column_config={
                        "Issue Date": st.column_config.DateColumn(
                            "Date",
                            format="DD/MM/YYYY" if st.session_state.config['date_format'] == 'dayfirst' else "MM/DD/YYYY"
                        ),
                        "Total": st.column_config.NumberColumn(
                            "Total Purchase",
                            format=f"{st.session_state.config['currency_symbol']}%.2f"
                        ),
                        "Customer": "Customer Name",
                        "Branch": "Branch",
                        "Invoice ID": "Invoice"
                    },
                    use_container_width=True,
                    height=500,
                    hide_index=True
                )

                # Calculate and display the total sum of purchases
                total_filtered_purchase = cust_purchase['Total'].sum()
                st.metric(label="Total Purchase for Filtered Records", value=format_currency(total_filtered_purchase))

                # Year-wise Total Purchases (Bar Chart)
                st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-chart-column" style="color:#3B82F6;"></i> Year-wise Purchase Totals</h3>', unsafe_allow_html=True)
                cust_yearly = cust_purchase.groupby(['Customer', 'Year'])['Total'].sum().reset_index()

                if not cust_yearly.empty:
                    fig_year = px.bar(
                        cust_yearly, x="Year", y="Total", color="Customer", barmode='group',
                        title="Yearly Purchase Summary",
                        color_discrete_sequence=px.colors.qualitative.Prism
                    )
                    fig_year.update_traces(
                        hovertemplate='<b>%{x}</b><br>Customer: %{fullData.name}<br>Total: $%{y:,.0f}<extra></extra>'
                    )
                    apply_chart_theme(fig_year, title="Annual Purchase Summary", height=400)
                    st.plotly_chart(fig_year, use_container_width=True, key='yearly_purchase_overview')
                else:
                    st.info("No yearly data available for selected customers/date range.")

                # Monthly Trend (Line Chart)
                st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-arrow-trend-up" style="color:#3B82F6;"></i> Monthly Purchase Trend</h3>', unsafe_allow_html=True)
                cust_purchase['Month'] = cust_purchase['Issue Date'].dt.to_period('M').astype(str)
                cust_monthly = cust_purchase.groupby(['Customer', 'Month'])['Total'].sum().reset_index()

                if not cust_monthly.empty:
                    fig_monthly_cust = px.line(
                        cust_monthly, x="Month", y="Total", color="Customer", markers=True,
                        title="Monthly Purchase Trend",
                        color_discrete_sequence=px.colors.qualitative.Prism
                    )
                    fig_monthly_cust.update_traces(
                        mode='lines+markers',
                        hovertemplate='<b>%{x}</b><br>Customer: %{fullData.name}<br>Total: $%{y:,.0f}<extra></extra>'
                    )
                    apply_chart_theme(fig_monthly_cust, title="Monthly Purchase History", height=450)
                    st.plotly_chart(fig_monthly_cust, use_container_width=True, key='monthly_purchase_overview')
                else:
                    st.info("No monthly data available for selected customers/date range.")

            else:
                st.info("No customers found for the selected filters.")
        
        with tab2:
            st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-calendar-days" style="color:#3B82F6;"></i> Quarter Analysis</h3>', unsafe_allow_html=True)
            
            # Add Quarter column to dataframe using configurable quarter definitions
            quarter_df = filtered_historical_df[['Financial Year', 'Quarter', 'Branch', 'Total', 'Week']].copy() if 'Quarter' in filtered_historical_df.columns else filtered_historical_df.copy()
            if 'Quarter' not in quarter_df.columns:
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
            # Apply table styling with reset index
            quarter_pivot_display = quarter_pivot.reset_index()
            numeric_cols = quarter_pivot.columns # Columns of pivot are branches + Total (all numeric)
            st.dataframe(
                apply_table_style(quarter_pivot_display, format_cols=numeric_cols),
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
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            apply_chart_theme(fig_quarter, title="Quarterly Sales Comparison", height=400)
            # Strip "Financial Year=" prefix from facet column labels
            fig_quarter.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            fig_quarter.update_traces(
                hovertemplate='<b>%{x}</b><br>Branch: %{fullData.name}<br>Total: $%{y:,.0f}<extra></extra>'
            )
            st.plotly_chart(fig_quarter, use_container_width=True, key='quarter_comparison')
            
            # --- Quarter Selection Analysis ---
            st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-filter" style="color:#3B82F6;"></i> Select Specific Quarter(s)</h3>', unsafe_allow_html=True)
            
            # Option to select specific quarters
            all_quarters = sorted(quarter_df['Quarter'].unique().tolist())
            selected_quarters = st.multiselect("Select Specific Quarter(s)", all_quarters)
            
            # Filter data based on quarter selection
            quarter_filtered_df = quarter_df.copy()
            
            # Apply specific quarter filter if selected
            if selected_quarters:
                quarter_filtered_df = quarter_filtered_df[quarter_filtered_df['Quarter'].isin(selected_quarters)]
            
            if not quarter_filtered_df.empty:
                st.write(f"**Detailed Sales for Selected Quarter(s)**")
                display_quarter_df = quarter_filtered_df[['Branch', 'Financial Year', 'Quarter', 'Total']].sort_values(['Branch', 'Financial Year', 'Quarter'])
                
                # Optimized rendering for large dataframe
                st.dataframe(
                    display_quarter_df,
                    column_config={
                        "Total": st.column_config.NumberColumn(
                            "Total Sales",
                            format=f"{st.session_state.config['currency_symbol']}%.2f"
                        )
                    },
                    use_container_width=True,
                    height=400
                )
                
                total_sales_for_quarters = quarter_filtered_df['Total'].sum()
                st.metric(label=f"Total Sales for Selected Quarter(s)", value=format_currency(total_sales_for_quarters))
                
                # Bar chart for selected quarters
                st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-chart-column" style="color:#3B82F6;"></i> Sales Trend for Selected Quarter(s)</h3>', unsafe_allow_html=True)
                
                quarter_agg = quarter_filtered_df.groupby(['Financial Year', 'Quarter', 'Branch'])['Total'].sum().reset_index()
                fig_selected_quarters = px.bar(
                    quarter_agg,
                    x='Quarter',
                    y='Total',
                    color='Branch',
                    facet_col='Financial Year',
                    barmode='group',
                    title='Sales by Quarter',
                    color_discrete_sequence=px.colors.qualitative.Prism
                )
                apply_chart_theme(fig_selected_quarters, title="Selected Quarter(s) Sales", height=400)
                fig_selected_quarters.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
                fig_selected_quarters.update_traces(
                    hovertemplate='<b>%{x}</b><br>Branch: %{fullData.name}<br>Total: $%{y:,.0f}<extra></extra>'
                )
                st.plotly_chart(fig_selected_quarters, use_container_width=True, key='selected_quarters_chart')
            else:
                st.warning("⚠️ No data available for the selected quarter(s).")
        
        with tab3:
            st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-calendar-week" style="color:#3B82F6;"></i> Week-wise Analysis</h3>', unsafe_allow_html=True)
            
            # --- Enhanced Week Range Analysis ---
            st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-filter" style="color:#3B82F6;"></i> Week Range Analysis</h3>', unsafe_allow_html=True)

            # Option to select specific week ranges
            all_weeks = sorted(filtered_historical_df['Week'].unique().tolist())
            selected_weeks = st.multiselect("Select Specific Week(s)", all_weeks)

            # Filter data based on week range selection
            quarter_week_filtered_df = filtered_historical_df.copy()

            # Apply specific week filter if selected
            if selected_weeks:
                quarter_week_filtered_df = quarter_week_filtered_df[quarter_week_filtered_df['Week'].isin(selected_weeks)]

            if not quarter_week_filtered_df.empty:
                st.write(f"**Detailed Sales for Selected Range**")
                display_quarter_week_df = quarter_week_filtered_df[['Branch', 'Financial Year', 'Week', 'Total']].sort_values(['Branch', 'Financial Year', 'Week'])
                
                # Optimized rendering for large dataframe
                st.dataframe(
                    display_quarter_week_df,
                    column_config={
                        "Total": st.column_config.NumberColumn(
                            "Total Sales",
                            format=f"{st.session_state.config['currency_symbol']}%.2f"
                        ),
                        "Week": st.column_config.NumberColumn("Week #", format="%d")
                    },
                    use_container_width=True,
                    height=400
                )

                total_sales_for_range = quarter_week_filtered_df['Total'].sum()
                st.metric(label=f"Total Sales for Selected Range", value=format_currency(total_sales_for_range))

                # Line chart for selected week range
                st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-chart-area" style="color:#3B82F6;"></i> Sales Trend for Selected Range</h3>', unsafe_allow_html=True)
                fig_quarter_week_trend = px.line(
                    quarter_week_filtered_df,
                    x='Week',
                    y='Total',
                    color='Branch',
                    line_dash='Financial Year',
                    markers=True,
                    title='Sales Trend by Week for Selected Range',
                    color_discrete_sequence=px.colors.qualitative.Prism
                )
                apply_chart_theme(fig_quarter_week_trend, title="Sales Trend by Week", height=450)
                # Use a compact vertical legend to avoid the large horizontal legend
                # squashing the chart area when many Branch × Financial Year combinations exist
                fig_quarter_week_trend.update_layout(
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.01,
                        font=dict(size=10),
                        title=dict(text="Branch, Financial Year", font=dict(size=11))
                    ),
                    margin=dict(r=220)  # make room for the vertical legend
                )
                fig_quarter_week_trend.update_traces(
                    hovertemplate='<b>Week %{x}</b><br>%{fullData.name}<br>$%{y:,.0f}<extra></extra>'
                )
                fig_quarter_week_trend.update_xaxes(dtick=1)
                st.plotly_chart(fig_quarter_week_trend, use_container_width=True, key='week_trend_tab3')

            else:
                st.info("No sales data available for the selected week range based on current filters.")

        with tab4:
            st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-scale-balanced" style="color:#3B82F6;"></i> Comparative Analysis</h3>', unsafe_allow_html=True)
            
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
                    st.markdown(f'<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-right-left" style="color:#3B82F6;"></i> Week-by-Week Comparison: {compare_year_1} vs {compare_year_2}</h3>', unsafe_allow_html=True)
                    
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
                        color_discrete_sequence=px.colors.qualitative.Prism
                    )
                    apply_chart_theme(fig_comparison, title=f'Sales Comparison: {compare_year_1} vs {compare_year_2}', height=500)
                    fig_comparison.update_traces(
                        hovertemplate='<b>Week %{x}</b><br>%{fullData.name}<br>$%{y:,.0f}<extra></extra>'
                    )
                    st.plotly_chart(fig_comparison, use_container_width=True, key='year_comparison')
                    
                    # Show detailed comparison table
                    with st.expander("View Detailed Comparison Table"):
                        currency_format = f"{st.session_state.config['currency_symbol']}{{:,.2f}}"
                        st.dataframe(
                            comparison_df.style.format({
                                f'{compare_year_1}': currency_format,
                                f'{compare_year_2}': currency_format,
                                'Difference': currency_format,
                                '% Change': '{:+.2f}%'
                            }).background_gradient(cmap='RdYlGn', subset=['% Change'], vmin=-50, vmax=50),
                            use_container_width=True
                        )
                else:
                    st.warning("Please select two different years for comparison.")
            else:
                st.info("Need at least 2 financial years for comparative analysis.")
        
        with tab5:
            st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-users" style="color:#3B82F6;"></i> Customer Analysis</h3>', unsafe_allow_html=True)
            
            # ---- Dropping & Rising Customers ---- #
            st.markdown('<h2><i class="fa-solid fa-users" style="color:#3B82F6;margin-right:0.4rem;"></i>Customer Trends <span style="font-size:0.9rem;color:#64748B;font-weight:500;">(Drop vs Rise)</span></h2>', unsafe_allow_html=True)

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
                    st.markdown(f'<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-arrow-trend-down" style="color:#EF4444;"></i> Dropping Customers ({previous_year} → {current_year})</h3>', unsafe_allow_html=True)
                    display_cols = ['Customer'] + [previous_year, current_year]
                    st.dataframe(
                        apply_table_style(dropping_customers[display_cols], format_cols=display_cols[1:]),
                        use_container_width=True
                    )

                with col2:
                    st.markdown(f'<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-arrow-trend-up" style="color:#10B981;"></i> Rising Customers ({previous_year} → {current_year})</h3>', unsafe_allow_html=True)
                    st.dataframe(
                        apply_table_style(rising_customers[display_cols], format_cols=display_cols[1:]),
                        use_container_width=True
                    )
            else:
                st.info(f"Not enough years for drop/rise analysis. Need at least {year_window} years of data.")

            # ---- Customer Purchase View ---- #
            st.markdown('<h2><i class="fa-solid fa-receipt" style="color:#3B82F6;margin-right:0.4rem;"></i>Customer-wise Purchase Detail</h2>', unsafe_allow_html=True)

            # Multiselect Customer - Check for Customer Name column
            # Find customer name column if it exists
            customer_name_col = None
            for col in filtered_df.columns:
                if 'customer' in col.lower() and 'name' in col.lower():
                    customer_name_col = col
                    break
            
            if customer_name_col and customer_name_col in filtered_df.columns:
                # Create a mapping between Customer ID and Customer Name
                customer_mapping = filtered_df[['Customer', customer_name_col]].drop_duplicates()
                customer_mapping = customer_mapping[customer_mapping[customer_name_col].notna()]
                
                # Create display options (Customer Name)
                display_options = sorted(customer_mapping[customer_name_col].unique())
                
                selected_customer_names = st.multiselect(
                    "Select Customer(s) to Analyze",
                    options=display_options,
                    default=display_options[:1] if len(display_options) > 0 else [],
                    key='customer_tab5'
                )
                
                # Map selected names back to Customer IDs
                selected_customers = customer_mapping[
                    customer_mapping[customer_name_col].isin(selected_customer_names)
                ]['Customer'].tolist()
            else:
                # Fallback to Customer ID if no Customer Name column exists
                cust_df = filtered_df.groupby(['Customer', 'Year'])['Total'].sum().reset_index()
                selected_customers = st.multiselect(
                    "Select Customer(s) to Analyze",
                    options=sorted(cust_df['Customer'].unique()),
                    default=cust_df['Customer'].unique()[:1],
                    key='customer_tab5'
                )
            
            if selected_customers and len(selected_customers) > 0:

                # Date Range Filter
                cust_date_range = st.date_input(
                    "Select Date Range for Purchase Analysis",
                    [filtered_df['Issue Date'].min(), filtered_df['Issue Date'].max()],
                    key='date_range_tab5'
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
                            # Optimized warning
                            st.warning(f"{cust} is a dropping customer (sales declined from {previous_year} to {current_year}).")

                # Show raw purchase records
                st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-table-list" style="color:#3B82F6;"></i> Filtered Purchase Records</h3>', unsafe_allow_html=True)
                display_cust_purchase = cust_purchase[['Customer', 'Issue Date', 'Branch', 'Invoice ID', 'Total']]
                
                # Optimized rendering: Using native column configuration for performance
                st.dataframe(
                    display_cust_purchase,
                    column_config={
                        "Issue Date": st.column_config.DateColumn(
                            "Date",
                            format="DD/MM/YYYY" if st.session_state.config['date_format'] == 'dayfirst' else "MM/DD/YYYY"
                        ),
                        "Total": st.column_config.NumberColumn(
                            "Total Purchase",
                            format=f"{st.session_state.config['currency_symbol']}%.2f"
                        ),
                        "Customer": "Customer Name",
                        "Branch": "Branch",
                        "Invoice ID": "Invoice"
                    },
                    use_container_width=True,
                    height=500,
                    hide_index=True
                )

                # Calculate and display the total sum of purchases
                total_filtered_purchase = cust_purchase['Total'].sum()
                st.metric(label="Total Purchase for Filtered Records", value=format_currency(total_filtered_purchase))

                # Year-wise Total Purchases (Bar Chart)
                st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-chart-column" style="color:#3B82F6;"></i> Year-wise Purchase Totals</h3>', unsafe_allow_html=True)
                cust_yearly = cust_purchase.groupby(['Customer', 'Year'])['Total'].sum().reset_index()

                if not cust_yearly.empty:
                    fig_year = px.bar(
                        cust_yearly, x="Year", y="Total", color="Customer", barmode='group',
                        title="Yearly Purchase Summary",
                        color_discrete_sequence=px.colors.qualitative.Prism
                    )
                    fig_year.update_traces(
                        hovertemplate='<b>%{x}</b><br>Customer: %{fullData.name}<br>Total: $%{y:,.0f}<extra></extra>'
                    )
                    apply_chart_theme(fig_year, title="Annual Purchase Summary", height=400)
                    st.plotly_chart(fig_year, use_container_width=True, key='yearly_purchase_customer_tab')
                else:
                    st.info("No yearly data available for selected customers/date range.")

                # Monthly Trend (Line Chart)
                st.markdown('<h3 style="display:flex;align-items:center;gap:0.5rem;"><i class="fa-solid fa-arrow-trend-up" style="color:#3B82F6;"></i> Monthly Purchase Trend</h3>', unsafe_allow_html=True)
                cust_purchase['Month'] = cust_purchase['Issue Date'].dt.to_period('M').astype(str)
                cust_monthly = cust_purchase.groupby(['Customer', 'Month'])['Total'].sum().reset_index()

                if not cust_monthly.empty:
                    fig_monthly = px.line(
                        cust_monthly, x="Month", y="Total", color="Customer", markers=True,
                        title="Monthly Purchase Trend",
                        color_discrete_sequence=px.colors.qualitative.Prism
                    )
                    fig_monthly.update_traces(
                        mode='lines+markers',
                        hovertemplate='<b>%{x}</b><br>Customer: %{fullData.name}<br>Total: $%{y:,.0f}<extra></extra>'
                    )
                    apply_chart_theme(fig_monthly, title="Monthly Purchase History", height=450)
                    st.plotly_chart(fig_monthly, use_container_width=True, key='monthly_purchase_customer_tab')
                else:
                    st.info("No monthly data available for selected customers/date range.")

            else:
                st.info("No customers found for the selected filters.")
    
    else:
        # Show message when no historical data is available
        st.info("""
        **No Historical Sales Data Available**
        
        Upload an Excel file in the sidebar (under 'Upload Historical Sales Data') to view:
        - Annual sales overview with key metrics
        - Quarter-by-quarter analysis
        - Week-by-week sales trends
        - Year-over-year comparative analysis
        
        Your Excel file should contain sheets named 'WA', 'QLD', and 'NSW' with historical sales data.
        """)

else:
    # --- 5. Phase 5: Enhanced Empty State ---
    st.markdown("<br><br>", unsafe_allow_html=True) 
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""<div style="text-align: center; padding: 2rem; background-color: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
<h1 style="border-bottom: none; margin-bottom: 0.5rem; color: #1e293b;">Welcome to Your Dashboard</h1>
<p style="color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;">Get powerful insights into your sales performance across <strong>{', '.join(st.session_state.config['branches'])}</strong>.</p>
<div style="display: flex; flex-direction: column; gap: 1rem; text-align: left; background-color: #f8fafc; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
<div style="display: flex; gap: 1rem; align-items: start;">
<div style="background-color: #dbeafe; color: #3b82f6; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0;">1</div>
<div>
<strong style="color: #334155;">Upload Branch Data</strong>
<p style="margin: 0; font-size: 0.9rem; color: #64748b;">Use the sidebar to upload CSV files for each branch.</p>
</div>
</div>
<div style="display: flex; gap: 1rem; align-items: start;">
<div style="background-color: #dbeafe; color: #3b82f6; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0;">2</div>
<div>
<strong style="color: #334155;">Optional History</strong>
<p style="margin: 0; font-size: 0.9rem; color: #64748b;">Upload historical Excel data for year-over-year comparisons.</p>
</div>
</div>
<div style="display: flex; gap: 1rem; align-items: start;">
<div style="background-color: #dbeafe; color: #3b82f6; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0;">3</div>
<div>
<strong style="color: #334155;">Visual Analysis</strong>
<p style="margin: 0; font-size: 0.9rem; color: #64748b;">Explore interactive charts, KPI cards, and detailed tables.</p>
</div>
</div>
</div>""", unsafe_allow_html=True)
