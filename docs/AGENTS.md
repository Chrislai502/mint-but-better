# Working with AI Agents for Finance Analyzer

This guide shows how to use AI agents (like ChatGPT, Claude, or Cursor) to help prepare your credit card transaction data for use with Finance Analyzer.

## Supported Card Types

Finance Analyzer is **primarily built to support**:
- **Apple Card** transactions
- **Chase credit cards** (Sapphire Preferred, Freedom Unlimited, etc.)
- **Bilt Rewards Card**

For other credit card providers, you'll need to format your CSV files to match the expected format.

## Standard CSV Format

Finance Analyzer expects CSV files with these columns:

```csv
Transaction Date,Post Date,Description,Merchant,Category,Type,Amount,Memo
2026-02-15,2026-02-16,TRADER JOE'S #123,Trader Joe's,Groceries,Sale,-45.67,
2026-02-14,2026-02-15,AMAZON.COM*AB123,Amazon,Shopping,Sale,-89.99,
2026-02-10,2026-02-11,PAYMENT THANK YOU,Payment,Payment,Payment,250.00,
```

### Required Fields
- **Transaction Date**: Date of the transaction (YYYY-MM-DD or MM/DD/YYYY)
- **Post Date**: Date transaction posted
- **Description**: Full transaction description from your statement
- **Amount**: Transaction amount (negative for charges, positive for refunds/payments)
- **Type**: Transaction type (Sale, Payment, Return, etc.)

### Optional but Recommended Fields
- **Merchant**: Clean merchant name (can be extracted from Description)
- **Category**: Spending category (Groceries, Travel, etc.)
- **Memo**: Additional notes

## Using ChatGPT to Format Your CSV

If your credit card provides a different CSV format, you can use ChatGPT or similar AI to help convert it.

### Step 1: Download Your CSV

Download your transaction CSV from your credit card provider's website.

### Step 2: Prompt Template for ChatGPT

Use this prompt structure (customize for your needs):

```
I need to convert my credit card CSV to match this target format:
Transaction Date,Post Date,Description,Merchant,Category,Type,Amount,Memo

My current CSV has these columns:
[paste your column headers here]

Here's a sample of my data:
[paste 5-10 sample rows]

Please:
1. Create a Python script or provide instructions to convert my CSV to the target format
2. Extract merchant names from the Description field if there's no Merchant column
3. Set Category to empty (blank) if not present - I'll assign them later
4. Map transaction types appropriately (purchases should be "Sale", payments should be "Payment", refunds should be "Return")
5. Ensure amounts are negative for purchases and positive for refunds/payments
6. Handle any date format conversions needed
```

### Step 3: Example Conversion Scenarios

#### Scenario 1: Basic CSV with Minimal Fields

**Your CSV:**
```csv
Date,Description,Amount
01/15/2026,STARBUCKS #12345,-5.67
01/14/2026,WAL-MART SUPERCENTER,-123.45
```

**What to ask AI:**
```
My CSV only has Date, Description, and Amount. Please create a conversion script that:
- Uses Date for both Transaction Date and Post Date
- Extracts merchant name from Description
- Sets Type to "Sale" for negative amounts and "Return" for positive amounts
- Leaves Category and Memo blank
```

#### Scenario 2: Different Column Names

**Your CSV:**
```csv
Purchase Date,Posting Date,Merchant Name,Transaction Type,Amount USD
02/15/2026,02/16/2026,Amazon.com,Debit,-89.99
```

**What to ask AI:**
```
My CSV has different column names. Please create a mapping:
- "Purchase Date" → "Transaction Date"
- "Posting Date" → "Post Date"  
- "Merchant Name" → both "Description" and "Merchant"
- "Transaction Type" should map: Debit→Sale, Credit→Return, Payment→Payment
- Keep Amount as is
- Add empty Category and Memo columns
```

#### Scenario 3: Foreign Currency or Different Format

**Your CSV:**
```csv
txn_date;description;debit;credit;currency
15.02.2026;GROCERY STORE;45.67;;EUR
```

**What to ask AI:**
```
My CSV uses semicolons, European date format, and has separate debit/credit columns. Please:
- Convert semicolons to commas
- Convert date from DD.MM.YYYY to MM/DD/YYYY
- Merge debit/credit into single Amount column (debit negative, credit positive)
- Extract merchant from description
- Add Type based on amount sign
- Note: Keep currency as is, I'll handle conversion separately
```

### Step 4: Common Python Script Pattern

ChatGPT will typically generate something like this:

