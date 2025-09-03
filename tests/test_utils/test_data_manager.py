"""Unit tests for data persistence and migration system."""

import unittest
from unittest.mock import Mock, patch, mock_open
import tempfile
import os
import json
import shutil
from datetime import datetime

from expense_tracker.utils.data_manager import (
    DataMigration, DataInitializer, DataPersistenceManager
)
from expense_tracker.utils.error_handling import DataError, FileOperationError


class TestDataMigration(unittest.TestCase):
    """Test cases for DataMigration class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.migration = DataMigration()
    
    def test_get_data_version_with_version(self):
        """Test getting data version when version is present."""
        data = {"schema_version": "1.0.0"}
        version = self.migration.get_data_version(data)
        self.assertEqual(version, "1.0.0")
    
    def test_get_data_version_without_version(self):
        """Test getting data version when version is missing."""
        data = {}
        version = self.migration.get_data_version(data)
        self.assertEqual(version, "0.8.0")  # Default version
    
    def test_needs_migration_current_version(self):
        """Test migration check for current version."""
        data = {"schema_version": DataMigration.CURRENT_VERSION}
        self.assertFalse(self.migration.needs_migration(data))
    
    def test_needs_migration_old_version(self):
        """Test migration check for old version."""
        data = {"schema_version": "0.8.0"}
        self.assertTrue(self.migration.needs_migration(data))
    
    def test_migrate_data_current_version(self):
        """Test migration of current version data (no changes)."""
        data = {"schema_version": DataMigration.CURRENT_VERSION}
        migrated = self.migration.migrate_data(data)
        self.assertEqual(migrated, data)
    
    def test_migrate_data_from_0_8_0(self):
        """Test migration from version 0.8.0."""
        old_data = {
            "schema_version": "0.8.0",
            "transactions": [
                {
                    "id": "1",
                    "amount": 100.0,
                    "description": "Test",
                    "type": "EXPENSE",
                    "category": "Food",
                    "date": "2024-01-01T00:00:00"
                }
            ],
            "categories": [
                {
                    "name": "Food",
                    "type": "EXPENSE"
                }
            ]
        }
        
        migrated = self.migration.migrate_data(old_data)
        
        # Check version updated
        self.assertEqual(migrated['schema_version'], DataMigration.CURRENT_VERSION)
        
        # Check migration history added
        self.assertIn('migration_history', migrated)
        self.assertTrue(len(migrated['migration_history']) > 0)
        
        # Check transaction fields added
        transaction = migrated['transactions'][0]
        self.assertIn('created_at', transaction)
        self.assertIn('updated_at', transaction)
        
        # Check category fields added
        category = migrated['categories'][0]
        self.assertIn('created_at', category)
        self.assertIn('is_default', category)
        
        # Check metadata added
        self.assertIn('metadata', migrated)
    
    def test_migrate_from_0_8_0_specific(self):
        """Test specific migration logic from 0.8.0 to 0.9.0."""
        data = {
            "transactions": [{"id": "1", "date": "2024-01-01T00:00:00"}],
            "categories": [{"name": "Food", "type": "EXPENSE"}]
        }
        
        migrated = self.migration._migrate_from_0_8_0(data)
        
        # Check transaction fields
        transaction = migrated['transactions'][0]
        self.assertEqual(transaction['created_at'], "2024-01-01T00:00:00")
        self.assertEqual(transaction['updated_at'], "2024-01-01T00:00:00")
        
        # Check category fields
        category = migrated['categories'][0]
        self.assertIn('created_at', category)
        self.assertFalse(category['is_default'])
    
    def test_migrate_from_0_9_0_specific(self):
        """Test specific migration logic from 0.9.0 to 1.0.0."""
        data = {
            "transactions": [
                {"amount": 100.0, "description": "Test"},  # No ID
                {"id": "existing", "amount": 200.0, "description": "Test 2"}  # Has ID
            ],
            "categories": []
        }
        
        migrated = self.migration._migrate_from_0_9_0(data)
        
        # Check metadata added
        self.assertIn('metadata', migrated)
        metadata = migrated['metadata']
        self.assertIn('created_at', metadata)
        self.assertIn('last_accessed', metadata)
        
        # Check transaction IDs
        self.assertIn('id', migrated['transactions'][0])  # ID should be generated
        self.assertEqual(migrated['transactions'][1]['id'], 'existing')  # ID should be preserved


class TestDataInitializer(unittest.TestCase):
    """Test cases for DataInitializer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.initializer = DataInitializer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_initial_data(self):
        """Test creation of initial data structure."""
        data = self.initializer.create_initial_data()
        
        # Check required keys
        required_keys = ['schema_version', 'transactions', 'categories', 'metadata', 'settings']
        for key in required_keys:
            self.assertIn(key, data)
        
        # Check schema version
        self.assertEqual(data['schema_version'], DataMigration.CURRENT_VERSION)
        
        # Check initial state
        self.assertEqual(data['transactions'], [])
        self.assertTrue(len(data['categories']) > 0)
        
        # Check default categories
        categories = data['categories']
        expense_categories = [cat for cat in categories if cat['type'] == 'EXPENSE']
        income_categories = [cat for cat in categories if cat['type'] == 'INCOME']
        
        self.assertTrue(len(expense_categories) > 0)
        self.assertTrue(len(income_categories) > 0)
        
        # Check all categories are marked as default
        for category in categories:
            self.assertTrue(category['is_default'])
            self.assertIn('created_at', category)
        
        # Check metadata
        metadata = data['metadata']
        self.assertIn('created_at', metadata)
        self.assertIn('total_transactions', metadata)
        self.assertIn('total_categories', metadata)
        self.assertEqual(metadata['total_transactions'], 0)
        self.assertEqual(metadata['total_categories'], len(categories))
        
        # Check settings
        settings = data['settings']
        self.assertIn('currency', settings)
        self.assertIn('auto_backup', settings)
    
    def test_initialize_data_file(self):
        """Test initialization of data file."""
        file_path = os.path.join(self.temp_dir, 'test_data.json')
        
        success = self.initializer.initialize_data_file(file_path)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(file_path))
        
        # Verify file content
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['schema_version'], DataMigration.CURRENT_VERSION)
        self.assertIn('transactions', data)
        self.assertIn('categories', data)
    
    def test_initialize_data_file_with_subdirectory(self):
        """Test initialization of data file in subdirectory."""
        subdir = os.path.join(self.temp_dir, 'data', 'subdir')
        file_path = os.path.join(subdir, 'test_data.json')
        
        success = self.initializer.initialize_data_file(file_path)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(os.path.exists(subdir))
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_initialize_data_file_permission_error(self, mock_open):
        """Test initialization failure due to permission error."""
        file_path = os.path.join(self.temp_dir, 'test_data.json')
        
        with self.assertRaises(FileOperationError):
            self.initializer.initialize_data_file(file_path)


