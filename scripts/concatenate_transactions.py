#!/usr/bin/env python3
"""
Script to concatenate all transaction CSV files from data/input/ directory
and add a Source column identifying which card each transaction came from.
"""

import csv
import os
import re
from pathlib import Path
from datetime import datetime

# Get the project root directory (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent

# Directory containing the CSV files
DATA_DIR = PROJECT_ROOT / 'data' / 'input'
OUTPUT_FILE = PROJECT_ROOT / 'data' / 'processed' / 'all_transactions.csv'

# List of example files that should be excluded when real data exists
EXAMPLE_FILES = [
    'example_apple.csv',
    'example_chase.csv',
    'example_bilt.csv'
]

# Note: example_ignored_transactions.json is stored separately in data/config/
# It provides an example format for the ignored transactions feature

def normalize_merchant(merchant):
    """
    Normalize merchant names by consolidating common variations.
    For example, all Amazon variations become "Amazon".
    """
    if not merchant or pd_isna(merchant):
        return "Unknown"
    
    merchant_upper = merchant.upper().strip()
    
    # Define merchant mappings (patterns -> normalized name)
    merchant_patterns = [
        (r'AMAZON|AMZN', 'Amazon'),
        (r'TRADER\s*JOE', 'Trader Joe\'s'),
        (r'SAFEWAY', 'Safeway'),
        (r'TARGET', 'Target'),
        (r'WALMART|WM\s*SUPERCENTER', 'Walmart'),
        (r'UBER', 'Uber'),
        (r'LYFT', 'Lyft'),
        (r'STARBUCKS', 'Starbucks'),
        (r'MCDONALD', 'McDonald\'s'),
        (r'WHOLE\s*FOODS|WHOLEFDS', 'Whole Foods'),
        (r'H\s*MART|HMART', 'H Mart'),
        (r'BILTPROTECT\s*RENT|BPS\*BILT\s*RENT', 'Bilt Rent Payment'),
        (r'LEMONADE\s*INSURANCE', 'Lemonade Insurance'),
        (r'SOUTHWEST|SOUTHWES', 'Southwest Airlines'),
        (r'DELTA\s*AIR', 'Delta Airlines'),
        (r'ALASKA\s*AIR', 'Alaska Airlines'),
        (r'AIRASIA', 'AirAsia'),
        (r'CATHAYPACAIR', 'Cathay Pacific'),
        (r'UNIQLO', 'Uniqlo'),
        (r'PAYMENT\s*THANK\s*YOU|ONLINE\s*ACH\s*PAYMENT|ACH\s*DEPOSIT', 'Payment/Transfer'),
        (r'TST\*.*IVARS|IVARS', 'Ivar\'s'),
        (r'TST\*.*SIZZLE.*CRUNCH|SIZZLE.*CRUNCH', 'Sizzle & Crunch'),
        (r'TST\*.*DONT\s*YELL|DONT\s*YELL', 'Don\'t Yell At Me'),
        (r'LEE.*S\s*KITCHEN', 'Lee\'s Kitchen'),
        (r'FOB\s*SUSHI|FOB\s*POKE', 'FOB'),
        (r'CHASE|Payment Thank You', 'Payment/Transfer'),
        (r'7-ELEVEN|7\s*ELEVEN|FAMILYMART|FAMILY\s*MART', '7-Eleven/FamilyMart'),
        (r'KFC', 'KFC'),
        (r'BURGER\s*KING', 'Burger King'),
        (r'CHICK-FIL-A|CHICKFILA', 'Chick-fil-A'),
        (r'ALADDIN', 'Aladdin'),
        (r'TASTE\s*OF\s*XI.*AN', 'Taste of Xi\'an'),
        (r'TAIWAN\s*PORRIDGE', 'Taiwan Porridge'),
        (r'CHA\s*YAN', 'Cha Yan'),
        (r'SL\.NORD|NORD.*VPN', 'NordVPN'),
        (r'NOW\s*WIFI', 'NOW WiFi'),
        (r'APPLE\s*ONLINE|AOS', 'Apple'),
    ]
    
    # Try to match patterns
    for pattern, normalized_name in merchant_patterns:
        if re.search(pattern, merchant_upper):
            return normalized_name
    
    # If no pattern matches, clean up the merchant name
    # Remove common prefixes
    merchant_clean = re.sub(r'^(TST\*|SQ\s*\*|BB\*|UEP\*|SP\s+)', '', merchant, flags=re.IGNORECASE)
    
    # Remove location info (city, state, zip, address numbers)
    merchant_clean = re.sub(r'\s+\d+.*$', '', merchant_clean)  # Remove everything after numbers
    merchant_clean = re.sub(r'\s+[A-Z]{2}\s+USA$', '', merchant_clean)  # Remove state + USA
    merchant_clean = re.sub(r'\s+\d{5}(-\d{4})?\s*$', '', merchant_clean)  # Remove ZIP codes
    
    # Limit length
    merchant_clean = merchant_clean.strip()
    if len(merchant_clean) > 50:
        merchant_clean = merchant_clean[:50]
    
    return merchant_clean if merchant_clean else merchant[:50]

