# Expense Tracker

A comprehensive personal finance management system built in Python with both console and GUI interfaces.

## Features

### Core Functionality
- **Transaction Management**: Add, edit, delete, and view income and expense transactions
- **Category Management**: Organize transactions with customizable categories
- **Financial Reporting**: Generate detailed reports with summaries and breakdowns
- **Data Visualization**: Create charts and graphs to visualize spending patterns
- **Data Export**: Export data to CSV and Excel formats
- **Data Backup & Recovery**: Automatic backups with restore capabilities

### User Interfaces
- **Console Interface**: Text-based interface for command-line users
- **GUI Interface**: User-friendly graphical interface built with tkinter
- **Dual Interface Support**: Switch between interfaces based on preference

### Data Management
- **JSON Storage**: Lightweight, human-readable data storage
- **Data Validation**: Comprehensive input validation and error handling
- **Schema Migration**: Automatic data migration for version updates
- **Data Integrity**: Built-in validation and corruption detection

## Installation

### Requirements
- Python 3.8 or higher
- Optional dependencies for enhanced features (see below)

### Basic Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/expense-tracker.git
cd expense-tracker
```

2. Install the application:
```bash
pip install -e .
```

### With Optional Features

For full functionality including charts and Excel export:
```bash
pip install -e .[full]
```

Or install specific feature sets:
```bash
# For chart generation
pip install -e .[charts]

# For Excel export
pip install -e .[excel]

# For enhanced GUI features
pip install -e .[gui]
```

### Development Installation

For development with testing tools:
```bash
pip install -e .[dev]
```

## Usage

### Command Line Interface

Start the application with various options:

```bash
# Start with GUI interface (default)
python main.py

# Start with console interface
python main.py --console

# Use custom data file
python main.py --data /path/to/custom/data.json

# Show application information
python main.py --info

# Validate data integrity
python main.py --validate

# Create data backup
python main.py --backup

# Restore from backup
python main.py --restore backup_file.json

