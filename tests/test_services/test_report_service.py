"""Unit tests for ReportService."""

import unittest
from unittest.mock import Mock, MagicMock
from decimal import Decimal
from datetime import datetime, date
import calendar

from expense_tracker.services.report_service import ReportService
from expense_tracker.models.transaction import Transaction
from expense_tracker.models.enums import TransactionType


class TestReportService(unittest.TestCase):
    """Test cases for ReportService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_transaction_service = Mock()
        self.mock_category_service = Mock()
        self.service = ReportService(self.mock_transaction_service, self.mock_category_service)
        
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
            ),
            Transaction(
                id='4',
                amount=Decimal('150'),
                description='Restaurant',
                category='Food',
                transaction_type=TransactionType.EXPENSE,
                date=datetime(2024, 2, 5)
            )
        ]
    
    def test_generate_summary_report_all_transactions(self):
        """Test generating summary report for all transactions."""
        self.mock_transaction_service.filter_transactions.return_value = self.sample_transactions
        
        result = self.service.generate_summary_report()
        
        # Verify calculations
        self.assertEqual(result['totals']['total_income'], Decimal('1000'))
        self.assertEqual(result['totals']['total_expenses'], Decimal('450'))  # 200 + 100 + 150
        self.assertEqual(result['totals']['net_balance'], Decimal('550'))  # 1000 - 450
        self.assertEqual(result['totals']['total_transactions'], 4)
        
        self.assertEqual(result['counts']['income_transactions'], 1)
        self.assertEqual(result['counts']['expense_transactions'], 3)
        
        self.assertEqual(result['averages']['average_income'], Decimal('1000'))
        self.assertEqual(result['averages']['average_expense'], Decimal('150'))  # 450 / 3
        
        # Verify service call
        self.mock_transaction_service.filter_transactions.assert_called_once_with(
            start_date=None, end_date=None, transaction_type=None
        )
    
    def test_generate_summary_report_with_date_filter(self):
        """Test generating summary report with date filtering."""
        january_transactions = self.sample_transactions[:3]  # First 3 transactions
        self.mock_transaction_service.filter_transactions.return_value = january_transactions
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        result = self.service.generate_summary_report(start_date, end_date)
        
        # Verify period information
        self.assertEqual(result['period']['start_date'], '2024-01-01')
        self.assertEqual(result['period']['end_date'], '2024-01-31')
        self.assertEqual(result['period']['total_days'], 31)
        
        # Verify calculations for January only
        self.assertEqual(result['totals']['total_income'], Decimal('1000'))
        self.assertEqual(result['totals']['total_expenses'], Decimal('300'))  # 200 + 100
        self.assertEqual(result['totals']['net_balance'], Decimal('700'))
        
        # Verify service call with date filters
        self.mock_transaction_service.filter_transactions.assert_called_once_with(
            start_date=start_date, end_date=end_date, transaction_type=None
        )
    
    def test_generate_summary_report_empty_transactions(self):
        """Test generating summary report with no transactions."""
        self.mock_transaction_service.filter_transactions.return_value = []
        
        result = self.service.generate_summary_report()
        
        # Verify zero values
        self.assertEqual(result['totals']['total_income'], Decimal('0'))
        self.assertEqual(result['totals']['total_expenses'], Decimal('0'))
        self.assertEqual(result['totals']['net_balance'], Decimal('0'))
        self.assertEqual(result['totals']['total_transactions'], 0)
        
        self.assertEqual(result['averages']['average_income'], Decimal('0'))
        self.assertEqual(result['averages']['average_expense'], Decimal('0'))
        self.assertEqual(result['averages']['average_transaction'], Decimal('0'))
    
    def test_generate_category_breakdown_report(self):
        """Test generating category breakdown report."""
        self.mock_transaction_service.filter_transactions.return_value = self.sample_transactions
        
        result = self.service.generate_category_breakdown_report()
        
        # Verify summary
        self.assertEqual(result['summary']['total_amount'], Decimal('1450'))  # Sum of all amounts
        self.assertEqual(result['summary']['total_transactions'], 4)
        self.assertEqual(result['summary']['categories_count'], 3)  # Salary, Food, Transportation
        
        # Verify category data
        categories = result['categories']
        
        # Salary category
        self.assertEqual(categories['Salary']['total_amount'], Decimal('1000'))
        self.assertEqual(categories['Salary']['transaction_count'], 1)
        self.assertAlmostEqual(float(categories['Salary']['percentage']), 68.97, places=1)  # 1000/1450 * 100
        
        # Food category (should have 2 transactions: 200 + 150)
        self.assertEqual(categories['Food']['total_amount'], Decimal('350'))
        self.assertEqual(categories['Food']['transaction_count'], 2)
        self.assertAlmostEqual(float(categories['Food']['percentage']), 24.14, places=1)  # 350/1450 * 100
        
        # Transportation category
        self.assertEqual(categories['Transportation']['total_amount'], Decimal('100'))
        self.assertEqual(categories['Transportation']['transaction_count'], 1)
        self.assertAlmostEqual(float(categories['Transportation']['percentage']), 6.90, places=1)  # 100/1450 * 100
    
    def test_generate_category_breakdown_report_with_type_filter(self):
        """Test generating category breakdown report filtered by transaction type."""
        expense_transactions = [t for t in self.sample_transactions if t.transaction_type == TransactionType.EXPENSE]
        self.mock_transaction_service.filter_transactions.return_value = expense_transactions
        
        result = self.service.generate_category_breakdown_report(
            transaction_type=TransactionType.EXPENSE
        )
        
        # Verify filter information
        self.assertEqual(result['filter']['transaction_type'], 'EXPENSE')
        
        # Verify only expense categories are included
        categories = result['categories']
        self.assertIn('Food', categories)
        self.assertIn('Transportation', categories)
        self.assertNotIn('Salary', categories)
        
        # Verify service call with type filter
        self.mock_transaction_service.filter_transactions.assert_called_once_with(
            start_date=None, end_date=None, transaction_type=TransactionType.EXPENSE
        )
    
    def test_generate_monthly_report(self):
        """Test generating monthly report for a specific year."""
        # Mock transactions for different months
        def mock_filter_transactions(start_date=None, end_date=None, **kwargs):
            if start_date and end_date:
                # Return transactions that fall within the date range
                return [t for t in self.sample_transactions 
                       if start_date <= t.date.date() <= end_date]
            return self.sample_transactions
        
        self.mock_transaction_service.filter_transactions.side_effect = mock_filter_transactions
        
        result = self.service.generate_monthly_report(2024)
        
        # Verify year summary
        self.assertEqual(result['year'], 2024)
        self.assertEqual(result['summary']['total_income'], Decimal('1000'))
        self.assertEqual(result['summary']['total_expenses'], Decimal('450'))
        self.assertEqual(result['summary']['net_balance'], Decimal('550'))
        
        # Verify monthly data structure
        monthly_data = result['monthly_data']
        self.assertIn('January', monthly_data)
        self.assertIn('February', monthly_data)
        
        # Verify January data (3 transactions)
        january = monthly_data['January']
        self.assertEqual(january['income'], Decimal('1000'))
        self.assertEqual(january['expenses'], Decimal('300'))  # 200 + 100
        self.assertEqual(january['net_balance'], Decimal('700'))
        self.assertEqual(january['transaction_count'], 3)
        
        # Verify February data (1 transaction)
        february = monthly_data['February']
        self.assertEqual(february['income'], Decimal('0'))
        self.assertEqual(february['expenses'], Decimal('150'))
        self.assertEqual(february['net_balance'], Decimal('-150'))
        self.assertEqual(february['transaction_count'], 1)
    
    def test_generate_trend_analysis_monthly(self):
        """Test generating monthly trend analysis."""
        self.mock_transaction_service.filter_transactions.return_value = self.sample_transactions
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 2, 29)
        
        result = self.service.generate_trend_analysis(start_date, end_date, 'monthly')
        
        # Verify metadata
        self.assertEqual(result['period_type'], 'monthly')
        self.assertEqual(result['start_date'], '2024-01-01')
        self.assertEqual(result['end_date'], '2024-02-29')
        
        # Verify trend data
        data = result['data']
        self.assertEqual(len(data), 2)  # January and February
        
        # January data
        jan_data = next(item for item in data if item['period'] == '2024-01')
        self.assertEqual(jan_data['income'], Decimal('1000'))
        self.assertEqual(jan_data['expenses'], Decimal('300'))
        self.assertEqual(jan_data['net_balance'], Decimal('700'))
        
        # February data
        feb_data = next(item for item in data if item['period'] == '2024-02')
        self.assertEqual(feb_data['income'], Decimal('0'))
        self.assertEqual(feb_data['expenses'], Decimal('150'))
        self.assertEqual(feb_data['net_balance'], Decimal('-150'))
    
    def test_generate_trend_analysis_invalid_period(self):
        """Test generating trend analysis with invalid period."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 2, 29)
        
        with self.assertRaises(ValueError) as context:
            self.service.generate_trend_analysis(start_date, end_date, 'invalid')
        
        self.assertIn("Period must be 'daily', 'weekly', or 'monthly'", str(context.exception))
    
    def test_generate_chart_data_pie(self):
        """Test generating pie chart data."""
        self.mock_transaction_service.filter_transactions.return_value = self.sample_transactions
        
        result = self.service.generate_chart_data('pie')
        
        # Verify chart metadata
        self.assertEqual(result['chart_type'], 'pie')
        self.assertIn('Category Breakdown', result['title'])
        
        # Verify data structure
        self.assertIn('labels', result)
        self.assertIn('values', result)
        self.assertIn('colors', result)
        
        # Verify labels include all categories
        labels = result['labels']
        self.assertIn('Salary', labels)
        self.assertIn('Food', labels)
        self.assertIn('Transportation', labels)
        
        # Verify values correspond to category totals
        values = result['values']
        self.assertEqual(len(values), len(labels))
        self.assertIn(1000.0, values)  # Salary
        self.assertIn(350.0, values)   # Food (200 + 150)
        self.assertIn(100.0, values)   # Transportation
    
    def test_generate_chart_data_bar(self):
        """Test generating bar chart data."""
        # Mock monthly report data
        def mock_filter_transactions(start_date=None, end_date=None, **kwargs):
            if start_date and end_date:
                return [t for t in self.sample_transactions 
                       if start_date <= t.date.date() <= end_date]
            return self.sample_transactions
        
        self.mock_transaction_service.filter_transactions.side_effect = mock_filter_transactions
        
        result = self.service.generate_chart_data('bar')
        
        # Verify chart metadata
        self.assertEqual(result['chart_type'], 'bar')
        self.assertIn('Monthly Income vs Expenses', result['title'])
        
        # Verify data structure
        self.assertIn('labels', result)
        self.assertIn('datasets', result)
        
        # Verify datasets
        datasets = result['datasets']
        self.assertEqual(len(datasets), 2)  # Income and Expenses
        
        income_dataset = next(ds for ds in datasets if ds['label'] == 'Income')
        expense_dataset = next(ds for ds in datasets if ds['label'] == 'Expenses')
        
        self.assertIsNotNone(income_dataset)
        self.assertIsNotNone(expense_dataset)
    
    def test_generate_chart_data_line(self):
        """Test generating line chart data."""
        self.mock_transaction_service.filter_transactions.return_value = self.sample_transactions
        
        result = self.service.generate_chart_data('line')
        
        # Verify chart metadata
        self.assertEqual(result['chart_type'], 'line')
        self.assertEqual(result['title'], 'Balance Over Time')
        
        # Verify data structure
        self.assertIn('labels', result)
        self.assertIn('datasets', result)
        
        # Verify dataset
        datasets = result['datasets']
        self.assertEqual(len(datasets), 1)
        
        balance_dataset = datasets[0]
        self.assertEqual(balance_dataset['label'], 'Running Balance')
        self.assertIn('data', balance_dataset)
    
    def test_generate_chart_data_invalid_type(self):
        """Test generating chart data with invalid chart type."""
        with self.assertRaises(ValueError) as context:
            self.service.generate_chart_data('invalid')
        
        self.assertIn("Chart type must be 'pie', 'bar', or 'line'", str(context.exception))


if __name__ == '__main__':
    unittest.main()