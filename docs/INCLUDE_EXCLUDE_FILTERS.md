# Include/Exclude Filters Added ✅

## New Feature: Include or Exclude Categories and Merchants

I've upgraded the filtering system to give you much more flexibility with **Include** and **Exclude** modes!

## What Changed

### 🎯 Sidebar Filters (Global)

#### **Categories**
Now has 3 options:
1. **All Categories** - Show everything
2. **Include Specific** - Select only the categories you want to see
3. **Exclude Specific** - Hide specific categories (see everything else)

#### **Merchants**
Now has 3 options:
1. **All Merchants** - Show everything
2. **Include Specific** - Select only the merchants you want to see
3. **Exclude Specific** - Hide specific merchants (see everything else)
   - Default: Excludes "Payment/Transfer" (commonly excluded)

### 🔍 Transaction Table Filters

Both Category and Merchant filters now have radio buttons:
- **All** - No filtering
- **Include** - Multi-select specific items to show
- **Exclude** - Multi-select specific items to hide

## Use Cases

### Example 1: Exclude Rent from Analysis
**Goal**: See all spending except rent

1. Sidebar → Categories → "Exclude Specific"
2. Select "Rent"
3. All charts and tables now exclude rent transactions

### Example 2: Focus on Food & Groceries
**Goal**: Only see food-related spending

1. Sidebar → Categories → "Include Specific"
2. Select "Food & Drink" and "Groceries"
3. Dashboard shows only these categories

### Example 3: Hide Payment Transfers
**Goal**: Remove payment noise from merchant analysis

1. Sidebar → Merchants → "Exclude Specific"
2. Select "Payment/Transfer" (already selected by default)
3. Cleaner merchant visualizations

### Example 4: Track Specific Merchants
**Goal**: See only Amazon, Trader Joe's, and Safeway

1. Sidebar → Merchants → "Include Specific"
2. Select just those 3 merchants
3. Focus analysis on those stores

### Example 5: Exclude Small Merchants in Table
**Goal**: Hide merchants with few transactions

1. Open Transaction Details
2. Expand "Additional Filters"
3. Merchant Filter → "Exclude"
4. Select merchants to hide
5. Table updates without those merchants

## Benefits

### ✅ More Flexible
- **Include mode**: Focus on specific items
- **Exclude mode**: Remove noise or outliers
- **All mode**: See everything

### ✅ Better Defaults
- Exclude mode defaults to "Payment/Transfer" for merchants
- Include mode starts with all items selected
- Easy to toggle between modes

### ✅ Two-Level Control
- **Sidebar**: Affects all visualizations
- **Table filters**: Additional refinement on the table only

### ✅ Multi-Select Power
- Include/Exclude modes use multi-select
- Select multiple categories or merchants at once
- Much more powerful than single-selection dropdowns

## Common Workflows

### Analyzing True Expenses (Exclude Payments & Rent)
```
Sidebar:
- Transaction Type: Expense, Refund
- Categories → Exclude: Rent
- Merchants → Exclude: Payment/Transfer
```

### Focusing on Discretionary Spending
```
Sidebar:
- Categories → Include: Food & Drink, Shopping, Travel
- Remove Groceries and Bills
```

### Finding Problem Areas
```
Sidebar:
- Categories → Exclude: Rent (known expense)
- Sort transactions by Amount (High-Low)
- See what's eating your budget
```

### Merchant Comparison
```
Sidebar:
- Merchants → Include: [Your top 3-5 merchants]
- See head-to-head comparison in charts
```

## Dashboard Access

**Live at**: http://localhost:8501

**Refresh your browser** to see the new Include/Exclude filters!

## Technical Details

- Uses `~df.isin()` for exclusion (pandas negation)
- Maintains filter state independently between sidebar and table
- Include mode defaults to all items for convenience
- Exclude mode defaults to empty (or common excludes like Payment/Transfer)

