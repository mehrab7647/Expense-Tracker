"""Transaction data model."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid

from .enums import TransactionType


@dataclass
class Transaction:
    """Transaction data model."""
    
    amount: Decimal
    description: str
    category: str
    transaction_type: TransactionType
    date: Optional[datetime] = None
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.id is None:
            self.id = str(uuid.uuid4())
        
        if self.date is None:
            self.date = datetime.now()
            
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def validate(self) -> list[str]:
        """Validate transaction data and return list of error messages."""
        errors = []
        
        # Validate amount
        if not isinstance(self.amount, Decimal):
            errors.append("Amount must be a Decimal")
        elif self.amount <= 0:
            errors.append("Amount must be greater than zero")
        
        # Validate description
        if not self.description or not self.description.strip():
            errors.append("Description is required")
        elif len(self.description.strip()) > 200:
            errors.append("Description must be 200 characters or less")
        
        # Validate category
        if not self.category or not self.category.strip():
            errors.append("Category is required")
        
        # Validate transaction type
        if not isinstance(self.transaction_type, TransactionType):
            errors.append("Transaction type must be INCOME or EXPENSE")
        
        # Validate date
        if self.date and not isinstance(self.date, datetime):
            errors.append("Date must be a datetime object")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if transaction is valid."""
        return len(self.validate()) == 0
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary for serialization."""
        return {
            'id': self.id,
            'amount': str(self.amount),
            'description': self.description,
            'category': self.category,
            'date': self.date.isoformat() if self.date else None,
            'transaction_type': self.transaction_type.value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create transaction from dictionary."""
        return cls(
            id=data.get('id'),
            amount=Decimal(data['amount']),
            description=data['description'],
            category=data['category'],
            date=datetime.fromisoformat(data['date']) if data.get('date') else None,
            transaction_type=TransactionType(data['transaction_type']),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )