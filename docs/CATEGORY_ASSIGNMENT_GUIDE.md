# Category Assignment Tool - Quick Start Guide

## Overview

The category assignment tool helps you assign categories and merchants to transactions interactively. Transactions are sorted by **absolute amount (highest first)**, so you assign the most important transactions first.

## Statistics

Check data completeness:
```bash
uv run python assign_categories.py --stats
```

This shows:
- Total transactions
- Number of missing categories
- Number of missing/unknown merchants

## Assign Categories

Start the interactive category assignment:
```bash
uv run python assign_categories.py --categories
```

### Features:
- **Sorted by amount**: Highest transactions shown first
- **Auto-suggestions**: Type `auto` to get AI-suggested categories based on merchant/description
- **Create new categories**: Type `new:CategoryName` to create and assign a new category
- **Skip transactions**: Type `skip` to skip
- **Save & quit**: Type `quit` at any time to save progress

### Available Commands:
- **Number (1-N)**: Assign from list of existing categories
- **`new:CategoryName`**: Create a new category
- **`auto`**: Get automatic category suggestion
- **`skip`**: Skip this transaction
- **`quit`**: Save changes and exit

### Example Session:
```
Transaction #1
================================================================================
Date:        02/13/2026
Description: Payment Thank You-Mobile
Merchant:    Payment/Transfer
Amount:      $47.84
Source:      Chase Sapphire Preferred
Type:        Payment
Category:    [MISSING]
--------------------------------------------------------------------------------

Assign category [1/72]: auto
  → Suggested: Bills & Utilities
    Accept? (y/n): y
  ✓ Assigned: Bills & Utilities
```

## Assign Merchants

For transactions with missing or "Unknown" merchants:
```bash
uv run python assign_categories.py --merchants
```

This allows you to assign proper merchant names to transactions.

## Safety Features

- **Auto-backup**: Every time you save, a backup is created with timestamp
- **Incremental work**: You can quit and resume later
- **Preview before assign**: See all transaction details before deciding

## Tips

1. **Start with categories**: Most important to fix
2. **Use auto-suggest**: Saves time with AI suggestions
3. **Create categories as needed**: Don't force transactions into wrong categories
4. **Take breaks**: You can quit and resume anytime
5. **Check dashboard**: Refresh dashboard after assignments to see updated visualizations

## After Assignment

1. The tool saves changes to `all_transactions.csv`
2. A backup is created (e.g., `all_transactions.csv.backup.20260216_123456`)
3. Refresh your browser dashboard to see updated data
4. Run `--stats` again to verify completion

