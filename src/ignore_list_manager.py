#!/usr/bin/env python3
"""
Ignore List Manager
Manages a persistent list of transactions to exclude from all calculations.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

# Get the project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent

class IgnoreListManager:
    def __init__(self, ignore_file=None):
        if ignore_file is None:
            ignore_file = PROJECT_ROOT / 'data' / 'config' / 'ignored_transactions.json'
        self.ignore_file = Path(ignore_file)
        self.ignored_transactions = self._load_ignore_list()
    
    def _load_ignore_list(self):
        """Load the ignore list from JSON file."""
        if self.ignore_file.exists():
            try:
                with open(self.ignore_file, 'r') as f:
                    data = json.load(f)
                    
                    # Handle legacy format (list) - convert to dict
                    if isinstance(data, list):
                        converted = {}
                        for item in data:
                            # Use existing id or generate new one
                            if 'id' in item:
                                tid = item['id']
                            else:
                                # Generate from transaction details
                                key_string = f"{item.get('date', '')}|{item.get('amount', 0)}|{item.get('description', '')}|{item.get('source', '')}"
                                tid = hashlib.md5(key_string.encode()).hexdigest()
                            
                            converted[tid] = {
                                'date': item.get('date', ''),
                                'description': item.get('description', ''),
                                'merchant': item.get('merchant', ''),
                                'category': item.get('category', ''),
                                'amount': float(item.get('amount', 0)),
                                'source': item.get('source', ''),
                                'ignored_at': item.get('ignored_at', item.get('ignored_on', datetime.now().isoformat()))
                            }
                        # Save converted format
                        self.ignored_transactions = converted
                        self._save_ignore_list()
                        return converted
                    
                    # Already in dict format
                    return data
            except Exception as e:
                print(f"Error loading ignore list: {e}")
                return {}
        return {}
    
    def _save_ignore_list(self):
        """Save the ignore list to JSON file."""
        try:
            with open(self.ignore_file, 'w') as f:
                json.dump(self.ignored_transactions, f, indent=2)
        except Exception as e:
            print(f"Error saving ignore list: {e}")
    
    def _generate_transaction_id(self, row):
        """
        Generate a unique ID for a transaction based on its key attributes.
        This creates a consistent ID even if the data is reloaded.
        """
        # Use date, amount, description, and source to create a unique hash
        key_string = f"{row['Transaction Date']}|{row['Amount']}|{row['Description']}|{row['Source']}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def add_transaction(self, row):
        """Add a transaction to the ignore list."""
        transaction_id = self._generate_transaction_id(row)
        
        if transaction_id not in self.ignored_transactions:
            self.ignored_transactions[transaction_id] = {
                'date': str(row['Transaction Date']),
                'description': row['Description'],
                'merchant': row.get('Normalized Merchant', ''),
                'category': row.get('Category', ''),
                'amount': float(row['Amount']),
                'source': row['Source'],
                'ignored_at': datetime.now().isoformat()
            }
            self._save_ignore_list()
            return True
        return False
    
    def remove_transaction(self, transaction_id):
        """Remove a transaction from the ignore list."""
        if transaction_id in self.ignored_transactions:
            del self.ignored_transactions[transaction_id]
            self._save_ignore_list()
            return True
        return False
    
    def is_ignored(self, row):
        """Check if a transaction should be ignored."""
        transaction_id = self._generate_transaction_id(row)
        return transaction_id in self.ignored_transactions
    
    def get_all_ignored(self):
        """Get all ignored transactions with their IDs."""
        return [
            {'id': tid, **details}
            for tid, details in self.ignored_transactions.items()
        ]
    
    def get_count(self):
        """Get the count of ignored transactions."""
        return len(self.ignored_transactions)
    
    def clear_all(self):
        """Clear all ignored transactions (use with caution)."""
        self.ignored_transactions = {}
        self._save_ignore_list()

if __name__ == '__main__':
    # Test the ignore list manager
    manager = IgnoreListManager()
    print(f"Current ignored transactions: {manager.get_count()}")
    
    # Show all ignored
    for ignored in manager.get_all_ignored():
        print(f"- {ignored['date']}: {ignored['description']} (${ignored['amount']:.2f})")

