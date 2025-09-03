"""Comprehensive error handling utilities for the expense tracker application."""

import logging
import traceback
import sys
from typing import Optional, Dict, Any, Callable
from functools import wraps
from datetime import datetime
import json


class ExpenseTrackerError(Exception):
    """Base exception class for expense tracker application."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __str__(self):
        return f"{self.error_code}: {self.message}"


class DataError(ExpenseTrackerError):
    """Exception for data-related errors."""
    pass


class ValidationError(ExpenseTrackerError):
    """Exception for validation errors."""
    pass


class FileOperationError(ExpenseTrackerError):
    """Exception for file operation errors."""
    pass


class ServiceError(ExpenseTrackerError):
    """Exception for service layer errors."""
    pass


class UIError(ExpenseTrackerError):
    """Exception for user interface errors."""
    pass


class ConfigurationError(ExpenseTrackerError):
    """Exception for configuration errors."""
    pass


class ErrorHandler:
    """Centralized error handling and logging system."""
    
    def __init__(self, logger_name: str = 'expense_tracker'):
        self.logger = logging.getLogger(logger_name)
        self._error_counts = {}
        self._user_friendly_messages = {
            'DataError': 'There was a problem with your data. Please check and try again.',
            'ValidationError': 'The information you entered is not valid. Please correct it and try again.',
            'FileOperationError': 'There was a problem accessing the data file. Please check file permissions.',
            'ServiceError': 'A service error occurred. Please try again later.',
            'UIError': 'There was a problem with the user interface. Please restart the application.',
            'ConfigurationError': 'There is a configuration problem. Please check your settings.',
            'ConnectionError': 'Unable to connect to required services. Please check your connection.',
            'PermissionError': 'You do not have permission to perform this action.',
            'FileNotFoundError': 'The required file was not found. Please check the file path.',
            'ValueError': 'Invalid value provided. Please check your input.',
            'TypeError': 'Incorrect data type provided. Please check your input.',
            'KeyError': 'Required information is missing. Please provide all necessary details.',
            'IndexError': 'Data access error. The requested item may not exist.',
            'AttributeError': 'Internal error occurred. Please restart the application.',
        }
    
    def handle_error(self, error: Exception, context: str = None, 
                    user_message: str = None, log_level: int = logging.ERROR) -> Dict[str, Any]:
        """
        Handle an error with logging and user-friendly message generation.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            user_message: Custom user-friendly message
            log_level: Logging level for this error
            
        Returns:
            Dictionary containing error information and user message
        """
        error_type = type(error).__name__
        
        # Count error occurrences
        self._error_counts[error_type] = self._error_counts.get(error_type, 0) + 1
        
        # Create error info
        error_info = {
            'error_type': error_type,
            'message': str(error),
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'count': self._error_counts[error_type]
        }
        
        # Add details for custom exceptions
        if isinstance(error, ExpenseTrackerError):
            error_info.update(error.to_dict())
        
        # Log the error
        log_message = f"Error in {context}: {error_type} - {str(error)}"
        if hasattr(error, 'details'):
            log_message += f" | Details: {error.details}"
        
        self.logger.log(log_level, log_message, exc_info=True)
        
        # Generate user-friendly message
        if user_message:
            friendly_message = user_message
        else:
            friendly_message = self._get_user_friendly_message(error_type, str(error))
        
        error_info['user_message'] = friendly_message
        
        return error_info
    
    def _get_user_friendly_message(self, error_type: str, error_message: str) -> str:
        """Generate a user-friendly error message."""
        base_message = self._user_friendly_messages.get(error_type, 
                                                       'An unexpected error occurred. Please try again.')
        
        # Add specific guidance for common errors
        if 'permission' in error_message.lower():
            return "You don't have permission to access this file. Please check file permissions or run as administrator."
        elif 'not found' in error_message.lower():
            return "The required file or data was not found. Please check the file path and try again."
        elif 'connection' in error_message.lower():
            return "Unable to establish connection. Please check your network and try again."
        elif 'disk' in error_message.lower() or 'space' in error_message.lower():
            return "Not enough disk space available. Please free up some space and try again."
        elif 'corrupt' in error_message.lower():
            return "The data file appears to be corrupted. Please restore from a backup or contact support."
        
        return base_message
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        return {
            'error_counts': self._error_counts.copy(),
            'total_errors': sum(self._error_counts.values()),
            'most_common_error': max(self._error_counts.items(), key=lambda x: x[1])[0] if self._error_counts else None
        }
    
    def reset_statistics(self):
        """Reset error statistics."""
        self._error_counts.clear()


def error_handler(context: str = None, user_message: str = None, 
                 reraise: bool = False, default_return: Any = None):
    """
    Decorator for automatic error handling.
    
    Args:
        context: Context description for the error
        user_message: Custom user-friendly message
        reraise: Whether to reraise the exception after handling
        default_return: Default value to return if error occurs and not reraising
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get error handler instance (create if needed)
                handler = getattr(wrapper, '_error_handler', None)
                if handler is None:
                    handler = ErrorHandler()
                    wrapper._error_handler = handler
                
                # Handle the error
                error_info = handler.handle_error(
                    e, 
                    context or f"{func.__module__}.{func.__name__}",
                    user_message
                )
                
                if reraise:
                    raise
                else:
                    return default_return
        
        return wrapper
    return decorator


