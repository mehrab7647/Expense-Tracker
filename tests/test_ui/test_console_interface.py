"""Unit tests for ConsoleInterface."""

import unittest
from unittest.mock import Mock, patch, call
from decimal import Decimal
from datetime import datetime, date
from io import StringIO

from expense_tracker.ui.console_interface import ConsoleInterface
from expense_tracker.models.transaction import Transaction
from expense_tracker.models.category import Category
from expense_tracker.models.enums import TransactionType, CategoryType


class TestConsoleInterface(unittest.TestCase):
    """Test cases for ConsoleInterface."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_transaction_service = Mock()
        self.mock_category_service = Mock()
        self.mock_report_service = Mock()
        self.mock_export_service = Mock()
        self.mock_chart_service = Mock()
        
        self.interface = ConsoleInterface(
            self.mock_transaction_service,
            self.mock_category_service,
            self.mock_report_service,
            self.mock_export_service,
            self.mock_chart_service
        )
        
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
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_handle_main_menu_choice_transaction_management(self, mock_system, mock_input):
        """Test handling transaction management menu choice."""
        # Mock user selecting transaction management and then back
        mock_input.side_effect = ['0']  # Just go back to main menu
        
        self.interface._handle_main_menu_choice('1')
        
        # Verify that the transaction menu was called
        mock_system.assert_called()  # Screen clearing
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_handle_main_menu_choice_invalid(self, mock_system, mock_input):
        """Test handling invalid main menu choice."""
        with patch('builtins.print') as mock_print:
            self.interface._handle_main_menu_choice('9')
            mock_print.assert_any_call("Invalid choice. Please try again.")
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_add_transaction_success(self, mock_system, mock_input):
        """Test successful transaction addition."""
        # Mock user inputs for adding a transaction
        mock_input.side_effect = [
            '2',  # Expense type
            '100.50',  # Amount
            'Test transaction',  # Description
            '1',  # Category selection
            '',  # Date (use today)
            '',  # Pause
        ]
        
        # Mock category service
        expense_categories = [Category('Food', CategoryType.EXPENSE, True)]
        self.mock_category_service.get_expense_categories.return_value = expense_categories
        
        # Mock transaction service
        self.mock_transaction_service.create_transaction.return_value = self.sample_transaction
        
        with patch('builtins.print') as mock_print:
            self.interface._add_transaction()
            
            # Verify transaction was created
            self.mock_transaction_service.create_transaction.assert_called_once()
            mock_print.assert_any_call("\n✓ Transaction added successfully!")
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_add_transaction_invalid_amount(self, mock_system, mock_input):
        """Test adding transaction with invalid amount."""
        mock_input.side_effect = [
            '2',  # Expense type
            'invalid',  # Invalid amount
            '',  # Pause
        ]
        
        # Mock category service
        expense_categories = [Category('Food', CategoryType.EXPENSE, True)]
        self.mock_category_service.get_expense_categories.return_value = expense_categories
        
        with patch('builtins.print') as mock_print:
            self.interface._add_transaction()
            mock_print.assert_any_call("Invalid amount format.")
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_view_all_transactions(self, mock_system, mock_input):
        """Test viewing all transactions."""
        mock_input.side_effect = ['']  # Pause
        
        transactions = [self.sample_transaction]
        self.mock_transaction_service.get_all_transactions.return_value = transactions
        
        with patch('builtins.print') as mock_print:
            self.interface._view_all_transactions()
            
            # Verify service was called
            self.mock_transaction_service.get_all_transactions.assert_called_once()
            
            # Check that transaction header was printed
            calls = mock_print.call_args_list
            header_found = any('ALL TRANSACTIONS' in str(call) for call in calls)
            self.assertTrue(header_found)
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_view_transactions_by_category(self, mock_system, mock_input):
        """Test viewing transactions by category."""
        mock_input.side_effect = ['1', '']  # Select first category, pause
        
        categories = [self.sample_category]
        transactions = [self.sample_transaction]
        
        self.mock_category_service.get_all_categories.return_value = categories
        self.mock_transaction_service.filter_transactions_by_category.return_value = transactions
        
        with patch('builtins.print') as mock_print:
            self.interface._view_transactions_by_category()
            
            # Verify services were called
            self.mock_category_service.get_all_categories.assert_called_once()
            self.mock_transaction_service.filter_transactions_by_category.assert_called_once_with('Food')
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_view_transactions_by_date_range(self, mock_system, mock_input):
        """Test viewing transactions by date range."""
        mock_input.side_effect = ['2024-01-01', '2024-01-31', '']  # Dates, pause
        
        transactions = [self.sample_transaction]
        self.mock_transaction_service.filter_transactions_by_date_range.return_value = transactions
        
        with patch('builtins.print') as mock_print:
            self.interface._view_transactions_by_date_range()
            
            # Verify service was called with correct dates
            self.mock_transaction_service.filter_transactions_by_date_range.assert_called_once_with(
                date(2024, 1, 1), date(2024, 1, 31)
            )
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_search_transactions(self, mock_system, mock_input):
        """Test searching transactions."""
        mock_input.side_effect = ['test', '']  # Search term, pause
        
        transactions = [self.sample_transaction]
        self.mock_transaction_service.get_all_transactions.return_value = transactions
        
        with patch('builtins.print') as mock_print:
            self.interface._search_transactions()
            
            # Verify service was called
            self.mock_transaction_service.get_all_transactions.assert_called_once()
            
            # Check that search results were displayed
            mock_print.assert_any_call("\nTransactions containing 'test':")
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_show_transaction_summary(self, mock_system, mock_input):
        """Test showing transaction summary."""
        mock_input.side_effect = ['']  # Pause
        
        summary = {
            'total_income': Decimal('1000'),
            'total_expenses': Decimal('500'),
            'net_balance': Decimal('500'),
            'transaction_count': 10,
            'income_count': 3,
            'expense_count': 7
        }
        self.mock_transaction_service.get_transaction_summary.return_value = summary
        
        with patch('builtins.print') as mock_print:
            self.interface._show_transaction_summary()
            
            # Verify service was called
            self.mock_transaction_service.get_transaction_summary.assert_called_once()
            
            # Check that summary header was printed
            calls = mock_print.call_args_list
            header_found = any('TRANSACTION SUMMARY' in str(call) for call in calls)
            self.assertTrue(header_found)
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_add_category_success(self, mock_system, mock_input):
        """Test successful category addition."""
        mock_input.side_effect = [
            'New Category',  # Category name
            '2',  # Expense type
            '',  # Pause
        ]
        
        # Mock category service
        self.mock_category_service.category_exists.return_value = False
        self.mock_category_service.create_category.return_value = self.sample_category
        
        with patch('builtins.print') as mock_print:
            self.interface._add_category()
            
            # Verify category was created
            self.mock_category_service.create_category.assert_called_once()
            mock_print.assert_any_call("\n✓ Category 'Food' added successfully!")
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_add_category_already_exists(self, mock_system, mock_input):
        """Test adding category that already exists."""
        mock_input.side_effect = ['Existing Category', '']  # Add pause input
        
        self.mock_category_service.category_exists.return_value = True
        
        with patch('builtins.print') as mock_print:
            self.interface._add_category()
            mock_print.assert_any_call("Category 'Existing Category' already exists.")
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_show_financial_summary(self, mock_system, mock_input):
        """Test showing financial summary."""
        mock_input.side_effect = ['n', '']  # No date filter, pause input
        
        summary = {
            'totals': {
                'total_income': Decimal('1000'),
                'total_expenses': Decimal('500'),
                'net_balance': Decimal('500'),
                'total_transactions': 10
            },
            'counts': {
                'income_transactions': 3,
                'expense_transactions': 7
            },
            'averages': {
                'average_income': Decimal('333.33'),
                'average_expense': Decimal('71.43')
            }
        }
        self.mock_report_service.generate_summary_report.return_value = summary
        
        with patch('builtins.print') as mock_print:
            self.interface._show_financial_summary()
            
            # Verify service was called
            self.mock_report_service.generate_summary_report.assert_called_once_with(None, None)
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_export_transactions_csv(self, mock_system, mock_input):
        """Test exporting transactions to CSV."""
        mock_input.side_effect = ['exports/transactions.csv', '']  # Add pause input
        
        self.mock_export_service.export_transactions_to_csv.return_value = True
        
        with patch('builtins.print') as mock_print:
            self.interface._export_transactions_csv()
            
            # Verify service was called
            self.mock_export_service.export_transactions_to_csv.assert_called_once_with(
                'exports/transactions.csv'
            )
            mock_print.assert_any_call("✓ Transactions exported successfully to: exports/transactions.csv")
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_generate_pie_chart(self, mock_system, mock_input):
        """Test generating pie chart."""
        mock_input.side_effect = ['charts/pie_chart.png', '']  # Add pause input
        
        self.mock_chart_service.is_matplotlib_available.return_value = True
        self.mock_chart_service.create_pie_chart.return_value = True
        
        with patch('builtins.print') as mock_print:
            self.interface._generate_pie_chart()
            
            # Verify service was called
            self.mock_chart_service.create_pie_chart.assert_called_once_with(
                save_path='charts/pie_chart.png'
            )
            mock_print.assert_any_call("✓ Pie chart generated successfully: charts/pie_chart.png")
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_generate_chart_matplotlib_not_available(self, mock_system, mock_input):
        """Test generating chart when matplotlib is not available."""
        mock_input.side_effect = ['charts/pie_chart.png']
        
        self.mock_chart_service.is_matplotlib_available.return_value = False
        
        with patch('builtins.print') as mock_print:
            self.interface._generate_pie_chart()
            
            mock_print.assert_any_call("Matplotlib is not available. Please install it with: pip install matplotlib")
    
    def test_display_transactions_empty(self):
        """Test displaying empty transaction list."""
        with patch('builtins.print') as mock_print:
            self.interface._display_transactions([])
            mock_print.assert_called_with("No transactions to display.")
    
    def test_display_transactions_with_data(self):
        """Test displaying transactions with data."""
        transactions = [self.sample_transaction]
        
        with patch('builtins.print') as mock_print:
            self.interface._display_transactions(transactions)
            
            # Check that header was printed
            calls = mock_print.call_args_list
            header_call = any('Date' in str(call) and 'Type' in str(call) for call in calls)
            self.assertTrue(header_call)
    
    @patch('expense_tracker.ui.console_interface.input')
    def test_get_user_input_keyboard_interrupt(self, mock_input):
        """Test handling keyboard interrupt in user input."""
        mock_input.side_effect = KeyboardInterrupt()
        
        with self.assertRaises(KeyboardInterrupt):
            self.interface._get_user_input("Test prompt: ")
    
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_clear_screen(self, mock_system):
        """Test screen clearing."""
        self.interface._clear_screen()
        mock_system.assert_called_once()
    
    def test_exit_application(self):
        """Test application exit."""
        with patch('builtins.print') as mock_print:
            self.interface._exit_application()
            
            self.assertFalse(self.interface.running)
            mock_print.assert_any_call("\nThank you for using Expense Tracker!")
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_show_app_info(self, mock_system, mock_input):
        """Test showing application info."""
        self.mock_chart_service.is_matplotlib_available.return_value = True
        
        with patch('builtins.print') as mock_print:
            self.interface._show_app_info()
            
            # Check that app info was displayed
            mock_print.assert_any_call("APPLICATION INFO".center(50))
            mock_print.assert_any_call("Expense Tracker v1.0")
    
    @patch('expense_tracker.ui.console_interface.input')
    @patch('expense_tracker.ui.console_interface.os.system')
    def test_show_chart_formats(self, mock_system, mock_input):
        """Test showing available chart formats."""
        self.mock_chart_service.is_matplotlib_available.return_value = True
        self.mock_chart_service.get_available_formats.return_value = ['.png', '.jpg', '.pdf']
        
        with patch('builtins.print') as mock_print:
            self.interface._show_chart_formats()
            
            # Verify service was called
            self.mock_chart_service.get_available_formats.assert_called_once()
            mock_print.assert_any_call("Supported chart formats:")


if __name__ == '__main__':
    unittest.main()