#!/bin/bash
# Run the Finance Analyzer Dashboard

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run the dashboard
uv run streamlit run src/dashboard.py --server.headless true
