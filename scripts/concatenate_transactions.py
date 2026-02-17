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

def load_chase_file(filepath, source_name):
    """Load a Chase CSV file (chase_sapphire_preferred, chase_freedom_unlimited, bilt)."""
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['Source'] = source_name
            # Add/normalize merchant from description
            if 'Merchant' not in row or not row.get('Merchant'):
                row['Merchant'] = row.get('Description', '')
            row['Normalized Merchant'] = normalize_merchant(row.get('Merchant', ''))
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
            new_row = {
                'Transaction Date': row.get('Transaction Date', ''),
                'Post Date': row.get('Clearing Date', ''),
                'Description': row.get('Description', ''),
                'Merchant': merchant,
                'Normalized Merchant': normalize_merchant(merchant),
                'Category': row.get('Category', ''),
                'Type': row.get('Type', ''),
                'Amount': row.get('Amount (USD)', ''),
                'Memo': '',
                'Source': source_name
            }
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
    csv_files = list(data_path.glob('*.csv')) + list(data_path.glob('*.CSV'))
    
    if not csv_files:
        raise ValueError(f"No CSV files found in {data_path}")
    
    print(f"Found {len(csv_files)} CSV file(s) to process:")
    
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
