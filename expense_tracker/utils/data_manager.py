"""Data persistence and migration system for the expense tracker application."""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging

from .error_handling import DataError, FileOperationError, BackupManager, DataIntegrityChecker
from .validation import InputValidator
from ..models.category import Category, CategoryType


class DataMigration:
    """Handles data schema migrations."""
    
    CURRENT_VERSION = "1.0.0"
    
    def __init__(self):
        self.logger = logging.getLogger('expense_tracker.migration')
        self.migrations = {
            "0.9.0": self._migrate_from_0_9_0,
            "0.8.0": self._migrate_from_0_8_0,
        }
    
    def get_data_version(self, data: Dict[str, Any]) -> str:
        """Get the version of the data schema."""
        return data.get('schema_version', '0.8.0')  # Default to oldest version
    
    def needs_migration(self, data: Dict[str, Any]) -> bool:
        """Check if data needs migration."""
        current_version = self.get_data_version(data)
        return current_version != self.CURRENT_VERSION
    
    def migrate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate data to the current schema version.
        
        Args:
            data: The data to migrate
            
        Returns:
            Migrated data
        """
        current_version = self.get_data_version(data)
        
        if current_version == self.CURRENT_VERSION:
            return data
        
        self.logger.info(f"Migrating data from version {current_version} to {self.CURRENT_VERSION}")
        
        # Apply migrations in order
        migrated_data = data.copy()
        
        if current_version == "0.8.0":
            migrated_data = self._migrate_from_0_8_0(migrated_data)
            current_version = "0.9.0"
        
        if current_version == "0.9.0":
            migrated_data = self._migrate_from_0_9_0(migrated_data)
            current_version = "1.0.0"
        
        # Update schema version
        migrated_data['schema_version'] = self.CURRENT_VERSION
        migrated_data['migration_history'] = migrated_data.get('migration_history', [])
        migrated_data['migration_history'].append({
            'from_version': self.get_data_version(data),
            'to_version': self.CURRENT_VERSION,
            'migrated_at': datetime.now().isoformat()
        })
        
        self.logger.info(f"Data migration completed successfully")
        return migrated_data
    
    def _migrate_from_0_8_0(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 0.8.0 to 0.9.0."""
        self.logger.info("Applying migration from 0.8.0 to 0.9.0")
        
        migrated_data = data.copy()
        
        # Add missing fields to transactions
        for transaction in migrated_data.get('transactions', []):
            if 'created_at' not in transaction:
                transaction['created_at'] = transaction.get('date', datetime.now().isoformat())
            if 'updated_at' not in transaction:
                transaction['updated_at'] = transaction.get('date', datetime.now().isoformat())
        
        # Add missing fields to categories
        for category in migrated_data.get('categories', []):
            if 'created_at' not in category:
                category['created_at'] = datetime.now().isoformat()
            if 'is_default' not in category:
                category['is_default'] = False
        
        return migrated_data
    
    def _migrate_from_0_9_0(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 0.9.0 to 1.0.0."""
        self.logger.info("Applying migration from 0.9.0 to 1.0.0")
        
        migrated_data = data.copy()
        
        # Add application metadata
        if 'metadata' not in migrated_data:
            migrated_data['metadata'] = {
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'total_transactions': len(migrated_data.get('transactions', [])),
                'total_categories': len(migrated_data.get('categories', []))
            }
        
        # Ensure all transactions have proper IDs
        for i, transaction in enumerate(migrated_data.get('transactions', [])):
            if not transaction.get('id'):
                transaction['id'] = f"tx_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
        
        return migrated_data


class DataInitializer:
    """Handles initialization of new data files."""
    
    def __init__(self):
        self.logger = logging.getLogger('expense_tracker.initializer')
    
    def create_initial_data(self) -> Dict[str, Any]:
        """Create initial data structure for new users."""
        self.logger.info("Creating initial data structure")
        
        # Default categories
        default_categories = [
            # Expense categories
            {"name": "Food & Dining", "type": "EXPENSE", "is_default": True, "created_at": datetime.now().isoformat()},
            {"name": "Transportation", "type": "EXPENSE", "is_default": True, "created_at": datetime.now().isoformat()},
            {"name": "Shopping", "type": "EXPENSE", "is_default": True, "created_at": datetime.now().isoformat()},
            {"name": "Entertainment", "type": "EXPENSE", "is_default": True, "created_at": datetime.now().isoformat()},
            {"name": "Bills & Utilities", "type": "EXPENSE", "is_default": True, "created_at": datetime.now().isoformat()},
            {"name": "Healthcare", "type": "EXPENSE", "is_default": True, "created_at": datetime.now().isoformat()},
            {"name": "Education", "type": "EXPENSE", "is_default": True, "created_at": datetime.now().isoformat()},
            {"name": "Travel", "type": "EXPENSE", "is_default": True, "created_at": datetime.now().isoformat()},
            {"name": "Personal Care", "type": "EXPENSE", "is_default": True, "created_at": datetime.now().isoformat()},
            {"name": "Other Expenses", "type": "EXPENSE", "is_default": True, "created_at": datetime.now().isoformat()},
            
            # Income categories
            {"name": "Salary", "type": "INCOME", "is_default": True, "created_at": datetime.now().isoformat()},
            {"name": "Freelance", "type": "INCOME", "is_default": True, "created_at": datetime.now().isoformat()},
            {"name": "Investment", "type": "INCOME", "is_default": True, "created_at": datetime.now().isoformat()},
            {"name": "Gift", "type": "INCOME", "is_default": True, "created_at": datetime.now().isoformat()},
            {"name": "Other Income", "type": "INCOME", "is_default": True, "created_at": datetime.now().isoformat()},
        ]
        
        initial_data = {
            "schema_version": DataMigration.CURRENT_VERSION,
            "transactions": [],
            "categories": default_categories,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "total_transactions": 0,
                "total_categories": len(default_categories),
                "application_version": "1.0.0"
            },
            "settings": {
                "currency": "USD",
                "date_format": "YYYY-MM-DD",
                "decimal_places": 2,
                "auto_backup": True,
                "backup_frequency": "daily"
            },
            "migration_history": []
        }
        
        return initial_data
    
    def initialize_data_file(self, file_path: str) -> bool:
        """
        Initialize a new data file with default structure.
        
        Args:
            file_path: Path to the data file to create
            
        Returns:
            True if initialization was successful
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Create initial data
            initial_data = self.create_initial_data()
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Data file initialized: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize data file {file_path}: {e}")
            raise FileOperationError(f"Failed to initialize data file: {e}")


class DataPersistenceManager:
    """Manages data persistence, validation, and migration."""
    
    def __init__(self, data_file_path: str, backup_enabled: bool = True):
        self.data_file_path = data_file_path
        self.backup_enabled = backup_enabled
        self.logger = logging.getLogger('expense_tracker.persistence')
        
        # Initialize components
        self.migration = DataMigration()
        self.initializer = DataInitializer()
        self.integrity_checker = DataIntegrityChecker()
        
        if backup_enabled:
            backup_dir = os.path.join(os.path.dirname(data_file_path), 'backups')
            self.backup_manager = BackupManager(data_file_path, backup_dir)
        else:
            self.backup_manager = None
    
    def ensure_data_file_exists(self) -> bool:
        """
        Ensure the data file exists, creating it if necessary.
        
        Returns:
            True if file exists or was created successfully
        """
        if os.path.exists(self.data_file_path):
            return True
        
        self.logger.info(f"Data file not found, creating new file: {self.data_file_path}")
        return self.initializer.initialize_data_file(self.data_file_path)
    
    def load_data(self, validate: bool = True, migrate: bool = True) -> Dict[str, Any]:
        """
        Load data from the data file with optional validation and migration.
        
        Args:
            validate: Whether to validate data integrity
            migrate: Whether to apply migrations if needed
            
        Returns:
            Loaded and processed data
        """
        # Ensure file exists
        if not self.ensure_data_file_exists():
            raise FileOperationError("Failed to create data file")
        
        try:
            # Load raw data
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.debug(f"Loaded data from {self.data_file_path}")
            
            # Validate data integrity if requested
            if validate:
                validation_results = self.integrity_checker.validate_data_file(self.data_file_path)
                if not validation_results['is_valid']:
                    error_msg = f"Data integrity validation failed: {'; '.join(validation_results['errors'])}"
                    self.logger.error(error_msg)
                    raise DataError(error_msg, details=validation_results)
                
                if validation_results['warnings']:
                    for warning in validation_results['warnings']:
                        self.logger.warning(f"Data validation warning: {warning}")
            
            # Apply migrations if needed
            if migrate and self.migration.needs_migration(data):
                self.logger.info("Data migration required")
                
                # Create backup before migration
                if self.backup_manager:
                    backup_path = self.backup_manager.create_backup("pre_migration_backup")
                    self.logger.info(f"Pre-migration backup created: {backup_path}")
                
                # Migrate data
                data = self.migration.migrate_data(data)
                
                # Save migrated data
                self.save_data(data, validate=False)  # Skip validation since we just migrated
                self.logger.info("Data migration completed and saved")
            
            # Update last accessed timestamp
            if 'metadata' in data:
                data['metadata']['last_accessed'] = datetime.now().isoformat()
            
            return data
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in data file: {e}"
            self.logger.error(error_msg)
            raise DataError(error_msg)
        
        except Exception as e:
            error_msg = f"Failed to load data: {e}"
            self.logger.error(error_msg)
            raise FileOperationError(error_msg)
    
    def save_data(self, data: Dict[str, Any], validate: bool = True, backup: bool = None) -> bool:
        """
        Save data to the data file with optional validation and backup.
        
        Args:
            data: Data to save
            validate: Whether to validate data before saving
            backup: Whether to create backup before saving (None = use default setting)
            
        Returns:
            True if save was successful
        """
        if backup is None:
            backup = self.backup_enabled
        
        try:
            # Validate data if requested
            if validate:
                # Create temporary file for validation
                temp_file = self.data_file_path + '.tmp'
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                validation_results = self.integrity_checker.validate_data_file(temp_file)
                os.remove(temp_file)
                
                if not validation_results['is_valid']:
                    error_msg = f"Data validation failed before save: {'; '.join(validation_results['errors'])}"
                    self.logger.error(error_msg)
                    raise DataError(error_msg, details=validation_results)
            
            # Create backup if requested and file exists
            if backup and self.backup_manager and os.path.exists(self.data_file_path):
                backup_path = self.backup_manager.create_backup()
                self.logger.debug(f"Backup created before save: {backup_path}")
            
            # Update metadata
            if 'metadata' in data:
                data['metadata']['last_modified'] = datetime.now().isoformat()
                data['metadata']['total_transactions'] = len(data.get('transactions', []))
                data['metadata']['total_categories'] = len(data.get('categories', []))
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_file_path), exist_ok=True)
            
            # Write to temporary file first
            temp_file = self.data_file_path + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic move to final location
            shutil.move(temp_file, self.data_file_path)
            
            self.logger.debug(f"Data saved to {self.data_file_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to save data: {e}"
            self.logger.error(error_msg)
            raise FileOperationError(error_msg)
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """
        Validate the integrity of the current data file.
        
        Returns:
            Validation results
        """
        if not os.path.exists(self.data_file_path):
            return {
                'is_valid': False,
                'errors': ['Data file does not exist'],
                'warnings': [],
                'statistics': {}
            }
        
        return self.integrity_checker.validate_data_file(self.data_file_path)
    
    def create_backup(self, backup_name: str = None) -> str:
        """
        Create a backup of the current data file.
        
        Args:
            backup_name: Custom backup name (optional)
            
        Returns:
            Path to the created backup file
        """
        if not self.backup_manager:
            raise FileOperationError("Backup manager not initialized")
        
        return self.backup_manager.create_backup(backup_name)
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restore data from a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            True if restoration was successful
        """
        if not self.backup_manager:
            raise FileOperationError("Backup manager not initialized")
        
        return self.backup_manager.restore_backup(backup_path)
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List available backup files.
        
        Returns:
            List of backup file information
        """
        if not self.backup_manager:
            return []
        
        return self.backup_manager.list_backups()
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Clean up old backup files.
        
        Args:
            keep_count: Number of backups to keep
            
        Returns:
            Number of backups deleted
        """
        if not self.backup_manager:
            return 0
        
        return self.backup_manager.cleanup_old_backups(keep_count)
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the data file.
        
        Returns:
            Dictionary with data statistics
        """
        if not os.path.exists(self.data_file_path):
            return {
                'file_exists': False,
                'file_size': 0,
                'last_modified': None,
                'schema_version': None,
                'total_transactions': 0,
                'total_categories': 0
            }
        
        try:
            # File statistics
            stat = os.stat(self.data_file_path)
            
            # Load data for content statistics
            data = self.load_data(validate=False, migrate=False)
            
            return {
                'file_exists': True,
                'file_size': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'schema_version': data.get('schema_version', 'unknown'),
                'total_transactions': len(data.get('transactions', [])),
                'total_categories': len(data.get('categories', [])),
                'metadata': data.get('metadata', {}),
                'needs_migration': self.migration.needs_migration(data)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get data statistics: {e}")
            return {
                'file_exists': True,
                'error': str(e)
            }