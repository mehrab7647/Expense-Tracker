"""Category service for business logic operations."""

from typing import List, Optional, Dict
from ..models.category import Category, DEFAULT_CATEGORIES
from ..models.enums import CategoryType
from ..repositories.data_repository import DataRepository


class CategoryService:
    """Service for category-related business logic."""
    
    def __init__(self, repository: DataRepository):
        """Initialize the category service.
        
        Args:
            repository: Data repository instance
        """
        self.repository = repository
        self._ensure_default_categories()
    
    def _ensure_default_categories(self) -> None:
        """Ensure default categories are available in the repository."""
        try:
            self.repository.initialize_storage()
        except Exception as e:
            print(f"Warning: Could not initialize default categories: {e}")
    
    def create_category(
        self,
        name: str,
        category_type: CategoryType,
        is_default: bool = False
    ) -> Optional[Category]:
        """Create a new category.
        
        Args:
            name: Category name
            category_type: INCOME or EXPENSE
            is_default: Whether this is a default category
            
        Returns:
            Created category or None if creation failed
        """
        try:
            # Check if category already exists
            existing = self.repository.get_category(name)
            if existing:
                return None  # Category already exists
            
            # Create category
            category = Category(
                name=name,
                category_type=category_type,
                is_default=is_default
            )
            
            # Validate category
            if not category.is_valid():
                return None
            
            # Save to repository
            if self.repository.save_category(category):
                return category
            else:
                return None
                
        except Exception as e:
            print(f"Error creating category: {e}")
            return None
    
    def get_category(self, category_name: str) -> Optional[Category]:
        """Get a category by name.
        
        Args:
            category_name: Name of the category
            
        Returns:
            Category or None if not found
        """
        return self.repository.get_category(category_name)
    
    def get_all_categories(self) -> List[Category]:
        """Get all categories.
        
        Returns:
            List of all categories
        """
        return self.repository.get_all_categories()
    
    def get_categories_by_type(self, category_type: CategoryType) -> List[Category]:
        """Get categories by type.
        
        Args:
            category_type: INCOME or EXPENSE
            
        Returns:
            List of categories of the specified type
        """
        all_categories = self.get_all_categories()
        return [cat for cat in all_categories if cat.category_type == category_type]
    
    def get_income_categories(self) -> List[Category]:
        """Get all income categories.
        
        Returns:
            List of income categories
        """
        return self.get_categories_by_type(CategoryType.INCOME)
    
    def get_expense_categories(self) -> List[Category]:
        """Get all expense categories.
        
        Returns:
            List of expense categories
        """
        return self.get_categories_by_type(CategoryType.EXPENSE)
    
    def get_default_categories(self) -> List[Category]:
        """Get all default categories.
        
        Returns:
            List of default categories
        """
        all_categories = self.get_all_categories()
        return [cat for cat in all_categories if cat.is_default]
    
    def get_custom_categories(self) -> List[Category]:
        """Get all custom (non-default) categories.
        
        Returns:
            List of custom categories
        """
        all_categories = self.get_all_categories()
        return [cat for cat in all_categories if not cat.is_default]
    
    def update_category(self, category: Category) -> bool:
        """Update an existing category.
        
        Args:
            category: Category to update
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Validate category
            if not category.is_valid():
                return False
            
            # Don't allow updating default categories to non-default
            existing = self.repository.get_category(category.name)
            if existing and existing.is_default and not category.is_default:
                return False
            
            # Update in repository
            return self.repository.save_category(category)
            
        except Exception as e:
            print(f"Error updating category: {e}")
            return False
    
    def delete_category(self, category_name: str) -> bool:
        """Delete a category.
        
        Args:
            category_name: Name of category to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # Check if category exists
            category = self.repository.get_category(category_name)
            if not category:
                return False
            
            # Don't allow deletion of default categories
            if category.is_default:
                return False
            
            # Check if category is in use by any transactions
            if self._is_category_in_use(category_name):
                return False
            
            # Delete from repository
            return self.repository.delete_category(category_name)
            
        except Exception as e:
            print(f"Error deleting category: {e}")
            return False
    
    def validate_category_name(self, name: str) -> List[str]:
        """Validate a category name.
        
        Args:
            name: Category name to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not name or not name.strip():
            errors.append("Category name is required")
        elif len(name.strip()) > 50:
            errors.append("Category name must be 50 characters or less")
        
        # Check for duplicate names
        existing = self.repository.get_category(name.strip())
        if existing:
            errors.append("Category name already exists")
        
        return errors
    
    def get_category_usage_stats(self) -> Dict[str, int]:
        """Get usage statistics for categories.
        
        Returns:
            Dictionary mapping category names to transaction counts
        """
        try:
            # Get all transactions to count usage
            all_transactions = self.repository.get_all_transactions()
            usage_stats = {}
            
            # Initialize all categories with 0 count
            all_categories = self.get_all_categories()
            for category in all_categories:
                usage_stats[category.name] = 0
            
            # Count transactions per category
            for transaction_data in all_transactions:
                category_name = transaction_data.get('category')
                if category_name in usage_stats:
                    usage_stats[category_name] += 1
            
            return usage_stats
            
        except Exception as e:
            print(f"Error getting category usage stats: {e}")
            return {}
    
    def _is_category_in_use(self, category_name: str) -> bool:
        """Check if a category is being used by any transactions.
        
        Args:
            category_name: Name of category to check
            
        Returns:
            True if category is in use, False otherwise
        """
        try:
            all_transactions = self.repository.get_all_transactions()
            for transaction_data in all_transactions:
                if transaction_data.get('category') == category_name:
                    return True
            return False
        except Exception:
            return True  # Assume in use if we can't check
    
    def get_category_names(self) -> List[str]:
        """Get list of all category names.
        
        Returns:
            List of category names
        """
        categories = self.get_all_categories()
        return [cat.name for cat in categories]
    
    def category_exists(self, category_name: str) -> bool:
        """Check if a category exists.
        
        Args:
            category_name: Name of category to check
            
        Returns:
            True if category exists, False otherwise
        """
        return self.repository.get_category(category_name) is not None