def pd_isna(value):
    """Simple check for None, empty string, or 'nan'."""
    return value is None or value == '' or str(value).lower() == 'nan'

def extract_card_name(filename):
    """Extract card name from filename, removing extension and cleaning up."""
    name = os.path.splitext(filename)[0]
    # Replace underscores with spaces and title case
    name = name.replace('_', ' ').title()
    return name

def parse_date(date_str):
    """Parse date string to datetime for sorting."""
    try:
        return datetime.strptime(date_str, '%m/%d/%Y')
    except:
        return datetime.min

def auto_assign_category(row):
    """
    Automatically assign category based on transaction type and description.
    This reduces manual category assignment work.
    """
    # If category already exists and is not empty, keep it
    if row.get('Category') and row['Category'].strip():
        return row['Category']
    
    transaction_type = str(row.get('Type', '')).strip().lower()
    description = str(row.get('Description', '')).upper()
    
    # Auto-assign based on transaction type
    if transaction_type == 'payment':
        return 'Payment'
    elif transaction_type == 'return':
        return 'Refund'
    
    # Auto-assign based on description patterns
    if 'PAYMENT' in description or 'ACH DEPOSIT' in description or 'ACH CREDIT' in description:
        return 'Payment'
    
    # Rent payments
    if 'BILT RENT' in description or 'BILTPROTECT RENT' in description:
        return 'Rent'
    
    # Insurance
    if 'INSURANCE' in description:
        return 'Insurance'
    
    # Daily cash redemption (Apple Card)
    if 'DAILY CASH REDEMPTION' in description:
        return 'Payment'
    
    # If no pattern matches, leave empty for manual assignment
    return ''

def load_chase_file(filepath, source_name):
    """Load a Chase CSV file (chase_sapphire_preferred, chase_freedom_unlimited, bilt)."""
    rows = []
    is_bilt = 'bilt' in filepath.name.lower()
    is_chase = any(x in filepath.name.lower() for x in ['chase', 'sapphire', 'freedom'])
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['Source'] = source_name
            # Add/normalize merchant from description
            if 'Merchant' not in row or not row.get('Merchant'):
                row['Merchant'] = row.get('Description', '')
            row['Normalized Merchant'] = normalize_merchant(row.get('Merchant', ''))
            
            # Auto-assign category if possible
            row['Category'] = auto_assign_category(row)
            
            # Normalize amount signs to standard convention:
            # Standard: Positive = Expenses, Negative = Refunds/Payments
            # - Apple: Already follows this (positive = expenses)
            # - Bilt: Already flipped in previous update (positive = expenses)
            # - Chase: Uses opposite (negative = expenses), need to flip
            if is_chase:
                # For Chase: flip the sign so expenses become positive
                amount = float(row.get('Amount', 0))
                row['Amount'] = str(-amount)
            elif is_bilt:
                # Bilt: Already flipped previously, keep the flip
                amount = float(row.get('Amount', 0))
                row['Amount'] = str(-amount)
            
            rows.append(row)
    return rows

