"""Report service for generating financial reports and analytics."""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
from collections import defaultdict
import calendar

from ..models.transaction import Transaction
from ..models.enums import TransactionType, CategoryType
from ..services.transaction_service import TransactionService
from ..services.category_service import CategoryService


class ReportService:
    """Service for generating financial reports and analytics."""
    
    def __init__(self, transaction_service: TransactionService, category_service: CategoryService):
        """Initialize the report service.
        
        Args:
            transaction_service: Transaction service instance
            category_service: Category service instance
        """
        self.transaction_service = transaction_service
        self.category_service = category_service
    
    def generate_summary_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive financial summary report.
        
        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            
        Returns:
            Dictionary containing summary report data
        """
        # Get filtered transactions
        transactions = self._get_filtered_transactions(start_date, end_date)
        
        # Calculate basic totals
        total_income = Decimal('0')
        total_expenses = Decimal('0')
        income_count = 0
        expense_count = 0
        
        for transaction in transactions:
            if transaction.transaction_type == TransactionType.INCOME:
                total_income += transaction.amount
                income_count += 1
            else:
                total_expenses += transaction.amount
                expense_count += 1
        
        net_balance = total_income - total_expenses
        
        # Calculate averages
        avg_income = total_income / income_count if income_count > 0 else Decimal('0')
        avg_expense = total_expenses / expense_count if expense_count > 0 else Decimal('0')
        
        return {
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'total_days': (end_date - start_date).days + 1 if start_date and end_date else None
            },
            'totals': {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_balance': net_balance,
                'total_transactions': len(transactions)
            },
            'counts': {
                'income_transactions': income_count,
                'expense_transactions': expense_count
            },
            'averages': {
                'average_income': avg_income,
                'average_expense': avg_expense,
                'average_transaction': (total_income + total_expenses) / len(transactions) if transactions else Decimal('0')
            },
            'percentages': {
                'income_percentage': (total_income / (total_income + total_expenses) * 100) if (total_income + total_expenses) > 0 else Decimal('0'),
                'expense_percentage': (total_expenses / (total_income + total_expenses) * 100) if (total_income + total_expenses) > 0 else Decimal('0')
            }
        }
    
    def generate_category_breakdown_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[TransactionType] = None
    ) -> Dict[str, Any]:
        """Generate a category breakdown report.
        
        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            transaction_type: Filter by transaction type (optional)
            
        Returns:
            Dictionary containing category breakdown data
        """
        # Get filtered transactions
        transactions = self._get_filtered_transactions(start_date, end_date, transaction_type)
        
        # Group by category
        category_data = defaultdict(lambda: {
            'total_amount': Decimal('0'),
            'transaction_count': 0,
            'transactions': []
        })
        
        total_amount = Decimal('0')
        
        for transaction in transactions:
            category_data[transaction.category]['total_amount'] += transaction.amount
            category_data[transaction.category]['transaction_count'] += 1
            category_data[transaction.category]['transactions'].append({
                'id': transaction.id,
                'amount': transaction.amount,
                'description': transaction.description,
                'date': transaction.date.isoformat() if transaction.date else None
            })
            total_amount += transaction.amount
        
        # Calculate percentages and averages
        categories = {}
        for category_name, data in category_data.items():
            percentage = (data['total_amount'] / total_amount * 100) if total_amount > 0 else Decimal('0')
            average = data['total_amount'] / data['transaction_count'] if data['transaction_count'] > 0 else Decimal('0')
            
            categories[category_name] = {
                'total_amount': data['total_amount'],
                'transaction_count': data['transaction_count'],
                'percentage': percentage,
                'average_amount': average,
                'transactions': data['transactions']
            }
        
        # Sort categories by total amount (descending)
        sorted_categories = dict(sorted(categories.items(), key=lambda x: x[1]['total_amount'], reverse=True))
        
        return {
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            },
            'filter': {
                'transaction_type': transaction_type.value if transaction_type else None
            },
            'summary': {
                'total_amount': total_amount,
                'total_transactions': len(transactions),
                'categories_count': len(categories)
            },
            'categories': sorted_categories
        }
    
    def generate_monthly_report(self, year: int) -> Dict[str, Any]:
        """Generate a monthly breakdown report for a specific year.
        
        Args:
            year: Year for the report
            
        Returns:
            Dictionary containing monthly breakdown data
        """
        monthly_data = {}
        year_total_income = Decimal('0')
        year_total_expenses = Decimal('0')
        
        for month in range(1, 13):
            # Get transactions for this month
            start_date = date(year, month, 1)
            end_date = date(year, month, calendar.monthrange(year, month)[1])
            
            transactions = self._get_filtered_transactions(start_date, end_date)
            
            # Calculate monthly totals
            monthly_income = Decimal('0')
            monthly_expenses = Decimal('0')
            
            for transaction in transactions:
                if transaction.transaction_type == TransactionType.INCOME:
                    monthly_income += transaction.amount
                else:
                    monthly_expenses += transaction.amount
            
            monthly_net = monthly_income - monthly_expenses
            
            month_name = calendar.month_name[month]
            monthly_data[month_name] = {
                'month': month,
                'year': year,
                'income': monthly_income,
                'expenses': monthly_expenses,
                'net_balance': monthly_net,
                'transaction_count': len(transactions)
            }
            
            year_total_income += monthly_income
            year_total_expenses += monthly_expenses
        
        return {
            'year': year,
            'summary': {
                'total_income': year_total_income,
                'total_expenses': year_total_expenses,
                'net_balance': year_total_income - year_total_expenses
            },
            'monthly_data': monthly_data
        }
    
    def generate_trend_analysis(
        self,
        start_date: date,
        end_date: date,
        period: str = 'monthly'
    ) -> Dict[str, Any]:
        """Generate trend analysis over a period.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            period: Period for grouping ('daily', 'weekly', 'monthly')
            
        Returns:
            Dictionary containing trend analysis data
        """
        transactions = self._get_filtered_transactions(start_date, end_date)
        
        if period == 'monthly':
            return self._generate_monthly_trends(transactions, start_date, end_date)
        elif period == 'weekly':
            return self._generate_weekly_trends(transactions, start_date, end_date)
        elif period == 'daily':
            return self._generate_daily_trends(transactions, start_date, end_date)
        else:
            raise ValueError("Period must be 'daily', 'weekly', or 'monthly'")
    
    def generate_chart_data(
        self,
        chart_type: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[TransactionType] = None
    ) -> Dict[str, Any]:
        """Generate data formatted for chart visualization.
        
        Args:
            chart_type: Type of chart ('pie', 'bar', 'line')
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            transaction_type: Filter by transaction type (optional)
            
        Returns:
            Dictionary containing chart data
        """
        if chart_type == 'pie':
            return self._generate_pie_chart_data(start_date, end_date, transaction_type)
        elif chart_type == 'bar':
            return self._generate_bar_chart_data(start_date, end_date)
        elif chart_type == 'line':
            return self._generate_line_chart_data(start_date, end_date)
        else:
            raise ValueError("Chart type must be 'pie', 'bar', or 'line'")
    
    def _get_filtered_transactions(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[TransactionType] = None
    ) -> List[Transaction]:
        """Get filtered transactions based on criteria."""
        return self.transaction_service.filter_transactions(
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type
        )
    
    def _generate_monthly_trends(
        self,
        transactions: List[Transaction],
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Generate monthly trend data."""
        monthly_data = defaultdict(lambda: {'income': Decimal('0'), 'expenses': Decimal('0')})
        
        for transaction in transactions:
            if transaction.date:
                month_key = transaction.date.strftime('%Y-%m')
                if transaction.transaction_type == TransactionType.INCOME:
                    monthly_data[month_key]['income'] += transaction.amount
                else:
                    monthly_data[month_key]['expenses'] += transaction.amount
        
        # Convert to sorted list
        trend_data = []
        for month_key in sorted(monthly_data.keys()):
            data = monthly_data[month_key]
            trend_data.append({
                'period': month_key,
                'income': data['income'],
                'expenses': data['expenses'],
                'net_balance': data['income'] - data['expenses']
            })
        
        return {
            'period_type': 'monthly',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'data': trend_data
        }
    
    def _generate_weekly_trends(
        self,
        transactions: List[Transaction],
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Generate weekly trend data."""
        weekly_data = defaultdict(lambda: {'income': Decimal('0'), 'expenses': Decimal('0')})
        
        for transaction in transactions:
            if transaction.date:
                # Get the start of the week (Monday)
                week_start = transaction.date.date() - datetime.timedelta(days=transaction.date.weekday())
                week_key = week_start.strftime('%Y-W%U')
                
                if transaction.transaction_type == TransactionType.INCOME:
                    weekly_data[week_key]['income'] += transaction.amount
                else:
                    weekly_data[week_key]['expenses'] += transaction.amount
        
        # Convert to sorted list
        trend_data = []
        for week_key in sorted(weekly_data.keys()):
            data = weekly_data[week_key]
            trend_data.append({
                'period': week_key,
                'income': data['income'],
                'expenses': data['expenses'],
                'net_balance': data['income'] - data['expenses']
            })
        
        return {
            'period_type': 'weekly',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'data': trend_data
        }
    
    def _generate_daily_trends(
        self,
        transactions: List[Transaction],
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Generate daily trend data."""
        daily_data = defaultdict(lambda: {'income': Decimal('0'), 'expenses': Decimal('0')})
        
        for transaction in transactions:
            if transaction.date:
                day_key = transaction.date.strftime('%Y-%m-%d')
                if transaction.transaction_type == TransactionType.INCOME:
                    daily_data[day_key]['income'] += transaction.amount
                else:
                    daily_data[day_key]['expenses'] += transaction.amount
        
        # Convert to sorted list
        trend_data = []
        for day_key in sorted(daily_data.keys()):
            data = daily_data[day_key]
            trend_data.append({
                'period': day_key,
                'income': data['income'],
                'expenses': data['expenses'],
                'net_balance': data['income'] - data['expenses']
            })
        
        return {
            'period_type': 'daily',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'data': trend_data
        }
    
    def _generate_pie_chart_data(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        transaction_type: Optional[TransactionType]
    ) -> Dict[str, Any]:
        """Generate data for pie chart (category breakdown)."""
        category_report = self.generate_category_breakdown_report(
            start_date, end_date, transaction_type
        )
        
        labels = []
        values = []
        colors = []
        
        # Generate colors for categories
        color_palette = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
        ]
        
        for i, (category, data) in enumerate(category_report['categories'].items()):
            labels.append(category)
            values.append(float(data['total_amount']))
            colors.append(color_palette[i % len(color_palette)])
        
        return {
            'chart_type': 'pie',
            'title': f"Category Breakdown - {transaction_type.value if transaction_type else 'All Transactions'}",
            'labels': labels,
            'values': values,
            'colors': colors
        }
    
    def _generate_bar_chart_data(
        self,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> Dict[str, Any]:
        """Generate data for bar chart (monthly comparison)."""
        if not start_date or not end_date:
            # Default to current year if no dates provided
            current_year = datetime.now().year
            monthly_report = self.generate_monthly_report(current_year)
        else:
            # Generate monthly data for the date range
            start_year = start_date.year
            end_year = end_date.year
            
            if start_year == end_year:
                monthly_report = self.generate_monthly_report(start_year)
            else:
                # For multi-year ranges, use trend analysis
                trend_data = self.generate_trend_analysis(start_date, end_date, 'monthly')
                return {
                    'chart_type': 'bar',
                    'title': 'Monthly Income vs Expenses',
                    'labels': [item['period'] for item in trend_data['data']],
                    'datasets': [
                        {
                            'label': 'Income',
                            'data': [float(item['income']) for item in trend_data['data']],
                            'backgroundColor': '#36A2EB'
                        },
                        {
                            'label': 'Expenses',
                            'data': [float(item['expenses']) for item in trend_data['data']],
                            'backgroundColor': '#FF6384'
                        }
                    ]
                }
        
        labels = []
        income_data = []
        expense_data = []
        
        for month_name, data in monthly_report['monthly_data'].items():
            labels.append(month_name)
            income_data.append(float(data['income']))
            expense_data.append(float(data['expenses']))
        
        return {
            'chart_type': 'bar',
            'title': f'Monthly Income vs Expenses - {monthly_report["year"]}',
            'labels': labels,
            'datasets': [
                {
                    'label': 'Income',
                    'data': income_data,
                    'backgroundColor': '#36A2EB'
                },
                {
                    'label': 'Expenses',
                    'data': expense_data,
                    'backgroundColor': '#FF6384'
                }
            ]
        }
    
    def _generate_line_chart_data(
        self,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> Dict[str, Any]:
        """Generate data for line chart (balance over time)."""
        if not start_date or not end_date:
            # Default to last 12 months
            end_date = date.today()
            start_date = date(end_date.year - 1, end_date.month, 1)
        
        trend_data = self.generate_trend_analysis(start_date, end_date, 'monthly')
        
        labels = []
        balance_data = []
        running_balance = Decimal('0')
        
        for item in trend_data['data']:
            labels.append(item['period'])
            running_balance += item['net_balance']
            balance_data.append(float(running_balance))
        
        return {
            'chart_type': 'line',
            'title': 'Balance Over Time',
            'labels': labels,
            'datasets': [
                {
                    'label': 'Running Balance',
                    'data': balance_data,
                    'borderColor': '#36A2EB',
                    'backgroundColor': 'rgba(54, 162, 235, 0.1)',
                    'fill': True
                }
            ]
        }