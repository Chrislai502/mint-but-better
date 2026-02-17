# Finley 🌿

An all-Python expense analysis tool with an interactive dashboard for tracking credit card transactions across multiple cards.

<img width="1837" height="927" alt="openMint" src="https://github.com/user-attachments/assets/7448a438-eb1e-48e9-9f3e-8a2a166f247a" />

## Quick Start

If you don't have UV package manager, install UV first:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Then, install the dependencies for the project and launch the dashboard!

```bash
# 1. Install dependencies
uv sync

# 2. Place your CSV transaction files in data/input/
cp /path/to/your/*.csv data/input/

# 3. Consolidate transactions
uv run python scripts/concatenate_transactions.py

# 4. Launch dashboard
./run_dashboard.sh
```

Open your browser to `http://localhost:8501`

## Features

✨ **Interactive Dashboard** with dynamic filtering and visualizations  
📊 **Multi-card Support** - Primarily for Apple Card, Chase Sapphire, Chase Freedom, and Bilt  
🎯 **Smart Merchant Normalization** (Amazon variations → "Amazon")  
🚫 **Transaction Ignore List** for excluding specific charges  
📈 **Visual Analytics** with charts and graphs  
💾 **Export Capabilities** for filtered data  
🤖 **AI-Assisted Setup** - Use ChatGPT/Claude to format CSVs from other card providers  

## Project Structure

```
finance_analyzer/
├── data/
│   ├── input/              # Your CSV files go here
│   │   ├── example_*.csv   # Example files (auto-excluded with real data)
│   ├── processed/          # Generated consolidated data
│   └── config/             # App configuration
│       └── example_ignored_transactions.json  # Example format
├── src/                    # Main application code
├── scripts/                # Data processing scripts
├── docs/                   # Full documentation
└── pyproject.toml          # Project dependencies
```

**Note:** Example files (`example_apple.csv`, `example_chase.csv`, `example_bilt.csv`) are automatically excluded from processing when real transaction files are present. They're kept in the repository to demonstrate the expected CSV format.

## Documentation

See [`docs/README.md`](docs/README.md) for complete documentation including:
- Detailed installation instructions
- Feature guides
- Troubleshooting
- Advanced usage

**Using a different credit card?** See [`docs/AGENTS.md`](docs/AGENTS.md) for instructions on using AI to format your CSVs.

## Requirements

- Python 3.9+
- uv package manager

## Data Privacy

🔒 All processing happens locally on your machine. No data leaves your computer.

## License

MIT License
