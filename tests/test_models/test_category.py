"""Unit tests for Category model."""

import unittest

from expense_tracker.models.category import Category, DEFAULT_CATEGORIES
from expense_tracker.models.enums import CategoryType


class TestCategory(unittest.TestCase):
    """Test cases for Category model."""
    
    def test_category_creation(self):
        """Test category creation."""
        category = Category("Food", CategoryType.EXPENSE, True)
        
        self.assertEqual(category.name, "Food")
        self.assertEqual(category.category_type, CategoryType.EXPENSE)
        self.assertTrue(category.is_default)
    
    def test_category_creation_with_defaults(self):
        """Test category creation with default values."""
        category = Category("Custom Category", CategoryType.INCOME)
        
        self.assertEqual(category.name, "Custom Category")
        self.assertEqual(category.category_type, CategoryType.INCOME)
        self.assertFalse(category.is_default)
    
    def test_category_validation_valid(self):
        """Test validation of valid category."""
        category = Category("Food", CategoryType.EXPENSE)
        
        self.assertTrue(category.is_valid())
        self.assertEqual(len(category.validate()), 0)
    
    def test_category_validation_empty_name(self):
        """Test validation with empty name."""
        category = Category("", CategoryType.EXPENSE)
        
        self.assertFalse(category.is_valid())
        errors = category.validate()
        self.assertIn("Category name is required", errors)
        
        # Test whitespace-only name
        category = Category("   ", CategoryType.EXPENSE)
        
        self.assertFalse(category.is_valid())
        errors = category.validate()
        self.assertIn("Category name is required", errors)
    
    def test_category_validation_long_name(self):
        """Test validation with overly long name."""
        category = Category("x" * 51, CategoryType.EXPENSE)  # 51 characters
        
        self.assertFalse(category.is_valid())
        errors = category.validate()
        self.assertIn("Category name must be 50 characters or less", errors)
    
    def test_category_to_dict(self):
        """Test conversion to dictionary."""
        category = Category("Food", CategoryType.EXPENSE, True)
        result = category.to_dict()
        
        expected = {
            'name': 'Food',
            'category_type': 'EXPENSE',
            'is_default': True
        }
        
        self.assertEqual(result, expected)
    
    def test_category_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'name': 'Transportation',
            'category_type': 'INCOME',
            'is_default': False
        }
        
        category = Category.from_dict(data)
        
        self.assertEqual(category.name, 'Transportation')
        self.assertEqual(category.category_type, CategoryType.INCOME)
        self.assertFalse(category.is_default)
    
    def test_category_from_dict_with_defaults(self):
        """Test creation from dictionary with missing optional fields."""
        data = {
            'name': 'Custom',
            'category_type': 'EXPENSE'
        }
        
        category = Category.from_dict(data)
        
        self.assertEqual(category.name, 'Custom')
        self.assertEqual(category.category_type, CategoryType.EXPENSE)
        self.assertFalse(category.is_default)  # Should default to False
    
    def test_default_categories_exist(self):
        """Test that default categories are properly defined."""
        self.assertGreater(len(DEFAULT_CATEGORIES), 0)
        
        # Check that we have both income and expense categories
        income_categories = [cat for cat in DEFAULT_CATEGORIES if cat.category_type == CategoryType.INCOME]
        expense_categories = [cat for cat in DEFAULT_CATEGORIES if cat.category_type == CategoryType.EXPENSE]
        
        self.assertGreater(len(income_categories), 0)
        self.assertGreater(len(expense_categories), 0)
        
        # Check that all default categories are marked as default
        for category in DEFAULT_CATEGORIES:
            self.assertTrue(category.is_default)
            self.assertTrue(category.is_valid())
    
    def test_default_categories_content(self):
        """Test that expected default categories are present."""
        category_names = [cat.name for cat in DEFAULT_CATEGORIES]
        
        # Check for expected income categories
        expected_income = ["Salary", "Freelance", "Investment", "Other Income"]
        for name in expected_income:
            self.assertIn(name, category_names)
        
        # Check for expected expense categories
        expected_expense = ["Food", "Transportation", "Entertainment", "Utilities", "Healthcare", "Shopping", "Other Expense"]
        for name in expected_expense:
            self.assertIn(name, category_names)


if __name__ == '__main__':
    unittest.main()