```python
import csv
from datetime import datetime

def convert_csv(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        
        fieldnames = ['Transaction Date', 'Post Date', 'Description', 'Merchant', 
                      'Category', 'Type', 'Amount', 'Memo']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            # Custom conversion logic here
            new_row = {
                'Transaction Date': convert_date(row['Date']),
                'Post Date': convert_date(row['Date']),
                'Description': row['Description'],
                'Merchant': extract_merchant(row['Description']),
                'Category': '',  # Leave blank
                'Type': 'Sale' if float(row['Amount']) < 0 else 'Return',
                'Amount': row['Amount'],
                'Memo': ''
            }
            writer.writerow(new_row)

def convert_date(date_str):
    # Add date conversion logic
    return datetime.strptime(date_str, '%m/%d/%Y').strftime('%Y-%m-%d')

def extract_merchant(description):
    # Simple extraction - you can make this more sophisticated
    return description.split()[0]

if __name__ == '__main__':
    convert_csv('my_transactions.csv', 'converted_transactions.csv')
```

## Adding Transaction Categories

If your CSV doesn't have categories, you can either:

### Option 1: Let Finance Analyzer Handle It
1. Leave the Category column blank
2. Run the concatenation script
3. Use the built-in category assignment tool:
   ```bash
   uv run python scripts/assign_categories.py
   ```

### Option 2: Use AI to Pre-populate Categories

**Prompt for ChatGPT:**
```
I have a CSV with transaction descriptions. Please add a Category column with appropriate categories.

Use these categories:
- Groceries
- Dining
- Travel
- Shopping
- Entertainment
- Utilities
- Gas/Fuel
- Healthcare
- Transportation
- Other

Here's my data:
[paste your CSV]

Please analyze each transaction description and assign the most appropriate category.
```

## Example Workflow with Cursor AI

Since you're already using Cursor, here's how to use it:

1. **Open your CSV in Cursor**
2. **Select the data** and ask Cursor:
   ```
   @data/input/my_card.csv
   
   Please convert this CSV to match the Finance Analyzer format:
   - Target columns: Transaction Date, Post Date, Description, Merchant, Category, Type, Amount, Memo
   - Extract merchant names from descriptions
   - Assign appropriate categories based on merchant
   - Map transaction types appropriately
   - Save to data/input/my_card_formatted.csv
   ```

3. **Cursor will generate and run the conversion** directly in your workspace

## Tips for Best Results

### When Prompting AI:

1. **Provide Examples**: Show 5-10 actual rows from your CSV
2. **Be Specific**: Clearly state what transformations are needed
3. **Mention Edge Cases**: Point out any unusual transactions (refunds, payments, etc.)
4. **Ask for Validation**: Request the AI to show before/after samples

### Common Issues and Solutions:

**Issue: Merchant names are messy**
```
Ask AI: "Please clean merchant names by removing location codes, 
transaction IDs, and standardizing formats"
```

**Issue: Dates in wrong format**
```
Ask AI: "Convert all dates from [current format] to YYYY-MM-DD format"
```

**Issue: Mixed positive/negative signs**
```
Ask AI: "Ensure all purchases are negative and all refunds/payments are positive"
```

**Issue: Multiple files to process**
```
Ask AI: "Create a script that processes all CSVs in a folder with the same logic"
```

## Validation Checklist

After converting your CSV, verify:
- [ ] All required columns are present
- [ ] Dates are in consistent format (YYYY-MM-DD or MM/DD/YYYY)
- [ ] Amounts have correct signs (purchases negative)
- [ ] No extra quotes or special characters
- [ ] File is saved in `data/input/` directory
- [ ] File has `.csv` extension

## Testing Your Converted CSV

1. Place your formatted CSV in `data/input/`
2. Run the concatenation script:
   ```bash
   uv run python scripts/concatenate_transactions.py
   ```
3. Check for errors in the output
4. If successful, launch the dashboard:
   ```bash
   ./run_dashboard.sh
   ```

## Need Help?

If you run into issues:

1. **Check the example files** in `data/input/` for reference format
2. **Ask the AI** to debug specific error messages
3. **Share sample data** (with sensitive info removed) in your prompt
4. **Use the category assignment tool** for missing categories

## Advanced: Automating Monthly Downloads

You can create a script to automatically download and format new transactions:

**Prompt for ChatGPT:**
```
Please create a Python script that:
1. Watches a "downloads" folder for new CSV files from [Your Bank]
2. Automatically converts them to Finance Analyzer format
3. Moves them to data/input/
4. Runs the concatenation script
5. Logs any errors

The script should run monthly and handle [specific requirements].
```

---

**Remember**: AI tools are assistants - always verify the converted data looks correct before using it in your financial analysis!

