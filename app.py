import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


st.set_page_config(layout="wide")

@st.cache_data
# ///

# ///


def load_data(nsw_file, qld_file, wa_file):
    columns = [
        "Entity Name", "Branch Region", "Branch", "Division", "Due Date", 
        "Top Level Customer ID", "Top Level Customer Name", "Customer ID", 
        "Customer", "Billing Group ID", "Billing Group", "Invoice ID", 
        "Invoice #", "Issue Date", "Total", "Outstanding", "Delivery", "Status"
    ]

    df_nsw = pd.read_csv(nsw_file, names=columns, header=None)
    df_qld = pd.read_csv(qld_file, names=columns, header=None)
    df_wa = pd.read_csv(wa_file, names=columns, header=None)

    df_nsw['Branch'] = 'NSW'
    df_qld['Branch'] = 'QLD'
    df_wa['Branch'] = 'WA'

    df = pd.concat([df_nsw, df_qld, df_wa], ignore_index=True)

    df.columns = df.columns.str.strip()
    df['Customer'] = df['Customer'].astype(str).str.strip()
    df['Branch'] = df['Branch'].astype(str).str.strip()
    df['Issue Date'] = pd.to_datetime(df['Issue Date'], dayfirst=True, errors='coerce')
    df['Year'] = df['Issue Date'].dt.year
    df['Month'] = df['Issue Date'].dt.to_period('M').astype(str)
    df['Total'] = pd.to_numeric(df['Total'].astype(str).str.replace(',', ''), errors='coerce')

    return df.dropna(subset=['Issue Date', 'Total', 'Branch'])

# File upload UI in sidebar
st.sidebar.title("⬆ Upload Sales Data")
st.sidebar.markdown("Upload CSV files for each branch:")

uploaded_nsw = st.sidebar.file_uploader("NSW Branch CSV", type=['csv'], key='nsw')
uploaded_qld = st.sidebar.file_uploader("QLD Branch CSV", type=['csv'], key='qld')
uploaded_wa = st.sidebar.file_uploader("WA Branch CSV", type=['csv'], key='wa')

st.sidebar.markdown("---")

# Historical Data Upload
st.sidebar.title("📊 Upload Historical Sales Data")
st.sidebar.markdown("Upload Excel file for annual sales analysis:")
uploaded_historical = st.sidebar.file_uploader(
    "Historical Sales Excel (with WA, QLD, NSW sheets)", 
    type=['xlsx', 'xls'], 
    key='historical',
    help="Upload an Excel file containing sheets named 'WA', 'QLD', and 'NSW' with historical sales data"
)

st.sidebar.markdown("---")

# Check if all files are uploaded
all_files_uploaded = uploaded_nsw is not None and uploaded_qld is not None and uploaded_wa is not None

if all_files_uploaded:
    df = load_data(uploaded_nsw, uploaded_qld, uploaded_wa)
else:
    st.sidebar.warning("⚠ Please upload all 3 CSV files to proceed")
    df = None

