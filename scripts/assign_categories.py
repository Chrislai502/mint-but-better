#!/usr/bin/env python3
"""
Category Assignment Tool
Interactive tool to assign categories to transactions that are missing them.
Transactions are sorted by absolute amount (highest first).
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Get the project root directory (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_CSV = PROJECT_ROOT / 'data' / 'processed' / 'all_transactions.csv'

class CategoryAssigner:
    def __init__(self, csv_file=None):
        if csv_file is None:
            csv_file = DEFAULT_CSV
        else:
            csv_file = Path(csv_file)
        
        if not csv_file.exists():
            raise FileNotFoundError(
                f"Transaction file not found: {csv_file}\n\n"
                f"Please run 'uv run python scripts/concatenate_transactions.py' first to generate the file."
            )
        
        self.csv_file = csv_file
        self.df = pd.read_csv(csv_file)
        self.changes_made = False
        
        # Available categories (from existing data)
        self.available_categories = sorted([
            cat for cat in self.df['Category'].unique() 
            if pd.notna(cat) and cat != ''
        ])
        self.available_categories.append('Other')
        
    def get_missing_category_transactions(self):
        """Get transactions with missing categories, sorted by absolute amount."""
        missing = self.df[self.df['Category'].isna() | (self.df['Category'] == '')].copy()
        missing['Absolute Amount'] = missing['Amount'].abs()
        missing = missing.sort_values('Absolute Amount', ascending=False)
        return missing
    
    def get_missing_merchant_transactions(self):
        """Get transactions with missing/unknown merchants, sorted by absolute amount."""
        missing = self.df[
            self.df['Normalized Merchant'].isna() | 
            (self.df['Normalized Merchant'] == '') |
            (self.df['Normalized Merchant'] == 'Unknown')
        ].copy()
        missing['Absolute Amount'] = missing['Amount'].abs()
        missing = missing.sort_values('Absolute Amount', ascending=False)
        return missing
    
    def display_transaction(self, row, index):
        """Display a transaction's details."""
        print("\n" + "="*80)
        print(f"Transaction #{index + 1}")
        print("="*80)
        print(f"Date:        {row['Transaction Date']}")
        print(f"Description: {row['Description']}")
        print(f"Merchant:    {row['Normalized Merchant']}")
        print(f"Amount:      ${row['Amount']:,.2f}")
        print(f"Source:      {row['Source']}")
        print(f"Type:        {row['Type']}")
        if pd.notna(row.get('Category')) and row.get('Category') != '':
            print(f"Category:    {row['Category']} (current)")
        else:
            print(f"Category:    [MISSING]")
        print("-"*80)
    
    def assign_categories(self):
        """Interactive category assignment for missing categories."""
        missing = self.get_missing_category_transactions()
        
        if len(missing) == 0:
            print("\n✓ All transactions have categories assigned!")
            return
        
        print(f"\n{'='*80}")
        print(f"CATEGORY ASSIGNMENT TOOL")
        print(f"{'='*80}")
        print(f"Found {len(missing)} transactions without categories")
        print(f"Transactions sorted by amount (highest first)\n")
        
        print("Available categories:")
        for i, cat in enumerate(self.available_categories, 1):
            print(f"  {i}. {cat}")
        print("\nCommands:")
        print("  - Enter category number to assign")
        print("  - Type 'new:CategoryName' to create a new category")
        print("  - Type 'skip' to skip this transaction")
        print("  - Type 'quit' to save and exit")
        print("  - Type 'auto' to suggest categories based on merchant")
        
        for idx, (_, row) in enumerate(missing.iterrows()):
            self.display_transaction(row, idx)
            
            while True:
                choice = input(f"\nAssign category [{idx+1}/{len(missing)}]: ").strip()
                
                if choice.lower() == 'quit':
                    self._save_changes()
                    return
                
                if choice.lower() == 'skip':
                    break
                
                if choice.lower() == 'auto':
                    suggested = self._suggest_category(row)
                    if suggested:
                        print(f"  → Suggested: {suggested}")
                        confirm = input(f"    Accept? (y/n): ").strip().lower()
                        if confirm == 'y':
                            self._update_category(row.name, suggested)
                            print(f"  ✓ Assigned: {suggested}")
                            break
                    else:
                        print("  → No suggestion available")
                    continue
                
                if choice.lower().startswith('new:'):
                    new_category = choice[4:].strip()
                    if new_category:
                        if new_category not in self.available_categories:
                            self.available_categories.append(new_category)
                            self.available_categories.sort()
                        self._update_category(row.name, new_category)
                        print(f"  ✓ Created and assigned: {new_category}")
                        break
                    else:
                        print("  ✗ Invalid category name")
                        continue
                
                try:
                    cat_idx = int(choice) - 1
                    if 0 <= cat_idx < len(self.available_categories):
                        category = self.available_categories[cat_idx]
                        self._update_category(row.name, category)
                        print(f"  ✓ Assigned: {category}")
                        break
                    else:
                        print(f"  ✗ Please enter a number between 1 and {len(self.available_categories)}")
                except ValueError:
                    print("  ✗ Invalid input. Enter a number, 'new:CategoryName', 'skip', 'auto', or 'quit'")
        
        self._save_changes()
    
    def assign_merchants(self):
        """Interactive merchant assignment for missing/unknown merchants."""
        missing = self.get_missing_merchant_transactions()
        
        if len(missing) == 0:
            print("\n✓ All transactions have valid merchants!")
            return
        
        print(f"\n{'='*80}")
        print(f"MERCHANT ASSIGNMENT TOOL")
        print(f"{'='*80}")
        print(f"Found {len(missing)} transactions with missing/unknown merchants")
        print(f"Transactions sorted by amount (highest first)\n")
        
        print("Commands:")
        print("  - Type merchant name to assign")
        print("  - Type 'skip' to skip this transaction")
        print("  - Type 'quit' to save and exit")
        
        for idx, (_, row) in enumerate(missing.iterrows()):
            self.display_transaction(row, idx)
            
            # Try to extract merchant from description
            suggested = self._extract_merchant_from_description(row['Description'])
            if suggested:
                print(f"  → Suggested from description: {suggested}")
            
            while True:
                choice = input(f"\nAssign merchant [{idx+1}/{len(missing)}]: ").strip()
                
                if choice.lower() == 'quit':
                    self._save_changes()
                    return
                
                if choice.lower() == 'skip':
                    break
                
                if choice:
                    self._update_merchant(row.name, choice)
                    print(f"  ✓ Assigned merchant: {choice}")
                    break
                else:
                    print("  ✗ Please enter a merchant name")
        
        self._save_changes()
    
    def _suggest_category(self, row):
        """Suggest a category based on merchant and description."""
        merchant = str(row.get('Normalized Merchant', '')).lower()
        desc = str(row.get('Description', '')).lower()
        
        # Category keywords
        category_keywords = {
            'Rent': ['rent', 'bilt rent', 'biltprotect'],
            'Groceries': ['trader joe', 'safeway', 'whole foods', 'h mart', 'walmart', 'target', 'grocery', 'market'],
            'Food & Drink': ['restaurant', 'cafe', 'coffee', 'sushi', 'pizza', 'burger', 'bar', 'starbucks', 'mcdonald'],
            'Travel': ['airline', 'southwest', 'delta', 'alaska', 'uber', 'lyft', 'hotel', 'airbnb'],
            'Shopping': ['amazon', 'uniqlo', 'mall', 'store'],
            'Bills & Utilities': ['insurance', 'wifi', 'internet', 'utility', 'lemonade'],
        }
        
        text = f"{merchant} {desc}"
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return None
    
    def _extract_merchant_from_description(self, description):
        """Extract a clean merchant name from description."""
        import re
        desc = str(description).strip()
        # Remove common prefixes
        desc = re.sub(r'^(TST\*|SQ\s*\*|BB\*|UEP\*|SP\s+)', '', desc, flags=re.IGNORECASE)
        # Take first part before location info
        parts = desc.split()
        if len(parts) > 0:
            return ' '.join(parts[:3])  # Take first 3 words
        return None
    
    def _update_category(self, index, category):
        """Update category for a transaction."""
        self.df.at[index, 'Category'] = category
        self.changes_made = True
    
    def _update_merchant(self, index, merchant):
        """Update normalized merchant for a transaction."""
        self.df.at[index, 'Normalized Merchant'] = merchant
        self.changes_made = True
    
    def _save_changes(self):
        """Save changes to CSV file."""
        if self.changes_made:
            # Save updated file directly (no backup needed since file is generated on-the-fly)
            self.df.to_csv(self.csv_file, index=False)
            print(f"\n✓ Changes saved to: {self.csv_file}")
        else:
            print("\nℹ️  No changes made")
    
    def show_stats(self):
        """Show statistics about missing data."""
        print(f"\n{'='*80}")
        print("DATA COMPLETENESS STATISTICS")
        print(f"{'='*80}")
        print(f"Total transactions: {len(self.df)}")
        
        missing_cat = self.df['Category'].isna().sum() + (self.df['Category'] == '').sum()
        missing_merchant = (
            self.df['Normalized Merchant'].isna().sum() + 
            (self.df['Normalized Merchant'] == '').sum() +
            (self.df['Normalized Merchant'] == 'Unknown').sum()
        )
        
        print(f"\nMissing Categories: {missing_cat} ({missing_cat/len(self.df)*100:.1f}%)")
        print(f"Missing/Unknown Merchants: {missing_merchant} ({missing_merchant/len(self.df)*100:.1f}%)")
        
        if missing_cat > 0 or missing_merchant > 0:
            print("\nTo fix:")
            if missing_cat > 0:
                print("  - Run: uv run python assign_categories.py --categories")
            if missing_merchant > 0:
                print("  - Run: uv run python assign_categories.py --merchants")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Assign categories and merchants to transactions')
    parser.add_argument('--categories', action='store_true', help='Assign missing categories')
    parser.add_argument('--merchants', action='store_true', help='Assign missing merchants')
    parser.add_argument('--stats', action='store_true', help='Show statistics only')
    parser.add_argument('--file', default=None, help='CSV file to process (default: data/processed/all_transactions.csv)')
    
    args = parser.parse_args()
    
    try:
        assigner = CategoryAssigner(args.file)
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        return 1
    
    if args.stats or (not args.categories and not args.merchants):
        assigner.show_stats()
        if not args.stats:
            print("\nUse --categories or --merchants to start assignment")
        return
    
    if args.categories:
        assigner.assign_categories()
    
    if args.merchants:
        assigner.assign_merchants()

if __name__ == '__main__':
    main()

