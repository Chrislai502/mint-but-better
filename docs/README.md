# Finance Analyzer 💰

A comprehensive personal finance analysis tool that provides an interactive dashboard for tracking and analyzing credit card transactions across multiple cards.

## 📁 Project Structure

```
finance_analyzer/
├── data/
│   ├── input/              # Place your CSV transaction files here
│   │   ├── example_chase.csv       # Example Chase format
│   │   ├── example_apple.csv       # Example Apple Card format
│   │   └── example_bilt.csv        # Example Bilt format
│   ├── processed/          # Generated consolidated data
│   └── config/             # Configuration files (ignored transactions, etc.)
│       └── example_ignored_transactions.json
├── src/
│   ├── dashboard.py        # Main Streamlit dashboard application
│   └── ignore_list_manager.py  # Transaction ignore list management
├── scripts/
│   ├── concatenate_transactions.py  # Merge CSV files
│   └── assign_categories.py         # Interactive category assignment tool
├── docs/                   # Documentation files
│   ├── AGENTS.md          # Guide for using AI to format CSVs
│   └── [other docs]
├── pyproject.toml          # Project configuration
├── run_dashboard.sh        # Quick start script
└── README.md              # This file
```

## ✨ Features

### Interactive Dashboard
- **Multi-card support**: Track transactions across Apple Card, Chase Sapphire Preferred, Chase Freedom Unlimited, and Bilt
  - **Note**: Primarily designed for Chase and Apple Card formats
  - Other credit cards supported via CSV conversion (see [AGENTS.md](AGENTS.md))
- **Dynamic filtering**: Filter by date range, card source, merchant, category, and transaction type
- **Visual analytics**: 
  - Spending by category (pie chart & bar graph)
  - Monthly spending trends
  - Top merchants analysis
  - Spending by card source
- **Transaction management**:
  - Search and filter transactions
  - Include/exclude categories and merchants
  - Persistent ignore list for excluding specific transactions
- **Credit card logic**: Correctly handles expenses, refunds, and payments

### Data Processing
- **CSV concatenation**: Automatically merges transaction files from multiple sources
- **Merchant normalization**: Consolidates merchant name variations (e.g., "Amazon.com*", "AMAZON MKTPL*" → "Amazon")
- **Category assignment**: Interactive tool for assigning categories to uncategorized transactions

