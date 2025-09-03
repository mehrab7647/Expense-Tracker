"""Application controller for coordinating between UI and services."""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from ..repositories.json_repository import JSONRepository
from ..services.transaction_service import TransactionService
from ..services.category_service import CategoryService
from ..services.report_service import ReportService
from ..services.export_service import ExportService
from ..services.chart_service import ChartService
from ..ui.console_interface import ConsoleInterface
from ..ui.gui_interface import GUIInterface


class ApplicationController:
    """
    Main application controller that coordinates between UI and services.
    
    This controller manages the application lifecycle, initializes services,
    and provides a unified interface for both console and GUI modes.
    """
    
    def __init__(self, data_file_path: Optional[str] = None, log_level: str = "INFO"):
        """
        Initialize the application controller.
        
        Args:
            data_file_path: Path to the data file (optional, defaults to data/expense_data.json)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.data_file_path = data_file_path or self._get_default_data_path()
        self.log_level = log_level
        
        # Initialize logging
        self._setup_logging()
        
        # Initialize services
        self._initialize_services()
        
        # Application state
        self.is_running = False
        self.current_interface = None
        
        self.logger.info("Application controller initialized")
    
    def _get_default_data_path(self) -> str:
        """Get the default data file path."""
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        return str(data_dir / "expense_data.json")
    
    def _setup_logging(self) -> None:
        """Set up application logging."""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Configure logging
        log_file = logs_dir / "expense_tracker.log"
        
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _initialize_services(self) -> None:
        """Initialize all application services."""
        try:
            # Initialize repository
            self.repository = JSONRepository(self.data_file_path)
            
            # Initialize services
            self.transaction_service = TransactionService(self.repository)
            self.category_service = CategoryService(self.repository)
            self.report_service = ReportService(self.transaction_service, self.category_service)
            self.export_service = ExportService(self.transaction_service, self.report_service)
            self.chart_service = ChartService(self.report_service)
            
            self.logger.info("All services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {e}")
            raise
    
    def start_console_interface(self) -> None:
        """Start the console interface."""
        try:
            self.logger.info("Starting console interface")
            
            self.current_interface = ConsoleInterface(
                self.transaction_service,
                self.category_service,
                self.report_service,
                self.export_service,
                self.chart_service
            )
            
            self.is_running = True
            self.current_interface.start()
            
        except KeyboardInterrupt:
            self.logger.info("Console interface interrupted by user")
        except Exception as e:
            self.logger.error(f"Error in console interface: {e}")
            raise
        finally:
            self._shutdown()
    
    def start_gui_interface(self) -> None:
        """Start the GUI interface."""
        try:
            self.logger.info("Starting GUI interface")
            
            self.current_interface = GUIInterface(
                self.transaction_service,
                self.category_service,
                self.report_service,
                self.export_service,
                self.chart_service
            )
            
            self.is_running = True
            self.current_interface.start()
            
        except Exception as e:
            self.logger.error(f"Error in GUI interface: {e}")
            raise
        finally:
            self._shutdown()
    
    def _shutdown(self) -> None:
        """Perform cleanup operations during shutdown."""
        try:
            self.logger.info("Shutting down application")
            
            # Ensure data is saved
            if hasattr(self.repository, 'save_data'):
                self.repository.save_data()
            
            self.is_running = False
            self.current_interface = None
            
            self.logger.info("Application shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def get_application_info(self) -> Dict[str, Any]:
        """Get application information and statistics."""
        try:
            # Get basic app info
            info = {
                'version': '1.0.0',
                'data_file': self.data_file_path,
                'data_file_exists': os.path.exists(self.data_file_path),
                'is_running': self.is_running,
                'current_interface': type(self.current_interface).__name__ if self.current_interface else None
            }
            
            # Get data statistics
            try:
                transactions = self.transaction_service.get_all_transactions()
                categories = self.category_service.get_all_categories()
                
                info.update({
                    'total_transactions': len(transactions),
                    'total_categories': len(categories),
                    'data_file_size': os.path.getsize(self.data_file_path) if os.path.exists(self.data_file_path) else 0
                })
                
                # Get financial summary
                summary = self.transaction_service.get_transaction_summary()
                info.update({
                    'total_income': float(summary['total_income']),
                    'total_expenses': float(summary['total_expenses']),
                    'net_balance': float(summary['net_balance'])
                })
                
            except Exception as e:
                self.logger.warning(f"Could not get data statistics: {e}")
                info.update({
                    'total_transactions': 0,
                    'total_categories': 0,
                    'data_file_size': 0,
                    'total_income': 0.0,
                    'total_expenses': 0.0,
                    'net_balance': 0.0
                })
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting application info: {e}")
            return {
                'version': '1.0.0',
                'error': str(e)
            }
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate the integrity of the application data."""
        try:
            self.logger.info("Validating data integrity")
            
            validation_results = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'statistics': {}
            }
            
            # Check if data file exists
            if not os.path.exists(self.data_file_path):
                validation_results['warnings'].append("Data file does not exist - will be created on first use")
                return validation_results
            
            # Validate transactions
            try:
                transactions = self.transaction_service.get_all_transactions()
                validation_results['statistics']['total_transactions'] = len(transactions)
                
                # Check for duplicate IDs
                transaction_ids = [t.id for t in transactions]
                if len(transaction_ids) != len(set(transaction_ids)):
                    validation_results['is_valid'] = False
                    validation_results['errors'].append("Duplicate transaction IDs found")
                
                # Check for invalid amounts
                invalid_amounts = [t for t in transactions if t.amount <= 0]
                if invalid_amounts:
                    validation_results['warnings'].append(f"Found {len(invalid_amounts)} transactions with invalid amounts")
                
            except Exception as e:
                validation_results['is_valid'] = False
                validation_results['errors'].append(f"Error validating transactions: {e}")
            
            # Validate categories
            try:
                categories = self.category_service.get_all_categories()
                validation_results['statistics']['total_categories'] = len(categories)
                
                # Check for duplicate category names
                category_names = [c.name for c in categories]
                if len(category_names) != len(set(category_names)):
                    validation_results['is_valid'] = False
                    validation_results['errors'].append("Duplicate category names found")
                
                # Check if default categories exist
                default_categories = [c for c in categories if c.is_default]
                if len(default_categories) == 0:
                    validation_results['warnings'].append("No default categories found")
                
            except Exception as e:
                validation_results['is_valid'] = False
                validation_results['errors'].append(f"Error validating categories: {e}")
            
            # Validate category references in transactions
            try:
                transactions = self.transaction_service.get_all_transactions()
                categories = self.category_service.get_all_categories()
                category_names = {c.name for c in categories}
                
                orphaned_transactions = [t for t in transactions if t.category not in category_names]
                if orphaned_transactions:
                    validation_results['warnings'].append(
                        f"Found {len(orphaned_transactions)} transactions with non-existent categories"
                    )
                
            except Exception as e:
                validation_results['warnings'].append(f"Could not validate category references: {e}")
            
            self.logger.info(f"Data validation complete. Valid: {validation_results['is_valid']}")
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error during data validation: {e}")
            return {
                'is_valid': False,
                'errors': [f"Validation failed: {e}"],
                'warnings': [],
                'statistics': {}
            }
    
    def backup_data(self, backup_path: Optional[str] = None) -> bool:
        """
        Create a backup of the current data.
        
        Args:
            backup_path: Path for the backup file (optional)
            
        Returns:
            bool: True if backup was successful, False otherwise
        """
        try:
            if not os.path.exists(self.data_file_path):
                self.logger.warning("No data file to backup")
                return False
            
            if backup_path is None:
                # Create backups directory
                backup_dir = Path("backups")
                backup_dir.mkdir(exist_ok=True)
                
                # Generate backup filename with timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"expense_data_backup_{timestamp}.json"
            
            # Copy the data file
            import shutil
            shutil.copy2(self.data_file_path, backup_path)
            
            self.logger.info(f"Data backed up to: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return False
    
    def restore_data(self, backup_path: str) -> bool:
        """
        Restore data from a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            bool: True if restore was successful, False otherwise
        """
        try:
            if not os.path.exists(backup_path):
                self.logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Create a backup of current data before restoring
            if os.path.exists(self.data_file_path):
                self.backup_data()
            
            # Copy backup to data file location
            import shutil
            shutil.copy2(backup_path, self.data_file_path)
            
            # Reinitialize services to load the restored data
            self._initialize_services()
            
            self.logger.info(f"Data restored from: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring data: {e}")
            return False
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get the status of all services."""
        status = {}
        
        services = [
            ('repository', self.repository),
            ('transaction_service', self.transaction_service),
            ('category_service', self.category_service),
            ('report_service', self.report_service),
            ('export_service', self.export_service),
            ('chart_service', self.chart_service)
        ]
        
        for service_name, service in services:
            try:
                # Try to call a basic method to check if service is working
                if hasattr(service, 'get_all_transactions'):
                    service.get_all_transactions()
                elif hasattr(service, 'get_all_categories'):
                    service.get_all_categories()
                elif hasattr(service, 'is_matplotlib_available'):
                    service.is_matplotlib_available()
                
                status[service_name] = True
                
            except Exception as e:
                self.logger.warning(f"Service {service_name} is not responding: {e}")
                status[service_name] = False
        
        return status