class TestDataPersistenceManager(unittest.TestCase):
    """Test cases for DataPersistenceManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_data.json')
        self.manager = DataPersistenceManager(self.data_file, backup_enabled=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_ensure_data_file_exists_new_file(self):
        """Test ensuring data file exists when file doesn't exist."""
        self.assertFalse(os.path.exists(self.data_file))
        
        success = self.manager.ensure_data_file_exists()
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.data_file))
    
    def test_ensure_data_file_exists_existing_file(self):
        """Test ensuring data file exists when file already exists."""
        # Create file first
        with open(self.data_file, 'w') as f:
            json.dump({}, f)
        
        success = self.manager.ensure_data_file_exists()
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.data_file))
    
    def test_load_data_new_file(self):
        """Test loading data from new file."""
        data = self.manager.load_data()
        
        # Should have created file and loaded initial data
        self.assertTrue(os.path.exists(self.data_file))
        self.assertIn('schema_version', data)
        self.assertIn('transactions', data)
        self.assertIn('categories', data)
    
    def test_load_data_existing_file(self):
        """Test loading data from existing file."""
        # Create test data
        test_data = {
            "schema_version": DataMigration.CURRENT_VERSION,
            "transactions": [{"id": "1", "amount": 100.0}],
            "categories": [{"name": "Food", "type": "EXPENSE"}],
            "metadata": {"created_at": "2024-01-01T00:00:00"}
        }
        
        with open(self.data_file, 'w') as f:
            json.dump(test_data, f)
        
        data = self.manager.load_data()
        
        self.assertEqual(len(data['transactions']), 1)
        self.assertEqual(len(data['categories']), 1)
        self.assertIn('last_accessed', data['metadata'])
    
    def test_load_data_with_migration(self):
        """Test loading data that requires migration."""
        # Create old version data
        old_data = {
            "schema_version": "0.8.0",
            "transactions": [{"id": "1", "amount": 100.0, "date": "2024-01-01T00:00:00"}],
            "categories": [{"name": "Food", "type": "EXPENSE"}]
        }
        
        with open(self.data_file, 'w') as f:
            json.dump(old_data, f)
        
        data = self.manager.load_data(migrate=True)
        
        # Should be migrated to current version
        self.assertEqual(data['schema_version'], DataMigration.CURRENT_VERSION)
        self.assertIn('migration_history', data)
        self.assertIn('metadata', data)
    
    def test_load_data_invalid_json(self):
        """Test loading data from invalid JSON file."""
        with open(self.data_file, 'w') as f:
            f.write("{ invalid json }")
        
        with self.assertRaises(DataError):
            self.manager.load_data()
    
    def test_save_data(self):
        """Test saving data to file."""
        test_data = {
            "schema_version": DataMigration.CURRENT_VERSION,
            "transactions": [{"id": "1", "amount": 100.0}],
            "categories": [{"name": "Food", "type": "EXPENSE"}],
            "metadata": {"created_at": "2024-01-01T00:00:00"}
        }
        
        success = self.manager.save_data(test_data)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.data_file))
        
        # Verify saved data
        with open(self.data_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(len(saved_data['transactions']), 1)
        self.assertIn('last_modified', saved_data['metadata'])
    
    def test_save_data_with_backup(self):
        """Test saving data with backup creation."""
        # Create initial file
        initial_data = {"test": "data"}
        with open(self.data_file, 'w') as f:
            json.dump(initial_data, f)
        
        # Save new data
        new_data = {
            "schema_version": DataMigration.CURRENT_VERSION,
            "transactions": [],
            "categories": [],
            "metadata": {}
        }
        
        success = self.manager.save_data(new_data, backup=True)
        
        self.assertTrue(success)
        
        # Check if backup was created
        backups = self.manager.list_backups()
        self.assertTrue(len(backups) > 0)
    
    def test_validate_data_integrity(self):
        """Test data integrity validation."""
        # Create valid data file
        valid_data = {
            "transactions": [
                {
                    "id": "1",
                    "amount": 100.0,
                    "description": "Test",
                    "type": "EXPENSE",
                    "category": "Food",
                    "date": "2024-01-01T00:00:00"
                }
            ],
            "categories": [
                {
                    "name": "Food",
                    "type": "EXPENSE"
                }
            ]
        }
        
        with open(self.data_file, 'w') as f:
            json.dump(valid_data, f)
        
        results = self.manager.validate_data_integrity()
        
        self.assertTrue(results['is_valid'])
        self.assertEqual(len(results['errors']), 0)
        self.assertIn('statistics', results)
    
    def test_validate_data_integrity_missing_file(self):
        """Test data integrity validation with missing file."""
        results = self.manager.validate_data_integrity()
        
        self.assertFalse(results['is_valid'])
        self.assertIn('Data file does not exist', results['errors'])
    
    def test_create_backup(self):
        """Test backup creation."""
        # Create data file
        test_data = {"test": "data"}
        with open(self.data_file, 'w') as f:
            json.dump(test_data, f)
        
        backup_path = self.manager.create_backup("test_backup.json")
        
        self.assertTrue(os.path.exists(backup_path))
        self.assertIn("test_backup.json", backup_path)
    
    def test_restore_from_backup(self):
        """Test restoration from backup."""
        # Create original data
        original_data = {"original": "data"}
        with open(self.data_file, 'w') as f:
            json.dump(original_data, f)
        
        # Create backup
        backup_path = self.manager.create_backup("test_backup.json")
        
        # Modify original data
        modified_data = {"modified": "data"}
        with open(self.data_file, 'w') as f:
            json.dump(modified_data, f)
        
        # Restore from backup
        success = self.manager.restore_from_backup(backup_path)
        
        self.assertTrue(success)
        
        # Verify restoration
        with open(self.data_file, 'r') as f:
            restored_data = json.load(f)
        
        self.assertEqual(restored_data, original_data)
    
    def test_list_backups(self):
        """Test listing backups."""
        # Create data file and some backups
        test_data = {"test": "data"}
        with open(self.data_file, 'w') as f:
            json.dump(test_data, f)
        
        self.manager.create_backup("backup1.json")
        self.manager.create_backup("backup2.json")
        
        backups = self.manager.list_backups()
        
        self.assertEqual(len(backups), 2)
        self.assertTrue(all('filename' in backup for backup in backups))
        self.assertTrue(all('created' in backup for backup in backups))
    
    def test_cleanup_old_backups(self):
        """Test cleanup of old backups."""
        # Create data file and multiple backups
        test_data = {"test": "data"}
        with open(self.data_file, 'w') as f:
            json.dump(test_data, f)
        
        for i in range(5):
            self.manager.create_backup(f"backup{i}.json")
        
        # Keep only 3 backups
        deleted_count = self.manager.cleanup_old_backups(keep_count=3)
        
        self.assertEqual(deleted_count, 2)
        
        remaining_backups = self.manager.list_backups()
        self.assertEqual(len(remaining_backups), 3)
    
    def test_get_data_statistics_existing_file(self):
        """Test getting statistics for existing file."""
        test_data = {
            "schema_version": "1.0.0",
            "transactions": [{"id": "1"}, {"id": "2"}],
            "categories": [{"name": "Food"}],
            "metadata": {"created_at": "2024-01-01T00:00:00"}
        }
        
        with open(self.data_file, 'w') as f:
            json.dump(test_data, f)
        
        stats = self.manager.get_data_statistics()
        
        self.assertTrue(stats['file_exists'])
        self.assertEqual(stats['schema_version'], '1.0.0')
        self.assertEqual(stats['total_transactions'], 2)
        self.assertEqual(stats['total_categories'], 1)
        self.assertIn('file_size', stats)
        self.assertIn('last_modified', stats)
    
    def test_get_data_statistics_missing_file(self):
        """Test getting statistics for missing file."""
        stats = self.manager.get_data_statistics()
        
        self.assertFalse(stats['file_exists'])
        self.assertEqual(stats['file_size'], 0)
        self.assertEqual(stats['total_transactions'], 0)
        self.assertEqual(stats['total_categories'], 0)
    
    def test_manager_without_backup(self):
        """Test manager with backup disabled."""
        manager = DataPersistenceManager(self.data_file, backup_enabled=False)
        
        self.assertIsNone(manager.backup_manager)
        
        # These operations should return empty/default values
        self.assertEqual(manager.list_backups(), [])
        self.assertEqual(manager.cleanup_old_backups(), 0)
        
        # These should raise errors
        with self.assertRaises(FileOperationError):
            manager.create_backup()
        
        with self.assertRaises(FileOperationError):
            manager.restore_from_backup("test.json")


if __name__ == '__main__':
    unittest.main()