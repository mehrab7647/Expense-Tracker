"""Abstract data repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.transaction import Transaction
from ..models.category import Category


class DataRepository(ABC):
    """Abstract interface for data operations."""
    
    @abstractmethod
    def save_transaction(self, transaction: Transaction) -> bool:
        """Save a transaction to storage."""
        pass
    
    @abstractmethod
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get a transaction by ID."""
        pass
    
    @abstractmethod
    def get_all_transactions(self) -> List[Transaction]:
        """Get all transactions."""
        pass
    
    @abstractmethod
    def update_transaction(self, transaction: Transaction) -> bool:
        """Update an existing transaction."""
        pass
    
    @abstractmethod
    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction by ID."""
        pass
    
    @abstractmethod
    def save_category(self, category: Category) -> bool:
        """Save a category to storage."""
        pass
    
    @abstractmethod
    def get_category(self, category_name: str) -> Optional[Category]:
        """Get a category by name."""
        pass
    
    @abstractmethod
    def get_all_categories(self) -> List[Category]:
        """Get all categories."""
        pass
    
    @abstractmethod
    def delete_category(self, category_name: str) -> bool:
        """Delete a category by name."""
        pass
    
    @abstractmethod
    def initialize_storage(self) -> bool:
        """Initialize storage (create files, tables, etc.)."""
        pass
    
    @abstractmethod
    def backup_data(self) -> bool:
        """Create a backup of the data."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get storage metadata."""
        pass