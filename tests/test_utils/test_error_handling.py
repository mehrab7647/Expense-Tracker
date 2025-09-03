"""Unit tests for error handling utilities."""

import unittest
from unittest.mock import Mock, patch, mock_open
import tempfile
import os
import json
from datetime import datetime

from expense_tracker.utils.error_handling import (
    ExpenseTrackerError, DataError, ValidationError, FileOperationError,
    ServiceError, UIError, ConfigurationError, ErrorHandler, 
    BackupManager, DataIntegrityChecker, error_handler
)


class TestExpenseTrackerError(unittest.TestCase):
    """Test cases for ExpenseTrackerError class."""
    
    def test_init_basic(self):
        """Test basic error initialization."""
        error = ExpenseTrackerError("Test message")
        
        self.assertEqual(error.message, "Test message")
        self.assertEqual(error.error_code, "ExpenseTrackerError")
        self.assertEqual(error.details, {})
        self.assertIsInstance(error.timestamp, datetime)
    
    def test_init_with_details(self):
        """Test error initialization with details."""
        details = {"field": "amount", "value": "invalid"}
        error = ExpenseTrackerError("Test message", "TEST_ERROR", details)
        
        self.assertEqual(error.message, "Test message")
        self.assertEqual(error.error_code, "TEST_ERROR")
        self.assertEqual(error.details, details)
    
    def test_to_dict(self):
        """Test error serialization to dictionary."""
        error = ExpenseTrackerError("Test message", "TEST_ERROR", {"key": "value"})
        error_dict = error.to_dict()
        
        self.assertEqual(error_dict['error_type'], 'ExpenseTrackerError')
        self.assertEqual(error_dict['error_code'], 'TEST_ERROR')
        self.assertEqual(error_dict['message'], 'Test message')
        self.assertEqual(error_dict['details'], {"key": "value"})
        self.assertIn('timestamp', error_dict)
    
    def test_str_representation(self):
        """Test string representation of error."""
        error = ExpenseTrackerError("Test message", "TEST_ERROR")
        self.assertEqual(str(error), "TEST_ERROR: Test message")


