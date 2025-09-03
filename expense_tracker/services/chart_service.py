"""Chart service for data visualization using Matplotlib."""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import date
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Wedge
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from ..services.report_service import ReportService
from ..models.enums import TransactionType


class ChartService:
    """Service for creating data visualizations using Matplotlib."""
    
    def __init__(self, report_service: ReportService):
        """Initialize the chart service.
        
        Args:
            report_service: Report service instance for data generation
        """
        self.report_service = report_service
        
        # Set up matplotlib style
        if MATPLOTLIB_AVAILABLE:
            plt.style.use('default')
            # Set default figure size and DPI
            plt.rcParams['figure.figsize'] = (10, 6)
            plt.rcParams['figure.dpi'] = 100
            plt.rcParams['savefig.dpi'] = 300
            plt.rcParams['font.size'] = 10
    
    def create_pie_chart(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[TransactionType] = None,
        save_path: Optional[str] = None,
        show_chart: bool = False
    ) -> bool:
        """Create a pie chart for category breakdown.
        
        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            transaction_type: Filter by transaction type (optional)
            save_path: Path to save the chart image (optional)
            show_chart: Whether to display the chart
            
        Returns:
            True if chart creation successful, False otherwise
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Error: matplotlib not available. Install with: pip install matplotlib")
            return False
        
        try:
            # Get chart data
            chart_data = self.report_service.generate_chart_data(
                'pie', start_date, end_date, transaction_type
            )
            
            if not chart_data['values'] or all(v == 0 for v in chart_data['values']):
                print("No data available for pie chart")
                return False
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                chart_data['values'],
                labels=chart_data['labels'],
                colors=chart_data['colors'],
                autopct='%1.1f%%',
                startangle=90,
                explode=[0.05] * len(chart_data['values'])  # Slightly separate all slices
            )
            
            # Enhance text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            for text in texts:
                text.set_fontsize(10)
            
            # Set title
            ax.set_title(chart_data['title'], fontsize=14, fontweight='bold', pad=20)
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            
            # Add legend
            ax.legend(wedges, chart_data['labels'], title="Categories", 
                     loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            # Adjust layout to prevent legend cutoff
            plt.tight_layout()
            
            # Save chart if path provided
            if save_path:
                if self._save_chart(fig, save_path):
                    print(f"Pie chart saved to: {save_path}")
                else:
                    return False
            
            # Show chart if requested
            if show_chart:
                plt.show()
            else:
                plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            return False
    
    def create_bar_chart(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        save_path: Optional[str] = None,
        show_chart: bool = False
    ) -> bool:
        """Create a bar chart for monthly income vs expenses.
        
        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            save_path: Path to save the chart image (optional)
            show_chart: Whether to display the chart
            
        Returns:
            True if chart creation successful, False otherwise
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Error: matplotlib not available. Install with: pip install matplotlib")
            return False
        
        try:
            # Get chart data
            chart_data = self.report_service.generate_chart_data(
                'bar', start_date, end_date
            )
            
            if not chart_data['labels']:
                print("No data available for bar chart")
                return False
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Set up data
            x = np.arange(len(chart_data['labels']))
            width = 0.35
            
            # Create bars
            income_bars = ax.bar(
                x - width/2, 
                chart_data['datasets'][0]['data'],
                width, 
                label=chart_data['datasets'][0]['label'],
                color=chart_data['datasets'][0]['backgroundColor'],
                alpha=0.8
            )
            
            expense_bars = ax.bar(
                x + width/2, 
                chart_data['datasets'][1]['data'],
                width, 
                label=chart_data['datasets'][1]['label'],
                color=chart_data['datasets'][1]['backgroundColor'],
                alpha=0.8
            )
            
            # Customize chart
            ax.set_xlabel('Period', fontweight='bold')
            ax.set_ylabel('Amount', fontweight='bold')
            ax.set_title(chart_data['title'], fontsize=14, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(chart_data['labels'], rotation=45, ha='right')
            ax.legend()
            
            # Add value labels on bars
            self._add_bar_labels(ax, income_bars)
            self._add_bar_labels(ax, expense_bars)
            
            # Add grid for better readability
            ax.grid(True, alpha=0.3, axis='y')
            ax.set_axisbelow(True)
            
            # Format y-axis to show currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Adjust layout
            plt.tight_layout()
            
            # Save chart if path provided
            if save_path:
                if self._save_chart(fig, save_path):
                    print(f"Bar chart saved to: {save_path}")
                else:
                    return False
            
            # Show chart if requested
            if show_chart:
                plt.show()
            else:
                plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Error creating bar chart: {e}")
            return False
    
    def create_line_chart(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        save_path: Optional[str] = None,
        show_chart: bool = False
    ) -> bool:
        """Create a line chart for balance over time.
        
        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            save_path: Path to save the chart image (optional)
            show_chart: Whether to display the chart
            
        Returns:
            True if chart creation successful, False otherwise
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Error: matplotlib not available. Install with: pip install matplotlib")
            return False
        
        try:
            # Get chart data
            chart_data = self.report_service.generate_chart_data(
                'line', start_date, end_date
            )
            
            if not chart_data['labels']:
                print("No data available for line chart")
                return False
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Create line chart
            dataset = chart_data['datasets'][0]
            line = ax.plot(
                chart_data['labels'],
                dataset['data'],
                color=dataset['borderColor'],
                linewidth=2,
                marker='o',
                markersize=6,
                label=dataset['label']
            )
            
            # Fill area under the line
            ax.fill_between(
                chart_data['labels'],
                dataset['data'],
                alpha=0.3,
                color=dataset['borderColor']
            )
            
            # Customize chart
            ax.set_xlabel('Period', fontweight='bold')
            ax.set_ylabel('Balance', fontweight='bold')
            ax.set_title(chart_data['title'], fontsize=14, fontweight='bold', pad=20)
            ax.legend()
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45, ha='right')
            
            # Add grid
            ax.grid(True, alpha=0.3)
            ax.set_axisbelow(True)
            
            # Format y-axis to show currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Add horizontal line at zero
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.7, linewidth=1)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save chart if path provided
            if save_path:
                if self._save_chart(fig, save_path):
                    print(f"Line chart saved to: {save_path}")
                else:
                    return False
            
            # Show chart if requested
            if show_chart:
                plt.show()
            else:
                plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Error creating line chart: {e}")
            return False
    
    def create_trend_chart(
        self,
        start_date: date,
        end_date: date,
        period: str = 'monthly',
        save_path: Optional[str] = None,
        show_chart: bool = False
    ) -> bool:
        """Create a trend chart showing income and expenses over time.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            period: Period for grouping ('daily', 'weekly', 'monthly')
            save_path: Path to save the chart image (optional)
            show_chart: Whether to display the chart
            
        Returns:
            True if chart creation successful, False otherwise
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Error: matplotlib not available. Install with: pip install matplotlib")
            return False
        
        try:
            # Get trend data
            trend_data = self.report_service.generate_trend_analysis(
                start_date, end_date, period
            )
            
            if not trend_data['data']:
                print("No data available for trend chart")
                return False
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Extract data
            periods = [item['period'] for item in trend_data['data']]
            income_data = [float(item['income']) for item in trend_data['data']]
            expense_data = [float(item['expenses']) for item in trend_data['data']]
            net_data = [float(item['net_balance']) for item in trend_data['data']]
            
            # Create lines
            ax.plot(periods, income_data, color='#36A2EB', linewidth=2, 
                   marker='o', markersize=4, label='Income')
            ax.plot(periods, expense_data, color='#FF6384', linewidth=2, 
                   marker='s', markersize=4, label='Expenses')
            ax.plot(periods, net_data, color='#4BC0C0', linewidth=2, 
                   marker='^', markersize=4, label='Net Balance')
            
            # Customize chart
            ax.set_xlabel('Period', fontweight='bold')
            ax.set_ylabel('Amount', fontweight='bold')
            ax.set_title(f'{period.title()} Financial Trend', fontsize=14, fontweight='bold', pad=20)
            ax.legend()
            
            # Rotate x-axis labels
            plt.xticks(rotation=45, ha='right')
            
            # Add grid
            ax.grid(True, alpha=0.3)
            ax.set_axisbelow(True)
            
            # Format y-axis
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Add horizontal line at zero
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=0.8)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save chart if path provided
            if save_path:
                if self._save_chart(fig, save_path):
                    print(f"Trend chart saved to: {save_path}")
                else:
                    return False
            
            # Show chart if requested
            if show_chart:
                plt.show()
            else:
                plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Error creating trend chart: {e}")
            return False
    
    def create_category_comparison_chart(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[TransactionType] = None,
        save_path: Optional[str] = None,
        show_chart: bool = False
    ) -> bool:
        """Create a horizontal bar chart comparing categories.
        
        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            transaction_type: Filter by transaction type (optional)
            save_path: Path to save the chart image (optional)
            show_chart: Whether to display the chart
            
        Returns:
            True if chart creation successful, False otherwise
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Error: matplotlib not available. Install with: pip install matplotlib")
            return False
        
        try:
            # Get category breakdown report
            report = self.report_service.generate_category_breakdown_report(
                start_date, end_date, transaction_type
            )
            
            if not report['categories']:
                print("No data available for category comparison chart")
                return False
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Extract and sort data by amount (descending)
            categories = list(report['categories'].keys())
            amounts = [float(report['categories'][cat]['total_amount']) for cat in categories]
            
            # Sort by amount
            sorted_data = sorted(zip(categories, amounts), key=lambda x: x[1], reverse=True)
            categories, amounts = zip(*sorted_data)
            
            # Create color palette
            colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
            
            # Create horizontal bar chart
            bars = ax.barh(categories, amounts, color=colors, alpha=0.8)
            
            # Customize chart
            ax.set_xlabel('Amount', fontweight='bold')
            ax.set_ylabel('Categories', fontweight='bold')
            
            title = f"Category Comparison - {transaction_type.value if transaction_type else 'All Transactions'}"
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Add value labels on bars
            for bar, amount in zip(bars, amounts):
                width = bar.get_width()
                ax.text(width + max(amounts) * 0.01, bar.get_y() + bar.get_height()/2,
                       f'${amount:,.0f}', ha='left', va='center', fontweight='bold')
            
            # Format x-axis
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Add grid
            ax.grid(True, alpha=0.3, axis='x')
            ax.set_axisbelow(True)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save chart if path provided
            if save_path:
                if self._save_chart(fig, save_path):
                    print(f"Category comparison chart saved to: {save_path}")
                else:
                    return False
            
            # Show chart if requested
            if show_chart:
                plt.show()
            else:
                plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Error creating category comparison chart: {e}")
            return False
    
    def _save_chart(self, fig, save_path: str) -> bool:
        """Save chart to file with validation.
        
        Args:
            fig: Matplotlib figure object
            save_path: Path to save the chart
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Validate file path
            path = Path(save_path)
            
            # Create directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Validate file extension
            valid_extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.svg']
            if path.suffix.lower() not in valid_extensions:
                print(f"Error: File extension must be one of {valid_extensions}")
                return False
            
            # Save the figure
            fig.savefig(save_path, bbox_inches='tight', facecolor='white', 
                       edgecolor='none', dpi=300)
            
            return True
            
        except Exception as e:
            print(f"Error saving chart: {e}")
            return False
    
    def _add_bar_labels(self, ax, bars) -> None:
        """Add value labels on top of bars.
        
        Args:
            ax: Matplotlib axis object
            bars: Bar objects from bar chart
        """
        for bar in bars:
            height = bar.get_height()
            if height > 0:  # Only add labels for non-zero bars
                ax.text(bar.get_x() + bar.get_width()/2., height + height * 0.01,
                       f'${height:,.0f}', ha='center', va='bottom', fontsize=8)
    
    def get_available_formats(self) -> List[str]:
        """Get list of available image formats for saving charts.
        
        Returns:
            List of supported file extensions
        """
        return ['.png', '.jpg', '.jpeg', '.pdf', '.svg']
    
    def is_matplotlib_available(self) -> bool:
        """Check if matplotlib is available.
        
        Returns:
            True if matplotlib is available, False otherwise
        """
        return MATPLOTLIB_AVAILABLE