# Set logging level
python main.py --log-level DEBUG
```

### Console Interface

The console interface provides a menu-driven experience:

1. **Transaction Management**
   - Add new transactions
   - View and filter transactions
   - Edit existing transactions
   - Delete transactions

2. **Category Management**
   - View categories
   - Add custom categories
   - Manage category types

3. **Reports and Analytics**
   - View financial summaries
   - Generate category breakdowns
   - Create date range reports

4. **Data Operations**
   - Export data to files
   - Generate charts
   - Backup and restore data

### GUI Interface

The GUI interface offers:

- **Main Dashboard**: Overview of financial status
- **Transaction Entry**: Easy-to-use forms for adding transactions
- **Transaction List**: Sortable and filterable transaction view
- **Reports Window**: Tabular reports with export options
- **Chart Display**: Interactive charts and graphs
- **Settings Panel**: Application configuration options

## Data Structure

### Transactions
```json
{
  "id": "unique_transaction_id",
  "amount": 50.00,
  "description": "Grocery shopping",
  "type": "EXPENSE",
  "category": "Food & Dining",
  "date": "2024-01-15T10:30:00",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Categories
```json
{
  "name": "Food & Dining",
  "type": "EXPENSE",
  "is_default": true,
  "created_at": "2024-01-01T00:00:00"
}
```

## Configuration

### Data File Location
By default, data is stored in `data/expense_data.json`. You can specify a custom location:

```bash
python main.py --data /path/to/your/data.json
```

### Settings
Application settings are stored within the data file:

```json
{
  "settings": {
    "currency": "USD",
    "date_format": "YYYY-MM-DD",
    "decimal_places": 2,
    "auto_backup": true,
    "backup_frequency": "daily"
  }
}
```

## Backup and Recovery

### Automatic Backups
- Backups are created automatically before data modifications
- Stored in the `backups/` directory
- Configurable backup frequency

### Manual Backup
```bash
# Create backup
python main.py --backup

# Restore from backup
python main.py --restore backup_file.json
```

### Backup Management
- List available backups
- Automatic cleanup of old backups
- Backup validation before restoration

## Data Validation and Integrity

### Input Validation
- Amount validation (positive numbers, proper decimal places)
- Date validation (valid dates, reasonable ranges)
- Description validation (length, character restrictions)
- Category validation (valid types, naming conventions)

### Data Integrity Checks
- Duplicate transaction ID detection
- Missing required fields validation
- Data type consistency checks
- Referential integrity validation

### Error Handling
- Comprehensive error messages
- Graceful degradation on errors
- Automatic recovery suggestions
- Detailed logging for troubleshooting

## Reporting and Analytics

### Financial Reports
- **Summary Report**: Total income, expenses, and net balance
- **Category Breakdown**: Spending by category
- **Monthly Reports**: Month-by-month analysis
- **Date Range Reports**: Custom period analysis

### Charts and Visualizations
- **Pie Charts**: Category distribution
- **Bar Charts**: Monthly spending trends
- **Line Charts**: Balance over time
- **Export Options**: Save charts as images

### Export Formats
- **CSV**: Compatible with spreadsheet applications
- **Excel**: Full-featured Excel workbooks with formatting
- **JSON**: Raw data export for integration

## Development

### Project Structure
```
expense-tracker/
├── expense_tracker/           # Main application package
│   ├── models/               # Data models
│   ├── repositories/         # Data access layer
│   ├── services/            # Business logic
│   ├── ui/                  # User interfaces
│   ├── controllers/         # Application controllers
│   └── utils/               # Utilities and helpers
├── tests/                   # Unit tests
├── data/                    # Default data directory
├── backups/                 # Backup storage
├── main.py                  # Application entry point
├── setup.py                 # Installation configuration
└── requirements.txt         # Dependencies
```

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=expense_tracker

# Run specific test file
python -m pytest tests/test_models/test_transaction.py
```

### Code Quality
```bash
# Format code
black expense_tracker/ tests/

# Lint code
flake8 expense_tracker/ tests/

# Type checking (if using mypy)
mypy expense_tracker/
```

## Architecture

### Design Patterns
- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic separation
- **MVC Pattern**: Clear separation of concerns
- **Observer Pattern**: UI updates and notifications

### Key Components
- **Models**: Data structures and validation
- **Repositories**: Data persistence and retrieval
- **Services**: Business logic and operations
- **Controllers**: Application coordination
- **UI**: User interface implementations
- **Utils**: Shared utilities and helpers

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Document new features
- Update README for significant changes
- Use meaningful commit messages

## Troubleshooting

### Common Issues

**Data file not found**
- The application will create a new data file automatically
- Check file permissions if creation fails

**Import errors**
- Ensure all dependencies are installed
- Check Python version compatibility

**GUI not displaying**
- Verify display environment variables
- Use `--console` flag as alternative

**Backup/restore failures**
- Check file permissions
- Verify backup file integrity
- Ensure sufficient disk space

### Logging
Enable debug logging for troubleshooting:
```bash
python main.py --log-level DEBUG
```

Logs include:
- Application startup and shutdown
- Data operations and validation
- Error details and stack traces
- Performance metrics

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python standard library for maximum compatibility
- Uses tkinter for cross-platform GUI support
- Matplotlib for chart generation
- openpyxl for Excel export functionality

## Version History

### v1.0.0
- Initial release
- Complete transaction and category management
- Dual interface support (console and GUI)
- Comprehensive reporting and analytics
- Data export and backup capabilities
- Full test coverage

## Support

For support, please:
1. Check the troubleshooting section
2. Review existing issues on GitHub
3. Create a new issue with detailed information
4. Include logs and system information

## Roadmap

Future enhancements may include:
- Web interface
- Mobile app companion
- Cloud synchronization
- Advanced analytics and forecasting
- Multi-currency support
- Receipt scanning and OCR
- Integration with banking APIs
