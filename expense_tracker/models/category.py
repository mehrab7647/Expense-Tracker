"""Category data model."""

from dataclasses import dataclass
from typing import Optional

from .enums import CategoryType


@dataclass
class Category:
    """Category data model."""
    
    name: str
    category_type: CategoryType
    is_default: bool = False
    
    def validate(self) -> list[str]:
        """Validate category data and return list of error messages."""
        errors = []
        
        # Validate name
        if not self.name or not self.name.strip():
            errors.append("Category name is required")
        elif len(self.name.strip()) > 50:
            errors.append("Category name must be 50 characters or less")
        
        # Validate category type
        if not isinstance(self.category_type, CategoryType):
            errors.append("Category type must be INCOME or EXPENSE")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if category is valid."""
        return len(self.validate()) == 0
    
    def to_dict(self) -> dict:
        """Convert category to dictionary for serialization."""
        return {
            'name': self.name,
            'category_type': self.category_type.value,
            'is_default': self.is_default
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Category':
        """Create category from dictionary."""
        return cls(
            name=data['name'],
            category_type=CategoryType(data['category_type']),
            is_default=data.get('is_default', False)
        )


# Default categories as defined in the design document
DEFAULT_CATEGORIES = [
    # Income categories
    Category("Salary", CategoryType.INCOME, True),
    Category("Freelance", CategoryType.INCOME, True),
    Category("Investment", CategoryType.INCOME, True),
    Category("Other Income", CategoryType.INCOME, True),
    
    # Expense categories
    Category("Food", CategoryType.EXPENSE, True),
    Category("Transportation", CategoryType.EXPENSE, True),
    Category("Entertainment", CategoryType.EXPENSE, True),
    Category("Utilities", CategoryType.EXPENSE, True),
    Category("Healthcare", CategoryType.EXPENSE, True),
    Category("Shopping", CategoryType.EXPENSE, True),
    Category("Other Expense", CategoryType.EXPENSE, True),
]