@st.cache_data
def load_historical_sales_data(excel_file=None):
    """Loads and preprocesses the historical weekly sales data from Excel sheets,
    handling the two-row header structure and selecting relevant columns."""
    if excel_file is None:
        excel_file_path = 'HISTORICAL_REPORT.xlsx' # Fallback to default file
    else:
        excel_file_path = excel_file
    
    sheet_names = ['WA', 'QLD', 'NSW'] # These are the sheet names within the Excel file

    all_historical_df = []

    try:
        for sheet_name in sheet_names:
            # Read the specific sheet from the Excel file with no header initially
            df_raw = pd.read_excel(excel_file_path, sheet_name=sheet_name, header=None)

            # Extract the relevant header information from the first two rows
            header_row_0 = df_raw.iloc[0] # Contains 'Financial Year', '18/19', 'Variance YOY', etc.

            # Identify the indices of the actual sales year columns in header_row_0
            # These are columns like '18/19', '19/20', etc., which are strings containing '/'
            sales_year_indices = [i for i, val in enumerate(header_row_0) if isinstance(val, str) and '/' in val]

            # Construct the list of new column names for the DataFrame
            # The first column will be 'Week' (from 'Week No' in row 1, which is df_raw.iloc[1,0])
            new_column_names = ['Week']
            for idx in sales_year_indices:
                new_column_names.append(str(header_row_0[idx]))

            # Select the actual data rows (starting from index 2, i.e., the 3rd row)
            # and only the columns that correspond to our new_column_names
            data_columns_to_select = [0] + sales_year_indices

            df_processed = df_raw.iloc[2:, data_columns_to_select].copy()
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
        historical_df = load_historical_sales_data(uploaded_historical)
    else:
        # Try to load from default file if it exists
        try:
            historical_df = load_historical_sales_data()
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
                st.metric("Total Sales", f"${total_sales:,.2f}")
            with col2:
                st.metric("Avg Weekly Sales", f"${avg_weekly_sales:,.2f}")
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
                st.dataframe(
                    pivot_annual.style.format("${:,.2f}"),
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
            
            # Add Quarter column to dataframe
            def get_quarter(week):
                if 1 <= week <= 13:
                    return 'Q1'
                elif 14 <= week <= 26:
                    return 'Q2'
                elif 27 <= week <= 39:
                    return 'Q3'
                else:
                    return 'Q4'
            
            quarter_df = filtered_historical_df.copy()
            quarter_df['Quarter'] = quarter_df['Week'].apply(get_quarter)
            
            # Quarter summary table
            quarter_summary = quarter_df.groupby(['Financial Year', 'Quarter', 'Branch'])['Total'].sum().reset_index()
            quarter_pivot = quarter_summary.pivot_table(
                index=['Financial Year', 'Quarter'], 
                columns='Branch', 
                values='Total', 
                fill_value=0
            )
            quarter_pivot['Total'] = quarter_pivot.sum(axis=1)
            
            st.dataframe(
                quarter_pivot.style.format("${:,.2f}"),
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

        # Option to select Quarters
        quarter_options = ["All Quarters", "Q1 (Weeks 1-13)", "Q2 (Weeks 14-26)", "Q3 (Weeks 27-39)", "Q4 (Weeks 40-52)"]
        selected_quarters_display = st.multiselect("Select Quarter(s)", quarter_options, default=["All Quarters"])

        quarter_mapping = {
            "Q1 (Weeks 1-13)": (1, 13),
            "Q2 (Weeks 14-26)": (14, 26),
            "Q3 (Weeks 27-39)": (27, 39),
            "Q4 (Weeks 40-52)": (40, 52)
        }

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
            st.metric(label=f"Total Sales for Selected Range", value=f"${total_sales_for_range:,.2f}")

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
                        st.metric(f"{compare_year_1} Total", f"${year1_total:,.2f}")
                    with col2:
                        st.metric(f"{compare_year_2} Total", f"${year2_total:,.2f}")
                    with col3:
                        st.metric("Change", f"${difference:,.2f}", f"{pct_change:+.2f}%")
                    
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
                        st.dataframe(
                            comparison_df.style.format({
                                f'{compare_year_1}': '${:,.2f}',
                                f'{compare_year_2}': '${:,.2f}',
                                'Difference': '${:,.2f}',
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
    if len(years) >= 2:
        sales_pivot['Drop?'] = sales_pivot[years[-1]] < sales_pivot[years[-2]]
        sales_pivot['Rise?'] = sales_pivot[years[-1]] > sales_pivot[years[-2]]

        dropping_customers = sales_pivot[sales_pivot['Drop?']].reset_index()
        rising_customers = sales_pivot[sales_pivot['Rise?']].reset_index()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"⬇ Dropping Customers ")
            st.dataframe(dropping_customers[['Customer', years[-2], years[-1]]])

        with col2:
            st.subheader(f"⬆ Rising Customers ")
            st.dataframe(rising_customers[['Customer', years[-2], years[-1]]])
    else:
        st.info("Not enough years for drop/rise analysis.")

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
        if 'dropping_customers' in locals():
            for cust in selected_customers:
                if cust in dropping_customers['Customer'].values:
                    st.warning(f" {cust} is a **dropping customer** (sales declined from {years[-2]} to {years[-1]}).")

        # Show raw purchase records
        # Show raw purchase records
        st.subheader("Filtered Purchase Records")
        st.dataframe(
            cust_purchase[['Customer', 'Issue Date', 'Branch', 'Invoice ID', 'Total']],
            use_container_width=True
        )

        # Calculate and display the total sum of purchases
        total_filtered_purchase = cust_purchase['Total'].sum()
        st.metric(label="Total Purchase for Filtered Records", value=f"${total_filtered_purchase:,.2f}")

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
    st.info("↑ Please upload CSV files for all three branches (NSW, QLD, WA) using the sidebar to begin analysis.")
    
    st.markdown("""
    ### ▸ Instructions:
    1. Use the sidebar on the left to upload your CSV files
    2. Upload one file for each branch: NSW, QLD, and WA
    3. Ensure your CSV files have the same structure with these columns:
       - Entity Name, Branch Region, Branch, Division, Due Date, Top Level Customer ID, 
         Top Level Customer Name, Customer ID, Customer, Billing Group ID, Billing Group, 
         Invoice ID, Invoice #, Issue Date, Total, Outstanding, Delivery, Status
    4. Once all files are uploaded, the dashboard will automatically display your analysis
    
    ### ▸ Available Visualizations:
    - Annual and Monthly Sales Analysis
    - Customer Trend Analysis (Rising vs Dropping Customers)
    - Customer-wise Purchase Details
    - Interactive Filters for Custom Analysis
    """)
