"""Unit tests for ApplicationController."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path
from decimal import Decimal
from datetime import datetime

from expense_tracker.controllers.app_controller import ApplicationController
from expense_tracker.models.transaction import Transaction
from expense_tracker.models.category import Category
from expense_tracker.models.enums import TransactionType, CategoryType


class TestApplicationController(unittest.TestCase):
    """Test cases for ApplicationController."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_file = os.path.join(self.temp_dir, "test_data.json")
        
        # Sample data for testing
        self.sample_transaction = Transaction(
            id='1',
            amount=Decimal('100.50'),
            description='Test transaction',
            category='Food',
            transaction_type=TransactionType.EXPENSE,
            date=datetime(2024, 1, 15)
        )
        
        self.sample_category = Category('Food', CategoryType.EXPENSE, True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_initialization_with_custom_data_path(self, mock_logging):
        """Test controller initialization with custom data path."""
        controller = ApplicationController(
            data_file_path=self.test_data_file,
            log_level="DEBUG"
        )
        
        self.assertEqual(controller.data_file_path, self.test_data_file)
        self.assertEqual(controller.log_level, "DEBUG")
        self.assertFalse(controller.is_running)
        self.assertIsNone(controller.current_interface)
        
        # Verify services are initialized
        self.assertIsNotNone(controller.repository)
        self.assertIsNotNone(controller.transaction_service)
        self.assertIsNotNone(controller.category_service)
        self.assertIsNotNone(controller.report_service)
        self.assertIsNotNone(controller.export_service)
        self.assertIsNotNone(controller.chart_service)
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_initialization_with_default_data_path(self, mock_logging):
        """Test controller initialization with default data path."""
        with patch('pathlib.Path.mkdir'):
            controller = ApplicationController()
            
            # Should create default path
            self.assertTrue(controller.data_file_path.endswith('expense_data.json'))
            self.assertEqual(controller.log_level, "INFO")
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_get_application_info_with_data(self, mock_logging):
        """Test getting application info when data exists."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        # Mock services to return test data
        controller.transaction_service.get_all_transactions = Mock(return_value=[self.sample_transaction])
        controller.category_service.get_all_categories = Mock(return_value=[self.sample_category])
        controller.transaction_service.get_transaction_summary = Mock(return_value={
            'total_income': Decimal('1000'),
            'total_expenses': Decimal('500'),
            'net_balance': Decimal('500')
        })
        
        # Create test data file
        with open(self.test_data_file, 'w') as f:
            f.write('{"test": "data"}')
        
        info = controller.get_application_info()
        
        self.assertEqual(info['version'], '1.0.0')
        self.assertEqual(info['data_file'], self.test_data_file)
        self.assertTrue(info['data_file_exists'])
        self.assertFalse(info['is_running'])
        self.assertIsNone(info['current_interface'])
        self.assertEqual(info['total_transactions'], 1)
        self.assertEqual(info['total_categories'], 1)
        self.assertEqual(info['total_income'], 1000.0)
        self.assertEqual(info['total_expenses'], 500.0)
        self.assertEqual(info['net_balance'], 500.0)
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_get_application_info_no_data(self, mock_logging):
        """Test getting application info when no data exists."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        info = controller.get_application_info()
        
        self.assertEqual(info['version'], '1.0.0')
        self.assertEqual(info['data_file'], self.test_data_file)
        self.assertFalse(info['data_file_exists'])
        self.assertEqual(info['total_transactions'], 0)
        self.assertEqual(info['total_categories'], 0)
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_validate_data_integrity_no_file(self, mock_logging):
        """Test data integrity validation when no data file exists."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        result = controller.validate_data_integrity()
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(len(result['warnings']), 1)
        self.assertIn("Data file does not exist", result['warnings'][0])
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_validate_data_integrity_with_valid_data(self, mock_logging):
        """Test data integrity validation with valid data."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        # Create test data file
        with open(self.test_data_file, 'w') as f:
            f.write('{"test": "data"}')
        
        # Mock services to return valid data
        controller.transaction_service.get_all_transactions = Mock(return_value=[self.sample_transaction])
        controller.category_service.get_all_categories = Mock(return_value=[self.sample_category])
        
        result = controller.validate_data_integrity()
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(result['statistics']['total_transactions'], 1)
        self.assertEqual(result['statistics']['total_categories'], 1)
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_validate_data_integrity_with_duplicate_ids(self, mock_logging):
        """Test data integrity validation with duplicate transaction IDs."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        # Create test data file
        with open(self.test_data_file, 'w') as f:
            f.write('{"test": "data"}')
        
        # Mock services to return duplicate IDs
        duplicate_transaction = Transaction(
            id='1',  # Same ID as sample_transaction
            amount=Decimal('200'),
            description='Duplicate',
            category='Food',
            transaction_type=TransactionType.EXPENSE,
            date=datetime(2024, 1, 16)
        )
        
        controller.transaction_service.get_all_transactions = Mock(
            return_value=[self.sample_transaction, duplicate_transaction]
        )
        controller.category_service.get_all_categories = Mock(return_value=[self.sample_category])
        
        result = controller.validate_data_integrity()
        
        self.assertFalse(result['is_valid'])
        self.assertIn("Duplicate transaction IDs found", result['errors'])
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_backup_data_success(self, mock_logging):
        """Test successful data backup."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        # Create test data file
        test_content = '{"test": "data"}'
        with open(self.test_data_file, 'w') as f:
            f.write(test_content)
        
        backup_path = os.path.join(self.temp_dir, "backup.json")
        
        result = controller.backup_data(backup_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(backup_path))
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_content = f.read()
        
        self.assertEqual(backup_content, test_content)
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_backup_data_no_source_file(self, mock_logging):
        """Test backup when source data file doesn't exist."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        backup_path = os.path.join(self.temp_dir, "backup.json")
        
        result = controller.backup_data(backup_path)
        
        self.assertFalse(result)
        self.assertFalse(os.path.exists(backup_path))
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_restore_data_success(self, mock_logging):
        """Test successful data restore."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        # Create backup file
        backup_path = os.path.join(self.temp_dir, "backup.json")
        backup_content = '{"restored": "data"}'
        with open(backup_path, 'w') as f:
            f.write(backup_content)
        
        result = controller.restore_data(backup_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_data_file))
        
        # Verify restored content
        with open(self.test_data_file, 'r') as f:
            restored_content = f.read()
        
        self.assertEqual(restored_content, backup_content)
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_restore_data_backup_not_found(self, mock_logging):
        """Test restore when backup file doesn't exist."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        backup_path = os.path.join(self.temp_dir, "nonexistent_backup.json")
        
        result = controller.restore_data(backup_path)
        
        self.assertFalse(result)
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_get_service_status_all_healthy(self, mock_logging):
        """Test getting service status when all services are healthy."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        # Mock all services to work properly
        controller.transaction_service.get_all_transactions = Mock(return_value=[])
        controller.category_service.get_all_categories = Mock(return_value=[])
        controller.chart_service.is_matplotlib_available = Mock(return_value=True)
        
        status = controller.get_service_status()
        
        expected_services = [
            'repository', 'transaction_service', 'category_service',
            'report_service', 'export_service', 'chart_service'
        ]
        
        for service in expected_services:
            self.assertIn(service, status)
            self.assertTrue(status[service])
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_get_service_status_with_failures(self, mock_logging):
        """Test getting service status when some services fail."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        # Mock some services to fail
        controller.transaction_service.get_all_transactions = Mock(side_effect=Exception("Service error"))
        controller.category_service.get_all_categories = Mock(return_value=[])
        controller.chart_service.is_matplotlib_available = Mock(return_value=True)
        
        status = controller.get_service_status()
        
        self.assertFalse(status['transaction_service'])
        self.assertTrue(status['category_service'])
        self.assertTrue(status['chart_service'])
    
    @patch('expense_tracker.controllers.app_controller.ConsoleInterface')
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_start_console_interface(self, mock_logging, mock_console_interface):
        """Test starting console interface."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        # Mock console interface
        mock_interface = Mock()
        mock_console_interface.return_value = mock_interface
        
        # Mock the start method to avoid blocking
        def mock_start():
            controller.is_running = True
            # Simulate interface completion
            controller._shutdown()
        
        mock_interface.start = mock_start
        
        controller.start_console_interface()
        
        # Verify interface was created and started
        mock_console_interface.assert_called_once()
        mock_interface.start.assert_called_once()
        
        # Verify state after completion
        self.assertFalse(controller.is_running)
        self.assertIsNone(controller.current_interface)
    
    @patch('expense_tracker.controllers.app_controller.GUIInterface')
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_start_gui_interface(self, mock_logging, mock_gui_interface):
        """Test starting GUI interface."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        # Mock GUI interface
        mock_interface = Mock()
        mock_gui_interface.return_value = mock_interface
        
        # Mock the start method to avoid blocking
        def mock_start():
            controller.is_running = True
            # Simulate interface completion
            controller._shutdown()
        
        mock_interface.start = mock_start
        
        controller.start_gui_interface()
        
        # Verify interface was created and started
        mock_gui_interface.assert_called_once()
        mock_interface.start.assert_called_once()
        
        # Verify state after completion
        self.assertFalse(controller.is_running)
        self.assertIsNone(controller.current_interface)
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_shutdown(self, mock_logging):
        """Test application shutdown."""
        controller = ApplicationController(data_file_path=self.test_data_file)
        
        # Set up running state
        controller.is_running = True
        controller.current_interface = Mock()
        
        # Mock repository save method
        controller.repository.save_data = Mock()
        
        controller._shutdown()
        
        # Verify shutdown state
        self.assertFalse(controller.is_running)
        self.assertIsNone(controller.current_interface)
        
        # Verify data was saved
        controller.repository.save_data.assert_called_once()
    
    @patch('expense_tracker.controllers.app_controller.logging')
    def test_initialization_service_failure(self, mock_logging):
        """Test controller initialization when service initialization fails."""
        with patch('expense_tracker.controllers.app_controller.JSONRepository', side_effect=Exception("Init error")):
            with self.assertRaises(Exception):
                ApplicationController(data_file_path=self.test_data_file)


if __name__ == '__main__':
    unittest.main()