class TestErrorHandler(unittest.TestCase):
    """Test cases for ErrorHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler('test_logger')
    
    def test_handle_error_basic(self):
        """Test basic error handling."""
        error = ValueError("Test error")
        
        with patch.object(self.handler.logger, 'log') as mock_log:
            result = self.handler.handle_error(error, "test_context")
            
            self.assertEqual(result['error_type'], 'ValueError')
            self.assertEqual(result['message'], 'Test error')
            self.assertEqual(result['context'], 'test_context')
            self.assertIn('user_message', result)
            self.assertEqual(result['count'], 1)
            
            mock_log.assert_called_once()
    
    def test_handle_custom_error(self):
        """Test handling of custom ExpenseTrackerError."""
        error = DataError("Data corruption detected", "DATA_CORRUPT", {"file": "test.json"})
        
        with patch.object(self.handler.logger, 'log') as mock_log:
            result = self.handler.handle_error(error)
            
            self.assertEqual(result['error_type'], 'DataError')
            self.assertEqual(result['error_code'], 'DATA_CORRUPT')
            self.assertIn('details', result)
            
            mock_log.assert_called_once()
    
    def test_error_counting(self):
        """Test error counting functionality."""
        error1 = ValueError("Error 1")
        error2 = ValueError("Error 2")
        error3 = TypeError("Different error")
        
        with patch.object(self.handler.logger, 'log'):
            self.handler.handle_error(error1)
            self.handler.handle_error(error2)
            self.handler.handle_error(error3)
        
        stats = self.handler.get_error_statistics()
        self.assertEqual(stats['total_errors'], 3)
        self.assertEqual(stats['error_counts']['ValueError'], 2)
        self.assertEqual(stats['error_counts']['TypeError'], 1)
        self.assertEqual(stats['most_common_error'], 'ValueError')
    
    def test_user_friendly_messages(self):
        """Test user-friendly message generation."""
        test_cases = [
            (ValueError("permission denied"), "permission"),
            (FileNotFoundError("file not found"), "not found"),
            (ConnectionError("connection failed"), "connection"),
        ]
        
        for error, expected_keyword in test_cases:
            with self.subTest(error=error):
                with patch.object(self.handler.logger, 'log'):
                    result = self.handler.handle_error(error)
                    self.assertIn(expected_keyword.lower(), result['user_message'].lower())
    
    def test_reset_statistics(self):
        """Test statistics reset functionality."""
        error = ValueError("Test error")
        
        with patch.object(self.handler.logger, 'log'):
            self.handler.handle_error(error)
        
        self.assertEqual(self.handler.get_error_statistics()['total_errors'], 1)
        
        self.handler.reset_statistics()
        self.assertEqual(self.handler.get_error_statistics()['total_errors'], 0)


class TestErrorHandlerDecorator(unittest.TestCase):
    """Test cases for error_handler decorator."""
    
    def test_decorator_success(self):
        """Test decorator with successful function execution."""
        @error_handler(context="test_function")
        def test_function(x, y):
            return x + y
        
        result = test_function(2, 3)
        self.assertEqual(result, 5)
    
    def test_decorator_with_exception_reraise(self):
        """Test decorator with exception and reraise=True."""
        @error_handler(context="test_function", reraise=True)
        def test_function():
            raise ValueError("Test error")
        
        with self.assertRaises(ValueError):
            test_function()
    
    def test_decorator_with_exception_no_reraise(self):
        """Test decorator with exception and reraise=False."""
        @error_handler(context="test_function", default_return="default")
        def test_function():
            raise ValueError("Test error")
        
        result = test_function()
        self.assertEqual(result, "default")


class TestBackupManager(unittest.TestCase):
    """Test cases for BackupManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, "test_data.json")
        self.backup_dir = os.path.join(self.temp_dir, "backups")
        
        # Create test data file
        test_data = {"transactions": [], "categories": []}
        with open(self.data_file, 'w') as f:
            json.dump(test_data, f)
        
        self.backup_manager = BackupManager(self.data_file, self.backup_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_backup(self):
        """Test backup creation."""
        backup_path = self.backup_manager.create_backup("test_backup.json")
        
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue(backup_path.endswith("test_backup.json"))
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        with open(self.data_file, 'r') as f:
            original_data = json.load(f)
        
        self.assertEqual(backup_data, original_data)
    
    def test_create_backup_auto_name(self):
        """Test backup creation with automatic naming."""
        backup_path = self.backup_manager.create_backup()
        
        self.assertTrue(os.path.exists(backup_path))
        self.assertIn("expense_data_backup_", os.path.basename(backup_path))
    
    def test_create_backup_missing_file(self):
        """Test backup creation with missing data file."""
        os.remove(self.data_file)
        
        with self.assertRaises(FileOperationError):
            self.backup_manager.create_backup()
    
    def test_restore_backup(self):
        """Test backup restoration."""
        # Create a backup
        backup_path = self.backup_manager.create_backup("test_backup.json")
        
        # Modify original data
        modified_data = {"transactions": [{"id": "test"}], "categories": []}
        with open(self.data_file, 'w') as f:
            json.dump(modified_data, f)
        
        # Restore from backup
        success = self.backup_manager.restore_backup(backup_path)
        self.assertTrue(success)
        
        # Verify restoration
        with open(self.data_file, 'r') as f:
            restored_data = json.load(f)
        
        self.assertEqual(restored_data["transactions"], [])
    
    def test_restore_backup_missing_file(self):
        """Test backup restoration with missing backup file."""
        with self.assertRaises(FileOperationError):
            self.backup_manager.restore_backup("nonexistent_backup.json")
    
    def test_list_backups(self):
        """Test backup listing."""
        # Create some backups
        self.backup_manager.create_backup("backup1.json")
        self.backup_manager.create_backup("backup2.json")
        
        backups = self.backup_manager.list_backups()
        
        self.assertEqual(len(backups), 2)
        self.assertTrue(all('filename' in backup for backup in backups))
        self.assertTrue(all('created' in backup for backup in backups))
    
    def test_cleanup_old_backups(self):
        """Test cleanup of old backups."""
        # Create multiple backups
        for i in range(5):
            self.backup_manager.create_backup(f"backup{i}.json")
        
        # Keep only 3 backups
        deleted_count = self.backup_manager.cleanup_old_backups(keep_count=3)
        
        self.assertEqual(deleted_count, 2)
        
        remaining_backups = self.backup_manager.list_backups()
        self.assertEqual(len(remaining_backups), 3)


class TestDataIntegrityChecker(unittest.TestCase):
    """Test cases for DataIntegrityChecker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.checker = DataIntegrityChecker()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_valid_data_file(self):
        """Test validation of valid data file."""
        valid_data = {
            "transactions": [
                {
                    "id": "1",
                    "amount": 100.0,
                    "description": "Test transaction",
                    "type": "EXPENSE",
                    "category": "Food",
                    "date": "2024-01-01T00:00:00"
                }
            ],
            "categories": [
                {
                    "name": "Food",
                    "type": "EXPENSE"
                }
            ]
        }
        
        data_file = os.path.join(self.temp_dir, "valid_data.json")
        with open(data_file, 'w') as f:
            json.dump(valid_data, f)
        
        results = self.checker.validate_data_file(data_file)
        
        self.assertTrue(results['is_valid'])
        self.assertEqual(len(results['errors']), 0)
        self.assertIn('statistics', results)
    
    def test_validate_invalid_data_file(self):
        """Test validation of invalid data file."""
        invalid_data = {
            "transactions": [
                {
                    "id": "1",
                    # Missing required fields
                    "amount": "invalid_amount"
                }
            ],
            "categories": [
                {
                    # Missing required fields
                }
            ]
        }
        
        data_file = os.path.join(self.temp_dir, "invalid_data.json")
        with open(data_file, 'w') as f:
            json.dump(invalid_data, f)
        
        results = self.checker.validate_data_file(data_file)
        
        self.assertFalse(results['is_valid'])
        self.assertTrue(len(results['errors']) > 0)
    
    def test_validate_missing_file(self):
        """Test validation of missing data file."""
        results = self.checker.validate_data_file("nonexistent_file.json")
        
        self.assertFalse(results['is_valid'])
        self.assertIn("Data file not found", results['errors'][0])
    
    def test_validate_invalid_json(self):
        """Test validation of invalid JSON file."""
        data_file = os.path.join(self.temp_dir, "invalid_json.json")
        with open(data_file, 'w') as f:
            f.write("{ invalid json }")
        
        results = self.checker.validate_data_file(data_file)
        
        self.assertFalse(results['is_valid'])
        self.assertTrue(any("Invalid JSON format" in error for error in results['errors']))
    
    def test_validate_duplicate_transaction_ids(self):
        """Test validation with duplicate transaction IDs."""
        data_with_duplicates = {
            "transactions": [
                {
                    "id": "1",
                    "amount": 100.0,
                    "description": "Transaction 1",
                    "type": "EXPENSE",
                    "category": "Food",
                    "date": "2024-01-01T00:00:00"
                },
                {
                    "id": "1",  # Duplicate ID
                    "amount": 200.0,
                    "description": "Transaction 2",
                    "type": "EXPENSE",
                    "category": "Food",
                    "date": "2024-01-02T00:00:00"
                }
            ],
            "categories": []
        }
        
        data_file = os.path.join(self.temp_dir, "duplicate_ids.json")
        with open(data_file, 'w') as f:
            json.dump(data_with_duplicates, f)
        
        results = self.checker.validate_data_file(data_file)
        
        self.assertFalse(results['is_valid'])
        self.assertTrue(any("Duplicate transaction ID" in error for error in results['errors']))


if __name__ == '__main__':
    unittest.main()