"""Transaction service for business logic operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from ..models.transaction import Transaction
from ..models.enums import TransactionType
from ..repositories.data_repository import DataRepository


class TransactionService:
    """Service for transaction-related business logic."""
    
    def __init__(self, repository: DataRepository):
        """Initialize the transaction service.
        
        Args:
            repository: Data repository instance
        """
        self.repository = repository
    
    def create_transaction(
        self,
        amount: Decimal,
        description: str,
        category: str,
        transaction_type: TransactionType,
        transaction_date: Optional[datetime] = None
    ) -> Optional[Transaction]:
        """Create a new transaction.
        
        Args:
            amount: Transaction amount
            description: Transaction description
            category: Transaction category
            transaction_type: INCOME or EXPENSE
            transaction_date: Transaction date (defaults to now)
            
        Returns:
            Created transaction or None if creation failed
        """
        try:
            # Validate category exists
            if not self._validate_category_exists(category):
                return None
            
            # Create transaction
            transaction = Transaction(
                amount=amount,
                description=description,
                category=category,
                transaction_type=transaction_type,
                date=transaction_date
            )
            
            # Validate transaction
            if not transaction.is_valid():
                return None
            
            # Save to repository
            if self.repository.save_transaction(transaction):
                return transaction
            else:
                return None
                
        except Exception as e:
            print(f"Error creating transaction: {e}")
            return None
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get a transaction by ID.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Transaction or None if not found
        """
        return self.repository.get_transaction(transaction_id)
    
    def get_all_transactions(self) -> List[Transaction]:
        """Get all transactions.
        
        Returns:
            List of all transactions
        """
        return self.repository.get_all_transactions()
    
    def update_transaction(self, transaction: Transaction) -> bool:
        """Update an existing transaction.
        
        Args:
            transaction: Transaction to update
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Validate transaction
            if not transaction.is_valid():
                return False
            
            # Validate category exists
            if not self._validate_category_exists(transaction.category):
                return False
            
            # Update in repository
            return self.repository.update_transaction(transaction)
            
        except Exception as e:
            print(f"Error updating transaction: {e}")
            return False
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction.
        
        Args:
            transaction_id: ID of transaction to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        return self.repository.delete_transaction(transaction_id)
    
    def filter_transactions_by_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[Transaction]:
        """Filter transactions by date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of transactions within date range
        """
        all_transactions = self.get_all_transactions()
        
        filtered = []
        for transaction in all_transactions:
            if transaction.date:
                transaction_date = transaction.date.date()
                if start_date <= transaction_date <= end_date:
                    filtered.append(transaction)
        
        return filtered
    
    def filter_transactions_by_category(self, category: str) -> List[Transaction]:
        """Filter transactions by category.
        
        Args:
            category: Category name
            
        Returns:
            List of transactions in the specified category
        """
        all_transactions = self.get_all_transactions()
        return [t for t in all_transactions if t.category == category]
    
    def filter_transactions_by_type(
        self,
        transaction_type: TransactionType
    ) -> List[Transaction]:
        """Filter transactions by type.
        
        Args:
            transaction_type: INCOME or EXPENSE
            
        Returns:
            List of transactions of the specified type
        """
        all_transactions = self.get_all_transactions()
        return [t for t in all_transactions if t.transaction_type == transaction_type]
    
    def filter_transactions(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[str] = None,
        transaction_type: Optional[TransactionType] = None
    ) -> List[Transaction]:
        """Filter transactions by multiple criteria.
        
        Args:
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            category: Category filter (optional)
            transaction_type: Type filter (optional)
            
        Returns:
            List of filtered transactions
        """
        transactions = self.get_all_transactions()
        
        # Apply date range filter
        if start_date and end_date:
            transactions = [
                t for t in transactions
                if t.date and start_date <= t.date.date() <= end_date
            ]
        elif start_date:
            transactions = [
                t for t in transactions
                if t.date and t.date.date() >= start_date
            ]
        elif end_date:
            transactions = [
                t for t in transactions
                if t.date and t.date.date() <= end_date
            ]
        
        # Apply category filter
        if category:
            transactions = [t for t in transactions if t.category == category]
        
        # Apply type filter
        if transaction_type:
            transactions = [t for t in transactions if t.transaction_type == transaction_type]
        
        return transactions
    
    def get_transaction_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all transactions.
        
        Returns:
            Dictionary with summary statistics
        """
        transactions = self.get_all_transactions()
        
        total_income = Decimal('0')
        total_expenses = Decimal('0')
        transaction_count = len(transactions)
        
        for transaction in transactions:
            if transaction.transaction_type == TransactionType.INCOME:
                total_income += transaction.amount
            else:
                total_expenses += transaction.amount
        
        net_balance = total_income - total_expenses
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance,
            'transaction_count': transaction_count,
            'income_count': len([t for t in transactions if t.transaction_type == TransactionType.INCOME]),
            'expense_count': len([t for t in transactions if t.transaction_type == TransactionType.EXPENSE])
        }
    
    def get_category_totals(self) -> Dict[str, Decimal]:
        """Get total amounts by category.
        
        Returns:
            Dictionary mapping category names to total amounts
        """
        transactions = self.get_all_transactions()
        category_totals = {}
        
        for transaction in transactions:
            if transaction.category not in category_totals:
                category_totals[transaction.category] = Decimal('0')
            category_totals[transaction.category] += transaction.amount
        
        return category_totals
    
    def _validate_category_exists(self, category_name: str) -> bool:
        """Validate that a category exists.
        
        Args:
            category_name: Name of category to validate
            
        Returns:
            True if category exists, False otherwise
        """
        category = self.repository.get_category(category_name)
        return category is not None