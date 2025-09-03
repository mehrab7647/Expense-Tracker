#!/usr/bin/env python3
"""Main entry point for the Expense Tracker application."""

import sys
import argparse
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from expense_tracker.controllers.app_controller import ApplicationController


def create_argument_parser():
    """Create and configure the command line argument parser."""
    parser = argparse.ArgumentParser(
        description='Expense Tracker - Personal Finance Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start with GUI interface (default)
  %(prog)s --console          # Start with console interface
  %(prog)s --gui              # Start with GUI interface
  %(prog)s --data custom.json # Use custom data file
  %(prog)s --console --debug  # Console mode with debug logging
  %(prog)s --info             # Show application information
  %(prog)s --validate         # Validate data integrity
  %(prog)s --backup           # Create data backup
  %(prog)s --restore backup.json # Restore from backup
"""
    )
    
    # Interface selection (mutually exclusive)
    interface_group = parser.add_mutually_exclusive_group()
    interface_group.add_argument(
        '--console', '-c',
        action='store_true',
        help='Start the console interface'
    )
    interface_group.add_argument(
        '--gui', '-g',
        action='store_true',
        help='Start the GUI interface (default)'
    )
    
    # Data file options
    parser.add_argument(
        '--data', '-d',
        type=str,
        metavar='FILE',
        help='Path to data file (default: data/expense_data.json)'
    )
    
    # Logging options
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    # Utility commands (mutually exclusive with interface)
    utility_group = parser.add_mutually_exclusive_group()
    utility_group.add_argument(
        '--info', '-i',
        action='store_true',
        help='Show application information and exit'
    )
    utility_group.add_argument(
        '--validate', '-v',
        action='store_true',
        help='Validate data integrity and exit'
    )
    utility_group.add_argument(
        '--backup', '-b',
        action='store_true',
        help='Create data backup and exit'
    )
    utility_group.add_argument(
        '--restore', '-r',
        type=str,
        metavar='BACKUP_FILE',
        help='Restore data from backup file and exit'
    )
    
    # Version information
    parser.add_argument(
        '--version',
        action='version',
        version='Expense Tracker v1.0.0'
    )
    
    return parser


def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                     EXPENSE TRACKER v1.0.0                  ║
║              Personal Finance Management System              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_application_info(controller):
    """Print detailed application information."""
    print("\n" + "=" * 60)
    print("APPLICATION INFORMATION")
    print("=" * 60)
    
    try:
        info = controller.get_application_info()
        
        print(f"Version: {info.get('version', 'Unknown')}")
        print(f"Data File: {info.get('data_file', 'Unknown')}")
        print(f"Data File Exists: {'Yes' if info.get('data_file_exists', False) else 'No'}")
        
        if info.get('data_file_exists', False):
            print(f"Data File Size: {info.get('data_file_size', 0):,} bytes")
        
        print(f"\nData Statistics:")
        print(f"  Total Transactions: {info.get('total_transactions', 0):,}")
        print(f"  Total Categories: {info.get('total_categories', 0):,}")
        
        print(f"\nFinancial Summary:")
        print(f"  Total Income: ${info.get('total_income', 0):,.2f}")
        print(f"  Total Expenses: ${info.get('total_expenses', 0):,.2f}")
        print(f"  Net Balance: ${info.get('net_balance', 0):,.2f}")
        
        print(f"\nApplication Status:")
        print(f"  Running: {'Yes' if info.get('is_running', False) else 'No'}")
        print(f"  Current Interface: {info.get('current_interface', 'None')}")
        
    except Exception as e:
        print(f"Error retrieving application information: {e}")
        return False
    
    return True


def print_validation_results(controller):
    """Print data validation results."""
    print("\n" + "=" * 60)
    print("DATA VALIDATION RESULTS")
    print("=" * 60)
    
    try:
        results = controller.validate_data_integrity()
        
        # Overall status
        status = "✓ VALID" if results['is_valid'] else "✗ INVALID"
        print(f"Data Integrity: {status}")
        
        # Statistics
        if results.get('statistics'):
            print(f"\nStatistics:")
            for key, value in results['statistics'].items():
                print(f"  {key.replace('_', ' ').title()}: {value:,}")
        
        # Errors
        if results.get('errors'):
            print(f"\nErrors ({len(results['errors'])}):")
            for i, error in enumerate(results['errors'], 1):
                print(f"  {i}. {error}")
        
        # Warnings
        if results.get('warnings'):
            print(f"\nWarnings ({len(results['warnings'])}):")
            for i, warning in enumerate(results['warnings'], 1):
                print(f"  {i}. {warning}")
        
        if not results['errors'] and not results['warnings']:
            print("\n✓ No issues found. Data integrity is excellent!")
        
    except Exception as e:
        print(f"Error during validation: {e}")
        return False
    
    return True


def create_backup(controller):
    """Create a data backup."""
    print("\n" + "=" * 60)
    print("CREATING DATA BACKUP")
    print("=" * 60)
    
    try:
        success = controller.backup_data()
        
        if success:
            print("✓ Data backup created successfully!")
            print("  Backup location: backups/ directory")
        else:
            print("✗ Failed to create backup.")
            print("  Check if data file exists and you have write permissions.")
        
        return success
        
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False


def restore_backup(controller, backup_file):
    """Restore data from backup."""
    print("\n" + "=" * 60)
    print("RESTORING DATA FROM BACKUP")
    print("=" * 60)
    
    try:
        if not os.path.exists(backup_file):
            print(f"✗ Backup file not found: {backup_file}")
            return False
        
        print(f"Restoring from: {backup_file}")
        success = controller.restore_data(backup_file)
        
        if success:
            print("✓ Data restored successfully!")
            print("  Previous data has been backed up automatically.")
        else:
            print("✗ Failed to restore data.")
        
        return success
        
    except Exception as e:
        print(f"Error restoring backup: {e}")
        return False


def check_dependencies():
    """Check for optional dependencies and warn if missing."""
    warnings = []
    
    # Check for matplotlib
    try:
        import matplotlib
    except ImportError:
        warnings.append("matplotlib not found - Chart generation will be disabled")
    
    # Check for openpyxl
    try:
        import openpyxl
    except ImportError:
        warnings.append("openpyxl not found - Excel export will be disabled")
    
    # Check for PIL/Pillow
    try:
        from PIL import Image
    except ImportError:
        warnings.append("Pillow not found - Chart display in GUI will be limited")
    
    if warnings:
        print("\n" + "⚠" * 60)
        print("OPTIONAL DEPENDENCIES")
        print("⚠" * 60)
        print("Some optional features may be limited:")
        for warning in warnings:
            print(f"  • {warning}")
        print("\nTo install all optional dependencies:")
        print("  pip install matplotlib openpyxl Pillow")
        print("⚠" * 60)


def main():
    """Main application entry point."""
    # Parse command line arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    try:
        # Initialize application controller
        controller = ApplicationController(
            data_file_path=args.data,
            log_level=args.log_level
        )
        
        # Handle utility commands
        if args.info:
            success = print_application_info(controller)
            sys.exit(0 if success else 1)
        
        elif args.validate:
            success = print_validation_results(controller)
            sys.exit(0 if success else 1)
        
        elif args.backup:
            success = create_backup(controller)
            sys.exit(0 if success else 1)
        
        elif args.restore:
            success = restore_backup(controller, args.restore)
            sys.exit(0 if success else 1)
        
        # Check dependencies
        check_dependencies()
        
        # Start appropriate interface
        if args.console:
            print("\nStarting Console Interface...")
            print("Press Ctrl+C to exit at any time.\n")
            controller.start_console_interface()
        
        else:  # Default to GUI
            print("\nStarting GUI Interface...")
            print("Close the window to exit.\n")
            
            # Check if we're in a GUI environment
            if os.environ.get('DISPLAY') is None and sys.platform != 'win32' and sys.platform != 'darwin':
                print("Warning: No display detected. GUI may not work properly.")
                print("Use --console flag to start in console mode.")
                response = input("Continue with GUI? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("Starting console interface instead...")
                    controller.start_console_interface()
                    return
            
            controller.start_gui_interface()
    
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Goodbye!")
        sys.exit(0)
    
    except ImportError as e:
        print(f"\nError: Missing required dependency: {e}")
        print("Please install required packages with: pip install -r requirements.txt")
        sys.exit(1)
    
    except Exception as e:
        print(f"\nFatal error: {e}")
        print("Please check the logs for more details.")
        sys.exit(1)


if __name__ == '__main__':
    main()