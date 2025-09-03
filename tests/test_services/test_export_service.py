"""Unit tests for ExportService."""

import unittest
from unittest.mock import Mock, patch, mock_open
import tempfile
import os
import csv
from decimal import Decimal
from datetime import datetime, date
from pathlib import Path

from expense_tracker.services.export_service import ExportService, EXCEL_AVAILABLE
from expense_tracker.models.transaction import Transaction
from expense_tracker.models.enums import TransactionType


class TestExportService(unittest.TestCase):
    """Test cases for ExportService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_transaction_service = Mock()
        self.mock_report_service = Mock()
        self.service = ExportService(self.mock_transaction_service, self.mock_report_service)
        
        # Sample transactions for testing
        self.sample_transactions = [
            Transaction(
                id='1',
                amount=Decimal('1000'),
                description='Salary',
                category='Salary',
                transaction_type=TransactionType.INCOME,
                date=datetime(2024, 1, 15)
            ),
            Transaction(
                id='2',
                amount=Decimal('200'),
                description='Groceries',
                category='Food',
                transaction_type=TransactionType.EXPENSE,
                date=datetime(2024, 1, 10)
            ),
            Transaction(
                id='3',
                amount=Decimal('100'),
                description='Gas',
                category='Transportation',
                transaction_type=TransactionType.EXPENSE,
                date=datetime(2024, 1, 20)
            )
        ]
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_export_transactions_to_csv_success(self):
        """Test successful CSV export of transactions."""
        self.mock_transaction_service.filter_transactions.return_value = self.sample_transactions
        
        csv_file = os.path.join(self.temp_dir, 'test_transactions.csv')
        result = self.service.export_transactions_to_csv(csv_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(csv_file))
        
        # Verify CSV content
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            self.assertEqual(len(rows), 3)
            
            # Check first row
            self.assertEqual(rows[0]['ID'], '1')
            self.assertEqual(rows[0]['Description'], 'Salary')
            self.assertEqual(rows[0]['Category'], 'Salary')
            self.assertEqual(rows[0]['Type'], 'INCOME')
            self.assertEqual(rows[0]['Amount'], '1000')
            self.assertEqual(rows[0]['Date'], '2024-01-15')
        
        # Verify service call
        self.mock_transaction_service.filter_transactions.assert_called_once_with(
            start_date=None, end_date=None, transaction_type=None, category=None
        )
    
    def test_export_transactions_to_csv_with_filters(self):
        """Test CSV export with date and type filters."""
        filtered_transactions = [self.sample_transactions[0]]  # Only income transaction
        self.mock_transaction_service.filter_transactions.return_value = filtered_transactions
        
        csv_file = os.path.join(self.temp_dir, 'test_filtered.csv')
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        result = self.service.export_transactions_to_csv(
            csv_file,
            start_date=start_date,
            end_date=end_date,
            transaction_type=TransactionType.INCOME
        )
        
        self.assertTrue(result)
        
        # Verify service call with filters
        self.mock_transaction_service.filter_transactions.assert_called_once_with(
            start_date=start_date,
            end_date=end_date,
            transaction_type=TransactionType.INCOME,
            category=None
        )
        
        # Verify only one transaction in CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['Type'], 'INCOME')
    
    def test_export_transactions_to_csv_invalid_extension(self):
        """Test CSV export with invalid file extension."""
        invalid_file = os.path.join(self.temp_dir, 'test.txt')
        result = self.service.export_transactions_to_csv(invalid_file)
        
        self.assertFalse(result)
    
    def test_export_transactions_to_csv_empty_transactions(self):
        """Test CSV export with no transactions."""
        self.mock_transaction_service.filter_transactions.return_value = []
        
        csv_file = os.path.join(self.temp_dir, 'test_empty.csv')
        result = self.service.export_transactions_to_csv(csv_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(csv_file))
        
        # Verify CSV has only header
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 0)
    
    @unittest.skipIf(not EXCEL_AVAILABLE, "openpyxl not available")
    def test_export_transactions_to_excel_success(self):
        """Test successful Excel export of transactions."""
        self.mock_transaction_service.filter_transactions.return_value = self.sample_transactions
        
        # Mock summary report for summary sheet
        mock_summary = {
            'totals': {
                'total_income': Decimal('1000'),
                'total_expenses': Decimal('300'),
                'net_balance': Decimal('700'),
                'total_transactions': 3
            },
            'counts': {
                'income_transactions': 1,
                'expense_transactions': 2
            },
            'averages': {
                'average_income': Decimal('1000'),
                'average_expense': Decimal('150')
            }
        }
        self.mock_report_service.generate_summary_report.return_value = mock_summary
        
        excel_file = os.path.join(self.temp_dir, 'test_transactions.xlsx')
        result = self.service.export_transactions_to_excel(excel_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(excel_file))
        
        # Verify service calls
        self.mock_transaction_service.filter_transactions.assert_called_once()
        self.mock_report_service.generate_summary_report.assert_called_once()
    
    @unittest.skipIf(not EXCEL_AVAILABLE, "openpyxl not available")
    def test_export_transactions_to_excel_no_summary(self):
        """Test Excel export without summary sheet."""
        self.mock_transaction_service.filter_transactions.return_value = self.sample_transactions
        
        excel_file = os.path.join(self.temp_dir, 'test_no_summary.xlsx')
        result = self.service.export_transactions_to_excel(excel_file, include_summary=False)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(excel_file))
        
        # Verify summary report was not called
        self.mock_report_service.generate_summary_report.assert_not_called()
    
    @unittest.skipIf(EXCEL_AVAILABLE, "Test only when openpyxl not available")
    def test_export_transactions_to_excel_no_openpyxl(self):
        """Test Excel export when openpyxl is not available."""
        excel_file = os.path.join(self.temp_dir, 'test.xlsx')
        result = self.service.export_transactions_to_excel(excel_file)
        
        self.assertFalse(result)
    
    def test_export_category_summary_to_csv_success(self):
        """Test successful category summary CSV export."""
        # Mock category breakdown report
        mock_report = {
            'categories': {
                'Salary': {
                    'total_amount': Decimal('1000'),
                    'transaction_count': 1,
                    'percentage': Decimal('76.92'),
                    'average_amount': Decimal('1000')
                },
                'Food': {
                    'total_amount': Decimal('200'),
                    'transaction_count': 1,
                    'percentage': Decimal('15.38'),
                    'average_amount': Decimal('200')
                },
                'Transportation': {
                    'total_amount': Decimal('100'),
                    'transaction_count': 1,
                    'percentage': Decimal('7.69'),
                    'average_amount': Decimal('100')
                }
            }
        }
        self.mock_report_service.generate_category_breakdown_report.return_value = mock_report
        
        csv_file = os.path.join(self.temp_dir, 'test_category_summary.csv')
        result = self.service.export_category_summary_to_csv(csv_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(csv_file))
        
        # Verify CSV content
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            self.assertEqual(len(rows), 3)
            
            # Check first row (should be Salary)
            salary_row = next(row for row in rows if row['Category'] == 'Salary')
            self.assertEqual(salary_row['Total Amount'], '1000')
            self.assertEqual(salary_row['Transaction Count'], '1')
            self.assertEqual(salary_row['Percentage'], '76.92%')
        
        # Verify service call
        self.mock_report_service.generate_category_breakdown_report.assert_called_once_with(
            None, None, None
        )
    
    def test_export_category_summary_to_csv_no_report_service(self):
        """Test category summary export without report service."""
        service_without_report = ExportService(self.mock_transaction_service)
        
        csv_file = os.path.join(self.temp_dir, 'test_no_report.csv')
        result = service_without_report.export_category_summary_to_csv(csv_file)
        
        self.assertFalse(result)
    
    @unittest.skipIf(not EXCEL_AVAILABLE, "openpyxl not available")
    def test_export_monthly_report_to_excel_success(self):
        """Test successful monthly report Excel export."""
        # Mock monthly report
        mock_report = {
            'year': 2024,
            'summary': {
                'total_income': Decimal('12000'),
                'total_expenses': Decimal('3600'),
                'net_balance': Decimal('8400')
            },
            'monthly_data': {
                'January': {
                    'income': Decimal('1000'),
                    'expenses': Decimal('300'),
                    'net_balance': Decimal('700'),
                    'transaction_count': 3
                },
                'February': {
                    'income': Decimal('1000'),
                    'expenses': Decimal('300'),
                    'net_balance': Decimal('700'),
                    'transaction_count': 2
                }
            }
        }
        self.mock_report_service.generate_monthly_report.return_value = mock_report
        
        excel_file = os.path.join(self.temp_dir, 'test_monthly.xlsx')
        result = self.service.export_monthly_report_to_excel(excel_file, 2024)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(excel_file))
        
        # Verify service call
        self.mock_report_service.generate_monthly_report.assert_called_once_with(2024)
    
    @unittest.skipIf(not EXCEL_AVAILABLE, "openpyxl not available")
    def test_export_monthly_report_to_excel_no_report_service(self):
        """Test monthly report export without report service."""
        service_without_report = ExportService(self.mock_transaction_service)
        
        excel_file = os.path.join(self.temp_dir, 'test_no_report.xlsx')
        result = service_without_report.export_monthly_report_to_excel(excel_file, 2024)
        
        self.assertFalse(result)
    
    def test_validate_file_path_valid_csv(self):
        """Test file path validation for valid CSV file."""
        csv_file = os.path.join(self.temp_dir, 'valid.csv')
        result = self.service._validate_file_path(csv_file, '.csv')
        
        self.assertTrue(result)
    
    def test_validate_file_path_invalid_extension(self):
        """Test file path validation for invalid extension."""
        txt_file = os.path.join(self.temp_dir, 'invalid.txt')
        result = self.service._validate_file_path(txt_file, '.csv')
        
        self.assertFalse(result)
    
    def test_validate_file_path_creates_directory(self):
        """Test that file path validation creates parent directories."""
        nested_file = os.path.join(self.temp_dir, 'nested', 'dir', 'file.csv')
        result = self.service._validate_file_path(nested_file, '.csv')
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(os.path.dirname(nested_file)))
    
    def test_get_filtered_transactions(self):
        """Test getting filtered transactions."""
        self.mock_transaction_service.filter_transactions.return_value = self.sample_transactions
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        result = self.service._get_filtered_transactions(
            start_date=start_date,
            end_date=end_date,
            transaction_type=TransactionType.EXPENSE,
            category='Food'
        )
        
        self.assertEqual(result, self.sample_transactions)
        self.mock_transaction_service.filter_transactions.assert_called_once_with(
            start_date=start_date,
            end_date=end_date,
            transaction_type=TransactionType.EXPENSE,
            category='Food'
        )


if __name__ == '__main__':
    unittest.main()