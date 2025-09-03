"""JSON file-based repository implementation."""

import json
import os
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from .data_repository import DataRepository
from ..models.transaction import Transaction
from ..models.category import Category, DEFAULT_CATEGORIES


class JSONRepository(DataRepository):
    """JSON file-based implementation of DataRepository."""
    
    def __init__(self, data_file_path: str = "expense_data.json"):
        """Initialize the JSON repository.
        
        Args:
            data_file_path: Path to the JSON data file
        """
        self.data_file_path = Path(data_file_path)
        self.backup_dir = self.data_file_path.parent / "backups"
        self._data = None
        self._load_data()
    
    def _load_data(self) -> None:
        """Load data from JSON file."""
        try:
            if self.data_file_path.exists():
                with open(self.data_file_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                    
                # Validate data structure
                if not isinstance(self._data, dict):
                    raise ValueError("Invalid data format")
                    
                # Ensure required keys exist
                if 'transactions' not in self._data:
                    self._data['transactions'] = []
                if 'categories' not in self._data:
                    self._data['categories'] = []
                if 'metadata' not in self._data:
                    self._data['metadata'] = {}
                    
            else:
                # Initialize with empty data structure
                self._data = {
                    'transactions': [],
                    'categories': [],
                    'metadata': {
                        'version': '1.0',
                        'created_at': datetime.now().isoformat(),
                        'last_modified': datetime.now().isoformat()
                    }
                }
                self._save_data()
                
        except (json.JSONDecodeError, ValueError, IOError) as e:
            # Handle corrupted or invalid data
            self._handle_data_corruption(e)
    
    def _handle_data_corruption(self, error: Exception) -> None:
        """Handle data corruption by creating backup and reinitializing."""
        print(f"Warning: Data corruption detected ({error}). Creating backup and reinitializing.")
        
        # Create backup of corrupted file if it exists
        if self.data_file_path.exists():
            backup_name = f"corrupted_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = self.backup_dir / backup_name
            self.backup_dir.mkdir(exist_ok=True)
            shutil.copy2(self.data_file_path, backup_path)
            print(f"Corrupted data backed up to: {backup_path}")
        
        # Initialize with empty data
        self._data = {
            'transactions': [],
            'categories': [],
            'metadata': {
                'version': '1.0',
                'created_at': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat()
            }
        }
        self._save_data()
    
    def _save_data(self) -> bool:
        """Save data to JSON file."""
        try:
            # Update last modified timestamp
            self._data['metadata']['last_modified'] = datetime.now().isoformat()
            
            # Create directory if it doesn't exist
            self.data_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first, then rename (atomic operation)
            temp_file = self.data_file_path.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_file.replace(self.data_file_path)
            return True
            
        except IOError as e:
            print(f"Error saving data: {e}")
            return False
    
    def save_transaction(self, transaction: Transaction) -> bool:
        """Save a transaction to storage."""
        if not transaction.is_valid():
            return False
        
        try:
            # Check if transaction already exists (update case)
            existing_index = None
            for i, existing_data in enumerate(self._data['transactions']):
                if existing_data.get('id') == transaction.id:
                    existing_index = i
                    break
            
            transaction_data = transaction.to_dict()
            
            if existing_index is not None:
                # Update existing transaction
                self._data['transactions'][existing_index] = transaction_data
            else:
                # Add new transaction
                self._data['transactions'].append(transaction_data)
            
            return self._save_data()
            
        except Exception as e:
            print(f"Error saving transaction: {e}")
            return False
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get a transaction by ID."""
        try:
            for transaction_data in self._data['transactions']:
                if transaction_data.get('id') == transaction_id:
                    return Transaction.from_dict(transaction_data)
            return None
            
        except Exception as e:
            print(f"Error getting transaction: {e}")
            return None
    
    def get_all_transactions(self) -> List[Transaction]:
        """Get all transactions."""
        try:
            transactions = []
            for transaction_data in self._data['transactions']:
                try:
                    transaction = Transaction.from_dict(transaction_data)
                    transactions.append(transaction)
                except Exception as e:
                    print(f"Warning: Skipping invalid transaction data: {e}")
                    continue
            
            # Sort by date (newest first)
            transactions.sort(key=lambda t: t.date, reverse=True)
            return transactions
            
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    def update_transaction(self, transaction: Transaction) -> bool:
        """Update an existing transaction."""
        return self.save_transaction(transaction)  # save_transaction handles both create and update
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction by ID."""
        try:
            original_length = len(self._data['transactions'])
            self._data['transactions'] = [
                t for t in self._data['transactions'] 
                if t.get('id') != transaction_id
            ]
            
            if len(self._data['transactions']) < original_length:
                return self._save_data()
            else:
                return False  # Transaction not found
                
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False
    
    def save_category(self, category: Category) -> bool:
        """Save a category to storage."""
        if not category.is_valid():
            return False
        
        try:
            # Check if category already exists
            existing_index = None
            for i, existing_data in enumerate(self._data['categories']):
                if existing_data.get('name') == category.name:
                    existing_index = i
                    break
            
            category_data = category.to_dict()
            
            if existing_index is not None:
                # Update existing category
                self._data['categories'][existing_index] = category_data
            else:
                # Add new category
                self._data['categories'].append(category_data)
            
            return self._save_data()
            
        except Exception as e:
            print(f"Error saving category: {e}")
            return False
    
    def get_category(self, category_name: str) -> Optional[Category]:
        """Get a category by name."""
        try:
            for category_data in self._data['categories']:
                if category_data.get('name') == category_name:
                    return Category.from_dict(category_data)
            return None
            
        except Exception as e:
            print(f"Error getting category: {e}")
            return None
    
    def get_all_categories(self) -> List[Category]:
        """Get all categories."""
        try:
            categories = []
            for category_data in self._data['categories']:
                try:
                    category = Category.from_dict(category_data)
                    categories.append(category)
                except Exception as e:
                    print(f"Warning: Skipping invalid category data: {e}")
                    continue
            
            # Sort by name
            categories.sort(key=lambda c: c.name)
            return categories
            
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def delete_category(self, category_name: str) -> bool:
        """Delete a category by name."""
        try:
            # Don't allow deletion of default categories
            for category_data in self._data['categories']:
                if (category_data.get('name') == category_name and 
                    category_data.get('is_default', False)):
                    return False
            
            original_length = len(self._data['categories'])
            self._data['categories'] = [
                c for c in self._data['categories'] 
                if c.get('name') != category_name
            ]
            
            if len(self._data['categories']) < original_length:
                return self._save_data()
            else:
                return False  # Category not found
                
        except Exception as e:
            print(f"Error deleting category: {e}")
            return False
    
    def initialize_storage(self) -> bool:
        """Initialize storage with default categories."""
        try:
            # Add default categories if they don't exist
            existing_category_names = {cat.get('name') for cat in self._data['categories']}
            
            for default_category in DEFAULT_CATEGORIES:
                if default_category.name not in existing_category_names:
                    self._data['categories'].append(default_category.to_dict())
            
            return self._save_data()
            
        except Exception as e:
            print(f"Error initializing storage: {e}")
            return False
    
    def backup_data(self) -> bool:
        """Create a backup of the data."""
        try:
            if not self.data_file_path.exists():
                return False
            
            # Create backup directory
            self.backup_dir.mkdir(exist_ok=True)
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"expense_data_backup_{timestamp}.json"
            backup_path = self.backup_dir / backup_filename
            
            # Copy current data file to backup
            shutil.copy2(self.data_file_path, backup_path)
            
            # Keep only the last 10 backups
            self._cleanup_old_backups()
            
            return True
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def _cleanup_old_backups(self) -> None:
        """Keep only the last 10 backups."""
        try:
            if not self.backup_dir.exists():
                return
            
            backup_files = list(self.backup_dir.glob("expense_data_backup_*.json"))
            backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Remove old backups (keep only 10 most recent)
            for old_backup in backup_files[10:]:
                old_backup.unlink()
                
        except Exception as e:
            print(f"Warning: Error cleaning up old backups: {e}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get storage metadata."""
        return self._data.get('metadata', {}).copy()