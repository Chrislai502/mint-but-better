#!/usr/bin/env python3
"""
Interactive Finance Dashboard
Displays spending analysis with pie charts and bar graphs, with dynamic filtering capabilities.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
from ignore_list_manager import IgnoreListManager

# Get the project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent
DATA_FILE = PROJECT_ROOT / 'data' / 'processed' / 'all_transactions.csv'

# Page configuration
st.set_page_config(
    page_title="Finley",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stSelectbox, .stMultiSelect {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(file_path=None):
    """Load and preprocess the transaction data."""
    if file_path is None:
        file_path = DATA_FILE
    df = pd.read_csv(file_path)
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
    df['Post Date'] = pd.to_datetime(df['Post Date'])
    
    # Fill missing categories and merchants
    df['Category'] = df['Category'].fillna('Other')
    df['Category'] = df['Category'].replace('', 'Other')
    
    # Fill missing merchants with "Unknown"
    df['Normalized Merchant'] = df['Normalized Merchant'].fillna('Unknown')
    df['Normalized Merchant'] = df['Normalized Merchant'].replace('', 'Unknown')
    
    return df
    """Load transaction data from CSV file."""
    df = pd.read_csv(file_path)
    # Convert Transaction Date to datetime
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], format='%m/%d/%Y')
    # Convert Amount to numeric
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    
    # Fill missing categories with "Other"
    df['Category'] = df['Category'].fillna('Other')
    df['Category'] = df['Category'].replace('', 'Other')
    
    # Fill missing merchants with "Unknown"
    df['Normalized Merchant'] = df['Normalized Merchant'].fillna('Unknown')
    df['Normalized Merchant'] = df['Normalized Merchant'].replace('', 'Unknown')
    
    return df

def categorize_transaction(row):
    """
    Categorize credit card transactions correctly:
    - Purchase/Sale = Expense (regardless of sign, different cards use different conventions)
    - Return = Refund (reduces expenses)
    - Payment = Credit card payment (excluded from expense calculations)
    """
    transaction_type = str(row['Type']).strip().lower()
    
    if transaction_type == 'payment':
        return 'Payment'
    elif transaction_type == 'return':
        return 'Refund'
    elif transaction_type in ['purchase', 'sale']:
        return 'Expense'
    else:
        # Fallback for unknown types
        return 'Other'

def main():
    st.markdown('<div class="main-header">🌿 Finley </div>', unsafe_allow_html=True)
    
    # Initialize ignore list manager
    ignore_manager = IgnoreListManager()
    
    # Load data - automatically concatenate if needed
    try:
        # Check if the data file exists
        if not DATA_FILE.exists():
            st.warning("⚠️ Transaction data not found. Running concatenation script...")
            
            # Import and run concatenation
            import sys
            sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))
            
            try:
                from concatenate_transactions import concatenate_transactions
                
                with st.spinner("🔄 Consolidating transaction files..."):
                    concatenate_transactions()
                
                st.success("✅ Successfully consolidated transaction files!")
                st.rerun()
                
            except FileNotFoundError as e:
                st.error(f"❌ Error: No CSV files found in `data/input/` directory.")
                st.info("💡 **Next Steps:**\n\n"
                       "1. Place your credit card CSV files in the `data/input/` directory\n"
                       "2. Supported formats: Chase, Apple Card, Bilt\n"
                       "3. For other cards, see [AGENTS.md](../docs/AGENTS.md) for conversion help")
                st.stop()
            except Exception as e:
                st.error(f"❌ Error during concatenation: {e}")
                st.info("Please check your CSV files and try running `scripts/concatenate_transactions.py` manually.")
                st.stop()
        
        df = load_data()
    except FileNotFoundError:
        st.error(f"❌ Error: {DATA_FILE} not found after concatenation attempt.")
        st.stop()
    
    # Filter out ignored transactions early
    original_count = len(df)
    df = df[~df.apply(ignore_manager.is_ignored, axis=1)].copy()
    ignored_count = original_count - len(df)
    
    if ignored_count > 0:
        st.info(f"ℹ️ {ignored_count} transaction(s) are currently ignored and excluded from all calculations.")
    
    # Add transaction type classification
    df['Transaction Type'] = df.apply(categorize_transaction, axis=1)
    
    # Sidebar filters
    st.sidebar.header("🎛️ Filters")
    
    # Date range filter
    st.sidebar.subheader("📅 Date Range")
    min_date = df['Transaction Date'].min().date()
    max_date = df['Transaction Date'].max().date()
    
    date_option = st.sidebar.radio(
        "Select date range:",
        ["All Time", "Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year", "Custom Range"]
    )
    
    if date_option == "Last 30 Days":
        start_date = max_date - timedelta(days=30)
        end_date = max_date
    elif date_option == "Last 90 Days":
        start_date = max_date - timedelta(days=90)
        end_date = max_date
    elif date_option == "Last 6 Months":
        start_date = max_date - timedelta(days=180)
        end_date = max_date
    elif date_option == "Last Year":
        start_date = max_date - timedelta(days=365)
        end_date = max_date
    elif date_option == "Custom Range":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Start", min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("End", max_date, min_value=min_date, max_value=max_date)
    else:  # All Time
        start_date = min_date
        end_date = max_date
    
    # Filter by date
    mask = (df['Transaction Date'].dt.date >= start_date) & (df['Transaction Date'].dt.date <= end_date)
    filtered_df = df[mask].copy()
    
    # Source (Card) filter
    st.sidebar.subheader("💳 Card Source")
    all_sources = sorted(df['Source'].unique())
    selected_sources = st.sidebar.multiselect(
        "Select cards:",
        options=all_sources,
        default=all_sources
    )
    filtered_df = filtered_df[filtered_df['Source'].isin(selected_sources)]
    
    # Transaction Type filter
    st.sidebar.subheader("📊 Transaction Type")
    transaction_types = st.sidebar.multiselect(
        "Select types:",
        options=['Expense', 'Refund', 'Payment', 'Other'],
        default=['Expense', 'Refund']
    )
    filtered_df = filtered_df[filtered_df['Transaction Type'].isin(transaction_types)]
    
    # Category filter
    st.sidebar.subheader("🏷️ Categories")
    all_categories = sorted([cat for cat in df['Category'].unique() if pd.notna(cat) and cat != ''])
    
    category_option = st.sidebar.radio("Category selection:", ["All Categories", "Include Specific", "Exclude Specific"])
    if category_option == "Include Specific":
        selected_categories = st.sidebar.multiselect(
            "Include these categories:",
            options=all_categories,
            default=[]
        )
        if selected_categories:
            filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
        else:
            # If no categories selected, show nothing
            filtered_df = filtered_df[filtered_df['Category'].isin([])]
    elif category_option == "Exclude Specific":
        excluded_categories = st.sidebar.multiselect(
            "Exclude these categories:",
            options=all_categories,
            default=[]
        )
        if excluded_categories:
            filtered_df = filtered_df[~filtered_df['Category'].isin(excluded_categories)]
    
    # Merchant filter
    st.sidebar.subheader("🏪 Merchants")
    all_merchants = sorted([m for m in df['Normalized Merchant'].unique() if pd.notna(m) and m != '' and m != 'Unknown'])
    
    merchant_option = st.sidebar.radio("Merchant selection:", ["All Merchants", "Include Specific", "Exclude Specific"])
    if merchant_option == "Include Specific":
        selected_merchants = st.sidebar.multiselect(
            "Include these merchants:",
            options=all_merchants,
            default=[]
        )
        if selected_merchants:
            filtered_df = filtered_df[filtered_df['Normalized Merchant'].isin(selected_merchants)]
        else:
            # If no merchants selected, show nothing
            filtered_df = filtered_df[filtered_df['Normalized Merchant'].isin([])]
    elif merchant_option == "Exclude Specific":
        excluded_merchants = st.sidebar.multiselect(
            "Exclude these merchants:",
            options=all_merchants,
            default=['Payment/Transfer']  # Commonly excluded
        )
        if excluded_merchants:
            filtered_df = filtered_df[~filtered_df['Normalized Merchant'].isin(excluded_merchants)]
    
    # Amount range filter
    st.sidebar.subheader("💵 Amount Range")
    if len(filtered_df) > 0:
        min_amount = float(filtered_df['Amount'].min())
        max_amount = float(filtered_df['Amount'].max())
        amount_range = st.sidebar.slider(
            "Filter by amount:",
            min_value=min_amount,
            max_value=max_amount,
            value=(min_amount, max_amount),
            format="$%.2f"
        )
        filtered_df = filtered_df[
            (filtered_df['Amount'] >= amount_range[0]) & 
            (filtered_df['Amount'] <= amount_range[1])
        ]
    
    # Ignore List Management in Sidebar
    st.sidebar.subheader("🚫 Ignore List")
    ignored_transactions = ignore_manager.get_all_ignored()
    st.sidebar.write(f"**{len(ignored_transactions)} transaction(s) ignored**")
    
    if len(ignored_transactions) > 0:
        with st.sidebar.expander("View & Manage Ignored"):
            for ignored in ignored_transactions:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"{ignored['date']}")
                    st.text(f"{ignored['description'][:30]}...")
                    st.text(f"${ignored['amount']:.2f} - {ignored['source']}")
                with col2:
                    if st.button("✓", key=f"remove_{ignored['id']}", help="Remove from ignore list"):
                        ignore_manager.remove_transaction(ignored['id'])
                        st.rerun()
                st.divider()
    
    # Category Management
    st.sidebar.subheader("✏️ Category Management")
    with st.sidebar.expander("Edit Categories"):
        st.info("Select transactions below to reassign categories")
        
        new_category = st.text_input("New category name:")
        if st.button("Add New Category") and new_category:
            st.success(f"Category '{new_category}' ready to use!")
    
    # Main content
    if len(filtered_df) == 0:
        st.warning("⚠️ No transactions found with the current filters.")
        st.stop()
    
    # Key metrics
    st.header("📈 Summary Metrics")
    
    # Check for missing data
    missing_categories = len(df[df['Category'] == 'Other'])
    missing_merchants = len(df[df['Normalized Merchant'] == 'Unknown'])
    
    if missing_categories > 0 or missing_merchants > 0:
        st.warning(f"⚠️ Data Quality: {missing_categories} transactions with 'Other' category, {missing_merchants} with 'Unknown' merchant. Use the category assignment tool to fix.")
        with st.expander("How to assign categories and merchants"):
            st.markdown("""
            Run the interactive assignment tool from your terminal:
            ```bash
            # View statistics
            uv run python assign_categories.py --stats
            
            # Assign missing categories
            uv run python assign_categories.py --categories
            
            # Assign missing merchants
            uv run python assign_categories.py --merchants
            ```
            The tool will:
            - Show transactions sorted by amount (highest first)
            - Suggest categories based on merchant/description
            - Allow you to create new categories
            - Auto-backup your data before saving
            """)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate expenses and refunds correctly for credit cards
    expense_transactions = filtered_df[filtered_df['Transaction Type'] == 'Expense']
    refund_transactions = filtered_df[filtered_df['Transaction Type'] == 'Refund']
    
    # For expenses: take absolute value (handles both positive and negative amounts)
    total_expenses = expense_transactions['Amount'].abs().sum()
    
    # For refunds: take absolute value (these reduce expenses)
    total_refunds = refund_transactions['Amount'].abs().sum()
    
    # Net expenses = expenses - refunds
    net_expenses = total_expenses - total_refunds
    
    total_transactions = len(filtered_df)
    
    with col1:
        st.metric("💸 Total Expenses", f"${total_expenses:,.2f}", 
                  delta=None, delta_color="inverse")
    with col2:
        st.metric("💰 Refunds", f"${total_refunds:,.2f}",
                  delta=None, delta_color="normal")
    with col3:
        st.metric("📊 Net Expenses", f"${net_expenses:,.2f}", 
                  delta=f"-${total_refunds:,.2f}" if total_refunds > 0 else None,
                  delta_color="normal")
    with col4:
        st.metric("🧾 Transactions", f"{total_transactions:,}")
    
    # Visualizations
    st.header("📊 Spending Analysis")
    
    # Prepare expense data for charts
    # Include both Expense and Refund types, but show refunds separately if needed
    expense_df = filtered_df[filtered_df['Transaction Type'] == 'Expense'].copy()
    expense_df['Absolute Amount'] = expense_df['Amount'].abs()
    
    if len(expense_df) > 0:
        # Show refund summary if there are refunds
        refund_df = filtered_df[filtered_df['Transaction Type'] == 'Refund'].copy()
        if len(refund_df) > 0:
            refund_total = refund_df['Amount'].abs().sum()
            st.info(f"💰 Note: You have ${refund_total:,.2f} in refunds. Net expenses shown below already subtract these refunds.")
        
        # Group by category
        category_spending = expense_df.groupby('Category')['Absolute Amount'].sum().reset_index()
        category_spending = category_spending.sort_values('Absolute Amount', ascending=False)
        
        # Two column layout for charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🥧 Expenses by Category (Pie Chart)")
            fig_pie = px.pie(
                category_spending, 
                values='Absolute Amount', 
                names='Category',
                title='Spending Distribution',
                hole=0.3,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("📊 Expenses by Category (Bar Chart)")
            fig_bar = px.bar(
                category_spending,
                x='Category',
                y='Absolute Amount',
                title='Spending by Category',
                labels={'Absolute Amount': 'Amount ($)', 'Category': 'Category'},
                color='Absolute Amount',
                color_continuous_scale='Blues'
            )
            fig_bar.update_layout(
                xaxis_tickangle=-45,
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Spending over time
        st.subheader("📈 Spending Over Time")
        expense_df['Month'] = expense_df['Transaction Date'].dt.to_period('M').astype(str)
        monthly_spending = expense_df.groupby('Month')['Absolute Amount'].sum().reset_index()
        
        fig_line = px.line(
            monthly_spending,
            x='Month',
            y='Absolute Amount',
            title='Monthly Spending Trend',
            labels={'Absolute Amount': 'Amount ($)', 'Month': 'Month'},
            markers=True
        )
        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Spending by card source
        st.subheader("💳 Spending by Card")
        source_spending = expense_df.groupby('Source')['Absolute Amount'].sum().reset_index()
        source_spending = source_spending.sort_values('Absolute Amount', ascending=True)
        
        fig_source = px.bar(
            source_spending,
            x='Absolute Amount',
            y='Source',
            title='Spending by Card Source',
            labels={'Absolute Amount': 'Amount ($)', 'Source': 'Card'},
            color='Absolute Amount',
            color_continuous_scale='Reds',
            orientation='h'
        )
        fig_source.update_layout(height=300)
        st.plotly_chart(fig_source, use_container_width=True)
        
        # Spending by Merchant
        st.subheader("🏪 Top Merchants by Spending")
        
        # Exclude Payment/Transfer from merchant analysis
        merchant_expense_df = expense_df[expense_df['Normalized Merchant'] != 'Payment/Transfer'].copy()
        
        if len(merchant_expense_df) > 0:
            merchant_spending = merchant_expense_df.groupby('Normalized Merchant')['Absolute Amount'].sum().reset_index()
            merchant_spending = merchant_spending.sort_values('Absolute Amount', ascending=False).head(15)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_merchant_bar = px.bar(
                    merchant_spending,
                    x='Normalized Merchant',
                    y='Absolute Amount',
                    title='Top 15 Merchants',
                    labels={'Absolute Amount': 'Amount ($)', 'Normalized Merchant': 'Merchant'},
                    color='Absolute Amount',
                    color_continuous_scale='Greens'
                )
                fig_merchant_bar.update_layout(
                    xaxis_tickangle=-45,
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig_merchant_bar, use_container_width=True)
            
            with col2:
                fig_merchant_pie = px.pie(
                    merchant_spending.head(10),
                    values='Absolute Amount',
                    names='Normalized Merchant',
                    title='Top 10 Merchants Distribution',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_merchant_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_merchant_pie.update_layout(height=400)
                st.plotly_chart(fig_merchant_pie, use_container_width=True)
            
            # Merchant frequency analysis
            st.subheader("📊 Merchant Transaction Frequency")
            merchant_freq = merchant_expense_df.groupby('Normalized Merchant').agg({
                'Absolute Amount': ['sum', 'mean', 'count']
            }).reset_index()
            merchant_freq.columns = ['Merchant', 'Total Spent', 'Avg per Transaction', 'Transaction Count']
            merchant_freq = merchant_freq.sort_values('Transaction Count', ascending=False).head(15)
            
            fig_freq = px.bar(
                merchant_freq,
                x='Merchant',
                y='Transaction Count',
                title='Top 15 Most Frequent Merchants',
                labels={'Transaction Count': 'Number of Transactions', 'Merchant': 'Merchant'},
                color='Total Spent',
                color_continuous_scale='Purples'
            )
            fig_freq.update_layout(
                xaxis_tickangle=-45,
                height=400
            )
            st.plotly_chart(fig_freq, use_container_width=True)
        
        # Category breakdown table
        st.subheader("📋 Category Breakdown")
        category_details = expense_df.groupby('Category').agg({
            'Absolute Amount': ['sum', 'mean', 'count']
        }).reset_index()
        category_details.columns = ['Category', 'Total Spent', 'Avg per Transaction', 'Number of Transactions']
        category_details['Total Spent'] = category_details['Total Spent'].apply(lambda x: f"${x:,.2f}")
        category_details['Avg per Transaction'] = category_details['Avg per Transaction'].apply(lambda x: f"${x:,.2f}")
        category_details = category_details.sort_values('Number of Transactions', ascending=False)
        st.dataframe(category_details, use_container_width=True)
    
    else:
        st.info("ℹ️ No expense transactions in the selected date range.")
    
    # Transaction details table
    st.header("🔍 Transaction Details")
    
    # Create a copy for transaction details filtering
    details_df = filtered_df.copy()
    
    # Additional filters for transaction details
    with st.expander("🎛️ Additional Filters for Transaction Table", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Category filter mode
            category_filter_mode = st.radio(
                "Category Filter:",
                ["All", "Include", "Exclude"],
                horizontal=True,
                key="category_filter_mode"
            )
            
            if category_filter_mode != "All":
                detail_categories = sorted([cat for cat in details_df['Category'].unique() if pd.notna(cat) and cat != ''])
                
                if category_filter_mode == "Include":
                    selected_detail_categories = st.multiselect(
                        "Include categories:",
                        options=detail_categories,
                        default=[],
                        key="include_categories"
                    )
                    if selected_detail_categories:
                        details_df = details_df[details_df['Category'].isin(selected_detail_categories)]
                    else:
                        # If no categories selected, show nothing
                        details_df = details_df[details_df['Category'].isin([])]
                else:  # Exclude
                    excluded_detail_categories = st.multiselect(
                        "Exclude categories:",
                        options=detail_categories,
                        default=[],
                        key="exclude_categories"
                    )
                    if excluded_detail_categories:
                        details_df = details_df[~details_df['Category'].isin(excluded_detail_categories)]
        
        with col2:
            # Merchant filter mode
            merchant_filter_mode = st.radio(
                "Merchant Filter:",
                ["All", "Include", "Exclude"],
                horizontal=True,
                key="merchant_filter_mode"
            )
            
            if merchant_filter_mode != "All":
                detail_merchants = sorted([m for m in details_df['Normalized Merchant'].unique() if pd.notna(m) and m != ''])
                
                if merchant_filter_mode == "Include":
                    selected_detail_merchants = st.multiselect(
                        "Include merchants:",
                        options=detail_merchants,
                        default=[],
                        key="include_merchants"
                    )
                    if selected_detail_merchants:
                        details_df = details_df[details_df['Normalized Merchant'].isin(selected_detail_merchants)]
                    else:
                        # If no merchants selected, show nothing
                        details_df = details_df[details_df['Normalized Merchant'].isin([])]
                else:  # Exclude
                    excluded_detail_merchants = st.multiselect(
                        "Exclude merchants:",
                        options=detail_merchants,
                        default=[],
                        key="exclude_merchants"
                    )
                    if excluded_detail_merchants:
                        details_df = details_df[~details_df['Normalized Merchant'].isin(excluded_detail_merchants)]
        
        with col3:
            # Transaction Type filter for details
            detail_types = ['All'] + sorted(details_df['Transaction Type'].unique().tolist())
            selected_detail_type = st.selectbox(
                "Filter by Type:",
                options=detail_types,
                index=0
            )
            if selected_detail_type != 'All':
                details_df = details_df[details_df['Transaction Type'] == selected_detail_type]
        
        # Amount range filter
        col1, col2 = st.columns(2)
        with col1:
            min_amount_filter = st.number_input(
                "Min Amount ($):",
                value=None,
                step=10.0,
                format="%.2f"
            )
        with col2:
            max_amount_filter = st.number_input(
                "Max Amount ($):",
                value=None,
                step=10.0,
                format="%.2f"
            )
        
        if min_amount_filter is not None:
            details_df = details_df[details_df['Amount'].abs() >= min_amount_filter]
        if max_amount_filter is not None:
            details_df = details_df[details_df['Amount'].abs() <= max_amount_filter]
    
    # Search functionality
    search_term = st.text_input("🔎 Search by description or merchant:", "")
    if search_term:
        details_df = details_df[
            details_df['Description'].str.contains(search_term, case=False, na=False) |
            details_df['Normalized Merchant'].str.contains(search_term, case=False, na=False)
        ]
    
    # Display options and sorting
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        rows_to_show = st.selectbox("Rows to display:", ["All", 10, 25, 50, 100])
    with col2:
        sort_by = st.selectbox("Sort by:", ["Date (Newest)", "Date (Oldest)", "Amount (High-Low)", "Amount (Low-High)", "Category", "Merchant"])
    
    # Apply sorting
    if sort_by == "Date (Newest)":
        details_df = details_df.sort_values('Transaction Date', ascending=False)
    elif sort_by == "Date (Oldest)":
        details_df = details_df.sort_values('Transaction Date', ascending=True)
    elif sort_by == "Amount (High-Low)":
        details_df['Sort_Amount'] = details_df['Amount'].abs()
        details_df = details_df.sort_values('Sort_Amount', ascending=False)
        details_df = details_df.drop('Sort_Amount', axis=1)
    elif sort_by == "Amount (Low-High)":
        details_df['Sort_Amount'] = details_df['Amount'].abs()
        details_df = details_df.sort_values('Sort_Amount', ascending=True)
        details_df = details_df.drop('Sort_Amount', axis=1)
    elif sort_by == "Category":
        details_df = details_df.sort_values(['Category', 'Transaction Date'], ascending=[True, False])
    elif sort_by == "Merchant":
        details_df = details_df.sort_values(['Normalized Merchant', 'Transaction Date'], ascending=[True, False])
    
    # Show count - display count vs total filtered
    total_filtered = len(details_df)
    rows_displayed = total_filtered if rows_to_show == "All" else min(rows_to_show, total_filtered)
    
    if rows_to_show == "All":
        st.info(f"📊 Showing all {total_filtered} transaction(s)")
    else:
        st.info(f"📊 Showing {rows_displayed} of {total_filtered} transaction(s)")
    
    # Transaction Table first
    st.subheader("📋 Transaction Table")
    
    # Format the display dataframe
    display_df = details_df[['Transaction Date', 'Description', 'Normalized Merchant', 'Category', 'Amount', 'Source', 'Transaction Type']].copy()
    display_df['Transaction Date'] = display_df['Transaction Date'].dt.strftime('%m/%d/%Y')
    display_df['Amount'] = display_df['Amount'].apply(lambda x: f"${x:,.2f}")
    display_df = display_df.rename(columns={'Normalized Merchant': 'Merchant'})
    
    if rows_to_show != "All":
        display_df = display_df.head(rows_to_show)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Now the Ignore transactions section
    st.subheader("🚫 Manage Ignored Transactions")
    st.write("Select transactions below to permanently exclude them from all calculations. They will be saved to a file and persist across sessions.")
    
    # Create columns for selection
    if len(details_df) > 0:
        # Initialize session state for selected transactions
        if 'selected_to_ignore' not in st.session_state:
            st.session_state.selected_to_ignore = []
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("**Select transactions to ignore:**")
        with col2:
            if st.button("🚫 Ignore Selected", type="primary", use_container_width=True):
                if st.session_state.selected_to_ignore:
                    ignored_count = 0
                    for idx in st.session_state.selected_to_ignore:
                        row = details_df.loc[idx]
                        if ignore_manager.add_transaction(row):
                            ignored_count += 1
                    st.success(f"✓ Added {ignored_count} transaction(s) to ignore list. Refreshing...")
                    st.session_state.selected_to_ignore = []
                    st.rerun()
                else:
                    st.warning("⚠️ No transactions selected. Check the boxes next to transactions you want to ignore.")
        
        # Display transactions with checkboxes
        # Reset details_df index for consistent selection
        details_display = details_df.reset_index(drop=False)
        
        # Limit rows if needed
        display_limit = len(details_display) if rows_to_show == "All" else min(rows_to_show, len(details_display))
        
        for i in range(display_limit):
            row = details_display.iloc[i]
            original_idx = row['index'] if 'index' in row else i
            
            col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 1, 2.5, 1.5, 1, 0.8, 0.8])
            
            with col1:
                is_selected = original_idx in st.session_state.selected_to_ignore
                if st.checkbox("", value=is_selected, key=f"ignore_check_{original_idx}_{i}", label_visibility="collapsed"):
                    if original_idx not in st.session_state.selected_to_ignore:
                        st.session_state.selected_to_ignore.append(original_idx)
                else:
                    if original_idx in st.session_state.selected_to_ignore:
                        st.session_state.selected_to_ignore.remove(original_idx)
            
            with col2:
                date_val = row['Transaction Date']
                if isinstance(date_val, pd.Timestamp):
                    st.text(date_val.strftime('%m/%d/%Y'))
                else:
                    st.text(str(date_val))
            
            with col3:
                desc = str(row['Description'])
                st.text(desc[:40] + "..." if len(desc) > 40 else desc)
            
            with col4:
                merchant = str(row['Normalized Merchant'])
                st.text(merchant[:20] + "..." if len(merchant) > 20 else merchant)
            
            with col5:
                st.text(str(row['Category']))
            
            with col6:
                st.text(row['Source'][:8])
            
            with col7:
                amt = row['Amount']
                st.text(f"${amt:,.2f}")
    
    # Export functionality
    st.header("💾 Export Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name=f"transactions_{start_date}_{end_date}.csv",
            mime="text/csv"
        )
    
    with col2:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(f"_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
    st.markdown(f"_Showing {len(filtered_df)} of {len(df)} total transactions_")

if __name__ == "__main__":
    main()

