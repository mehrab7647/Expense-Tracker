"""Unit tests for GUIInterface."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, date

from expense_tracker.models.transaction import Transaction
from expense_tracker.models.category import Category
from expense_tracker.models.enums import TransactionType, CategoryType


class TestGUIInterface(unittest.TestCase):
    """Test cases for GUIInterface."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_transaction_service = Mock()
        self.mock_category_service = Mock()
        self.mock_report_service = Mock()
        self.mock_export_service = Mock()
        self.mock_chart_service = Mock()
        
        # Mock all tkinter components to avoid creating actual windows during tests
        self.tk_patches = [
            patch('tkinter.Tk'),
            patch('tkinter.ttk.Style'),
            patch('tkinter.ttk.Frame'),
            patch('tkinter.ttk.Label'),
            patch('tkinter.ttk.Button'),
            patch('tkinter.ttk.Entry'),
            patch('tkinter.ttk.Combobox'),
            patch('tkinter.ttk.Radiobutton'),
            patch('tkinter.ttk.LabelFrame'),
            patch('tkinter.ttk.Notebook'),
            patch('tkinter.ttk.Treeview'),
            patch('tkinter.ttk.Scrollbar'),
            patch('tkinter.StringVar'),
            patch('tkinter.BOTH'),
            patch('tkinter.X'),
            patch('tkinter.Y'),
            patch('tkinter.LEFT'),
            patch('tkinter.RIGHT'),
            patch('tkinter.W'),
            patch('tkinter.END')
        ]
        
        # Start all patches
        self.mocks = {}
        for patch_obj in self.tk_patches:
            mock_obj = patch_obj.start()
            self.mocks[patch_obj.attribute] = mock_obj
        
        # Configure specific mocks
        self.root_mock = self.mocks['Tk'].return_value
        self.root_mock.winfo_children.return_value = []
        
        # Import and create interface after patching
        from expense_tracker.ui.gui_interface import GUIInterface
        self.interface = GUIInterface(
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
    
    def tearDown(self):
        """Clean up patches."""
        for patch_obj in self.tk_patches:
            patch_obj.stop()
        
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
    
    def test_initialization(self):
        """Test GUI interface initialization."""
        self.assertIsNotNone(self.interface.transaction_service)
        self.assertIsNotNone(self.interface.category_service)
        self.assertIsNotNone(self.interface.report_service)
        self.assertIsNotNone(self.interface.export_service)
        self.assertIsNotNone(self.interface.chart_service)
        self.assertEqual(self.interface.root, self.root_mock)
    
    @patch('expense_tracker.ui.gui_interface.messagebox')
    def test_add_transaction_success(self, mock_messagebox):
        """Test successful transaction addition."""
        # Set up form variables
        self.interface.transaction_type_var = Mock()
        self.interface.transaction_type_var.get.return_value = "EXPENSE"
        
        self.interface.amount_var = Mock()
        self.interface.amount_var.get.return_value = "100.50"
        
        self.interface.description_var = Mock()
        self.interface.description_var.get.return_value = "Test transaction"
        
        self.interface.category_var = Mock()
        self.interface.category_var.get.return_value = "Food"
        
        self.interface.date_var = Mock()
        self.interface.date_var.get.return_value = "2024-01-15"
        
        # Mock service response
        self.mock_transaction_service.create_transaction.return_value = self.sample_transaction
        
        # Mock form clearing method
        self.interface._clear_transaction_form = Mock()
        self.interface._update_summary = Mock()
        
        # Call method
        self.interface._add_transaction()
        
        # Verify service was called
        self.mock_transaction_service.create_transaction.assert_called_once()
        
        # Verify success message
        mock_messagebox.showinfo.assert_called_once_with("Success", "Transaction added successfully!")
        
        # Verify form was cleared and summary updated
        self.interface._clear_transaction_form.assert_called_once()
        self.interface._update_summary.assert_called_once()
    
    @patch('expense_tracker.ui.gui_interface.messagebox')
    def test_add_transaction_invalid_amount(self, mock_messagebox):
        """Test transaction addition with invalid amount."""
        # Set up form variables
        self.interface.amount_var = Mock()
        self.interface.amount_var.get.return_value = "invalid"
        
        # Call method
        self.interface._add_transaction()
        
        # Verify error message
        mock_messagebox.showerror.assert_called_once_with("Error", "Invalid amount format.")
        
        # Verify service was not called
        self.mock_transaction_service.create_transaction.assert_not_called()
    
    @patch('expense_tracker.ui.gui_interface.messagebox')
    def test_add_transaction_empty_description(self, mock_messagebox):
        """Test transaction addition with empty description."""
        # Set up form variables
        self.interface.amount_var = Mock()
        self.interface.amount_var.get.return_value = "100.50"
        
        self.interface.description_var = Mock()
        self.interface.description_var.get.return_value = ""
        
        # Call method
        self.interface._add_transaction()
        
        # Verify error message
        mock_messagebox.showerror.assert_called_once_with("Error", "Description is required.")
        
        # Verify service was not called
        self.mock_transaction_service.create_transaction.assert_not_called()
    
    @patch('expense_tracker.ui.gui_interface.messagebox')
    def test_add_category_success(self, mock_messagebox):
        """Test successful category addition."""
        # Set up form variables
        self.interface.new_category_name_var = Mock()
        self.interface.new_category_name_var.get.return_value = "New Category"
        self.interface.new_category_name_var.set = Mock()
        
        self.interface.new_category_type_var = Mock()
        self.interface.new_category_type_var.get.return_value = "EXPENSE"
        
        # Mock service responses
        self.mock_category_service.category_exists.return_value = False
        self.mock_category_service.create_category.return_value = self.sample_category
        
        # Mock refresh method
        self.interface._refresh_categories_list = Mock()
        
        # Call method
        self.interface._add_category()
        
        # Verify service was called
        self.mock_category_service.create_category.assert_called_once()
        
        # Verify success message
        mock_messagebox.showinfo.assert_called_once_with("Success", "Category 'Food' added successfully!")
        
        # Verify form was cleared and list refreshed
        self.interface.new_category_name_var.set.assert_called_once_with("")
        self.interface._refresh_categories_list.assert_called_once()
    
    @patch('expense_tracker.ui.gui_interface.messagebox')
    def test_add_category_already_exists(self, mock_messagebox):
        """Test adding category that already exists."""
        # Set up form variables
        self.interface.new_category_name_var = Mock()
        self.interface.new_category_name_var.get.return_value = "Existing Category"
        
        # Mock service response
        self.mock_category_service.category_exists.return_value = True
        
        # Call method
        self.interface._add_category()
        
        # Verify error message
        mock_messagebox.showerror.assert_called_once_with("Error", "Category 'Existing Category' already exists.")
        
        # Verify create was not called
        self.mock_category_service.create_category.assert_not_called()
    
    def test_update_summary(self):
        """Test summary update."""
        # Reset the mock to clear any calls from initialization
        self.mock_transaction_service.reset_mock()
        
        # Mock summary data
        summary = {
            'net_balance': Decimal('500'),
            'total_income': Decimal('1000'),
            'total_expenses': Decimal('500'),
            'transaction_count': 10
        }
        self.mock_transaction_service.get_transaction_summary.return_value = summary
        
        # Mock summary label
        self.interface.summary_label = Mock()
        
        # Call method
        self.interface._update_summary()
        
        # Verify service was called
        self.mock_transaction_service.get_transaction_summary.assert_called_once()
        
        # Verify label was updated
        expected_text = "Balance: $500.00 | Income: $1,000.00 | Expenses: $500.00 | Transactions: 10"
        self.interface.summary_label.config.assert_called_once_with(text=expected_text)
    
    def test_update_summary_error(self):
        """Test summary update with error."""
        # Mock service to raise exception
        self.mock_transaction_service.get_transaction_summary.side_effect = Exception("Test error")
        
        # Mock summary label
        self.interface.summary_label = Mock()
        
        # Call method
        self.interface._update_summary()
        
        # Verify error message was set
        self.interface.summary_label.config.assert_called_once_with(text="Error loading summary")
    
    def test_on_transaction_type_change_income(self):
        """Test transaction type change to income."""
        # Set up mocks
        self.interface.transaction_type_var = Mock()
        self.interface.transaction_type_var.get.return_value = "INCOME"
        
        # Create a mock combo box that supports item assignment
        self.interface.category_combo = Mock()
        self.interface.category_combo.__setitem__ = Mock()
        self.interface.category_var = Mock()
        
        # Mock service response
        income_categories = [Category('Salary', CategoryType.INCOME, True)]
        self.mock_category_service.get_income_categories.return_value = income_categories
        
        # Call method
        self.interface._on_transaction_type_change()
        
        # Verify service was called
        self.mock_category_service.get_income_categories.assert_called_once()
        
        # Verify combo box was updated
        self.interface.category_combo.__setitem__.assert_called_once_with('values', ['Salary'])
        self.interface.category_var.set.assert_called_once_with('Salary')
    
    def test_on_transaction_type_change_expense(self):
        """Test transaction type change to expense."""
        # Set up mocks
        self.interface.transaction_type_var = Mock()
        self.interface.transaction_type_var.get.return_value = "EXPENSE"
        
        # Create a mock combo box that supports item assignment
        self.interface.category_combo = Mock()
        self.interface.category_combo.__setitem__ = Mock()
        self.interface.category_var = Mock()
        
        # Mock service response
        expense_categories = [Category('Food', CategoryType.EXPENSE, True)]
        self.mock_category_service.get_expense_categories.return_value = expense_categories
        
        # Call method
        self.interface._on_transaction_type_change()
        
        # Verify service was called
        self.mock_category_service.get_expense_categories.assert_called_once()
        
        # Verify combo box was updated
        self.interface.category_combo.__setitem__.assert_called_once_with('values', ['Food'])
        self.interface.category_var.set.assert_called_once_with('Food')
    
    def test_get_filtered_transactions_no_filters(self):
        """Test getting filtered transactions with no filters applied."""
        # Set up filter variables
        self.interface.filter_category_var = Mock()
        self.interface.filter_category_var.get.return_value = "All"
        
        self.interface.filter_type_var = Mock()
        self.interface.filter_type_var.get.return_value = "All"
        
        self.interface.filter_start_date_var = Mock()
        self.interface.filter_start_date_var.get.return_value = ""
        
        self.interface.filter_end_date_var = Mock()
        self.interface.filter_end_date_var.get.return_value = ""
        
        # Mock service response
        transactions = [self.sample_transaction]
        self.mock_transaction_service.get_all_transactions.return_value = transactions
        
        # Call method
        result = self.interface._get_filtered_transactions()
        
        # Verify result
        self.assertEqual(result, transactions)
        self.mock_transaction_service.get_all_transactions.assert_called_once()
    
    def test_get_filtered_transactions_with_category_filter(self):
        """Test getting filtered transactions with category filter."""
        # Set up filter variables
        self.interface.filter_category_var = Mock()
        self.interface.filter_category_var.get.return_value = "Food"
        
        self.interface.filter_type_var = Mock()
        self.interface.filter_type_var.get.return_value = "All"
        
        self.interface.filter_start_date_var = Mock()
        self.interface.filter_start_date_var.get.return_value = ""
        
        self.interface.filter_end_date_var = Mock()
        self.interface.filter_end_date_var.get.return_value = ""
        
        # Mock service response
        transactions = [
            self.sample_transaction,  # Food category
            Transaction(
                id='2',
                amount=Decimal('50'),
                description='Transport',
                category='Transportation',
                transaction_type=TransactionType.EXPENSE,
                date=datetime(2024, 1, 16)
            )
        ]
        self.mock_transaction_service.get_all_transactions.return_value = transactions
        
        # Call method
        result = self.interface._get_filtered_transactions()
        
        # Verify result - should only include Food category
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].category, "Food")
    
    def test_get_filtered_transactions_with_type_filter(self):
        """Test getting filtered transactions with type filter."""
        # Set up filter variables
        self.interface.filter_category_var = Mock()
        self.interface.filter_category_var.get.return_value = "All"
        
        self.interface.filter_type_var = Mock()
        self.interface.filter_type_var.get.return_value = "Income"
        
        self.interface.filter_start_date_var = Mock()
        self.interface.filter_start_date_var.get.return_value = ""
        
        self.interface.filter_end_date_var = Mock()
        self.interface.filter_end_date_var.get.return_value = ""
        
        # Mock service response
        transactions = [
            self.sample_transaction,  # Expense
            Transaction(
                id='2',
                amount=Decimal('1000'),
                description='Salary',
                category='Salary',
                transaction_type=TransactionType.INCOME,
                date=datetime(2024, 1, 16)
            )
        ]
        self.mock_transaction_service.get_all_transactions.return_value = transactions
        
        # Call method
        result = self.interface._get_filtered_transactions()
        
        # Verify result - should only include Income
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].transaction_type, TransactionType.INCOME)
    
    def test_get_filtered_transactions_with_date_filter(self):
        """Test getting filtered transactions with date filter."""
        # Set up filter variables
        self.interface.filter_category_var = Mock()
        self.interface.filter_category_var.get.return_value = "All"
        
        self.interface.filter_type_var = Mock()
        self.interface.filter_type_var.get.return_value = "All"
        
        self.interface.filter_start_date_var = Mock()
        self.interface.filter_start_date_var.get.return_value = "2024-01-15"
        
        self.interface.filter_end_date_var = Mock()
        self.interface.filter_end_date_var.get.return_value = "2024-01-15"
        
        # Mock service response
        transactions = [
            self.sample_transaction,  # 2024-01-15
            Transaction(
                id='2',
                amount=Decimal('50'),
                description='Transport',
                category='Transportation',
                transaction_type=TransactionType.EXPENSE,
                date=datetime(2024, 1, 16)
            )
        ]
        self.mock_transaction_service.get_all_transactions.return_value = transactions
        
        # Call method
        result = self.interface._get_filtered_transactions()
        
        # Verify result - should only include transaction from 2024-01-15
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].date.date(), date(2024, 1, 15))
    
    def test_display_summary_report(self):
        """Test displaying summary report."""
        # Mock report data
        summary = {
            'totals': {
                'total_income': Decimal('1000'),
                'total_expenses': Decimal('500'),
                'net_balance': Decimal('500'),
                'total_transactions': 10
            }
        }
        
        # Mock report service
        self.mock_report_service.generate_summary_report.return_value = summary
        
        # Mock report display frame
        self.interface.report_display_frame = Mock()
        
        # Call method
        self.interface._display_summary_report(None, None)
        
        # Verify report service was called
        self.mock_report_service.generate_summary_report.assert_called_once_with(None, None)
    
    @patch('expense_tracker.ui.gui_interface.messagebox')
    def test_generate_chart_matplotlib_not_available(self, mock_messagebox):
        """Test chart generation when matplotlib is not available."""
        # Mock chart service
        self.mock_chart_service.is_matplotlib_available.return_value = False
        
        # Call method
        self.interface._generate_chart()
        
        # Verify error message
        mock_messagebox.showerror.assert_called_once_with(
            "Error", 
            "Matplotlib is not available. Please install it with: pip install matplotlib"
        )
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.path.exists')
    def test_generate_chart_success(self, mock_exists, mock_tempfile):
        """Test successful chart generation."""
        # Mock chart service
        self.mock_chart_service.is_matplotlib_available.return_value = True
        self.mock_chart_service.create_pie_chart.return_value = True
        
        # Mock tempfile
        mock_temp = Mock()
        mock_temp.name = "/tmp/test_chart.png"
        mock_tempfile.return_value = mock_temp
        
        # Mock file exists
        mock_exists.return_value = True
        
        # Mock chart type variable
        self.interface.chart_type_var = Mock()
        self.interface.chart_type_var.get.return_value = "Pie Chart"
        
        # Mock display frame
        self.interface.chart_display_frame = Mock()
        self.interface.chart_display_frame.winfo_children.return_value = []
        
        # Mock display method
        self.interface._display_chart_image = Mock()
        
        # Call method
        self.interface._generate_chart()
        
        # Verify chart service was called
        self.mock_chart_service.create_pie_chart.assert_called_once_with(save_path="/tmp/test_chart.png")
        
        # Verify display method was called
        self.interface._display_chart_image.assert_called_once_with("/tmp/test_chart.png")
    
    @patch('expense_tracker.ui.gui_interface.filedialog')
    @patch('expense_tracker.ui.gui_interface.messagebox')
    def test_export_data_csv_success(self, mock_messagebox, mock_filedialog):
        """Test successful CSV data export."""
        # Mock file dialog
        mock_filedialog.asksaveasfilename.return_value = "/tmp/test_export.csv"
        
        # Mock export service
        self.mock_export_service.export_transactions_to_csv.return_value = True
        
        # Mock export type variable
        self.interface.export_type_var = Mock()
        self.interface.export_type_var.get.return_value = "Transactions CSV"
        
        # Mock status frame
        self.interface.export_status_frame = Mock()
        self.interface.export_status_frame.winfo_children.return_value = []
        
        # Mock root update
        self.interface.root = Mock()
        
        # Call method
        self.interface._export_data()
        
        # Verify export service was called
        self.mock_export_service.export_transactions_to_csv.assert_called_once_with("/tmp/test_export.csv")
    
    @patch('expense_tracker.ui.gui_interface.filedialog')
    def test_export_data_no_file_selected(self, mock_filedialog):
        """Test export when no file is selected."""
        # Mock file dialog to return empty string
        mock_filedialog.asksaveasfilename.return_value = ""
        
        # Mock export type variable
        self.interface.export_type_var = Mock()
        self.interface.export_type_var.get.return_value = "Transactions CSV"
        
        # Call method
        self.interface._export_data()
        
        # Verify export service was not called
        self.mock_export_service.export_transactions_to_csv.assert_not_called()
    
    def test_clear_transaction_form(self):
        """Test clearing transaction form."""
        # Mock form variables
        self.interface.amount_var = Mock()
        self.interface.description_var = Mock()
        self.interface.date_var = Mock()
        
        # Mock transaction type change method
        self.interface._on_transaction_type_change = Mock()
        
        # Call method
        self.interface._clear_transaction_form()
        
        # Verify form was cleared
        self.interface.amount_var.set.assert_called_once_with("")
        self.interface.description_var.set.assert_called_once_with("")
        self.interface.date_var.set.assert_called_once()
        self.interface._on_transaction_type_change.assert_called_once()


if __name__ == '__main__':
    unittest.main()