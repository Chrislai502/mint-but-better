# Finance Analyzer - Complete Feature Summary

## 📊 Current Status

- **Total Transactions**: 434
- **Missing Categories**: 72 (16.6%) - automatically shown as "Other" 
- **Missing Merchants**: 0 (0%)
- **Cards Tracked**: 4 (Bilt, Apple Card, Chase Sapphire Preferred, Chase Freedom Unlimited)

## 🎯 Key Features Implemented

### 1. **Interactive Web Dashboard** (http://localhost:8501)
- Real-time visualizations with Plotly
- Fully responsive and modern UI
- Automatic data refresh

### 2. **Merchant Intelligence**
- **58 Amazon transactions** consolidated from various formats
- Smart merchant normalization (Amazon, Trader Joe's, Southwest, etc.)
- Filter by merchant with "All", "Select Specific", or "Exclude Payments" options

### 3. **Comprehensive Visualizations**
- 📊 **Category Analysis**: Pie chart + bar chart
- 📈 **Time Series**: Monthly spending trends
- 💳 **Card Comparison**: Spending by source
- 🏪 **Merchant Analysis**: 
  - Top 15 merchants (bar chart)
  - Top 10 merchants distribution (pie chart)
  - Transaction frequency analysis

### 4. **Dynamic Filtering**
✅ Date Range (6 preset options + custom)
✅ Card Source (multi-select)
✅ Transaction Type (Expense/Income/Payment)
✅ Categories (all or specific)
✅ Merchants (all or specific)
✅ Amount Range (slider)
✅ Search (by description)

### 5. **Category Assignment Tool** ⭐ NEW!

**What it does:**
- Interactive terminal tool for assigning categories
- Sorts transactions by **highest amount first**
- Auto-suggests categories based on merchant/description
- Allows creating new categories on the fly
- Auto-backups before saving

**How to use:**
```bash
# Check what needs fixing
uv run python assign_categories.py --stats

# Start assigning categories
uv run python assign_categories.py --categories

# Assign merchants (if needed)
uv run python assign_categories.py --merchants
```

**Features:**
- 🎯 **Smart Suggestions**: Type `auto` for AI-suggested categories
- ➕ **Create Categories**: Type `new:CategoryName` 
- ⏭️ **Skip**: Type `skip` to skip
- 💾 **Safe**: Auto-backup with timestamps
- 🔄 **Resume**: Quit and resume anytime

### 6. **Data Quality Alerts**
- Dashboard shows warning if data has "Other" category or "Unknown" merchants
- Provides instructions to fix using the assignment tool
- Shows percentage of incomplete data

## 📁 Project Structure

```
finance_analyzer/
├── dashboard.py                    # Main web dashboard
├── concatenate_transactions.py     # CSV merger with merchant normalization
├── assign_categories.py            # Interactive category assignment tool
├── run_dashboard.sh               # Quick start script
├── README.md                      # Main documentation
├── CATEGORY_ASSIGNMENT_GUIDE.md   # Detailed tool guide
├── data/All/                      # Source CSV files
│   ├── bilt.csv
│   ├── apple.csv
│   ├── chase_sapphire_preferred.CSV
│   └── chase_freedom_unlimited.CSV
├── all_transactions.csv           # Combined & normalized data
└── .venv/                         # UV virtual environment
```

## 🚀 Quick Start

1. **View Dashboard**
   ```bash
   ./run_dashboard.sh
   # Or: uv run streamlit run dashboard.py
   ```
   Open: http://localhost:8501

2. **Fix Missing Categories** (72 transactions)
   ```bash
   uv run python assign_categories.py --categories
   ```

3. **Refresh Dashboard**
   - Click "🔄 Refresh Data" button in dashboard
   - Or refresh browser page

## 💡 Workflow Example

```bash
# 1. Check data quality
uv run python assign_categories.py --stats

# 2. Assign categories (interactive)
uv run python assign_categories.py --categories
# - See highest transactions first
# - Type 'auto' for suggestions
# - Type 'new:Dining' to create new category
# - Type 'quit' when done

# 3. View updated dashboard
# Browser will auto-update or click Refresh Data

# 4. Export filtered data
# Use Download CSV button in dashboard
```

## 🎨 Dashboard Sections

1. **Summary Metrics** - Total expenses, income, net change, transaction count
2. **Data Quality Alert** - Shows if categories/merchants need fixing
3. **Category Visualizations** - Pie + bar charts
4. **Time Analysis** - Monthly trends
5. **Card Comparison** - Spending by source
6. **Merchant Analysis** - Top merchants + frequency
7. **Category Breakdown Table** - Detailed statistics
8. **Transaction Details** - Searchable, filterable table
9. **Export Tools** - Download CSV, refresh data

## 🔧 Technical Details

- **Environment**: UV (Python 3.11)
- **Framework**: Streamlit
- **Visualization**: Plotly
- **Data**: Pandas CSV processing
- **Merchant Normalization**: Regex pattern matching (40+ patterns)
- **Auto-backup**: Timestamped before each save

## 📈 Next Steps

1. Run category assignment tool to fix 72 transactions
2. Explore different filters and visualizations
3. Export data for specific date ranges
4. Create custom categories as needed
5. Track spending trends over time

## 🔗 Quick Links

- **Dashboard**: http://localhost:8501
- **Guide**: CATEGORY_ASSIGNMENT_GUIDE.md
- **README**: README.md

