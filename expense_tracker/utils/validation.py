"""Input validation utilities for the expense tracker application."""

import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, List, Tuple, Any
from enum import Enum

from ..models.transaction import TransactionType
from ..models.category import CategoryType


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.message = message
        self.field = field
    
    def __str__(self):
        if self.field:
            return f"{self.field}: {self.message}"
        return self.message


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add an error to the result."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)
    
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False


class InputValidator:
    """Comprehensive input validation utilities."""
    
    # Constants for validation
    MIN_AMOUNT = Decimal('0.01')
    MAX_AMOUNT = Decimal('999999999.99')
    MIN_DATE = date(1900, 1, 1)
    MAX_DATE = date(2100, 12, 31)
    
    # Regex patterns
    DESCRIPTION_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_.,!?()]+$')
    CATEGORY_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_]+$')
    
    @staticmethod
    def validate_amount(amount: Any, field_name: str = "Amount") -> ValidationResult:
        """
        Validate a monetary amount.
        
        Args:
            amount: The amount to validate
            field_name: Name of the field for error messages
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult()
        
        if amount is None:
            result.add_error(f"{field_name} is required")
            return result
        
        # Convert to string first if needed
        if not isinstance(amount, (str, int, float, Decimal)):
            result.add_error(f"{field_name} must be a number")
            return result
        
        try:
            # Convert to Decimal for precise validation
            decimal_amount = Decimal(str(amount))
            
            # Check if amount is positive
            if decimal_amount <= 0:
                result.add_error(f"{field_name} must be greater than zero")
            
            # Check minimum amount
            elif decimal_amount < InputValidator.MIN_AMOUNT:
                result.add_error(f"{field_name} must be at least ${InputValidator.MIN_AMOUNT}")
            
            # Check maximum amount
            elif decimal_amount > InputValidator.MAX_AMOUNT:
                result.add_error(f"{field_name} cannot exceed ${InputValidator.MAX_AMOUNT:,}")
            
            # Check decimal places (max 2)
            elif decimal_amount.as_tuple().exponent < -2:
                result.add_error(f"{field_name} cannot have more than 2 decimal places")
            
            # Add warnings for large amounts
            elif decimal_amount > Decimal('10000'):
                result.add_warning(f"{field_name} is unusually large (${decimal_amount:,})")
                
        except (InvalidOperation, ValueError, TypeError):
            result.add_error(f"{field_name} must be a valid number")
        
        return result
    
    @staticmethod
    def validate_date(date_value: Any, field_name: str = "Date") -> ValidationResult:
        """
        Validate a date value.
        
        Args:
            date_value: The date to validate (string, date, or datetime)
            field_name: Name of the field for error messages
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult()
        
        if date_value is None:
            result.add_error(f"{field_name} is required")
            return result
        
        try:
            # Handle different input types
            if isinstance(date_value, str):
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                    try:
                        parsed_date = datetime.strptime(date_value, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    result.add_error(f"{field_name} must be in format YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY")
                    return result
            
            elif isinstance(date_value, datetime):
                parsed_date = date_value.date()
            
            elif isinstance(date_value, date):
                parsed_date = date_value
            
            else:
                result.add_error(f"{field_name} must be a valid date")
                return result
            
            # Check date range
            if parsed_date < InputValidator.MIN_DATE:
                result.add_error(f"{field_name} cannot be before {InputValidator.MIN_DATE}")
            
            elif parsed_date > InputValidator.MAX_DATE:
                result.add_error(f"{field_name} cannot be after {InputValidator.MAX_DATE}")
            
            # Check if date is in the future
            elif parsed_date > date.today():
                result.add_warning(f"{field_name} is in the future")
            
            # Check if date is very old
            elif parsed_date < date.today().replace(year=date.today().year - 10):
                result.add_warning(f"{field_name} is more than 10 years old")
                
        except (ValueError, TypeError) as e:
            result.add_error(f"{field_name} is not a valid date: {str(e)}")
        
        return result
    
    @staticmethod
    def validate_description(description: Any, field_name: str = "Description") -> ValidationResult:
        """
        Validate a transaction description.
        
        Args:
            description: The description to validate
            field_name: Name of the field for error messages
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult()
        
        if description is None:
            result.add_error(f"{field_name} is required")
            return result
        
        if not isinstance(description, str):
            result.add_error(f"{field_name} must be text")
            return result
        
        # Check length
        description = description.strip()
        if len(description) == 0:
            result.add_error(f"{field_name} cannot be empty")
        
        elif len(description) < 2:
            result.add_error(f"{field_name} must be at least 2 characters long")
        
        elif len(description) > 200:
            result.add_error(f"{field_name} cannot exceed 200 characters")
        
        # Check for valid characters
        elif not InputValidator.DESCRIPTION_PATTERN.match(description):
            result.add_error(f"{field_name} contains invalid characters")
        
        # Add warnings
        elif len(description) > 100:
            result.add_warning(f"{field_name} is quite long ({len(description)} characters)")
        
        return result
    
    @staticmethod
    def validate_transaction_type(transaction_type: Any, field_name: str = "Transaction Type") -> ValidationResult:
        """
        Validate a transaction type.
        
        Args:
            transaction_type: The transaction type to validate
            field_name: Name of the field for error messages
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult()
        
        if transaction_type is None:
            result.add_error(f"{field_name} is required")
            return result
        
        # Handle string input
        if isinstance(transaction_type, str):
            try:
                transaction_type = TransactionType(transaction_type.upper())
            except ValueError:
                valid_types = [t.value for t in TransactionType]
                result.add_error(f"{field_name} must be one of: {', '.join(valid_types)}")
                return result
        
        # Check if it's a valid TransactionType enum
        elif not isinstance(transaction_type, TransactionType):
            result.add_error(f"{field_name} must be a valid transaction type")
        
        return result
    
    @staticmethod
    def validate_category_name(category_name: Any, field_name: str = "Category") -> ValidationResult:
        """
        Validate a category name.
        
        Args:
            category_name: The category name to validate
            field_name: Name of the field for error messages
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult()
        
        if category_name is None:
            result.add_error(f"{field_name} is required")
            return result
        
        if not isinstance(category_name, str):
            result.add_error(f"{field_name} must be text")
            return result
        
        # Check length
        category_name = category_name.strip()
        if len(category_name) == 0:
            result.add_error(f"{field_name} cannot be empty")
        
        elif len(category_name) < 2:
            result.add_error(f"{field_name} must be at least 2 characters long")
        
        elif len(category_name) > 50:
            result.add_error(f"{field_name} cannot exceed 50 characters")
        
        # Check for valid characters
        elif not InputValidator.CATEGORY_NAME_PATTERN.match(category_name):
            result.add_error(f"{field_name} can only contain letters, numbers, spaces, hyphens, and underscores")
        
        return result
    
    @staticmethod
    def validate_category_type(category_type: Any, field_name: str = "Category Type") -> ValidationResult:
        """
        Validate a category type.
        
        Args:
            category_type: The category type to validate
            field_name: Name of the field for error messages
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult()
        
        if category_type is None:
            result.add_error(f"{field_name} is required")
            return result
        
        # Handle string input
        if isinstance(category_type, str):
            try:
                category_type = CategoryType(category_type.upper())
            except ValueError:
                valid_types = [t.value for t in CategoryType]
                result.add_error(f"{field_name} must be one of: {', '.join(valid_types)}")
                return result
        
        # Check if it's a valid CategoryType enum
        elif not isinstance(category_type, CategoryType):
            result.add_error(f"{field_name} must be a valid category type")
        
        return result
    
    @staticmethod
    def validate_date_range(start_date: Any, end_date: Any) -> ValidationResult:
        """
        Validate a date range.
        
        Args:
            start_date: The start date
            end_date: The end date
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult()
        
        # Validate individual dates
        start_result = InputValidator.validate_date(start_date, "Start Date")
        end_result = InputValidator.validate_date(end_date, "End Date")
        
        result.merge(start_result)
        result.merge(end_result)
        
        # If individual dates are valid, check range
        if start_result.is_valid and end_result.is_valid:
            try:
                # Convert to date objects for comparison
                if isinstance(start_date, str):
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                elif isinstance(start_date, datetime):
                    start_date = start_date.date()
                
                if isinstance(end_date, str):
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                elif isinstance(end_date, datetime):
                    end_date = end_date.date()
                
                if start_date > end_date:
                    result.add_error("Start date must be before or equal to end date")
                
                # Check for very large date ranges
                elif (end_date - start_date).days > 3650:  # 10 years
                    result.add_warning("Date range is very large (more than 10 years)")
                    
            except (ValueError, TypeError):
                result.add_error("Invalid date range")
        
        return result
    
    @staticmethod
    def validate_file_path(file_path: Any, field_name: str = "File Path", 
                          must_exist: bool = False, extension: str = None) -> ValidationResult:
        """
        Validate a file path.
        
        Args:
            file_path: The file path to validate
            field_name: Name of the field for error messages
            must_exist: Whether the file must already exist
            extension: Required file extension (without dot)
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult()
        
        if file_path is None:
            result.add_error(f"{field_name} is required")
            return result
        
        if not isinstance(file_path, str):
            result.add_error(f"{field_name} must be a valid path")
            return result
        
        file_path = file_path.strip()
        if len(file_path) == 0:
            result.add_error(f"{field_name} cannot be empty")
            return result
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in file_path for char in invalid_chars):
            result.add_error(f"{field_name} contains invalid characters")
        
        # Check extension if specified
        if extension and not file_path.lower().endswith(f'.{extension.lower()}'):
            result.add_error(f"{field_name} must have .{extension} extension")
        
        # Check if file exists when required
        if must_exist:
            import os
            if not os.path.exists(file_path):
                result.add_error(f"{field_name} does not exist")
        
        return result