### Advanced Features
- Export filtered data to CSV
- Add/edit spending categories
- Transaction ignore list with persistent storage
- Refund tracking with net expense calculations
- Credit card payment exclusion from expense totals

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd finance_analyzer
   ```

2. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

### Setup Your Data

1. **Place your CSV transaction files** in `data/input/`:
   ```bash
   cp /path/to/your/transactions/*.csv data/input/
   ```

2. **Supported CSV formats**:
   - **Apple Card**: `Transaction Date, Post Date, Description, Merchant, Category, Type, Amount, Memo`
   - **Chase**: `Transaction Date, Post Date, Description, Category, Type, Amount`
   - **Bilt**: Similar format with required fields
   - **Other cards**: See [AGENTS.md](AGENTS.md) for conversion instructions using AI tools

   **Example files** are provided in `data/input/` for reference:
   - `example_chase.csv` - Chase card format
   - `example_apple.csv` - Apple Card format  
   - `example_bilt.csv` - Bilt card format

### Run the Application

1. **Consolidate your transactions**:
   ```bash
   uv run python scripts/concatenate_transactions.py
   ```
   This creates `data/processed/all_transactions.csv` with a `Source` column identifying each card.

2. **(Optional) Assign categories to uncategorized transactions**:
   ```bash
   uv run python scripts/assign_categories.py
   ```

3. **Launch the dashboard**:
   ```bash
   ./run_dashboard.sh
   ```
   Or manually:
   ```bash
   uv run streamlit run src/dashboard.py --server.headless true
   ```

4. **Open your browser** to `http://localhost:8501`

## 📊 Using the Dashboard

### Main Features

#### **Sidebar Filters**
- **Date Range**: Select start and end dates
- **Card Source**: Filter by specific credit cards
- **Transaction Type**: Expenses, Refunds, or Payments
- **Category Selection**: Include or exclude specific categories
- **Merchant Selection**: Include or exclude specific merchants
- **Amount Range**: Filter by transaction amount

#### **Summary Metrics**
- Total Expenses
- Total Refunds
- Net Expenses (Expenses - Refunds)

#### **Visualizations**
1. **Expenses by Category**: Pie chart and bar graph
2. **Spending Over Time**: Line chart showing monthly trends
3. **Spending by Card Source**: Bar chart comparison
4. **Top Merchants**: Most spent merchants
5. **Merchant Distribution**: Pie chart of top merchants

#### **Transaction Details**
- Searchable and filterable table
- Sort by date, amount, category, or merchant
- Export to CSV
- Additional inline filters for the transaction table

#### **Manage Ignored Transactions**
- Select transactions to permanently exclude from calculations
- View and manage ignored items in sidebar
- Persistent storage across sessions

### Category Management

Add or edit spending categories directly in the sidebar:
- Click "Add New Category"
- Enter category name
- Categories are saved to your data file

### Ignore List

Exclude specific transactions (e.g., business expenses, reimbursements):
1. Search for the transaction
2. Check the box next to it
3. Click "🚫 Ignore Selected"
4. View ignored transactions in sidebar → "🚫 Ignore List"
5. Click "✓" to restore a transaction

## 🛠️ Advanced Usage

### Using Other Credit Cards

If your credit card isn't Chase, Apple, or Bilt, see **[AGENTS.md](AGENTS.md)** for detailed instructions on:
- Using ChatGPT/Claude/Cursor to convert your CSV format
- Example prompts for common conversion scenarios
- Adding transaction categories with AI assistance
- Automating the conversion process

### Category Assignment Tool

For batch category assignment:

```bash
# Assign categories to transactions missing them
uv run python scripts/assign_categories.py --categories

# Assign merchants to transactions missing them
uv run python scripts/assign_categories.py --merchants
```

Features:
- Sorted by transaction amount (highest first)
- Auto-suggestions based on description keywords
- Bulk assignment with "apply to similar" option
- Creates backups before saving changes

### Custom CSV Processing

Edit `scripts/concatenate_transactions.py` to:
- Add support for new card types
- Customize merchant normalization rules
- Add custom data transformations

### Merchant Normalization

Common patterns are automatically normalized:
- Amazon variations → "Amazon"
- Trader Joe's variations → "Trader Joe's"
- Southwest Airlines variations → "Southwest Airlines"
- And many more...

Add custom patterns in `scripts/concatenate_transactions.py`:
```python
merchant_patterns = [
    (r'YOUR_PATTERN', 'Normalized Name'),
    # ...
]
```

## 📋 Requirements

- Python 3.9+
- `pandas>=2.0.0`
- `streamlit>=1.30.0`
- `plotly>=5.18.0`

## 📝 Data Privacy

- All data processing happens **locally** on your machine
- No data is sent to external servers
- Transaction files remain in your `data/` directory
- Ignored transactions are stored in `data/config/ignored_transactions.json`

## 🐛 Troubleshooting

### "File not found" errors
- Ensure CSV files are in `data/input/`
- Run `concatenate_transactions.py` before launching dashboard

### Dashboard won't start
- Check that port 8501 is available
- Kill existing processes: `pkill -f "streamlit run"`
- Restart: `./run_dashboard.sh`

### Missing categories
- Use `scripts/assign_categories.py` to assign categories interactively
- Or manually edit `data/processed/all_transactions.csv`

### Incorrect merchant names
- Edit merchant normalization patterns in `scripts/concatenate_transactions.py`
- Re-run the concatenation script

## 📚 Documentation

Additional documentation in `docs/`:
- `CATEGORY_ASSIGNMENT_GUIDE.md` - Category assignment tutorial
- `CREDIT_CARD_LOGIC_FIX.md` - How credit card transactions are handled
- `FEATURE_SUMMARY.md` - Complete feature list
- `IGNORE_LIST_FEATURE.md` - Ignore list detailed guide
- `INCLUDE_EXCLUDE_FILTERS.md` - Filter system documentation

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Dashboard framework
- [Plotly](https://plotly.com/) - Interactive visualizations
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

---

**Happy Analyzing! 💰📊**
