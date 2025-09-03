"""Unit tests for ChartService."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from datetime import date
from pathlib import Path

from expense_tracker.services.chart_service import ChartService, MATPLOTLIB_AVAILABLE
from expense_tracker.models.enums import TransactionType


class TestChartService(unittest.TestCase):
    """Test cases for ChartService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_report_service = Mock()
        self.service = ChartService(self.mock_report_service)
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample chart data for testing
        self.sample_pie_data = {
            'chart_type': 'pie',
            'title': 'Category Breakdown - All Transactions',
            'labels': ['Food', 'Transportation', 'Entertainment'],
            'values': [300.0, 150.0, 100.0],
            'colors': ['#FF6384', '#36A2EB', '#FFCE56']
        }
        
        self.sample_bar_data = {
            'chart_type': 'bar',
            'title': 'Monthly Income vs Expenses - 2024',
            'labels': ['January', 'February', 'March'],
            'datasets': [
                {
                    'label': 'Income',
                    'data': [1000.0, 1200.0, 1100.0],
                    'backgroundColor': '#36A2EB'
                },
                {
                    'label': 'Expenses',
                    'data': [800.0, 900.0, 850.0],
                    'backgroundColor': '#FF6384'
                }
            ]
        }
        
        self.sample_line_data = {
            'chart_type': 'line',
            'title': 'Balance Over Time',
            'labels': ['2024-01', '2024-02', '2024-03'],
            'datasets': [
                {
                    'label': 'Running Balance',
                    'data': [200.0, 500.0, 750.0],
                    'borderColor': '#36A2EB',
                    'backgroundColor': 'rgba(54, 162, 235, 0.1)'
                }
            ]
        }
        
        self.sample_trend_data = {
            'period_type': 'monthly',
            'start_date': '2024-01-01',
            'end_date': '2024-03-31',
            'data': [
                {'period': '2024-01', 'income': 1000.0, 'expenses': 800.0, 'net_balance': 200.0},
                {'period': '2024-02', 'income': 1200.0, 'expenses': 900.0, 'net_balance': 300.0},
                {'period': '2024-03', 'income': 1100.0, 'expenses': 850.0, 'net_balance': 250.0}
            ]
        }
        
        self.sample_category_report = {
            'categories': {
                'Food': {'total_amount': 300.0, 'transaction_count': 5},
                'Transportation': {'total_amount': 150.0, 'transaction_count': 3},
                'Entertainment': {'total_amount': 100.0, 'transaction_count': 2}
            }
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_create_pie_chart_success(self):
        """Test successful pie chart creation."""
        self.mock_report_service.generate_chart_data.return_value = self.sample_pie_data
        
        save_path = os.path.join(self.temp_dir, 'test_pie.png')
        result = self.service.create_pie_chart(save_path=save_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(save_path))
        
        # Verify service call
        self.mock_report_service.generate_chart_data.assert_called_once_with(
            'pie', None, None, None
        )
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_create_pie_chart_with_filters(self):
        """Test pie chart creation with filters."""
        self.mock_report_service.generate_chart_data.return_value = self.sample_pie_data
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        transaction_type = TransactionType.EXPENSE
        
        result = self.service.create_pie_chart(
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type
        )
        
        self.assertTrue(result)
        
        # Verify service call with filters
        self.mock_report_service.generate_chart_data.assert_called_once_with(
            'pie', start_date, end_date, transaction_type
        )
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_create_pie_chart_no_data(self):
        """Test pie chart creation with no data."""
        empty_data = self.sample_pie_data.copy()
        empty_data['values'] = []
        self.mock_report_service.generate_chart_data.return_value = empty_data
        
        result = self.service.create_pie_chart()
        
        self.assertFalse(result)
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_create_bar_chart_success(self):
        """Test successful bar chart creation."""
        self.mock_report_service.generate_chart_data.return_value = self.sample_bar_data
        
        save_path = os.path.join(self.temp_dir, 'test_bar.png')
        result = self.service.create_bar_chart(save_path=save_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(save_path))
        
        # Verify service call
        self.mock_report_service.generate_chart_data.assert_called_once_with(
            'bar', None, None
        )
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_create_bar_chart_with_date_range(self):
        """Test bar chart creation with date range."""
        self.mock_report_service.generate_chart_data.return_value = self.sample_bar_data
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 3, 31)
        
        result = self.service.create_bar_chart(
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertTrue(result)
        
        # Verify service call with date range
        self.mock_report_service.generate_chart_data.assert_called_once_with(
            'bar', start_date, end_date
        )
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_create_line_chart_success(self):
        """Test successful line chart creation."""
        self.mock_report_service.generate_chart_data.return_value = self.sample_line_data
        
        save_path = os.path.join(self.temp_dir, 'test_line.png')
        result = self.service.create_line_chart(save_path=save_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(save_path))
        
        # Verify service call
        self.mock_report_service.generate_chart_data.assert_called_once_with(
            'line', None, None
        )
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_create_trend_chart_success(self):
        """Test successful trend chart creation."""
        self.mock_report_service.generate_trend_analysis.return_value = self.sample_trend_data
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 3, 31)
        save_path = os.path.join(self.temp_dir, 'test_trend.png')
        
        result = self.service.create_trend_chart(
            start_date=start_date,
            end_date=end_date,
            save_path=save_path
        )
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(save_path))
        
        # Verify service call
        self.mock_report_service.generate_trend_analysis.assert_called_once_with(
            start_date, end_date, 'monthly'
        )
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_create_trend_chart_different_periods(self):
        """Test trend chart creation with different periods."""
        self.mock_report_service.generate_trend_analysis.return_value = self.sample_trend_data
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        # Test weekly period
        result = self.service.create_trend_chart(
            start_date=start_date,
            end_date=end_date,
            period='weekly'
        )
        
        self.assertTrue(result)
        
        # Verify service call with weekly period
        self.mock_report_service.generate_trend_analysis.assert_called_with(
            start_date, end_date, 'weekly'
        )
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_create_category_comparison_chart_success(self):
        """Test successful category comparison chart creation."""
        self.mock_report_service.generate_category_breakdown_report.return_value = self.sample_category_report
        
        save_path = os.path.join(self.temp_dir, 'test_category.png')
        result = self.service.create_category_comparison_chart(save_path=save_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(save_path))
        
        # Verify service call
        self.mock_report_service.generate_category_breakdown_report.assert_called_once_with(
            None, None, None
        )
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_create_category_comparison_chart_with_filters(self):
        """Test category comparison chart with filters."""
        self.mock_report_service.generate_category_breakdown_report.return_value = self.sample_category_report
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        transaction_type = TransactionType.EXPENSE
        
        result = self.service.create_category_comparison_chart(
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type
        )
        
        self.assertTrue(result)
        
        # Verify service call with filters
        self.mock_report_service.generate_category_breakdown_report.assert_called_once_with(
            start_date, end_date, transaction_type
        )
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_save_chart_different_formats(self):
        """Test saving charts in different formats."""
        self.mock_report_service.generate_chart_data.return_value = self.sample_pie_data
        
        formats = ['.png', '.jpg', '.pdf', '.svg']
        
        for fmt in formats:
            save_path = os.path.join(self.temp_dir, f'test_chart{fmt}')
            result = self.service.create_pie_chart(save_path=save_path)
            
            self.assertTrue(result, f"Failed to create chart with format {fmt}")
            self.assertTrue(os.path.exists(save_path), f"Chart file not created for format {fmt}")
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_save_chart_invalid_extension(self):
        """Test saving chart with invalid file extension."""
        self.mock_report_service.generate_chart_data.return_value = self.sample_pie_data
        
        save_path = os.path.join(self.temp_dir, 'test_chart.txt')
        result = self.service.create_pie_chart(save_path=save_path)
        
        self.assertFalse(result)
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_save_chart_creates_directory(self):
        """Test that chart saving creates parent directories."""
        self.mock_report_service.generate_chart_data.return_value = self.sample_pie_data
        
        nested_path = os.path.join(self.temp_dir, 'nested', 'dir', 'chart.png')
        result = self.service.create_pie_chart(save_path=nested_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(nested_path))
        self.assertTrue(os.path.exists(os.path.dirname(nested_path)))
    
    @unittest.skipIf(MATPLOTLIB_AVAILABLE, "Test only when matplotlib not available")
    def test_charts_without_matplotlib(self):
        """Test chart creation when matplotlib is not available."""
        result_pie = self.service.create_pie_chart()
        result_bar = self.service.create_bar_chart()
        result_line = self.service.create_line_chart()
        result_trend = self.service.create_trend_chart(date(2024, 1, 1), date(2024, 1, 31))
        result_category = self.service.create_category_comparison_chart()
        
        self.assertFalse(result_pie)
        self.assertFalse(result_bar)
        self.assertFalse(result_line)
        self.assertFalse(result_trend)
        self.assertFalse(result_category)
    
    def test_get_available_formats(self):
        """Test getting available chart formats."""
        formats = self.service.get_available_formats()
        
        expected_formats = ['.png', '.jpg', '.jpeg', '.pdf', '.svg']
        self.assertEqual(formats, expected_formats)
    
    def test_is_matplotlib_available(self):
        """Test checking matplotlib availability."""
        result = self.service.is_matplotlib_available()
        self.assertEqual(result, MATPLOTLIB_AVAILABLE)
    
    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib not available")
    def test_chart_no_data_scenarios(self):
        """Test chart creation with various no-data scenarios."""
        # Empty labels
        empty_bar_data = self.sample_bar_data.copy()
        empty_bar_data['labels'] = []
        self.mock_report_service.generate_chart_data.return_value = empty_bar_data
        
        result = self.service.create_bar_chart()
        self.assertFalse(result)
        
        # Empty line data
        empty_line_data = self.sample_line_data.copy()
        empty_line_data['labels'] = []
        self.mock_report_service.generate_chart_data.return_value = empty_line_data
        
        result = self.service.create_line_chart()
        self.assertFalse(result)
        
        # Empty trend data
        empty_trend_data = self.sample_trend_data.copy()
        empty_trend_data['data'] = []
        self.mock_report_service.generate_trend_analysis.return_value = empty_trend_data
        
        result = self.service.create_trend_chart(date(2024, 1, 1), date(2024, 1, 31))
        self.assertFalse(result)
        
        # Empty category data
        empty_category_report = {'categories': {}}
        self.mock_report_service.generate_category_breakdown_report.return_value = empty_category_report
        
        result = self.service.create_category_comparison_chart()
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()