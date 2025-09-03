"""Unit tests for TransactionService."""

import unittest
from unittest.mock import Mock, MagicMock
from decimal import Decimal
from datetime import datetime, date

from expense_tracker.services.transaction_service import TransactionService
from expense_tracker.models.transaction import Transaction
from expense_tracker.models.category import Category
from expense_tracker.models.enums import TransactionType, CategoryType


class TestTransactionService(unittest.TestCase):
    """Test cases for TransactionService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = Mock()
        self.service = TransactionService(self.mock_repository)
        
        # Sample data
        self.sample_category = Category("Food", CategoryType.EXPENSE, True)
        self.sample_transaction = Transaction(
            amount=Decimal('100.50'),
            description='Test transaction',
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
    
    def test_create_transaction_success(self):
        """Test successful transaction creation."""
        # Mock category validation
        self.mock_repository.get_category.return_value = self.sample_category
        self.mock_repository.save_transaction.return_value = True
        
        result = self.service.create_transaction(
            amount=Decimal('100.50'),
            description='Test transaction',
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.amount, Decimal('100.50'))
        self.assertEqual(result.description, 'Test transaction')
        self.assertEqual(result.category, 'Food')
        self.assertEqual(result.transaction_type, TransactionType.EXPENSE)
        
        # Verify repository calls
        self.mock_repository.get_category.assert_called_once_with('Food')
        self.mock_repository.save_transaction.assert_called_once()
    
    def test_create_transaction_invalid_category(self):
        """Test transaction creation with invalid category."""
        # Mock category not found
        self.mock_repository.get_category.return_value = None
        
        result = self.service.create_transaction(
            amount=Decimal('100.50'),
            description='Test transaction',
            category='NonexistentCategory',
            transaction_type=TransactionType.EXPENSE
        )
        
        self.assertIsNone(result)
        self.mock_repository.get_category.assert_called_once_with('NonexistentCategory')
        self.mock_repository.save_transaction.assert_not_called()
    
    def test_create_transaction_invalid_data(self):
        """Test transaction creation with invalid data."""
        # Mock category validation
        self.mock_repository.get_category.return_value = self.sample_category
        
        result = self.service.create_transaction(
            amount=Decimal('0'),  # Invalid amount
            description='',  # Invalid description
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
        
        self.assertIsNone(result)
        self.mock_repository.save_transaction.assert_not_called()
    
    def test_create_transaction_repository_failure(self):
        """Test transaction creation when repository save fails."""
        # Mock category validation
        self.mock_repository.get_category.return_value = self.sample_category
        self.mock_repository.save_transaction.return_value = False
        
        result = self.service.create_transaction(
            amount=Decimal('100.50'),
            description='Test transaction',
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
        
        self.assertIsNone(result)
    
    def test_get_transaction(self):
        """Test getting a transaction by ID."""
        self.mock_repository.get_transaction.return_value = self.sample_transaction
        
        result = self.service.get_transaction('test-id')
        
        self.assertEqual(result, self.sample_transaction)
        self.mock_repository.get_transaction.assert_called_once_with('test-id')
    
    def test_get_all_transactions(self):
        """Test getting all transactions."""
        transactions = [self.sample_transaction]
        self.mock_repository.get_all_transactions.return_value = transactions
        
        result = self.service.get_all_transactions()
        
        self.assertEqual(result, transactions)
        self.mock_repository.get_all_transactions.assert_called_once()
    
    def test_update_transaction_success(self):
        """Test successful transaction update."""
        # Mock category validation
        self.mock_repository.get_category.return_value = self.sample_category
        self.mock_repository.update_transaction.return_value = True
        
        result = self.service.update_transaction(self.sample_transaction)
        
        self.assertTrue(result)
        self.mock_repository.get_category.assert_called_once_with('Food')
        self.mock_repository.update_transaction.assert_called_once_with(self.sample_transaction)
    
    def test_update_transaction_invalid_data(self):
        """Test transaction update with invalid data."""
        invalid_transaction = Transaction(
            amount=Decimal('0'),  # Invalid
            description='Test',
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
        
        result = self.service.update_transaction(invalid_transaction)
        
        self.assertFalse(result)
        self.mock_repository.update_transaction.assert_not_called()
    
    def test_delete_transaction(self):
        """Test transaction deletion."""
        self.mock_repository.delete_transaction.return_value = True
        
        result = self.service.delete_transaction('test-id')
        
        self.assertTrue(result)
        self.mock_repository.delete_transaction.assert_called_once_with('test-id')
    
    def test_filter_transactions_by_date_range(self):
        """Test filtering transactions by date range."""
        # Create test transactions with different dates
        transaction1 = Transaction(
            amount=Decimal('100'),
            description='Transaction 1',
            category='Food',
            transaction_type=TransactionType.EXPENSE,
            date=datetime(2024, 1, 15)
        )
        
        transaction2 = Transaction(
            amount=Decimal('200'),
            description='Transaction 2',
            category='Food',
            transaction_type=TransactionType.EXPENSE,
            date=datetime(2024, 1, 25)
        )
        
        transaction3 = Transaction(
            amount=Decimal('300'),
            description='Transaction 3',
            category='Food',
            transaction_type=TransactionType.EXPENSE,
            date=datetime(2024, 2, 5)
        )
        
        self.mock_repository.get_all_transactions.return_value = [
            transaction1, transaction2, transaction3
        ]
        
        # Filter for January 2024
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        result = self.service.filter_transactions_by_date_range(start_date, end_date)
        
        self.assertEqual(len(result), 2)
        self.assertIn(transaction1, result)
        self.assertIn(transaction2, result)
        self.assertNotIn(transaction3, result)
    
    def test_filter_transactions_by_category(self):
        """Test filtering transactions by category."""
        transaction1 = Transaction(
            amount=Decimal('100'),
            description='Food transaction',
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
        
        transaction2 = Transaction(
            amount=Decimal('200'),
            description='Transport transaction',
            category='Transportation',
            transaction_type=TransactionType.EXPENSE
        )
        
        self.mock_repository.get_all_transactions.return_value = [
            transaction1, transaction2
        ]
        
        result = self.service.filter_transactions_by_category('Food')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], transaction1)
    
    def test_filter_transactions_by_type(self):
        """Test filtering transactions by type."""
        income_transaction = Transaction(
            amount=Decimal('1000'),
            description='Salary',
            category='Salary',
            transaction_type=TransactionType.INCOME
        )
        
        expense_transaction = Transaction(
            amount=Decimal('100'),
            description='Food',
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
        
        self.mock_repository.get_all_transactions.return_value = [
            income_transaction, expense_transaction
        ]
        
        result = self.service.filter_transactions_by_type(TransactionType.INCOME)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], income_transaction)
    
    def test_filter_transactions_multiple_criteria(self):
        """Test filtering transactions with multiple criteria."""
        transaction1 = Transaction(
            amount=Decimal('100'),
            description='Food transaction',
            category='Food',
            transaction_type=TransactionType.EXPENSE,
            date=datetime(2024, 1, 15)
        )
        
        transaction2 = Transaction(
            amount=Decimal('200'),
            description='Food transaction 2',
            category='Food',
            transaction_type=TransactionType.EXPENSE,
            date=datetime(2024, 2, 15)
        )
        
        transaction3 = Transaction(
            amount=Decimal('1000'),
            description='Salary',
            category='Salary',
            transaction_type=TransactionType.INCOME,
            date=datetime(2024, 1, 15)
        )
        
        self.mock_repository.get_all_transactions.return_value = [
            transaction1, transaction2, transaction3
        ]
        
        # Filter for Food expenses in January 2024
        result = self.service.filter_transactions(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], transaction1)
    
    def test_get_transaction_summary(self):
        """Test getting transaction summary statistics."""
        income_transaction = Transaction(
            amount=Decimal('1000'),
            description='Salary',
            category='Salary',
            transaction_type=TransactionType.INCOME
        )
        
        expense_transaction1 = Transaction(
            amount=Decimal('100'),
            description='Food',
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
        
        expense_transaction2 = Transaction(
            amount=Decimal('50'),
            description='Transport',
            category='Transportation',
            transaction_type=TransactionType.EXPENSE
        )
        
        self.mock_repository.get_all_transactions.return_value = [
            income_transaction, expense_transaction1, expense_transaction2
        ]
        
        result = self.service.get_transaction_summary()
        
        self.assertEqual(result['total_income'], Decimal('1000'))
        self.assertEqual(result['total_expenses'], Decimal('150'))
        self.assertEqual(result['net_balance'], Decimal('850'))
        self.assertEqual(result['transaction_count'], 3)
        self.assertEqual(result['income_count'], 1)
        self.assertEqual(result['expense_count'], 2)
    
    def test_get_category_totals(self):
        """Test getting totals by category."""
        transaction1 = Transaction(
            amount=Decimal('100'),
            description='Food 1',
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
        
        transaction2 = Transaction(
            amount=Decimal('50'),
            description='Food 2',
            category='Food',
            transaction_type=TransactionType.EXPENSE
        )
        
        transaction3 = Transaction(
            amount=Decimal('200'),
            description='Transport',
            category='Transportation',
            transaction_type=TransactionType.EXPENSE
        )
        
        self.mock_repository.get_all_transactions.return_value = [
            transaction1, transaction2, transaction3
        ]
        
        result = self.service.get_category_totals()
        
        self.assertEqual(result['Food'], Decimal('150'))
        self.assertEqual(result['Transportation'], Decimal('200'))


if __name__ == '__main__':
    unittest.main()