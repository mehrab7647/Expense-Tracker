"""Console interface for the expense tracker application."""

import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from ..models.enums import TransactionType
from ..services.transaction_service import TransactionService
from ..services.category_service import CategoryService
from ..services.report_service import ReportService
from ..services.export_service import ExportService
from ..services.chart_service import ChartService


class ConsoleInterface:
    """Text-based console interface for the expense tracker."""
    
    def __init__(
        self,
        transaction_service: TransactionService,
        category_service: CategoryService,
        report_service: ReportService,
        export_service: ExportService,
        chart_service: ChartService
    ):
        """Initialize the console interface."""
        self.transaction_service = transaction_service
        self.category_service = category_service
        self.report_service = report_service
        self.export_service = export_service
        self.chart_service = chart_service
        self.running = False
    
    def start(self) -> None:
        """Start the console interface main loop."""
        self.running = True
        self._print_welcome()
        
        while self.running:
            try:
                self._show_main_menu()
                choice = self._get_user_input("Enter your choice: ").strip()
                self._handle_main_menu_choice(choice)
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                self.running = False
            except Exception as e:
                print(f"\nError: {e}")
                self._pause()
    
    def _print_welcome(self) -> None:
        """Print welcome message."""
        self._clear_screen()
        print("=" * 60)
        print("           EXPENSE TRACKER - CONSOLE INTERFACE")
        print("=" * 60)
        print("Welcome to your personal expense tracking system!")
        print()
    
    def _show_main_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "=" * 40)
        print("              MAIN MENU")
        print("=" * 40)
        print("1. Transaction Management")
        print("2. Category Management")
        print("3. Reports & Analytics")
        print("4. Data Export")
        print("5. Charts & Visualization")
        print("6. Settings")
        print("0. Exit")
        print("-" * 40)
    
    def _handle_main_menu_choice(self, choice: str) -> None:
        """Handle main menu choice selection."""
        menu_actions = {
            '1': self._transaction_menu,
            '2': self._category_menu,
            '3': self._reports_menu,
            '4': self._export_menu,
            '5': self._charts_menu,
            '6': self._settings_menu,
            '0': self._exit_application
        }
        
        action = menu_actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice. Please try again.")
            self._pause()
    
    def _transaction_menu(self) -> None:
        """Display and handle transaction management menu."""
        while True:
            self._clear_screen()
            print("=" * 40)
            print("        TRANSACTION MANAGEMENT")
            print("=" * 40)
            print("1. Add New Transaction")
            print("2. View All Transactions")
            print("3. View Transactions by Category")
            print("4. View Transactions by Date Range")
            print("5. Search Transactions")
            print("6. Transaction Summary")
            print("0. Back to Main Menu")
            print("-" * 40)
            
            choice = self._get_user_input("Enter your choice: ").strip()
            
            if choice == '1':
                self._add_transaction()
            elif choice == '2':
                self._view_all_transactions()
            elif choice == '3':
                self._view_transactions_by_category()
            elif choice == '4':
                self._view_transactions_by_date_range()
            elif choice == '5':
                self._search_transactions()
            elif choice == '6':
                self._show_transaction_summary()
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
                self._pause()
    
    def _add_transaction(self) -> None:
        """Add a new transaction."""
        self._clear_screen()
        print("=" * 40)
        print("           ADD TRANSACTION")
        print("=" * 40)
        
        try:
            # Get transaction type
            print("Transaction Type:")
            print("1. Income")
            print("2. Expense")
            type_choice = self._get_user_input("Select type (1-2): ").strip()
            
            if type_choice == '1':
                transaction_type = TransactionType.INCOME
                categories = self.category_service.get_income_categories()
            elif type_choice == '2':
                transaction_type = TransactionType.EXPENSE
                categories = self.category_service.get_expense_categories()
            else:
                print("Invalid transaction type.")
                self._pause()
                return
            
            # Get amount
            amount_str = self._get_user_input("Enter amount: $").strip()
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    print("Amount must be greater than zero.")
                    self._pause()
                    return
            except InvalidOperation:
                print("Invalid amount format.")
                self._pause()
                return
            
            # Get description
            description = self._get_user_input("Enter description: ").strip()
            if not description:
                print("Description is required.")
                self._pause()
                return
            
            # Show categories and get selection
            print("\nAvailable Categories:")
            for i, category in enumerate(categories, 1):
                print(f"{i}. {category.name}")
            
            category_choice = self._get_user_input("Select category (number): ").strip()
            try:
                category_index = int(category_choice) - 1
                if 0 <= category_index < len(categories):
                    category = categories[category_index].name
                else:
                    print("Invalid category selection.")
                    self._pause()
                    return
            except ValueError:
                print("Invalid category selection.")
                self._pause()
                return
            
            # Get date (optional)
            date_str = self._get_user_input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            transaction_date = None
            if date_str:
                try:
                    transaction_date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    print("Invalid date format. Using today's date.")
            
            # Create transaction
            transaction = self.transaction_service.create_transaction(
                amount=amount,
                description=description,
                category=category,
                transaction_type=transaction_type,
                transaction_date=transaction_date
            )
            
            if transaction:
                print(f"\n✓ Transaction added successfully!")
                print(f"  ID: {transaction.id}")
                print(f"  Amount: ${transaction.amount}")
                print(f"  Description: {transaction.description}")
                print(f"  Category: {transaction.category}")
                print(f"  Type: {transaction.transaction_type.value}")
                print(f"  Date: {transaction.date.strftime('%Y-%m-%d')}")
            else:
                print("Failed to add transaction.")
            
        except Exception as e:
            print(f"Error adding transaction: {e}")
        
        self._pause()
    
    def _view_all_transactions(self) -> None:
        """View all transactions."""
        self._clear_screen()
        print("=" * 80)
        print("                           ALL TRANSACTIONS")
        print("=" * 80)
        
        transactions = self.transaction_service.get_all_transactions()
        
        if not transactions:
            print("No transactions found.")
        else:
            self._display_transactions(transactions)
        
        self._pause()
    
    def _view_transactions_by_category(self) -> None:
        """View transactions filtered by category."""
        self._clear_screen()
        print("=" * 40)
        print("      TRANSACTIONS BY CATEGORY")
        print("=" * 40)
        
        categories = self.category_service.get_all_categories()
        if not categories:
            print("No categories found.")
            self._pause()
            return
        
        print("Available Categories:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category.name}")
        
        choice = self._get_user_input("Select category (number): ").strip()
        try:
            category_index = int(choice) - 1
            if 0 <= category_index < len(categories):
                selected_category = categories[category_index].name
                transactions = self.transaction_service.filter_transactions_by_category(selected_category)
                
                print(f"\nTransactions in category '{selected_category}':")
                print("=" * 80)
                
                if not transactions:
                    print("No transactions found in this category.")
                else:
                    self._display_transactions(transactions)
            else:
                print("Invalid category selection.")
        except ValueError:
            print("Invalid category selection.")
        
        self._pause()
    
    def _view_transactions_by_date_range(self) -> None:
        """View transactions filtered by date range."""
        self._clear_screen()
        print("=" * 40)
        print("     TRANSACTIONS BY DATE RANGE")
        print("=" * 40)
        
        try:
            start_date_str = self._get_user_input("Enter start date (YYYY-MM-DD): ").strip()
            end_date_str = self._get_user_input("Enter end date (YYYY-MM-DD): ").strip()
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if start_date > end_date:
                print("Start date must be before end date.")
                self._pause()
                return
            
            transactions = self.transaction_service.filter_transactions_by_date_range(start_date, end_date)
            
            print(f"\nTransactions from {start_date} to {end_date}:")
            print("=" * 80)
            
            if not transactions:
                print("No transactions found in this date range.")
            else:
                self._display_transactions(transactions)
                
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
        
        self._pause()
    
    def _search_transactions(self) -> None:
        """Search transactions by description."""
        self._clear_screen()
        print("=" * 40)
        print("         SEARCH TRANSACTIONS")
        print("=" * 40)
        
        search_term = self._get_user_input("Enter search term: ").strip().lower()
        if not search_term:
            print("Search term cannot be empty.")
            self._pause()
            return
        
        all_transactions = self.transaction_service.get_all_transactions()
        matching_transactions = [
            t for t in all_transactions 
            if search_term in t.description.lower()
        ]
        
        print(f"\nTransactions containing '{search_term}':")
        print("=" * 80)
        
        if not matching_transactions:
            print("No matching transactions found.")
        else:
            self._display_transactions(matching_transactions)
        
        self._pause()
    
    def _show_transaction_summary(self) -> None:
        """Show transaction summary statistics."""
        self._clear_screen()
        print("=" * 40)
        print("        TRANSACTION SUMMARY")
        print("=" * 40)
        
        summary = self.transaction_service.get_transaction_summary()
        
        print(f"Total Income:      ${summary['total_income']:>10,.2f}")
        print(f"Total Expenses:    ${summary['total_expenses']:>10,.2f}")
        print(f"Net Balance:       ${summary['net_balance']:>10,.2f}")
        print("-" * 40)
        print(f"Total Transactions: {summary['transaction_count']:>9}")
        print(f"Income Transactions: {summary['income_count']:>8}")
        print(f"Expense Transactions: {summary['expense_count']:>7}")
        
        self._pause()
    
    def _category_menu(self) -> None:
        """Display and handle category management menu."""
        while True:
            self._clear_screen()
            print("=" * 40)
            print("         CATEGORY MANAGEMENT")
            print("=" * 40)
            print("1. View All Categories")
            print("2. Add New Category")
            print("3. Category Usage Statistics")
            print("0. Back to Main Menu")
            print("-" * 40)
            
            choice = self._get_user_input("Enter your choice: ").strip()
            
            if choice == '1':
                self._view_all_categories()
            elif choice == '2':
                self._add_category()
            elif choice == '3':
                self._show_category_usage()
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
                self._pause()
    
    def _view_all_categories(self) -> None:
        """View all categories."""
        self._clear_screen()
        print("=" * 50)
        print("                ALL CATEGORIES")
        print("=" * 50)
        
        categories = self.category_service.get_all_categories()
        
        if not categories:
            print("No categories found.")
        else:
            income_categories = [cat for cat in categories if cat.category_type.value == 'INCOME']
            expense_categories = [cat for cat in categories if cat.category_type.value == 'EXPENSE']
            
            if income_categories:
                print("\nINCOME CATEGORIES:")
                print("-" * 30)
                for category in income_categories:
                    status = "(Default)" if category.is_default else "(Custom)"
                    print(f"  • {category.name} {status}")
            
            if expense_categories:
                print("\nEXPENSE CATEGORIES:")
                print("-" * 30)
                for category in expense_categories:
                    status = "(Default)" if category.is_default else "(Custom)"
                    print(f"  • {category.name} {status}")
        
        self._pause()
    
    def _add_category(self) -> None:
        """Add a new category."""
        self._clear_screen()
        print("=" * 40)
        print("            ADD CATEGORY")
        print("=" * 40)
        
        try:
            # Get category name
            name = self._get_user_input("Enter category name: ").strip()
            if not name:
                print("Category name is required.")
                self._pause()
                return
            
            # Check if category already exists
            if self.category_service.category_exists(name):
                print(f"Category '{name}' already exists.")
                self._pause()
                return
            
            # Get category type
            print("\nCategory Type:")
            print("1. Income")
            print("2. Expense")
            type_choice = self._get_user_input("Select type (1-2): ").strip()
            
            if type_choice == '1':
                from ..models.enums import CategoryType
                category_type = CategoryType.INCOME
            elif type_choice == '2':
                from ..models.enums import CategoryType
                category_type = CategoryType.EXPENSE
            else:
                print("Invalid category type.")
                self._pause()
                return
            
            # Create category
            category = self.category_service.create_category(name, category_type)
            
            if category:
                print(f"\n✓ Category '{category.name}' added successfully!")
                print(f"  Type: {category.category_type.value}")
            else:
                print("Failed to add category.")
            
        except Exception as e:
            print(f"Error adding category: {e}")
        
        self._pause()
    
    def _show_category_usage(self) -> None:
        """Show category usage statistics."""
        self._clear_screen()
        print("=" * 50)
        print("           CATEGORY USAGE STATISTICS")
        print("=" * 50)
        
        usage_stats = self.category_service.get_category_usage_stats()
        
        if not usage_stats:
            print("No usage statistics available.")
        else:
            # Sort by usage count (descending)
            sorted_stats = sorted(usage_stats.items(), key=lambda x: x[1], reverse=True)
            
            print(f"{'Category':<20} {'Transactions':<12}")
            print("-" * 35)
            
            for category, count in sorted_stats:
                print(f"{category:<20} {count:<12}")
        
        self._pause()
    
    def _reports_menu(self) -> None:
        """Display and handle reports menu."""
        while True:
            self._clear_screen()
            print("=" * 40)
            print("          REPORTS & ANALYTICS")
            print("=" * 40)
            print("1. Financial Summary")
            print("2. Category Breakdown")
            print("3. Monthly Report")
            print("4. Trend Analysis")
            print("0. Back to Main Menu")
            print("-" * 40)
            
            choice = self._get_user_input("Enter your choice: ").strip()
            
            if choice == '1':
                self._show_financial_summary()
            elif choice == '2':
                self._show_category_breakdown()
            elif choice == '3':
                self._show_monthly_report()
            elif choice == '4':
                self._show_trend_analysis()
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
                self._pause()
    
    def _show_financial_summary(self) -> None:
        """Show financial summary report."""
        self._clear_screen()
        print("=" * 50)
        print("              FINANCIAL SUMMARY")
        print("=" * 50)
        
        # Get date range (optional)
        use_date_filter = self._get_user_input("Filter by date range? (y/n): ").strip().lower()
        start_date = None
        end_date = None
        
        if use_date_filter == 'y':
            try:
                start_date_str = self._get_user_input("Enter start date (YYYY-MM-DD): ").strip()
                end_date_str = self._get_user_input("Enter end date (YYYY-MM-DD): ").strip()
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                print("Invalid date format. Showing all data.")
                start_date = None
                end_date = None
        
        summary = self.report_service.generate_summary_report(start_date, end_date)
        
        # Display period info
        if start_date and end_date:
            print(f"Period: {start_date} to {end_date}")
            print("-" * 50)
        
        # Display totals
        print(f"Total Income:      ${summary['totals']['total_income']:>12,.2f}")
        print(f"Total Expenses:    ${summary['totals']['total_expenses']:>12,.2f}")
        print(f"Net Balance:       ${summary['totals']['net_balance']:>12,.2f}")
        print("-" * 50)
        
        # Display counts
        print(f"Total Transactions: {summary['totals']['total_transactions']:>11}")
        print(f"Income Transactions: {summary['counts']['income_transactions']:>10}")
        print(f"Expense Transactions: {summary['counts']['expense_transactions']:>9}")
        print("-" * 50)
        
        # Display averages
        print(f"Average Income:    ${summary['averages']['average_income']:>12,.2f}")
        print(f"Average Expense:   ${summary['averages']['average_expense']:>12,.2f}")
        
        self._pause()
    
    def _show_category_breakdown(self) -> None:
        """Show category breakdown report."""
        self._clear_screen()
        print("=" * 60)
        print("                 CATEGORY BREAKDOWN")
        print("=" * 60)
        
        # Get transaction type filter
        print("Filter by transaction type:")
        print("1. All transactions")
        print("2. Income only")
        print("3. Expenses only")
        type_choice = self._get_user_input("Select option (1-3): ").strip()
        
        transaction_type = None
        if type_choice == '2':
            transaction_type = TransactionType.INCOME
        elif type_choice == '3':
            transaction_type = TransactionType.EXPENSE
        
        report = self.report_service.generate_category_breakdown_report(
            transaction_type=transaction_type
        )
        
        if not report['categories']:
            print("No data available for the selected criteria.")
        else:
            print(f"\n{'Category':<20} {'Amount':<12} {'Count':<8} {'Percentage':<10}")
            print("-" * 55)
            
            for category, data in report['categories'].items():
                print(f"{category:<20} ${data['total_amount']:>10,.2f} "
                      f"{data['transaction_count']:>6} {data['percentage']:>8.1f}%")
            
            print("-" * 55)
            print(f"{'TOTAL':<20} ${report['summary']['total_amount']:>10,.2f} "
                  f"{report['summary']['total_transactions']:>6}")
        
        self._pause()
    
    def _show_monthly_report(self) -> None:
        """Show monthly report."""
        self._clear_screen()
        print("=" * 60)
        print("                  MONTHLY REPORT")
        print("=" * 60)
        
        try:
            year_str = self._get_user_input("Enter year (YYYY): ").strip()
            year = int(year_str)
            
            report = self.report_service.generate_monthly_report(year)
            
            print(f"\nMonthly Report for {year}")
            print("=" * 60)
            print(f"{'Month':<12} {'Income':<12} {'Expenses':<12} {'Net Balance':<12}")
            print("-" * 60)
            
            for month_name, data in report['monthly_data'].items():
                print(f"{month_name:<12} ${data['income']:>10,.2f} "
                      f"${data['expenses']:>10,.2f} ${data['net_balance']:>10,.2f}")
            
            print("-" * 60)
            print(f"{'TOTAL':<12} ${report['summary']['total_income']:>10,.2f} "
                  f"${report['summary']['total_expenses']:>10,.2f} "
                  f"${report['summary']['net_balance']:>10,.2f}")
            
        except ValueError:
            print("Invalid year format.")
        except Exception as e:
            print(f"Error generating monthly report: {e}")
        
        self._pause()
    
    def _show_trend_analysis(self) -> None:
        """Show trend analysis."""
        self._clear_screen()
        print("=" * 50)
        print("              TREND ANALYSIS")
        print("=" * 50)
        
        try:
            start_date_str = self._get_user_input("Enter start date (YYYY-MM-DD): ").strip()
            end_date_str = self._get_user_input("Enter end date (YYYY-MM-DD): ").strip()
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            print("Select period:")
            print("1. Daily")
            print("2. Weekly")
            print("3. Monthly")
            period_choice = self._get_user_input("Select period (1-3): ").strip()
            
            period_map = {'1': 'daily', '2': 'weekly', '3': 'monthly'}
            period = period_map.get(period_choice, 'monthly')
            
            trend_data = self.report_service.generate_trend_analysis(start_date, end_date, period)
            
            print(f"\n{period.title()} Trend Analysis")
            print("=" * 60)
            print(f"{'Period':<12} {'Income':<12} {'Expenses':<12} {'Net Balance':<12}")
            print("-" * 60)
            
            for item in trend_data['data']:
                print(f"{item['period']:<12} ${item['income']:>10,.2f} "
                      f"${item['expenses']:>10,.2f} ${item['net_balance']:>10,.2f}")
            
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
        except Exception as e:
            print(f"Error generating trend analysis: {e}")
        
        self._pause()
    
    def _export_menu(self) -> None:
        """Display and handle export menu."""
        while True:
            self._clear_screen()
            print("=" * 40)
            print("            DATA EXPORT")
            print("=" * 40)
            print("1. Export Transactions to CSV")
            print("2. Export Transactions to Excel")
            print("3. Export Category Summary to CSV")
            print("4. Export Monthly Report to Excel")
            print("0. Back to Main Menu")
            print("-" * 40)
            
            choice = self._get_user_input("Enter your choice: ").strip()
            
            if choice == '1':
                self._export_transactions_csv()
            elif choice == '2':
                self._export_transactions_excel()
            elif choice == '3':
                self._export_category_summary()
            elif choice == '4':
                self._export_monthly_report()
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
                self._pause()
    
    def _export_transactions_csv(self) -> None:
        """Export transactions to CSV."""
        self._clear_screen()
        print("=" * 40)
        print("      EXPORT TRANSACTIONS TO CSV")
        print("=" * 40)
        
        file_path = self._get_user_input("Enter file path (e.g., exports/transactions.csv): ").strip()
        if not file_path:
            print("File path is required.")
            self._pause()
            return
        
        # Add .csv extension if not present
        if not file_path.lower().endswith('.csv'):
            file_path += '.csv'
        
        try:
            success = self.export_service.export_transactions_to_csv(file_path)
            if success:
                print(f"✓ Transactions exported successfully to: {file_path}")
            else:
                print("Failed to export transactions.")
        except Exception as e:
            print(f"Error exporting transactions: {e}")
        
        self._pause()
    
    def _export_transactions_excel(self) -> None:
        """Export transactions to Excel."""
        self._clear_screen()
        print("=" * 40)
        print("     EXPORT TRANSACTIONS TO EXCEL")
        print("=" * 40)
        
        file_path = self._get_user_input("Enter file path (e.g., exports/transactions.xlsx): ").strip()
        if not file_path:
            print("File path is required.")
            self._pause()
            return
        
        # Add .xlsx extension if not present
        if not file_path.lower().endswith('.xlsx'):
            file_path += '.xlsx'
        
        include_summary = self._get_user_input("Include summary sheet? (y/n): ").strip().lower() == 'y'
        
        try:
            success = self.export_service.export_transactions_to_excel(
                file_path, include_summary=include_summary
            )
            if success:
                print(f"✓ Transactions exported successfully to: {file_path}")
            else:
                print("Failed to export transactions.")
        except Exception as e:
            print(f"Error exporting transactions: {e}")
        
        self._pause()
    
    def _export_category_summary(self) -> None:
        """Export category summary to CSV."""
        self._clear_screen()
        print("=" * 40)
        print("    EXPORT CATEGORY SUMMARY TO CSV")
        print("=" * 40)
        
        file_path = self._get_user_input("Enter file path (e.g., exports/category_summary.csv): ").strip()
        if not file_path:
            print("File path is required.")
            self._pause()
            return
        
        # Add .csv extension if not present
        if not file_path.lower().endswith('.csv'):
            file_path += '.csv'
        
        try:
            # Generate category breakdown report
            report = self.report_service.generate_category_breakdown_report()
            
            # Create CSV data
            csv_data = []
            csv_data.append(['Category', 'Total Amount', 'Transaction Count', 'Percentage'])
            
            for category, data in report['categories'].items():
                csv_data.append([
                    category,
                    str(data['total_amount']),
                    str(data['transaction_count']),
                    f"{data['percentage']:.1f}%"
                ])
            
            # Add summary row
            csv_data.append(['TOTAL', str(report['summary']['total_amount']), 
                           str(report['summary']['total_transactions']), '100.0%'])
            
            success = self.export_service.export_data_to_csv(file_path, csv_data)
            if success:
                print(f"✓ Category summary exported successfully to: {file_path}")
            else:
                print("Failed to export category summary.")
        except Exception as e:
            print(f"Error exporting category summary: {e}")
        
        self._pause()
    
    def _export_monthly_report(self) -> None:
        """Export monthly report to Excel."""
        self._clear_screen()
        print("=" * 40)
        print("   EXPORT MONTHLY REPORT TO EXCEL")
        print("=" * 40)
        
        try:
            year_str = self._get_user_input("Enter year (YYYY): ").strip()
            year = int(year_str)
            
            file_path = self._get_user_input("Enter file path (e.g., exports/monthly_report.xlsx): ").strip()
            if not file_path:
                print("File path is required.")
                self._pause()
                return
            
            # Add .xlsx extension if not present
            if not file_path.lower().endswith('.xlsx'):
                file_path += '.xlsx'
            
            # Generate monthly report
            report = self.report_service.generate_monthly_report(year)
            
            # Create Excel data
            excel_data = []
            excel_data.append(['Month', 'Income', 'Expenses', 'Net Balance'])
            
            for month_name, data in report['monthly_data'].items():
                excel_data.append([
                    month_name,
                    float(data['income']),
                    float(data['expenses']),
                    float(data['net_balance'])
                ])
            
            # Add summary row
            excel_data.append([
                'TOTAL',
                float(report['summary']['total_income']),
                float(report['summary']['total_expenses']),
                float(report['summary']['net_balance'])
            ])
            
            success = self.export_service.export_data_to_excel(file_path, excel_data, 'Monthly Report')
            if success:
                print(f"✓ Monthly report exported successfully to: {file_path}")
            else:
                print("Failed to export monthly report.")
        except ValueError:
            print("Invalid year format.")
        except Exception as e:
            print(f"Error exporting monthly report: {e}")
        
        self._pause()
    
    def _charts_menu(self) -> None:
        """Display and handle charts menu."""
        while True:
            self._clear_screen()
            print("=" * 40)
            print("        CHARTS & VISUALIZATION")
            print("=" * 40)
            print("1. Generate Pie Chart")
            print("2. Generate Bar Chart")
            print("3. Generate Line Chart")
            print("4. Generate Trend Chart")
            print("5. Generate Category Comparison Chart")
            print("0. Back to Main Menu")
            print("-" * 40)
            
            choice = self._get_user_input("Enter your choice: ").strip()
            
            if choice == '1':
                self._generate_pie_chart()
            elif choice == '2':
                self._generate_bar_chart()
            elif choice == '3':
                self._generate_line_chart()
            elif choice == '4':
                self._generate_trend_chart()
            elif choice == '5':
                self._generate_category_comparison_chart()
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
                self._pause()
    
    def _generate_pie_chart(self) -> None:
        """Generate pie chart."""
        self._clear_screen()
        print("=" * 40)
        print("         GENERATE PIE CHART")
        print("=" * 40)
        
        if not self.chart_service.is_matplotlib_available():
            print("Matplotlib is not available. Please install it with: pip install matplotlib")
            self._pause()
            return
        
        file_path = self._get_user_input("Enter save path (e.g., charts/pie_chart.png): ").strip()
        if not file_path:
            print("File path is required.")
            self._pause()
            return
        
        try:
            success = self.chart_service.create_pie_chart(save_path=file_path)
            if success:
                print(f"✓ Pie chart generated successfully: {file_path}")
            else:
                print("Failed to generate pie chart.")
        except Exception as e:
            print(f"Error generating pie chart: {e}")
        
        self._pause()
    
    def _generate_bar_chart(self) -> None:
        """Generate bar chart."""
        self._clear_screen()
        print("=" * 40)
        print("         GENERATE BAR CHART")
        print("=" * 40)
        
        if not self.chart_service.is_matplotlib_available():
            print("Matplotlib is not available. Please install it with: pip install matplotlib")
            self._pause()
            return
        
        file_path = self._get_user_input("Enter save path (e.g., charts/bar_chart.png): ").strip()
        if not file_path:
            print("File path is required.")
            self._pause()
            return
        
        try:
            success = self.chart_service.create_bar_chart(save_path=file_path)
            if success:
                print(f"✓ Bar chart generated successfully: {file_path}")
            else:
                print("Failed to generate bar chart.")
        except Exception as e:
            print(f"Error generating bar chart: {e}")
        
        self._pause()
    
    def _generate_line_chart(self) -> None:
        """Generate line chart."""
        self._clear_screen()
        print("=" * 40)
        print("         GENERATE LINE CHART")
        print("=" * 40)
        
        if not self.chart_service.is_matplotlib_available():
            print("Matplotlib is not available. Please install it with: pip install matplotlib")
            self._pause()
            return
        
        file_path = self._get_user_input("Enter save path (e.g., charts/line_chart.png): ").strip()
        if not file_path:
            print("File path is required.")
            self._pause()
            return
        
        try:
            success = self.chart_service.create_line_chart(save_path=file_path)
            if success:
                print(f"✓ Line chart generated successfully: {file_path}")
            else:
                print("Failed to generate line chart.")
        except Exception as e:
            print(f"Error generating line chart: {e}")
        
        self._pause()
    
    def _generate_trend_chart(self) -> None:
        """Generate trend chart."""
        self._clear_screen()
        print("=" * 40)
        print("        GENERATE TREND CHART")
        print("=" * 40)
        
        if not self.chart_service.is_matplotlib_available():
            print("Matplotlib is not available. Please install it with: pip install matplotlib")
            self._pause()
            return
        
        try:
            start_date_str = self._get_user_input("Enter start date (YYYY-MM-DD): ").strip()
            end_date_str = self._get_user_input("Enter end date (YYYY-MM-DD): ").strip()
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            file_path = self._get_user_input("Enter save path (e.g., charts/trend_chart.png): ").strip()
            if not file_path:
                print("File path is required.")
                self._pause()
                return
            
            success = self.chart_service.create_trend_chart(
                start_date=start_date,
                end_date=end_date,
                save_path=file_path
            )
            if success:
                print(f"✓ Trend chart generated successfully: {file_path}")
            else:
                print("Failed to generate trend chart.")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
        except Exception as e:
            print(f"Error generating trend chart: {e}")
        
        self._pause()
    
    def _generate_category_comparison_chart(self) -> None:
        """Generate category comparison chart."""
        self._clear_screen()
        print("=" * 40)
        print("   GENERATE CATEGORY COMPARISON CHART")
        print("=" * 40)
        
        if not self.chart_service.is_matplotlib_available():
            print("Matplotlib is not available. Please install it with: pip install matplotlib")
            self._pause()
            return
        
        file_path = self._get_user_input("Enter save path (e.g., charts/category_comparison.png): ").strip()
        if not file_path:
            print("File path is required.")
            self._pause()
            return
        
        try:
            success = self.chart_service.create_category_comparison_chart(save_path=file_path)
            if success:
                print(f"✓ Category comparison chart generated successfully: {file_path}")
            else:
                print("Failed to generate category comparison chart.")
        except Exception as e:
            print(f"Error generating category comparison chart: {e}")
        
        self._pause()
    
    def _settings_menu(self) -> None:
        """Display and handle settings menu."""
        while True:
            self._clear_screen()
            print("=" * 40)
            print("             SETTINGS")
            print("=" * 40)
            print("1. Application Information")
            print("2. Data File Information")
            print("3. Chart Format Information")
            print("0. Back to Main Menu")
            print("-" * 40)
            
            choice = self._get_user_input("Enter your choice: ").strip()
            
            if choice == '1':
                self._show_app_info()
            elif choice == '2':
                self._show_data_file_info()
            elif choice == '3':
                self._show_chart_formats()
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
                self._pause()
    
    def _show_app_info(self) -> None:
        """Show application information."""
        self._clear_screen()
        print("APPLICATION INFO".center(50))
        print("=" * 50)
        print("Expense Tracker v1.0")
        print("Personal Finance Management System")
        print()
        print("Features:")
        print("• Transaction Management")
        print("• Category Organization")
        print("• Financial Reports")
        print("• Data Export (CSV/Excel)")
        print("• Chart Generation")
        print()
        print("Chart Support:")
        if self.chart_service.is_matplotlib_available():
            print("✓ Matplotlib available - Charts enabled")
        else:
            print("✗ Matplotlib not available - Charts disabled")
        
        self._pause()
    
    def _show_data_file_info(self) -> None:
        """Show data file information."""
        self._clear_screen()
        print("=" * 50)
        print("           DATA FILE INFORMATION")
        print("=" * 50)
        
        # Get transaction count
        transactions = self.transaction_service.get_all_transactions()
        categories = self.category_service.get_all_categories()
        
        print(f"Total Transactions: {len(transactions)}")
        print(f"Total Categories: {len(categories)}")
        print()
        print("Data Storage: JSON format")
        print("Location: data/expense_data.json")
        
        self._pause()
    
    def _show_chart_formats(self) -> None:
        """Show available chart formats."""
        self._clear_screen()
        print("=" * 50)
        print("         CHART FORMAT INFORMATION")
        print("=" * 50)
        
        if self.chart_service.is_matplotlib_available():
            formats = self.chart_service.get_available_formats()
            print("Supported chart formats:")
            for fmt in formats:
                print(f"  • {fmt}")
        else:
            print("Matplotlib is not available.")
            print("Install with: pip install matplotlib")
        
        self._pause()
    
    def _exit_application(self) -> None:
        """Exit the application."""
        print("\nThank you for using Expense Tracker!")
        print("Goodbye!")
        self.running = False
    
    def _display_transactions(self, transactions: List) -> None:
        """Display a list of transactions in a formatted table."""
        if not transactions:
            print("No transactions to display.")
            return
        
        print(f"{'Date':<12} {'Type':<8} {'Category':<15} {'Description':<25} {'Amount':<10}")
        print("-" * 80)
        
        for transaction in transactions:
            date_str = transaction.date.strftime('%Y-%m-%d')
            type_str = transaction.transaction_type.value[:7]
            category_str = transaction.category[:14]
            description_str = transaction.description[:24]
            amount_str = f"${transaction.amount:.2f}"
            
            print(f"{date_str:<12} {type_str:<8} {category_str:<15} {description_str:<25} {amount_str:<10}")
    
    def _clear_screen(self) -> None:
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _get_user_input(self, prompt: str) -> str:
        """Get user input with prompt."""
        try:
            return input(prompt)
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt()
    
    def _pause(self) -> None:
        """Pause and wait for user input."""
        try:
            input("\nPress Enter to continue...")
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt()