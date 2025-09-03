"""GUI interface for the expense tracker application using tkinter."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import os

from ..models.enums import TransactionType, CategoryType
from ..services.transaction_service import TransactionService
from ..services.category_service import CategoryService
from ..services.report_service import ReportService
from ..services.export_service import ExportService
from ..services.chart_service import ChartService


class GUIInterface:
    """Tkinter-based GUI interface for the expense tracker."""
    
    def __init__(
        self,
        transaction_service: TransactionService,
        category_service: CategoryService,
        report_service: ReportService,
        export_service: ExportService,
        chart_service: ChartService
    ):
        """Initialize the GUI interface."""
        self.transaction_service = transaction_service
        self.category_service = category_service
        self.report_service = report_service
        self.export_service = export_service
        self.chart_service = chart_service
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Expense Tracker")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Initialize UI components
        self._setup_ui()
        
        # Track current view
        self.current_frame = None
    
    def start(self) -> None:
        """Start the GUI application."""
        self._show_main_view()
        self.root.mainloop()
    
    def _setup_ui(self) -> None:
        """Set up the main UI structure."""
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header
        self._create_header()
        
        # Create navigation
        self._create_navigation()
        
        # Create content area
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
    
    def _create_header(self) -> None:
        """Create the application header."""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame,
            text="Expense Tracker",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # Add summary info
        self.summary_label = ttk.Label(
            header_frame,
            text="Loading...",
            font=('Arial', 10)
        )
        self.summary_label.pack(side=tk.RIGHT)
        
        # Update summary
        self._update_summary()
    
    def _create_navigation(self) -> None:
        """Create the navigation menu."""
        nav_frame = ttk.Frame(self.main_container)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self._show_main_view),
            ("Add Transaction", self._show_add_transaction),
            ("View Transactions", self._show_transactions),
            ("Categories", self._show_categories),
            ("Reports", self._show_reports),
            ("Charts", self._show_charts),
            ("Export", self._show_export)
        ]
        
        for text, command in nav_buttons:
            btn = ttk.Button(nav_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=(0, 5))
    
    def _update_summary(self) -> None:
        """Update the summary information in the header."""
        try:
            summary = self.transaction_service.get_transaction_summary()
            summary_text = (
                f"Balance: ${summary['net_balance']:,.2f} | "
                f"Income: ${summary['total_income']:,.2f} | "
                f"Expenses: ${summary['total_expenses']:,.2f} | "
                f"Transactions: {summary['transaction_count']}"
            )
            self.summary_label.config(text=summary_text)
        except Exception as e:
            self.summary_label.config(text="Error loading summary")
    
    def _clear_content(self) -> None:
        """Clear the content area."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _show_main_view(self) -> None:
        """Show the main dashboard view."""
        self._clear_content()
        self._update_summary()
        
        # Create dashboard
        dashboard_frame = ttk.Frame(self.content_frame)
        dashboard_frame.pack(fill=tk.BOTH, expand=True)
        
        # Welcome section
        welcome_frame = ttk.LabelFrame(dashboard_frame, text="Welcome", padding=10)
        welcome_frame.pack(fill=tk.X, pady=(0, 10))
        
        welcome_text = (
            "Welcome to Expense Tracker! Use the navigation buttons above to:\n"
            "• Add new income and expense transactions\n"
            "• View and filter your transaction history\n"
            "• Manage categories for better organization\n"
            "• Generate detailed financial reports\n"
            "• Create charts and visualizations\n"
            "• Export your data to CSV or Excel"
        )
        
        ttk.Label(welcome_frame, text=welcome_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Quick stats
        stats_frame = ttk.LabelFrame(dashboard_frame, text="Quick Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        try:
            summary = self.transaction_service.get_transaction_summary()
            
            # Create stats grid
            stats_grid = ttk.Frame(stats_frame)
            stats_grid.pack(fill=tk.X)
            
            stats_data = [
                ("Total Income", f"${summary['total_income']:,.2f}"),
                ("Total Expenses", f"${summary['total_expenses']:,.2f}"),
                ("Net Balance", f"${summary['net_balance']:,.2f}"),
                ("Total Transactions", str(summary['transaction_count']))
            ]
            
            for i, (label, value) in enumerate(stats_data):
                row = i // 2
                col = i % 2
                
                stat_frame = ttk.Frame(stats_grid)
                stat_frame.grid(row=row, column=col, padx=10, pady=5, sticky=tk.W)
                
                ttk.Label(stat_frame, text=f"{label}:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
                ttk.Label(stat_frame, text=value, font=('Arial', 12)).pack(anchor=tk.W)
        
        except Exception as e:
            ttk.Label(stats_frame, text=f"Error loading statistics: {e}").pack()
        
        # Recent transactions
        recent_frame = ttk.LabelFrame(dashboard_frame, text="Recent Transactions", padding=10)
        recent_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_transaction_list(recent_frame, limit=10)
    
    def _show_add_transaction(self) -> None:
        """Show the add transaction form."""
        self._clear_content()
        
        # Create form
        form_frame = ttk.LabelFrame(self.content_frame, text="Add New Transaction", padding=20)
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Transaction type
        ttk.Label(form_frame, text="Transaction Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.transaction_type_var = tk.StringVar(value="EXPENSE")
        type_frame = ttk.Frame(form_frame)
        type_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(type_frame, text="Income", variable=self.transaction_type_var, 
                       value="INCOME", command=self._on_transaction_type_change).pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Expense", variable=self.transaction_type_var, 
                       value="EXPENSE", command=self._on_transaction_type_change).pack(side=tk.LEFT, padx=(10, 0))
        
        # Amount
        ttk.Label(form_frame, text="Amount:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(form_frame, textvariable=self.amount_var, width=20)
        amount_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.description_var = tk.StringVar()
        description_entry = ttk.Entry(form_frame, textvariable=self.description_var, width=40)
        description_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Category
        ttk.Label(form_frame, text="Category:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, width=30, state="readonly")
        self.category_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Date
        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(form_frame, textvariable=self.date_var, width=20)
        date_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add Transaction", command=self._add_transaction).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear Form", command=self._clear_transaction_form).pack(side=tk.LEFT)
        
        # Initialize categories
        self._on_transaction_type_change()
    
    def _on_transaction_type_change(self) -> None:
        """Handle transaction type change."""
        transaction_type = self.transaction_type_var.get()
        
        if transaction_type == "INCOME":
            categories = self.category_service.get_income_categories()
        else:
            categories = self.category_service.get_expense_categories()
        
        category_names = [cat.name for cat in categories]
        self.category_combo['values'] = category_names
        
        if category_names:
            self.category_var.set(category_names[0])
    
    def _add_transaction(self) -> None:
        """Add a new transaction."""
        try:
            # Validate inputs
            amount_str = self.amount_var.get().strip()
            if not amount_str:
                messagebox.showerror("Error", "Amount is required.")
                return
            
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than zero.")
                    return
            except InvalidOperation:
                messagebox.showerror("Error", "Invalid amount format.")
                return
            
            description = self.description_var.get().strip()
            if not description:
                messagebox.showerror("Error", "Description is required.")
                return
            
            category = self.category_var.get()
            if not category:
                messagebox.showerror("Error", "Category is required.")
                return
            
            # Parse date
            date_str = self.date_var.get().strip()
            transaction_date = None
            if date_str:
                try:
                    transaction_date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                    return
            
            # Create transaction
            transaction_type = TransactionType.INCOME if self.transaction_type_var.get() == "INCOME" else TransactionType.EXPENSE
            
            transaction = self.transaction_service.create_transaction(
                amount=amount,
                description=description,
                category=category,
                transaction_type=transaction_type,
                transaction_date=transaction_date
            )
            
            if transaction:
                messagebox.showinfo("Success", "Transaction added successfully!")
                self._clear_transaction_form()
                self._update_summary()
            else:
                messagebox.showerror("Error", "Failed to add transaction.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error adding transaction: {e}")
    
    def _clear_transaction_form(self) -> None:
        """Clear the transaction form."""
        self.amount_var.set("")
        self.description_var.set("")
        self.date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self._on_transaction_type_change()  # Reset category
    
    def _show_transactions(self) -> None:
        """Show the transactions view."""
        self._clear_content()
        
        # Create transactions view
        transactions_frame = ttk.Frame(self.content_frame)
        transactions_frame.pack(fill=tk.BOTH, expand=True)
        
        # Filters
        filter_frame = ttk.LabelFrame(transactions_frame, text="Filters", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Filter controls
        filter_controls = ttk.Frame(filter_frame)
        filter_controls.pack(fill=tk.X)
        
        # Category filter
        ttk.Label(filter_controls, text="Category:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.filter_category_var = tk.StringVar(value="All")
        category_filter = ttk.Combobox(filter_controls, textvariable=self.filter_category_var, width=20, state="readonly")
        category_filter.grid(row=0, column=1, padx=(0, 10))
        
        # Type filter
        ttk.Label(filter_controls, text="Type:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.filter_type_var = tk.StringVar(value="All")
        type_filter = ttk.Combobox(filter_controls, textvariable=self.filter_type_var, 
                                  values=["All", "Income", "Expense"], width=15, state="readonly")
        type_filter.grid(row=0, column=3, padx=(0, 10))
        
        # Date filters
        ttk.Label(filter_controls, text="From:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.filter_start_date_var = tk.StringVar()
        start_date_entry = ttk.Entry(filter_controls, textvariable=self.filter_start_date_var, width=12)
        start_date_entry.grid(row=0, column=5, padx=(0, 10))
        
        ttk.Label(filter_controls, text="To:").grid(row=0, column=6, sticky=tk.W, padx=(0, 5))
        self.filter_end_date_var = tk.StringVar()
        end_date_entry = ttk.Entry(filter_controls, textvariable=self.filter_end_date_var, width=12)
        end_date_entry.grid(row=0, column=7, padx=(0, 10))
        
        # Filter button
        ttk.Button(filter_controls, text="Apply Filters", command=self._apply_transaction_filters).grid(row=0, column=8, padx=(10, 0))
        ttk.Button(filter_controls, text="Clear Filters", command=self._clear_transaction_filters).grid(row=0, column=9, padx=(5, 0))
        
        # Initialize category filter
        categories = self.category_service.get_all_categories()
        category_names = ["All"] + [cat.name for cat in categories]
        category_filter['values'] = category_names
        
        # Transaction list
        list_frame = ttk.LabelFrame(transactions_frame, text="Transactions", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_transaction_list(list_frame)
    
    def _apply_transaction_filters(self) -> None:
        """Apply filters to the transaction list."""
        # This will refresh the transaction list with filters
        list_frame = None
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and "Transactions" in str(child.cget('text')):
                        list_frame = child
                        break
        
        if list_frame:
            # Clear existing list
            for widget in list_frame.winfo_children():
                widget.destroy()
            
            # Recreate with filters
            self._create_transaction_list(list_frame, apply_filters=True)
    
    def _clear_transaction_filters(self) -> None:
        """Clear all transaction filters."""
        self.filter_category_var.set("All")
        self.filter_type_var.set("All")
        self.filter_start_date_var.set("")
        self.filter_end_date_var.set("")
        self._apply_transaction_filters()
    
    def _create_transaction_list(self, parent_frame: ttk.Frame, limit: Optional[int] = None, apply_filters: bool = False) -> None:
        """Create a transaction list widget."""
        # Create treeview
        columns = ("Date", "Type", "Category", "Description", "Amount")
        tree = ttk.Treeview(parent_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        tree.heading("Date", text="Date")
        tree.heading("Type", text="Type")
        tree.heading("Category", text="Category")
        tree.heading("Description", text="Description")
        tree.heading("Amount", text="Amount")
        
        tree.column("Date", width=100)
        tree.column("Type", width=80)
        tree.column("Category", width=120)
        tree.column("Description", width=300)
        tree.column("Amount", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Get transactions
        try:
            if apply_filters:
                transactions = self._get_filtered_transactions()
            else:
                transactions = self.transaction_service.get_all_transactions()
            
            # Sort by date (newest first)
            transactions.sort(key=lambda x: x.date, reverse=True)
            
            # Apply limit if specified
            if limit:
                transactions = transactions[:limit]
            
            # Populate tree
            for transaction in transactions:
                values = (
                    transaction.date.strftime('%Y-%m-%d'),
                    transaction.transaction_type.value,
                    transaction.category,
                    transaction.description,
                    f"${transaction.amount:.2f}"
                )
                tree.insert("", tk.END, values=values)
        
        except Exception as e:
            tree.insert("", tk.END, values=("Error", "", "", f"Failed to load transactions: {e}", ""))
    
    def _get_filtered_transactions(self) -> List:
        """Get transactions with applied filters."""
        transactions = self.transaction_service.get_all_transactions()
        
        # Apply category filter
        category_filter = self.filter_category_var.get()
        if category_filter != "All":
            transactions = [t for t in transactions if t.category == category_filter]
        
        # Apply type filter
        type_filter = self.filter_type_var.get()
        if type_filter == "Income":
            transactions = [t for t in transactions if t.transaction_type == TransactionType.INCOME]
        elif type_filter == "Expense":
            transactions = [t for t in transactions if t.transaction_type == TransactionType.EXPENSE]
        
        # Apply date filters
        start_date_str = self.filter_start_date_var.get().strip()
        end_date_str = self.filter_end_date_var.get().strip()
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                transactions = [t for t in transactions if t.date.date() >= start_date]
            except ValueError:
                pass  # Ignore invalid date format
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                transactions = [t for t in transactions if t.date.date() <= end_date]
            except ValueError:
                pass  # Ignore invalid date format
        
        return transactions
    
    def _show_categories(self) -> None:
        """Show the categories management view."""
        self._clear_content()
        
        # Create categories view
        categories_frame = ttk.Frame(self.content_frame)
        categories_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add category form
        add_frame = ttk.LabelFrame(categories_frame, text="Add New Category", padding=10)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill=tk.X)
        
        # Category name
        ttk.Label(form_frame, text="Category Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.new_category_name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=self.new_category_name_var, width=30)
        name_entry.grid(row=0, column=1, padx=(0, 10))
        
        # Category type
        ttk.Label(form_frame, text="Type:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.new_category_type_var = tk.StringVar(value="EXPENSE")
        type_frame = ttk.Frame(form_frame)
        type_frame.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Radiobutton(type_frame, text="Income", variable=self.new_category_type_var, value="INCOME").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Expense", variable=self.new_category_type_var, value="EXPENSE").pack(side=tk.LEFT, padx=(10, 0))
        
        # Add button
        ttk.Button(form_frame, text="Add Category", command=self._add_category).grid(row=0, column=4, padx=(10, 0))
        
        # Categories list
        list_frame = ttk.LabelFrame(categories_frame, text="Categories", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_categories_list(list_frame)
    
    def _add_category(self) -> None:
        """Add a new category."""
        try:
            name = self.new_category_name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Category name is required.")
                return
            
            if self.category_service.category_exists(name):
                messagebox.showerror("Error", f"Category '{name}' already exists.")
                return
            
            category_type = CategoryType.INCOME if self.new_category_type_var.get() == "INCOME" else CategoryType.EXPENSE
            
            category = self.category_service.create_category(name, category_type)
            
            if category:
                messagebox.showinfo("Success", f"Category '{category.name}' added successfully!")
                self.new_category_name_var.set("")
                self._refresh_categories_list()
            else:
                messagebox.showerror("Error", "Failed to add category.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error adding category: {e}")
    
    def _create_categories_list(self, parent_frame: ttk.Frame) -> None:
        """Create a categories list widget."""
        # Create notebook for income/expense tabs
        notebook = ttk.Notebook(parent_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Income categories tab
        income_frame = ttk.Frame(notebook)
        notebook.add(income_frame, text="Income Categories")
        
        # Expense categories tab
        expense_frame = ttk.Frame(notebook)
        notebook.add(expense_frame, text="Expense Categories")
        
        try:
            # Get categories
            income_categories = self.category_service.get_income_categories()
            expense_categories = self.category_service.get_expense_categories()
            
            # Create income categories list
            self._create_category_tab_content(income_frame, income_categories)
            
            # Create expense categories list
            self._create_category_tab_content(expense_frame, expense_categories)
        
        except Exception as e:
            ttk.Label(income_frame, text=f"Error loading categories: {e}").pack()
    
    def _create_category_tab_content(self, parent_frame: ttk.Frame, categories: List) -> None:
        """Create content for a category tab."""
        # Create treeview
        columns = ("Name", "Type", "Status", "Usage")
        tree = ttk.Treeview(parent_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        tree.heading("Name", text="Name")
        tree.heading("Type", text="Type")
        tree.heading("Status", text="Status")
        tree.heading("Usage", text="Usage Count")
        
        tree.column("Name", width=200)
        tree.column("Type", width=100)
        tree.column("Status", width=100)
        tree.column("Usage", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Get usage stats
        usage_stats = self.category_service.get_category_usage_stats()
        
        # Populate tree
        for category in categories:
            status = "Default" if category.is_default else "Custom"
            usage_count = usage_stats.get(category.name, 0)
            
            values = (
                category.name,
                category.category_type.value,
                status,
                str(usage_count)
            )
            tree.insert("", tk.END, values=values)
    
    def _refresh_categories_list(self) -> None:
        """Refresh the categories list."""
        # Find and refresh the categories list
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and "Categories" in str(child.cget('text')):
                        # Clear and recreate
                        for subchild in child.winfo_children():
                            subchild.destroy()
                        self._create_categories_list(child)
                        break
    
    def _show_reports(self) -> None:
        """Show the reports view."""
        self._clear_content()
        
        # Create reports view
        reports_frame = ttk.Frame(self.content_frame)
        reports_frame.pack(fill=tk.BOTH, expand=True)
        
        # Report controls
        controls_frame = ttk.LabelFrame(reports_frame, text="Report Options", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Report type selection
        ttk.Label(controls_frame, text="Report Type:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.report_type_var = tk.StringVar(value="Summary")
        report_combo = ttk.Combobox(controls_frame, textvariable=self.report_type_var, 
                                   values=["Summary", "Category Breakdown", "Monthly Report"], 
                                   width=20, state="readonly")
        report_combo.grid(row=0, column=1, padx=(0, 10))
        
        # Date range
        ttk.Label(controls_frame, text="From:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.report_start_date_var = tk.StringVar()
        start_entry = ttk.Entry(controls_frame, textvariable=self.report_start_date_var, width=12)
        start_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(controls_frame, text="To:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.report_end_date_var = tk.StringVar()
        end_entry = ttk.Entry(controls_frame, textvariable=self.report_end_date_var, width=12)
        end_entry.grid(row=0, column=5, padx=(0, 10))
        
        # Generate button
        ttk.Button(controls_frame, text="Generate Report", command=self._generate_report).grid(row=0, column=6, padx=(10, 0))
        
        # Report display area
        self.report_display_frame = ttk.LabelFrame(reports_frame, text="Report Results", padding=10)
        self.report_display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Generate initial summary report
        self._generate_report()
    
    def _generate_report(self) -> None:
        """Generate and display the selected report."""
        # Clear previous report
        for widget in self.report_display_frame.winfo_children():
            widget.destroy()
        
        try:
            report_type = self.report_type_var.get()
            
            # Parse date range
            start_date = None
            end_date = None
            
            start_date_str = self.report_start_date_var.get().strip()
            end_date_str = self.report_end_date_var.get().strip()
            
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                except ValueError:
                    messagebox.showerror("Error", "Invalid start date format. Use YYYY-MM-DD.")
                    return
            
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    messagebox.showerror("Error", "Invalid end date format. Use YYYY-MM-DD.")
                    return
            
            if report_type == "Summary":
                self._display_summary_report(start_date, end_date)
            elif report_type == "Category Breakdown":
                self._display_category_breakdown_report()
            elif report_type == "Monthly Report":
                self._display_monthly_report()
        
        except Exception as e:
            ttk.Label(self.report_display_frame, text=f"Error generating report: {e}").pack()
    
    def _display_summary_report(self, start_date: Optional[date], end_date: Optional[date]) -> None:
        """Display summary report."""
        summary = self.report_service.generate_summary_report(start_date, end_date)
        
        # Create summary display
        summary_frame = ttk.Frame(self.report_display_frame)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Period info
        if start_date and end_date:
            period_label = ttk.Label(summary_frame, text=f"Period: {start_date} to {end_date}", 
                                   font=('Arial', 10, 'bold'))
            period_label.pack(anchor=tk.W)
        
        # Totals
        totals_frame = ttk.LabelFrame(summary_frame, text="Financial Summary", padding=10)
        totals_frame.pack(fill=tk.X, pady=(5, 0))
        
        totals_data = [
            ("Total Income", f"${summary['totals']['total_income']:,.2f}"),
            ("Total Expenses", f"${summary['totals']['total_expenses']:,.2f}"),
            ("Net Balance", f"${summary['totals']['net_balance']:,.2f}"),
            ("Total Transactions", str(summary['totals']['total_transactions']))
        ]
        
        for i, (label, value) in enumerate(totals_data):
            row = i // 2
            col = i % 2
            
            item_frame = ttk.Frame(totals_frame)
            item_frame.grid(row=row, column=col, padx=20, pady=5, sticky=tk.W)
            
            ttk.Label(item_frame, text=f"{label}:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            ttk.Label(item_frame, text=value, font=('Arial', 12)).pack(anchor=tk.W)
    
    def _display_category_breakdown_report(self) -> None:
        """Display category breakdown report."""
        report = self.report_service.generate_category_breakdown_report()
        
        if not report['categories']:
            ttk.Label(self.report_display_frame, text="No data available.").pack()
            return
        
        # Create treeview for category breakdown
        columns = ("Category", "Amount", "Count", "Percentage")
        tree = ttk.Treeview(self.report_display_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        tree.heading("Category", text="Category")
        tree.heading("Amount", text="Amount")
        tree.heading("Count", text="Transaction Count")
        tree.heading("Percentage", text="Percentage")
        
        tree.column("Category", width=200)
        tree.column("Amount", width=150)
        tree.column("Count", width=150)
        tree.column("Percentage", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.report_display_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate tree
        for category, data in report['categories'].items():
            values = (
                category,
                f"${data['total_amount']:,.2f}",
                str(data['transaction_count']),
                f"{data['percentage']:.1f}%"
            )
            tree.insert("", tk.END, values=values)
        
        # Add total row
        tree.insert("", tk.END, values=(
            "TOTAL",
            f"${report['summary']['total_amount']:,.2f}",
            str(report['summary']['total_transactions']),
            "100.0%"
        ))
    
    def _display_monthly_report(self) -> None:
        """Display monthly report."""
        # Get year input
        year_dialog = tk.Toplevel(self.root)
        year_dialog.title("Select Year")
        year_dialog.geometry("300x150")
        year_dialog.transient(self.root)
        year_dialog.grab_set()
        
        # Center the dialog
        year_dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        ttk.Label(year_dialog, text="Enter year for monthly report:").pack(pady=20)
        
        year_var = tk.StringVar(value=str(datetime.now().year))
        year_entry = ttk.Entry(year_dialog, textvariable=year_var, width=10)
        year_entry.pack(pady=10)
        
        def generate_monthly():
            try:
                year = int(year_var.get())
                year_dialog.destroy()
                
                report = self.report_service.generate_monthly_report(year)
                
                # Create treeview for monthly report
                columns = ("Month", "Income", "Expenses", "Net Balance")
                tree = ttk.Treeview(self.report_display_frame, columns=columns, show="headings", height=15)
                
                # Configure columns
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=150)
                
                # Add scrollbar
                scrollbar = ttk.Scrollbar(self.report_display_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                
                # Pack widgets
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                # Populate tree
                for month_name, data in report['monthly_data'].items():
                    values = (
                        month_name,
                        f"${data['income']:,.2f}",
                        f"${data['expenses']:,.2f}",
                        f"${data['net_balance']:,.2f}"
                    )
                    tree.insert("", tk.END, values=values)
                
                # Add total row
                tree.insert("", tk.END, values=(
                    "TOTAL",
                    f"${report['summary']['total_income']:,.2f}",
                    f"${report['summary']['total_expenses']:,.2f}",
                    f"${report['summary']['net_balance']:,.2f}"
                ))
                
            except ValueError:
                messagebox.showerror("Error", "Invalid year format.")
            except Exception as e:
                messagebox.showerror("Error", f"Error generating monthly report: {e}")
        
        button_frame = ttk.Frame(year_dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Generate", command=generate_monthly).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=year_dialog.destroy).pack(side=tk.LEFT)
    
    def _show_charts(self) -> None:
        """Show the charts view."""
        self._clear_content()
        
        # Create charts view
        charts_frame = ttk.Frame(self.content_frame)
        charts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chart controls
        controls_frame = ttk.LabelFrame(charts_frame, text="Chart Options", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Chart type selection
        ttk.Label(controls_frame, text="Chart Type:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.chart_type_var = tk.StringVar(value="Pie Chart")
        chart_combo = ttk.Combobox(controls_frame, textvariable=self.chart_type_var, 
                                  values=["Pie Chart", "Bar Chart", "Line Chart", "Trend Chart"], 
                                  width=20, state="readonly")
        chart_combo.grid(row=0, column=1, padx=(0, 10))
        
        # Generate and save buttons
        ttk.Button(controls_frame, text="Generate Chart", command=self._generate_chart).grid(row=0, column=2, padx=(10, 0))
        ttk.Button(controls_frame, text="Save Chart", command=self._save_chart).grid(row=0, column=3, padx=(5, 0))
        
        # Chart display area
        self.chart_display_frame = ttk.LabelFrame(charts_frame, text="Chart Display", padding=10)
        self.chart_display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Check matplotlib availability
        if not self.chart_service.is_matplotlib_available():
            ttk.Label(self.chart_display_frame, 
                     text="Matplotlib is not available. Please install it with: pip install matplotlib").pack()
        else:
            ttk.Label(self.chart_display_frame, 
                     text="Select a chart type and click 'Generate Chart' to create visualizations.").pack()
    
    def _generate_chart(self) -> None:
        """Generate and display the selected chart."""
        if not self.chart_service.is_matplotlib_available():
            messagebox.showerror("Error", "Matplotlib is not available. Please install it with: pip install matplotlib")
            return
        
        try:
            chart_type = self.chart_type_var.get()
            
            # Clear previous chart display
            for widget in self.chart_display_frame.winfo_children():
                widget.destroy()
            
            # Create temporary file for chart
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            success = False
            
            if chart_type == "Pie Chart":
                success = self.chart_service.create_pie_chart(save_path=temp_path)
            elif chart_type == "Bar Chart":
                success = self.chart_service.create_bar_chart(save_path=temp_path)
            elif chart_type == "Line Chart":
                success = self.chart_service.create_line_chart(save_path=temp_path)
            elif chart_type == "Trend Chart":
                # For trend chart, we need date range - use last 30 days as default
                from datetime import timedelta
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=30)
                success = self.chart_service.create_trend_chart(
                    start_date=start_date, 
                    end_date=end_date, 
                    save_path=temp_path
                )
            
            if success and os.path.exists(temp_path):
                # Display chart in GUI
                self._display_chart_image(temp_path)
                self.current_chart_path = temp_path
            else:
                ttk.Label(self.chart_display_frame, text="Failed to generate chart or no data available.").pack()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error generating chart: {e}")
    
    def _display_chart_image(self, image_path: str) -> None:
        """Display chart image in the GUI."""
        try:
            from PIL import Image, ImageTk
            
            # Load and resize image
            image = Image.open(image_path)
            # Resize to fit in the display area (max 600x400)
            image.thumbnail((600, 400), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Display in label
            image_label = ttk.Label(self.chart_display_frame, image=photo)
            image_label.image = photo  # Keep a reference
            image_label.pack()
            
        except ImportError:
            # PIL not available, show message
            ttk.Label(self.chart_display_frame, 
                     text="Chart generated successfully! Install Pillow (pip install Pillow) to display charts in GUI.").pack()
        except Exception as e:
            ttk.Label(self.chart_display_frame, text=f"Error displaying chart: {e}").pack()
    
    def _save_chart(self) -> None:
        """Save the current chart to a file."""
        if not hasattr(self, 'current_chart_path') or not os.path.exists(self.current_chart_path):
            messagebox.showerror("Error", "No chart to save. Please generate a chart first.")
            return
        
        # Open file dialog
        file_path = filedialog.asksaveasfilename(
            title="Save Chart",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                import shutil
                shutil.copy2(self.current_chart_path, file_path)
                messagebox.showinfo("Success", f"Chart saved to: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving chart: {e}")
    
    def _show_export(self) -> None:
        """Show the export view."""
        self._clear_content()
        
        # Create export view
        export_frame = ttk.Frame(self.content_frame)
        export_frame.pack(fill=tk.BOTH, expand=True)
        
        # Export options
        options_frame = ttk.LabelFrame(export_frame, text="Export Options", padding=20)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Export type
        ttk.Label(options_frame, text="Export Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.export_type_var = tk.StringVar(value="Transactions CSV")
        export_combo = ttk.Combobox(options_frame, textvariable=self.export_type_var, 
                                   values=["Transactions CSV", "Transactions Excel", "Category Summary CSV", "Monthly Report Excel"], 
                                   width=25, state="readonly")
        export_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Date range filters
        ttk.Label(options_frame, text="Date Range (optional):").grid(row=1, column=0, sticky=tk.W, pady=5)
        date_frame = ttk.Frame(options_frame)
        date_frame.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(date_frame, text="From:").pack(side=tk.LEFT)
        self.export_start_date_var = tk.StringVar()
        start_entry = ttk.Entry(date_frame, textvariable=self.export_start_date_var, width=12)
        start_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(date_frame, text="To:").pack(side=tk.LEFT)
        self.export_end_date_var = tk.StringVar()
        end_entry = ttk.Entry(date_frame, textvariable=self.export_end_date_var, width=12)
        end_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Export button
        ttk.Button(options_frame, text="Export Data", command=self._export_data).grid(row=2, column=0, columnspan=2, pady=20)
        
        # Export status
        self.export_status_frame = ttk.LabelFrame(export_frame, text="Export Status", padding=10)
        self.export_status_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.export_status_frame, text="Select export options and click 'Export Data' to begin.").pack()
    
    def _export_data(self) -> None:
        """Export data based on selected options."""
        export_type = self.export_type_var.get()
        
        # Get file path
        if "CSV" in export_type:
            file_path = filedialog.asksaveasfilename(
                title="Save CSV File",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
        else:
            file_path = filedialog.asksaveasfilename(
                title="Save Excel File",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
        
        if not file_path:
            return
        
        try:
            # Clear status
            for widget in self.export_status_frame.winfo_children():
                widget.destroy()
            
            status_label = ttk.Label(self.export_status_frame, text="Exporting...")
            status_label.pack()
            
            self.root.update()  # Update GUI
            
            success = False
            
            if export_type == "Transactions CSV":
                success = self.export_service.export_transactions_to_csv(file_path)
            elif export_type == "Transactions Excel":
                success = self.export_service.export_transactions_to_excel(file_path, include_summary=True)
            elif export_type == "Category Summary CSV":
                # Generate category report and export
                report = self.report_service.generate_category_breakdown_report()
                csv_data = [['Category', 'Total Amount', 'Transaction Count', 'Percentage']]
                
                for category, data in report['categories'].items():
                    csv_data.append([
                        category,
                        str(data['total_amount']),
                        str(data['transaction_count']),
                        f"{data['percentage']:.1f}%"
                    ])
                
                csv_data.append(['TOTAL', str(report['summary']['total_amount']), 
                               str(report['summary']['total_transactions']), '100.0%'])
                
                success = self.export_service.export_data_to_csv(file_path, csv_data)
            elif export_type == "Monthly Report Excel":
                # Get year for monthly report
                year = datetime.now().year
                report = self.report_service.generate_monthly_report(year)
                
                excel_data = [['Month', 'Income', 'Expenses', 'Net Balance']]
                
                for month_name, data in report['monthly_data'].items():
                    excel_data.append([
                        month_name,
                        float(data['income']),
                        float(data['expenses']),
                        float(data['net_balance'])
                    ])
                
                excel_data.append([
                    'TOTAL',
                    float(report['summary']['total_income']),
                    float(report['summary']['total_expenses']),
                    float(report['summary']['net_balance'])
                ])
                
                success = self.export_service.export_data_to_excel(file_path, excel_data, 'Monthly Report')
            
            # Update status
            status_label.destroy()
            
            if success:
                ttk.Label(self.export_status_frame, text=f"✓ Export completed successfully!\nFile saved to: {file_path}", 
                         foreground="green").pack()
            else:
                ttk.Label(self.export_status_frame, text="✗ Export failed.", foreground="red").pack()
        
        except Exception as e:
            # Update status
            for widget in self.export_status_frame.winfo_children():
                widget.destroy()
            ttk.Label(self.export_status_frame, text=f"✗ Export error: {e}", foreground="red").pack()