class BackupManager:
    """Manages data backup and recovery operations."""
    
    def __init__(self, data_file_path: str, backup_dir: str = "backups"):
        self.data_file_path = data_file_path
        self.backup_dir = backup_dir
        self.logger = logging.getLogger('expense_tracker.backup')
        
        # Ensure backup directory exists
        import os
        os.makedirs(backup_dir, exist_ok=True)
    
    @error_handler(context="backup_creation", user_message="Failed to create backup")
    def create_backup(self, backup_name: str = None) -> str:
        """
        Create a backup of the data file.
        
        Args:
            backup_name: Custom backup name (optional)
            
        Returns:
            Path to the created backup file
        """
        import os
        import shutil
        
        if not os.path.exists(self.data_file_path):
            raise FileOperationError(f"Data file not found: {self.data_file_path}")
        
        # Generate backup filename
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"expense_data_backup_{timestamp}.json"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # Create backup
        shutil.copy2(self.data_file_path, backup_path)
        
        self.logger.info(f"Backup created: {backup_path}")
        return backup_path
    
    @error_handler(context="backup_restoration", user_message="Failed to restore from backup")
    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore data from a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            True if restoration was successful
        """
        import os
        import shutil
        
        if not os.path.exists(backup_path):
            raise FileOperationError(f"Backup file not found: {backup_path}")
        
        # Create backup of current data before restoration
        if os.path.exists(self.data_file_path):
            current_backup = self.create_backup("pre_restore_backup")
            self.logger.info(f"Current data backed up to: {current_backup}")
        
        # Restore from backup
        shutil.copy2(backup_path, self.data_file_path)
        
        self.logger.info(f"Data restored from: {backup_path}")
        return True
    
    def list_backups(self) -> list:
        """List available backup files."""
        import os
        
        if not os.path.exists(self.backup_dir):
            return []
        
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime),
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    @error_handler(context="backup_cleanup", user_message="Failed to clean up old backups")
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Clean up old backup files, keeping only the most recent ones.
        
        Args:
            keep_count: Number of backups to keep
            
        Returns:
            Number of backups deleted
        """
        import os
        
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return 0
        
        # Delete old backups
        deleted_count = 0
        for backup in backups[keep_count:]:
            try:
                os.remove(backup['path'])
                deleted_count += 1
                self.logger.info(f"Deleted old backup: {backup['filename']}")
            except OSError as e:
                self.logger.warning(f"Failed to delete backup {backup['filename']}: {e}")
        
        return deleted_count


class DataIntegrityChecker:
    """Validates data integrity and consistency."""
    
    def __init__(self):
        self.logger = logging.getLogger('expense_tracker.integrity')
    
    @error_handler(context="data_validation", user_message="Data validation failed")
    def validate_data_file(self, data_file_path: str) -> Dict[str, Any]:
        """
        Validate the integrity of a data file.
        
        Args:
            data_file_path: Path to the data file
            
        Returns:
            Dictionary with validation results
        """
        import os
        
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # Check if file exists
        if not os.path.exists(data_file_path):
            results['errors'].append(f"Data file not found: {data_file_path}")
            results['is_valid'] = False
            return results
        
        try:
            # Load and parse JSON
            with open(data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            self._validate_data_structure(data, results)
            
            # Validate transactions
            if 'transactions' in data:
                self._validate_transactions(data['transactions'], results)
            
            # Validate categories
            if 'categories' in data:
                self._validate_categories(data['categories'], results)
            
            # Generate statistics
            self._generate_statistics(data, results)
            
        except json.JSONDecodeError as e:
            results['errors'].append(f"Invalid JSON format: {e}")
            results['is_valid'] = False
        except Exception as e:
            results['errors'].append(f"Validation error: {e}")
            results['is_valid'] = False
        
        return results
    
    def _validate_data_structure(self, data: Dict[str, Any], results: Dict[str, Any]):
        """Validate the basic structure of the data."""
        required_keys = ['transactions', 'categories']
        
        for key in required_keys:
            if key not in data:
                results['errors'].append(f"Missing required key: {key}")
                results['is_valid'] = False
            elif not isinstance(data[key], list):
                results['errors'].append(f"Key '{key}' must be a list")
                results['is_valid'] = False
    
    def _validate_transactions(self, transactions: list, results: Dict[str, Any]):
        """Validate transaction data."""
        transaction_ids = set()
        
        for i, transaction in enumerate(transactions):
            if not isinstance(transaction, dict):
                results['errors'].append(f"Transaction {i} is not a dictionary")
                results['is_valid'] = False
                continue
            
            # Check required fields
            required_fields = ['id', 'amount', 'description', 'type', 'category', 'date']
            for field in required_fields:
                if field not in transaction:
                    results['errors'].append(f"Transaction {i} missing field: {field}")
                    results['is_valid'] = False
            
            # Check for duplicate IDs
            if 'id' in transaction:
                if transaction['id'] in transaction_ids:
                    results['errors'].append(f"Duplicate transaction ID: {transaction['id']}")
                    results['is_valid'] = False
                else:
                    transaction_ids.add(transaction['id'])
            
            # Validate amount
            if 'amount' in transaction:
                try:
                    amount = float(transaction['amount'])
                    if amount <= 0:
                        results['warnings'].append(f"Transaction {i} has non-positive amount")
                except (ValueError, TypeError):
                    results['errors'].append(f"Transaction {i} has invalid amount")
                    results['is_valid'] = False
            
            # Validate date
            if 'date' in transaction:
                try:
                    datetime.fromisoformat(transaction['date'].replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    results['errors'].append(f"Transaction {i} has invalid date format")
                    results['is_valid'] = False
    
    def _validate_categories(self, categories: list, results: Dict[str, Any]):
        """Validate category data."""
        category_names = set()
        
        for i, category in enumerate(categories):
            if not isinstance(category, dict):
                results['errors'].append(f"Category {i} is not a dictionary")
                results['is_valid'] = False
                continue
            
            # Check required fields
            required_fields = ['name', 'type']
            for field in required_fields:
                if field not in category:
                    results['errors'].append(f"Category {i} missing field: {field}")
                    results['is_valid'] = False
            
            # Check for duplicate names
            if 'name' in category:
                if category['name'] in category_names:
                    results['warnings'].append(f"Duplicate category name: {category['name']}")
                else:
                    category_names.add(category['name'])
    
    def _generate_statistics(self, data: Dict[str, Any], results: Dict[str, Any]):
        """Generate data statistics."""
        stats = {}
        
        if 'transactions' in data:
            stats['total_transactions'] = len(data['transactions'])
            
            # Calculate totals
            total_income = 0
            total_expenses = 0
            
            for transaction in data['transactions']:
                if isinstance(transaction, dict) and 'amount' in transaction and 'type' in transaction:
                    try:
                        amount = float(transaction['amount'])
                        if transaction['type'].upper() == 'INCOME':
                            total_income += amount
                        elif transaction['type'].upper() == 'EXPENSE':
                            total_expenses += amount
                    except (ValueError, TypeError):
                        pass
            
            stats['total_income'] = total_income
            stats['total_expenses'] = total_expenses
            stats['net_balance'] = total_income - total_expenses
        
        if 'categories' in data:
            stats['total_categories'] = len(data['categories'])
        
        results['statistics'] = stats