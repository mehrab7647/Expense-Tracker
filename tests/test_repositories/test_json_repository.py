"""Unit tests for JSONRepository."""

import unittest
import tempfile
import json
import os
from pathlib import Path
from decimal import Decimal
from datetime import datetime

from expense_tracker.repositories.json_repository import JSONRepository
from expense_tracker.models.transaction import Transaction
from expense_tracker.models.category import Category, DEFAULT_CATEGORIES
from expense_tracker.models.enums import TransactionType, CategoryType


class TestJSONRepository(unittest.TestCase):
    """Test cases for JSONRepository."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_data.json")
        self.repository = JSONRepository(self.test_file)
        
        # Sample transaction data
        self.sample_transaction = Transaction(
            amount=Decimal('100.50'),
            description='Test transaction',
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
        
        # Sample category data
        self.sample_category = Category(
            name='Test Category',
            category_type=CategoryType.EXPENSE,
            is_default=False
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization_new_file(self):
        """Test repository initialization with new file."""
        self.assertTrue(Path(self.test_file).exists())
        
        # Check initial data structure
        with open(self.test_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn('transactions', data)
        self.assertIn('categories', data)
        self.assertIn('metadata', data)
        self.assertEqual(data['transactions'], [])
        self.assertEqual(data['categories'], [])
        self.assertIn('version', data['metadata'])
    
    def test_save_and_get_transaction(self):
        """Test saving and retrieving a transaction."""
        # Save transaction
        result = self.repository.save_transaction(self.sample_transaction)
        self.assertTrue(result)
        
        # Retrieve transaction
        retrieved = self.repository.get_transaction(self.sample_transaction.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.amount, self.sample_transaction.amount)
        self.assertEqual(retrieved.description, self.sample_transaction.description)
        self.assertEqual(retrieved.category, self.sample_transaction.category)
        self.assertEqual(retrieved.transaction_type, self.sample_transaction.transaction_type)
    
    def test_save_invalid_transaction(self):
        """Test saving invalid transaction."""
        invalid_transaction = Transaction(
            amount=Decimal('0'),  # Invalid amount
            description='',  # Invalid description
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
        
        result = self.repository.save_transaction(invalid_transaction)
        self.assertFalse(result)
    
    def test_get_all_transactions(self):
        """Test getting all transactions."""
        # Save multiple transactions
        transaction1 = Transaction(
            amount=Decimal('50.00'),
            description='Transaction 1',
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
        
        transaction2 = Transaction(
            amount=Decimal('1000.00'),
            description='Transaction 2',
            category='Salary',
            transaction_type=TransactionType.INCOME
        )
        
        self.repository.save_transaction(transaction1)
        self.repository.save_transaction(transaction2)
        
        # Get all transactions
        all_transactions = self.repository.get_all_transactions()
        self.assertEqual(len(all_transactions), 2)
        
        # Check sorting (newest first)
        self.assertGreaterEqual(all_transactions[0].date, all_transactions[1].date)
    
    def test_update_transaction(self):
        """Test updating an existing transaction."""
        # Save original transaction
        self.repository.save_transaction(self.sample_transaction)
        
        # Update transaction
        self.sample_transaction.description = 'Updated description'
        self.sample_transaction.amount = Decimal('200.00')
        
        result = self.repository.update_transaction(self.sample_transaction)
        self.assertTrue(result)
        
        # Verify update
        retrieved = self.repository.get_transaction(self.sample_transaction.id)
        self.assertEqual(retrieved.description, 'Updated description')
        self.assertEqual(retrieved.amount, Decimal('200.00'))
    
    def test_delete_transaction(self):
        """Test deleting a transaction."""
        # Save transaction
        self.repository.save_transaction(self.sample_transaction)
        
        # Verify it exists
        retrieved = self.repository.get_transaction(self.sample_transaction.id)
        self.assertIsNotNone(retrieved)
        
        # Delete transaction
        result = self.repository.delete_transaction(self.sample_transaction.id)
        self.assertTrue(result)
        
        # Verify it's gone
        retrieved = self.repository.get_transaction(self.sample_transaction.id)
        self.assertIsNone(retrieved)
    
    def test_delete_nonexistent_transaction(self):
        """Test deleting a non-existent transaction."""
        result = self.repository.delete_transaction('nonexistent-id')
        self.assertFalse(result)
    
    def test_save_and_get_category(self):
        """Test saving and retrieving a category."""
        # Save category
        result = self.repository.save_category(self.sample_category)
        self.assertTrue(result)
        
        # Retrieve category
        retrieved = self.repository.get_category(self.sample_category.name)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, self.sample_category.name)
        self.assertEqual(retrieved.category_type, self.sample_category.category_type)
        self.assertEqual(retrieved.is_default, self.sample_category.is_default)
    
    def test_save_invalid_category(self):
        """Test saving invalid category."""
        invalid_category = Category(
            name='',  # Invalid name
            category_type=CategoryType.EXPENSE
        )
        
        result = self.repository.save_category(invalid_category)
        self.assertFalse(result)
    
    def test_get_all_categories(self):
        """Test getting all categories."""
        # Save multiple categories
        category1 = Category('Category A', CategoryType.EXPENSE)
        category2 = Category('Category B', CategoryType.INCOME)
        
        self.repository.save_category(category1)
        self.repository.save_category(category2)
        
        # Get all categories
        all_categories = self.repository.get_all_categories()
        self.assertGreaterEqual(len(all_categories), 2)
        
        # Check sorting (by name)
        category_names = [cat.name for cat in all_categories]
        self.assertEqual(category_names, sorted(category_names))
    
    def test_delete_category(self):
        """Test deleting a category."""
        # Save category
        self.repository.save_category(self.sample_category)
        
        # Verify it exists
        retrieved = self.repository.get_category(self.sample_category.name)
        self.assertIsNotNone(retrieved)
        
        # Delete category
        result = self.repository.delete_category(self.sample_category.name)
        self.assertTrue(result)
        
        # Verify it's gone
        retrieved = self.repository.get_category(self.sample_category.name)
        self.assertIsNone(retrieved)
    
    def test_delete_default_category(self):
        """Test that default categories cannot be deleted."""
        # Initialize storage to add default categories
        self.repository.initialize_storage()
        
        # Try to delete a default category
        result = self.repository.delete_category('Food')
        self.assertFalse(result)
        
        # Verify it still exists
        retrieved = self.repository.get_category('Food')
        self.assertIsNotNone(retrieved)
    
    def test_initialize_storage(self):
        """Test storage initialization with default categories."""
        result = self.repository.initialize_storage()
        self.assertTrue(result)
        
        # Check that default categories were added
        all_categories = self.repository.get_all_categories()
        category_names = [cat.name for cat in all_categories]
        
        for default_category in DEFAULT_CATEGORIES:
            self.assertIn(default_category.name, category_names)
    
    def test_backup_data(self):
        """Test data backup functionality."""
        # Add some data first
        self.repository.save_transaction(self.sample_transaction)
        self.repository.save_category(self.sample_category)
        
        # Create backup
        result = self.repository.backup_data()
        self.assertTrue(result)
        
        # Check that backup file was created
        backup_dir = Path(self.temp_dir) / "backups"
        self.assertTrue(backup_dir.exists())
        
        backup_files = list(backup_dir.glob("expense_data_backup_*.json"))
        self.assertGreater(len(backup_files), 0)
    
    def test_get_metadata(self):
        """Test getting metadata."""
        metadata = self.repository.get_metadata()
        
        self.assertIn('version', metadata)
        self.assertIn('created_at', metadata)
        self.assertIn('last_modified', metadata)
        self.assertEqual(metadata['version'], '1.0')
    
    def test_data_corruption_handling(self):
        """Test handling of corrupted data files."""
        # Write invalid JSON to the file
        with open(self.test_file, 'w') as f:
            f.write("invalid json content")
        
        # Create new repository instance (should handle corruption)
        new_repo = JSONRepository(self.test_file)
        
        # Should have clean data structure
        all_transactions = new_repo.get_all_transactions()
        self.assertEqual(len(all_transactions), 0)
        
        # Should be able to save new data
        result = new_repo.save_transaction(self.sample_transaction)
        self.assertTrue(result)
    
    def test_atomic_save_operation(self):
        """Test that save operations are atomic."""
        # Save initial transaction
        self.repository.save_transaction(self.sample_transaction)
        
        # Verify file exists and is valid
        self.assertTrue(Path(self.test_file).exists())
        
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data['transactions']), 1)


if __name__ == '__main__':
    unittest.main()