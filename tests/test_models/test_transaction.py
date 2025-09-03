"""Unit tests for Transaction model."""

import unittest
from datetime import datetime
from decimal import Decimal

from expense_tracker.models.transaction import Transaction
from expense_tracker.models.enums import TransactionType


class TestTransaction(unittest.TestCase):
    """Test cases for Transaction model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_transaction_data = {
            'amount': Decimal('100.50'),
            'description': 'Test transaction',
            'category': 'Food',
            'transaction_type': TransactionType.EXPENSE
        }
    
    def test_transaction_creation_with_defaults(self):
        """Test transaction creation with default values."""
        transaction = Transaction(**self.valid_transaction_data)
        
        self.assertIsNotNone(transaction.id)
        self.assertIsNotNone(transaction.date)
        self.assertIsNotNone(transaction.created_at)
        self.assertEqual(transaction.amount, Decimal('100.50'))
        self.assertEqual(transaction.description, 'Test transaction')
        self.assertEqual(transaction.category, 'Food')
        self.assertEqual(transaction.transaction_type, TransactionType.EXPENSE)
    
    def test_transaction_creation_with_custom_values(self):
        """Test transaction creation with custom values."""
        custom_date = datetime(2024, 1, 15, 10, 30)
        custom_created = datetime(2024, 1, 15, 10, 30)
        custom_id = "test-id-123"
        
        transaction = Transaction(
            id=custom_id,
            amount=Decimal('50.25'),
            description='Custom transaction',
            category='Transportation',
            transaction_type=TransactionType.INCOME,
            date=custom_date,
            created_at=custom_created
        )
        
        self.assertEqual(transaction.id, custom_id)
        self.assertEqual(transaction.date, custom_date)
        self.assertEqual(transaction.created_at, custom_created)
    
    def test_transaction_validation_valid(self):
        """Test validation of valid transaction."""
        transaction = Transaction(**self.valid_transaction_data)
        
        self.assertTrue(transaction.is_valid())
        self.assertEqual(len(transaction.validate()), 0)
    
    def test_transaction_validation_invalid_amount(self):
        """Test validation with invalid amount."""
        # Test zero amount
        data = self.valid_transaction_data.copy()
        data['amount'] = Decimal('0')
        transaction = Transaction(**data)
        
        self.assertFalse(transaction.is_valid())
        errors = transaction.validate()
        self.assertIn("Amount must be greater than zero", errors)
        
        # Test negative amount
        data['amount'] = Decimal('-10.50')
        transaction = Transaction(**data)
        
        self.assertFalse(transaction.is_valid())
        errors = transaction.validate()
        self.assertIn("Amount must be greater than zero", errors)
    
    def test_transaction_validation_empty_description(self):
        """Test validation with empty description."""
        data = self.valid_transaction_data.copy()
        data['description'] = ''
        transaction = Transaction(**data)
        
        self.assertFalse(transaction.is_valid())
        errors = transaction.validate()
        self.assertIn("Description is required", errors)
        
        # Test whitespace-only description
        data['description'] = '   '
        transaction = Transaction(**data)
        
        self.assertFalse(transaction.is_valid())
        errors = transaction.validate()
        self.assertIn("Description is required", errors)
    
    def test_transaction_validation_long_description(self):
        """Test validation with overly long description."""
        data = self.valid_transaction_data.copy()
        data['description'] = 'x' * 201  # 201 characters
        transaction = Transaction(**data)
        
        self.assertFalse(transaction.is_valid())
        errors = transaction.validate()
        self.assertIn("Description must be 200 characters or less", errors)
    
    def test_transaction_validation_empty_category(self):
        """Test validation with empty category."""
        data = self.valid_transaction_data.copy()
        data['category'] = ''
        transaction = Transaction(**data)
        
        self.assertFalse(transaction.is_valid())
        errors = transaction.validate()
        self.assertIn("Category is required", errors)
    
    def test_transaction_to_dict(self):
        """Test conversion to dictionary."""
        transaction = Transaction(**self.valid_transaction_data)
        result = transaction.to_dict()
        
        self.assertEqual(result['amount'], '100.50')
        self.assertEqual(result['description'], 'Test transaction')
        self.assertEqual(result['category'], 'Food')
        self.assertEqual(result['transaction_type'], 'EXPENSE')
        self.assertIsNotNone(result['id'])
        self.assertIsNotNone(result['date'])
        self.assertIsNotNone(result['created_at'])
    
    def test_transaction_from_dict(self):
        """Test creation from dictionary."""
        transaction = Transaction(**self.valid_transaction_data)
        data = transaction.to_dict()
        
        recreated = Transaction.from_dict(data)
        
        self.assertEqual(recreated.id, transaction.id)
        self.assertEqual(recreated.amount, transaction.amount)
        self.assertEqual(recreated.description, transaction.description)
        self.assertEqual(recreated.category, transaction.category)
        self.assertEqual(recreated.transaction_type, transaction.transaction_type)
        self.assertEqual(recreated.date, transaction.date)
        self.assertEqual(recreated.created_at, transaction.created_at)


if __name__ == '__main__':
    unittest.main()