def load_apple_file(filepath, source_name):
    """Load an Apple CSV file with different column structure."""
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Map Apple columns to standard format
            # Apple: Transaction Date, Clearing Date, Description, Merchant, Category, Type, Amount (USD), Purchased By
            # Standard: Transaction Date, Post Date, Description, Merchant, Category, Type, Amount, Memo
            
            merchant = row.get('Merchant', row.get('Description', ''))
            
            # Apple already uses the standard convention (positive = expenses, negative = refunds)
            # No sign normalization needed
            amount = row.get('Amount (USD)', '0')
            
            new_row = {
                'Transaction Date': row.get('Transaction Date', ''),
                'Post Date': row.get('Clearing Date', ''),
                'Description': row.get('Description', ''),
                'Merchant': merchant,
                'Normalized Merchant': normalize_merchant(merchant),
                'Category': row.get('Category', ''),
                'Type': row.get('Type', ''),
                'Amount': amount,
                'Memo': '',
                'Source': source_name
            }
            
            # Auto-assign category if missing
            new_row['Category'] = auto_assign_category(new_row)
            
            rows.append(new_row)
    return rows

def concatenate_transactions(data_dir=None, output_file=None):
    """
    Concatenate all CSV transaction files from data_dir and save to output_file.
    
    Args:
        data_dir: Directory containing CSV files (default: PROJECT_ROOT/data/input)
        output_file: Output filename for concatenated transactions (default: PROJECT_ROOT/data/processed/all_transactions.csv)
    """
    if data_dir is None:
        data_path = DATA_DIR
    else:
        data_path = Path(data_dir)
    
    if output_file is None:
        output_path = OUTPUT_FILE
    else:
        output_path = Path(output_file)
    
    if not data_path.exists():
        raise FileNotFoundError(f"Directory {data_path} not found")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    all_rows = []
    
    # Get all CSV files in the directory
    all_csv_files = list(data_path.glob('*.csv')) + list(data_path.glob('*.CSV'))
    
    if not all_csv_files:
        raise ValueError(f"No CSV files found in {data_path}")
    
    # Check if there are any real (non-example) data files
    real_files = [f for f in all_csv_files if f.name not in EXAMPLE_FILES]
    
    # If real files exist, exclude example files; otherwise use example files
    if real_files:
        csv_files = real_files
        print(f"\n✓ Found {len(real_files)} real data file(s) - excluding {len([f for f in all_csv_files if f.name in EXAMPLE_FILES])} example file(s)")
    else:
        csv_files = all_csv_files
        print(f"\n⚠ No real data files found - using {len(csv_files)} example file(s) for demonstration")
    
    print(f"\nProcessing {len(csv_files)} CSV file(s):")
    
    for csv_file in csv_files:
        source_name = extract_card_name(csv_file.name)
        print(f"  - Processing {csv_file.name} -> Source: {source_name}")
        
        # Determine file type based on filename
        filename_lower = csv_file.name.lower()
        
        if 'apple' in filename_lower:
            rows = load_apple_file(csv_file, source_name)
        else:
            # Assume Chase format for others (chase_sapphire_preferred, chase_freedom_unlimited, bilt)
            rows = load_chase_file(csv_file, source_name)
        
        all_rows.extend(rows)
        print(f"    Loaded {len(rows)} transactions")
    
    # Sort by Transaction Date (most recent first)
    print("\nSorting transactions by date...")
    all_rows.sort(key=lambda x: parse_date(x.get('Transaction Date', '')), reverse=True)
    
    # Get all unique column names
    all_columns = set()
    for row in all_rows:
        all_columns.update(row.keys())
    
    # Define column order: Source first, then standard order
    standard_columns = ['Transaction Date', 'Post Date', 'Description', 'Merchant', 'Normalized Merchant', 'Category', 'Type', 'Amount', 'Memo']
    column_order = ['Source'] + [col for col in standard_columns if col in all_columns]
    # Add any remaining columns
    for col in sorted(all_columns):
        if col not in column_order:
            column_order.append(col)
    
    # Write to output file
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=column_order)
        writer.writeheader()
        writer.writerows(all_rows)
    
    # Count by source
    source_counts = {}
    for row in all_rows:
        source = row.get('Source', 'Unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    print(f"\n✓ Successfully concatenated {len(all_rows)} transactions")
    print(f"✓ Saved to {output_path.absolute()}")
    print(f"\nBreakdown by source:")
    for source, count in sorted(source_counts.items()):
        print(f"  {source}: {count} transactions")
    
    return all_rows

if __name__ == '__main__':
    concatenate_transactions()
