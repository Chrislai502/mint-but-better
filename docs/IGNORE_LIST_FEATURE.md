# Persistent Ignore List Feature ✅

## New Feature: Ignore Transactions

You can now permanently exclude specific transactions (like the Best Western charge) from all calculations. The ignore list persists across sessions in a file.

## How It Works

### 🗂️ Persistent Storage
- Ignored transactions are saved to `ignored_transactions.json`
- The file persists across dashboard sessions
- Unique transaction ID based on date, amount, description, and source
- Won't break if you reload your CSV data

### 📊 Where to Use It

#### **1. Transaction Details Section**

At the bottom of the Transaction Details section, you'll find:

**"🚫 Manage Ignored Transactions"** section with:
- Checkbox next to each transaction
- Select one or more transactions
- Click "🚫 Ignore Selected" button
- Transactions are immediately excluded and dashboard refreshes

**Visual Layout:**
```
☐ | Date | Description | Merchant | Category | Source | Amount
☐ | 02/06/2026 | BEST WESTERN UNIVERSIT | Best Western | Travel | Chase | $1,233.07
```

#### **2. Sidebar Management**

In the sidebar, you'll see:

**"🚫 Ignore List"** section showing:
- Count of ignored transactions
- Expandable "View & Manage Ignored" section
- Each ignored transaction with details
- "✓" button to remove from ignore list

### 🎯 Example: Ignoring Best Western Transaction

1. Go to **Transaction Details** section
2. Search for "Best Western" in search box
3. Check the box next to the transaction
4. Click "🚫 Ignore Selected"
5. Transaction disappears from all calculations immediately
6. Check sidebar → "🚫 Ignore List" → Shows "1 transaction(s) ignored"

### ✨ What Gets Excluded

When you ignore a transaction, it's **excluded from:**
- ✅ Total Expenses calculation
- ✅ All pie charts and bar graphs
- ✅ Monthly spending trends
- ✅ Category breakdowns
- ✅ Merchant analysis
- ✅ Transaction counts
- ✅ Every visualization and metric

### 🔄 Managing Ignored Transactions

**View Ignored:**
1. Sidebar → "🚫 Ignore List"
2. Click "View & Manage Ignored"
3. See all ignored transactions with details

**Remove from Ignore List:**
1. Click the "✓" button next to any ignored transaction
2. Transaction immediately returns to calculations
3. Dashboard refreshes automatically

### 📁 File Structure

**`ignored_transactions.json`** contains:
```json
{
  "a1b2c3d4...": {
    "date": "2026-02-06",
    "description": "BEST WESTERN UNIVERSIT",
    "merchant": "Best Western",
    "category": "Travel",
    "amount": -1233.07,
    "source": "Chase Sapphire Preferred",
    "ignored_at": "2026-02-16T16:50:00.000000"
  }
}
```

### 🛡️ Safety Features

1. **Unique IDs**: Transaction ID is a hash of date+amount+description+source
2. **Persistent**: Survives dashboard restarts
3. **Backup-friendly**: JSON file is human-readable
4. **Reversible**: Easy to un-ignore transactions
5. **Git-friendly**: JSON file can be version controlled

### 💡 Use Cases

**Business Expenses:**
- Ignore reimbursed expenses
- Example: "Paid for team dinner, will be reimbursed"

**Split Expenses:**
- Ignore amounts others will pay back
- Example: "Paid for group hotel, friends will Venmo me"

**One-time Unusual Expenses:**
- Exclude outliers from analysis
- Example: "Emergency car repair, not typical spending"

**Gifts/Special Occasions:**
- Exclude from regular budget analysis
- Example: "Wedding gift, not part of monthly budget"

## Dashboard Access

**Live at**: http://localhost:8501

**Files Created:**
- `ignore_list_manager.py` - Manager class
- `ignored_transactions.json` - Persistent storage (created on first ignore)

## Commands

**Check ignore list from terminal:**
```bash
cd /home/art-chris/testing/finance_analyzer
uv run python ignore_list_manager.py
```

**Clear all ignored (use with caution):**
```python
from ignore_list_manager import IgnoreListManager
m = IgnoreListManager()
m.clear_all()
```

## Tips

1. **Start with search**: Search for the transaction first to find it quickly
2. **Bulk ignore**: Select multiple transactions at once before clicking ignore
3. **Review regularly**: Check sidebar ignore list to remember what's excluded
4. **Document**: Add comments in the JSON file if needed for future reference
5. **Backup**: The JSON file is small, easy to back up or share

Refresh your browser to use the new feature! 🎉

