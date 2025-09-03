"""Unit tests for validation utilities."""

import unittest
from decimal import Decimal
from datetime import date, datetime, timedelta

from expense_tracker.utils.validation import (
    ValidationError, ValidationResult, InputValidator, 
    TransactionValidator, CategoryValidator
)
from expense_tracker.models.transaction import TransactionType
from expense_tracker.models.category import CategoryType


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult class."""
    
    def test_init_default(self):
        """Test ValidationResult initialization with defaults."""
        result = ValidationResult()
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])
    
    def test_init_with_values(self):
        """Test ValidationResult initialization with values."""
        errors = ["Error 1", "Error 2"]
        warnings = ["Warning 1"]
        result = ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors, errors)
        self.assertEqual(result.warnings, warnings)
    
    def test_add_error(self):
        """Test adding errors."""
        result = ValidationResult()
        result.add_error("Test error")
        
        self.assertFalse(result.is_valid)
        self.assertIn("Test error", result.errors)
    
    def test_add_warning(self):
        """Test adding warnings."""
        result = ValidationResult()
        result.add_warning("Test warning")
        
        self.assertTrue(result.is_valid)  # Warnings don't affect validity
        self.assertIn("Test warning", result.warnings)
    
    def test_merge(self):
        """Test merging validation results."""
        result1 = ValidationResult()
        result1.add_error("Error 1")
        result1.add_warning("Warning 1")
        
        result2 = ValidationResult()
        result2.add_error("Error 2")
        result2.add_warning("Warning 2")
        
        result1.merge(result2)
        
        self.assertFalse(result1.is_valid)
        self.assertEqual(len(result1.errors), 2)
        self.assertEqual(len(result1.warnings), 2)


class TestInputValidator(unittest.TestCase):
    """Test cases for InputValidator class."""
    
    def test_validate_amount_valid(self):
        """Test valid amount validation."""
        test_cases = [
            "10.50",
            10.50,
            Decimal("10.50"),
            100,
            "0.01"  # Minimum amount
        ]
        
        for amount in test_cases:
            with self.subTest(amount=amount):
                result = InputValidator.validate_amount(amount)
                self.assertTrue(result.is_valid, f"Amount {amount} should be valid")
    
    def test_validate_amount_invalid(self):
        """Test invalid amount validation."""
        test_cases = [
            None,  # Required
            "",    # Empty string
            "abc", # Non-numeric
            -10,   # Negative
            0,     # Zero
            "10.123", # Too many decimal places
            "999999999999.99"  # Too large
        ]
        
        for amount in test_cases:
            with self.subTest(amount=amount):
                result = InputValidator.validate_amount(amount)
                self.assertFalse(result.is_valid, f"Amount {amount} should be invalid")
                self.assertTrue(len(result.errors) > 0)
    
    def test_validate_amount_warnings(self):
        """Test amount validation warnings."""
        result = InputValidator.validate_amount("15000")  # Large amount
        self.assertTrue(result.is_valid)
        self.assertTrue(len(result.warnings) > 0)
    
    def test_validate_date_valid(self):
        """Test valid date validation."""
        today = date.today()
        test_cases = [
            today.strftime("%Y-%m-%d"),
            today.strftime("%m/%d/%Y"),
            today,
            datetime.now()
        ]
        
        for date_value in test_cases:
            with self.subTest(date_value=date_value):
                result = InputValidator.validate_date(date_value)
                self.assertTrue(result.is_valid, f"Date {date_value} should be valid")
    
    def test_validate_date_invalid(self):
        """Test invalid date validation."""
        test_cases = [
            None,
            "",
            "invalid-date",
            "2023-13-01",  # Invalid month
            "2023-02-30",  # Invalid day
            123456,        # Invalid type
        ]
        
        for date_value in test_cases:
            with self.subTest(date_value=date_value):
                result = InputValidator.validate_date(date_value)
                self.assertFalse(result.is_valid, f"Date {date_value} should be invalid")
    
    def test_validate_date_warnings(self):
        """Test date validation warnings."""
        # Future date
        future_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
        result = InputValidator.validate_date(future_date)
        self.assertTrue(result.is_valid)
        self.assertTrue(len(result.warnings) > 0)
        
        # Very old date
        old_date = (date.today() - timedelta(days=4000)).strftime("%Y-%m-%d")
        result = InputValidator.validate_date(old_date)
        self.assertTrue(result.is_valid)
        self.assertTrue(len(result.warnings) > 0)
    
    def test_validate_description_valid(self):
        """Test valid description validation."""
        test_cases = [
            "Grocery shopping",
            "Coffee at Starbucks",
            "Monthly salary payment",
            "Gas bill - January 2024"
        ]
        
        for description in test_cases:
            with self.subTest(description=description):
                result = InputValidator.validate_description(description)
                self.assertTrue(result.is_valid, f"Description '{description}' should be valid")
    
    def test_validate_description_invalid(self):
        """Test invalid description validation."""
        test_cases = [
            None,
            "",
            "   ",  # Only whitespace
            "A",    # Too short
            "A" * 201,  # Too long
            "Invalid@#$%^&*()chars"  # Invalid characters
        ]
        
        for description in test_cases:
            with self.subTest(description=description):
                result = InputValidator.validate_description(description)
                self.assertFalse(result.is_valid, f"Description '{description}' should be invalid")
    
    def test_validate_transaction_type_valid(self):
        """Test valid transaction type validation."""
        test_cases = [
            TransactionType.INCOME,
            TransactionType.EXPENSE,
            "INCOME",
            "EXPENSE",
            "income",
            "expense"
        ]
        
        for t_type in test_cases:
            with self.subTest(t_type=t_type):
                result = InputValidator.validate_transaction_type(t_type)
                self.assertTrue(result.is_valid, f"Transaction type {t_type} should be valid")
    
    def test_validate_transaction_type_invalid(self):
        """Test invalid transaction type validation."""
        test_cases = [
            None,
            "",
            "INVALID",
            123,
            []
        ]
        
        for t_type in test_cases:
            with self.subTest(t_type=t_type):
                result = InputValidator.validate_transaction_type(t_type)
                self.assertFalse(result.is_valid, f"Transaction type {t_type} should be invalid")
    
    def test_validate_category_name_valid(self):
        """Test valid category name validation."""
        test_cases = [
            "Food",
            "Transportation",
            "Health Care",
            "Entertainment-Movies",
            "Utilities_Electric"
        ]
        
        for name in test_cases:
            with self.subTest(name=name):
                result = InputValidator.validate_category_name(name)
                self.assertTrue(result.is_valid, f"Category name '{name}' should be valid")
    
    def test_validate_category_name_invalid(self):
        """Test invalid category name validation."""
        test_cases = [
            None,
            "",
            "A",  # Too short
            "A" * 51,  # Too long
            "Invalid@#$%chars"  # Invalid characters
        ]
        
        for name in test_cases:
            with self.subTest(name=name):
                result = InputValidator.validate_category_name(name)
                self.assertFalse(result.is_valid, f"Category name '{name}' should be invalid")
    
    def test_validate_date_range_valid(self):
        """Test valid date range validation."""
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        
        result = InputValidator.validate_date_range(start_date, end_date)
        self.assertTrue(result.is_valid)
    
    def test_validate_date_range_invalid(self):
        """Test invalid date range validation."""
        # End date before start date
        start_date = "2024-01-31"
        end_date = "2024-01-01"
        
        result = InputValidator.validate_date_range(start_date, end_date)
        self.assertFalse(result.is_valid)
    
    def test_validate_file_path_valid(self):
        """Test valid file path validation."""
        test_cases = [
            "data.json",
            "exports/report.csv",
            "/home/user/expenses.xlsx"
        ]
        
        for path in test_cases:
            with self.subTest(path=path):
                result = InputValidator.validate_file_path(path)
                self.assertTrue(result.is_valid, f"File path '{path}' should be valid")
    
    def test_validate_file_path_invalid(self):
        """Test invalid file path validation."""
        test_cases = [
            None,
            "",
            "invalid<>path",  # Invalid characters
            "file|with|pipes"
        ]
        
        for path in test_cases:
            with self.subTest(path=path):
                result = InputValidator.validate_file_path(path)
                self.assertFalse(result.is_valid, f"File path '{path}' should be invalid")


class TestTransactionValidator(unittest.TestCase):
    """Test cases for TransactionValidator class."""
    
    def test_validate_transaction_data_valid(self):
        """Test valid transaction data validation."""
        result = TransactionValidator.validate_transaction_data(
            amount="50.00",
            description="Grocery shopping",
            transaction_type="EXPENSE",
            category="Food",
            transaction_date="2024-01-15"
        )
        
        self.assertTrue(result.is_valid)
    
    def test_validate_transaction_data_invalid(self):
        """Test invalid transaction data validation."""
        result = TransactionValidator.validate_transaction_data(
            amount=None,  # Invalid
            description="",  # Invalid
            transaction_type="INVALID",  # Invalid
            category="",  # Invalid
            transaction_date="invalid-date"  # Invalid
        )
        
        self.assertFalse(result.is_valid)
        self.assertTrue(len(result.errors) > 0)
    
    def test_validate_transaction_data_warnings(self):
        """Test transaction data validation warnings."""
        # Small income
        result = TransactionValidator.validate_transaction_data(
            amount="0.50",
            description="Small income",
            transaction_type="INCOME",
            category="Other"
        )
        
        self.assertTrue(result.is_valid)
        self.assertTrue(len(result.warnings) > 0)
        
        # Large expense
        result = TransactionValidator.validate_transaction_data(
            amount="5000.00",
            description="Large expense",
            transaction_type="EXPENSE",
            category="Other"
        )
        
        self.assertTrue(result.is_valid)
        self.assertTrue(len(result.warnings) > 0)


class TestCategoryValidator(unittest.TestCase):
    """Test cases for CategoryValidator class."""
    
    def test_validate_category_data_valid(self):
        """Test valid category data validation."""
        result = CategoryValidator.validate_category_data(
            name="Food",
            category_type="EXPENSE",
            description="Food and dining expenses"
        )
        
        self.assertTrue(result.is_valid)
    
    def test_validate_category_data_invalid(self):
        """Test invalid category data validation."""
        result = CategoryValidator.validate_category_data(
            name="",  # Invalid
            category_type="INVALID",  # Invalid
            description="A" * 201  # Too long
        )
        
        self.assertFalse(result.is_valid)
        self.assertTrue(len(result.errors) > 0)
    
    def test_validate_category_data_optional_description(self):
        """Test category validation with optional description."""
        # Without description
        result = CategoryValidator.validate_category_data(
            name="Food",
            category_type="EXPENSE"
        )
        
        self.assertTrue(result.is_valid)
        
        # With valid description
        result = CategoryValidator.validate_category_data(
            name="Food",
            category_type="EXPENSE",
            description="Food expenses"
        )
        
        self.assertTrue(result.is_valid)


if __name__ == '__main__':
    unittest.main()