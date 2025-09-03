"""Unit tests for CategoryService."""

import unittest
from unittest.mock import Mock, MagicMock

from expense_tracker.services.category_service import CategoryService
from expense_tracker.models.category import Category, DEFAULT_CATEGORIES
from expense_tracker.models.enums import CategoryType


class TestCategoryService(unittest.TestCase):
    """Test cases for CategoryService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = Mock()
        
        # Mock initialize_storage to avoid side effects
        self.mock_repository.initialize_storage.return_value = True
        
        self.service = CategoryService(self.mock_repository)
        
        # Sample data
        self.sample_category = Category("Test Category", CategoryType.EXPENSE, False)
        self.default_category = Category("Food", CategoryType.EXPENSE, True)
    
    def test_initialization_calls_initialize_storage(self):
        """Test that service initialization calls repository initialize_storage."""
        self.mock_repository.initialize_storage.assert_called_once()
    
    def test_create_category_success(self):
        """Test successful category creation."""
        # Mock category doesn't exist
        self.mock_repository.get_category.return_value = None
        self.mock_repository.save_category.return_value = True
        
        result = self.service.create_category(
            name="New Category",
            category_type=CategoryType.EXPENSE
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "New Category")
        self.assertEqual(result.category_type, CategoryType.EXPENSE)
        self.assertFalse(result.is_default)
        
        # Verify repository calls
        self.mock_repository.get_category.assert_called_with("New Category")
        self.mock_repository.save_category.assert_called_once()
    
    def test_create_category_already_exists(self):
        """Test category creation when category already exists."""
        # Mock category already exists
        self.mock_repository.get_category.return_value = self.sample_category
        
        result = self.service.create_category(
            name="Test Category",
            category_type=CategoryType.EXPENSE
        )
        
        self.assertIsNone(result)
        self.mock_repository.save_category.assert_not_called()
    
    def test_create_category_invalid_data(self):
        """Test category creation with invalid data."""
        # Mock category doesn't exist
        self.mock_repository.get_category.return_value = None
        
        result = self.service.create_category(
            name="",  # Invalid name
            category_type=CategoryType.EXPENSE
        )
        
        self.assertIsNone(result)
        self.mock_repository.save_category.assert_not_called()
    
    def test_create_category_repository_failure(self):
        """Test category creation when repository save fails."""
        # Mock category doesn't exist but save fails
        self.mock_repository.get_category.return_value = None
        self.mock_repository.save_category.return_value = False
        
        result = self.service.create_category(
            name="New Category",
            category_type=CategoryType.EXPENSE
        )
        
        self.assertIsNone(result)
    
    def test_get_category(self):
        """Test getting a category by name."""
        self.mock_repository.get_category.return_value = self.sample_category
        
        result = self.service.get_category("Test Category")
        
        self.assertEqual(result, self.sample_category)
        self.mock_repository.get_category.assert_called_with("Test Category")
    
    def test_get_all_categories(self):
        """Test getting all categories."""
        categories = [self.sample_category, self.default_category]
        self.mock_repository.get_all_categories.return_value = categories
        
        result = self.service.get_all_categories()
        
        self.assertEqual(result, categories)
        self.mock_repository.get_all_categories.assert_called_once()
    
    def test_get_categories_by_type(self):
        """Test getting categories by type."""
        income_category = Category("Salary", CategoryType.INCOME, True)
        expense_category = Category("Food", CategoryType.EXPENSE, True)
        categories = [income_category, expense_category]
        
        self.mock_repository.get_all_categories.return_value = categories
        
        result = self.service.get_categories_by_type(CategoryType.INCOME)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], income_category)
    
    def test_get_income_categories(self):
        """Test getting income categories."""
        income_category = Category("Salary", CategoryType.INCOME, True)
        expense_category = Category("Food", CategoryType.EXPENSE, True)
        categories = [income_category, expense_category]
        
        self.mock_repository.get_all_categories.return_value = categories
        
        result = self.service.get_income_categories()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], income_category)
    
    def test_get_expense_categories(self):
        """Test getting expense categories."""
        income_category = Category("Salary", CategoryType.INCOME, True)
        expense_category = Category("Food", CategoryType.EXPENSE, True)
        categories = [income_category, expense_category]
        
        self.mock_repository.get_all_categories.return_value = categories
        
        result = self.service.get_expense_categories()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], expense_category)
    
    def test_get_default_categories(self):
        """Test getting default categories."""
        default_category = Category("Food", CategoryType.EXPENSE, True)
        custom_category = Category("Custom", CategoryType.EXPENSE, False)
        categories = [default_category, custom_category]
        
        self.mock_repository.get_all_categories.return_value = categories
        
        result = self.service.get_default_categories()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], default_category)
    
    def test_get_custom_categories(self):
        """Test getting custom categories."""
        default_category = Category("Food", CategoryType.EXPENSE, True)
        custom_category = Category("Custom", CategoryType.EXPENSE, False)
        categories = [default_category, custom_category]
        
        self.mock_repository.get_all_categories.return_value = categories
        
        result = self.service.get_custom_categories()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], custom_category)
    
    def test_update_category_success(self):
        """Test successful category update."""
        self.mock_repository.get_category.return_value = self.sample_category
        self.mock_repository.save_category.return_value = True
        
        result = self.service.update_category(self.sample_category)
        
        self.assertTrue(result)
        self.mock_repository.save_category.assert_called_once_with(self.sample_category)
    
    def test_update_category_invalid_data(self):
        """Test category update with invalid data."""
        invalid_category = Category("", CategoryType.EXPENSE)  # Invalid name
        
        result = self.service.update_category(invalid_category)
        
        self.assertFalse(result)
        self.mock_repository.save_category.assert_not_called()
    
    def test_update_category_default_to_non_default(self):
        """Test that default categories cannot be changed to non-default."""
        # Mock existing default category
        existing_default = Category("Food", CategoryType.EXPENSE, True)
        self.mock_repository.get_category.return_value = existing_default
        
        # Try to update to non-default
        updated_category = Category("Food", CategoryType.EXPENSE, False)
        
        result = self.service.update_category(updated_category)
        
        self.assertFalse(result)
        self.mock_repository.save_category.assert_not_called()
    
    def test_delete_category_success(self):
        """Test successful category deletion."""
        # Mock custom category (not default, not in use)
        custom_category = Category("Custom", CategoryType.EXPENSE, False)
        self.mock_repository.get_category.return_value = custom_category
        self.mock_repository.get_all_transactions.return_value = []
        self.mock_repository.delete_category.return_value = True
        
        result = self.service.delete_category("Custom")
        
        self.assertTrue(result)
        self.mock_repository.delete_category.assert_called_once_with("Custom")
    
    def test_delete_category_not_found(self):
        """Test deleting non-existent category."""
        self.mock_repository.get_category.return_value = None
        
        result = self.service.delete_category("NonExistent")
        
        self.assertFalse(result)
        self.mock_repository.delete_category.assert_not_called()
    
    def test_delete_default_category(self):
        """Test that default categories cannot be deleted."""
        self.mock_repository.get_category.return_value = self.default_category
        
        result = self.service.delete_category("Food")
        
        self.assertFalse(result)
        self.mock_repository.delete_category.assert_not_called()
    
    def test_delete_category_in_use(self):
        """Test that categories in use cannot be deleted."""
        # Mock custom category
        custom_category = Category("Custom", CategoryType.EXPENSE, False)
        self.mock_repository.get_category.return_value = custom_category
        
        # Mock transaction using this category
        transaction_data = {'category': 'Custom'}
        self.mock_repository.get_all_transactions.return_value = [transaction_data]
        
        result = self.service.delete_category("Custom")
        
        self.assertFalse(result)
        self.mock_repository.delete_category.assert_not_called()
    
    def test_validate_category_name_valid(self):
        """Test validation of valid category name."""
        self.mock_repository.get_category.return_value = None  # Name doesn't exist
        
        errors = self.service.validate_category_name("Valid Name")
        
        self.assertEqual(len(errors), 0)
    
    def test_validate_category_name_empty(self):
        """Test validation of empty category name."""
        errors = self.service.validate_category_name("")
        
        self.assertIn("Category name is required", errors)
    
    def test_validate_category_name_too_long(self):
        """Test validation of overly long category name."""
        long_name = "x" * 51  # 51 characters
        self.mock_repository.get_category.return_value = None
        
        errors = self.service.validate_category_name(long_name)
        
        self.assertIn("Category name must be 50 characters or less", errors)
    
    def test_validate_category_name_duplicate(self):
        """Test validation of duplicate category name."""
        self.mock_repository.get_category.return_value = self.sample_category
        
        errors = self.service.validate_category_name("Test Category")
        
        self.assertIn("Category name already exists", errors)
    
    def test_get_category_usage_stats(self):
        """Test getting category usage statistics."""
        # Mock categories
        categories = [
            Category("Food", CategoryType.EXPENSE, True),
            Category("Transportation", CategoryType.EXPENSE, True)
        ]
        self.mock_repository.get_all_categories.return_value = categories
        
        # Mock transactions
        transactions = [
            {'category': 'Food'},
            {'category': 'Food'},
            {'category': 'Transportation'}
        ]
        self.mock_repository.get_all_transactions.return_value = transactions
        
        result = self.service.get_category_usage_stats()
        
        self.assertEqual(result['Food'], 2)
        self.assertEqual(result['Transportation'], 1)
    
    def test_get_category_names(self):
        """Test getting list of category names."""
        categories = [
            Category("Food", CategoryType.EXPENSE, True),
            Category("Transportation", CategoryType.EXPENSE, True)
        ]
        self.mock_repository.get_all_categories.return_value = categories
        
        result = self.service.get_category_names()
        
        self.assertEqual(result, ["Food", "Transportation"])
    
    def test_category_exists(self):
        """Test checking if category exists."""
        self.mock_repository.get_category.return_value = self.sample_category
        
        result = self.service.category_exists("Test Category")
        
        self.assertTrue(result)
        self.mock_repository.get_category.assert_called_with("Test Category")
    
    def test_category_not_exists(self):
        """Test checking if category doesn't exist."""
        self.mock_repository.get_category.return_value = None
        
        result = self.service.category_exists("NonExistent")
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()