class TransactionValidator:
    """Specialized validator for transaction data."""
    
    @staticmethod
    def validate_transaction_data(amount: Any, description: Any, transaction_type: Any, 
                                category: Any, transaction_date: Any = None) -> ValidationResult:
        """
        Validate complete transaction data.
        
        Args:
            amount: Transaction amount
            description: Transaction description
            transaction_type: Transaction type
            category: Transaction category
            transaction_date: Transaction date (optional, defaults to today)
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult()
        
        # Validate each field
        result.merge(InputValidator.validate_amount(amount))
        result.merge(InputValidator.validate_description(description))
        result.merge(InputValidator.validate_transaction_type(transaction_type))
        result.merge(InputValidator.validate_category_name(category))
        
        if transaction_date is not None:
            result.merge(InputValidator.validate_date(transaction_date))
        
        # Cross-field validation
        if result.is_valid:
            # Check if transaction type matches category expectations
            try:
                t_type = TransactionType(transaction_type) if isinstance(transaction_type, str) else transaction_type
                
                # Add business logic warnings
                if t_type == TransactionType.INCOME and float(amount) < 1:
                    result.add_warning("Income amount seems unusually small")
                elif t_type == TransactionType.EXPENSE and float(amount) > 1000:
                    result.add_warning("Expense amount is quite large")
                    
            except (ValueError, TypeError):
                pass  # Already handled by individual field validation
        
        return result


class CategoryValidator:
    """Specialized validator for category data."""
    
    @staticmethod
    def validate_category_data(name: Any, category_type: Any, description: Any = None) -> ValidationResult:
        """
        Validate complete category data.
        
        Args:
            name: Category name
            category_type: Category type
            description: Category description (optional)
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult()
        
        # Validate required fields
        result.merge(InputValidator.validate_category_name(name))
        result.merge(InputValidator.validate_category_type(category_type))
        
        # Validate optional description
        if description is not None:
            result.merge(InputValidator.validate_description(description, "Category Description"))
        
        return result