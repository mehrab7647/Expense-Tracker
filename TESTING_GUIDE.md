# 🧪 Expense Tracker Testing Guide

This guide will walk you through testing all features of the Expense Tracker application.

## ✅ **Pre-Testing Verification**

### 1. **Run Automated Tests**
```bash
# Run our manual test suite
python3 test_manual.py

# Expected output: "🎉 ALL TESTS PASSED! The application is ready to use."
```

### 2. **Check Application Status**
```bash
# Check version
python3 main.py --version

# Check application info
python3 main.py --info

# Validate data integrity
python3 main.py --validate
```

## 🖥️ **Console Interface Testing**

### **Start Console Interface**
```bash
python3 main.py --console
```

### **Test Scenarios for Console Interface:**

#### **1. Navigation Testing**
- ✅ Main menu displays correctly
- ✅ All menu options are accessible (1-7)
- ✅ Invalid menu choices show error messages
- ✅ Exit option (7) works properly

#### **2. Transaction Management**
**Add Transactions:**
- ✅ Add an expense transaction:
  - Amount: $25.50
  - Description: "Grocery shopping"
  - Category: "Food & Dining"
  - Type: Expense
- ✅ Add an income transaction:
  - Amount: $1500.00
  - Description: "Monthly salary"
  - Category: "Salary"
  - Type: Income
- ✅ Test validation errors:
  - Try negative amount
  - Try empty description
  - Try invalid date format

**View Transactions:**
- ✅ View all transactions
- ✅ Filter by date range
- ✅ Filter by category
- ✅ Filter by type (income/expense)

**Edit Transactions:**
- ✅ Edit an existing transaction
- ✅ Update amount, description, category
- ✅ Verify changes are saved

**Delete Transactions:**
- ✅ Delete a transaction
- ✅ Confirm deletion prompt works
- ✅ Verify transaction is removed

#### **3. Category Management**
- ✅ View all categories
- ✅ View categories by type (income/expense)
- ✅ Add custom category
- ✅ Try to delete category in use (should fail)
- ✅ Delete unused custom category

#### **4. Reports Testing**
- ✅ Generate summary report
- ✅ Generate category breakdown
- ✅ Generate monthly report
- ✅ Generate date range report
- ✅ Verify calculations are correct

#### **5. Export Testing**
- ✅ Export to CSV
- ✅ Export to Excel (if openpyxl installed)
- ✅ Export with date filters
- ✅ Verify exported files contain correct data

#### **6. Chart Generation**
- ✅ Generate pie chart (category breakdown)
- ✅ Generate bar chart (monthly trends)
- ✅ Generate line chart (balance over time)
- ✅ Verify chart files are created

## 🖼️ **GUI Interface Testing**

### **Start GUI Interface**
```bash
python3 main.py --gui
```

### **Test Scenarios for GUI Interface:**

#### **1. Window and Layout**
- ✅ Main window opens correctly
- ✅ All UI elements are visible
- ✅ Window can be resized
- ✅ Menus are accessible

#### **2. Transaction Forms**
- ✅ Add transaction form works
- ✅ All fields accept input
- ✅ Validation errors display properly
- ✅ Success messages appear
- ✅ Form clears after submission

#### **3. Transaction List**
- ✅ Transactions display in list/table
- ✅ Sorting works (by date, amount, category)
- ✅ Filtering controls work
- ✅ Edit/delete buttons function

#### **4. Reports Window**
- ✅ Reports display in separate window
- ✅ Data is formatted correctly
- ✅ Export buttons work from reports

#### **5. Chart Display**
- ✅ Charts display within GUI
- ✅ Chart types can be switched
- ✅ Charts update with data changes
- ✅ Chart export works

#### **6. Menu System**
- ✅ File menu (New, Open, Save, Exit)
- ✅ Edit menu (Add, Edit, Delete)
- ✅ View menu (Reports, Charts)
- ✅ Tools menu (Export, Backup)
- ✅ Help menu (About)

## 🔧 **Advanced Testing Scenarios**

### **1. Data File Management**
```bash
# Test with custom data file
python3 main.py --console --data test_expenses.json

# Test backup creation
python3 main.py --backup

# Test backup restoration
python3 main.py --restore backups/expense_data_backup_YYYYMMDD_HHMMSS.json
```

### **2. Error Handling Testing**
- ✅ Test with corrupted data file
- ✅ Test with missing data file (should create new)
- ✅ Test with invalid JSON
- ✅ Test file permission errors
- ✅ Test disk space issues (if possible)

### **3. Edge Cases**
- ✅ Very large amounts (999999999.99)
- ✅ Very small amounts (0.01)
- ✅ Very long descriptions (200 characters)
- ✅ Special characters in descriptions
- ✅ Future dates
- ✅ Very old dates
- ✅ Many transactions (performance test)

### **4. Data Integrity Testing**
- ✅ Add 100+ transactions
- ✅ Verify all calculations are correct
- ✅ Test data validation
- ✅ Test backup/restore with large dataset

## 📊 **Sample Test Data**

### **Recommended Test Transactions:**
```
1. Income: $3000.00, "January Salary", Salary, 2024-01-01
2. Expense: $1200.00, "Rent Payment", Bills & Utilities, 2024-01-01
3. Expense: $150.00, "Groceries", Food & Dining, 2024-01-02
4. Expense: $50.00, "Gas", Transportation, 2024-01-03
5. Expense: $25.00, "Coffee", Food & Dining, 2024-01-04
6. Income: $500.00, "Freelance Work", Freelance, 2024-01-05
7. Expense: $100.00, "Utilities", Bills & Utilities, 2024-01-06
8. Expense: $75.00, "Internet", Bills & Utilities, 2024-01-07
9. Expense: $200.00, "Shopping", Shopping, 2024-01-08
10. Income: $100.00, "Gift", Gift, 2024-01-09
```

### **Expected Results:**
- Total Income: $3,600.00
- Total Expenses: $1,800.00
- Net Balance: $1,800.00
- Most expensive category: Bills & Utilities ($1,375.00)

## 🚨 **Common Issues and Solutions**

### **Issue: GUI doesn't start**
```bash
# Solution: Use console interface
python3 main.py --console

# Or check display environment
echo $DISPLAY
```

### **Issue: Charts don't generate**
```bash
# Solution: Install matplotlib
pip install matplotlib
```

### **Issue: Excel export fails**
```bash
# Solution: Install openpyxl
pip install openpyxl
```

### **Issue: Permission denied**
```bash
# Solution: Check file permissions
ls -la data/
chmod 644 data/expense_data.json
```

## ✅ **Testing Checklist**

### **Basic Functionality**
- [ ] Application starts without errors
- [ ] Version command works
- [ ] Info command shows correct data
- [ ] Validation command passes

### **Console Interface**
- [ ] Menu navigation works
- [ ] Can add transactions
- [ ] Can view transactions
- [ ] Can edit transactions
- [ ] Can delete transactions
- [ ] Can manage categories
- [ ] Can generate reports
- [ ] Can export data
- [ ] Can create charts

### **GUI Interface**
- [ ] Window opens correctly
- [ ] Forms work properly
- [ ] Lists display data
- [ ] Charts display correctly
- [ ] Menus function
- [ ] Export works from GUI

### **Data Management**
- [ ] Data persists between sessions
- [ ] Backups can be created
- [ ] Backups can be restored
- [ ] Data validation works
- [ ] Custom data files work

### **Error Handling**
- [ ] Invalid inputs show errors
- [ ] File errors are handled gracefully
- [ ] User gets helpful error messages
- [ ] Application doesn't crash

## 🎯 **Performance Testing**

### **Load Testing**
```bash
# Create test with many transactions
python3 -c "
import sys
sys.path.insert(0, '.')
from expense_tracker.repositories.json_repository import JSONRepository
from expense_tracker.services.transaction_service import TransactionService
from expense_tracker.models.transaction import TransactionType
from decimal import Decimal
from datetime import datetime, timedelta
import random

repo = JSONRepository('performance_test.json')
service = TransactionService(repo)

# Add 1000 transactions
for i in range(1000):
    service.create_transaction(
        amount=Decimal(str(random.uniform(1, 1000))),
        description=f'Test transaction {i}',
        transaction_type=random.choice([TransactionType.INCOME, TransactionType.EXPENSE]),
        category='Food & Dining',
        transaction_date=datetime.now() - timedelta(days=random.randint(0, 365))
    )

print('Created 1000 test transactions')
"

# Test performance with large dataset
python3 main.py --data performance_test.json --info
python3 main.py --data performance_test.json --validate
```

## 🏆 **Success Criteria**

The application passes testing if:
- ✅ All basic functionality works without errors
- ✅ Both interfaces (console and GUI) are functional
- ✅ Data persists correctly between sessions
- ✅ All calculations are accurate
- ✅ Error handling is graceful and informative
- ✅ Performance is acceptable with reasonable data sizes
- ✅ Export and backup features work correctly

## 🎉 **Congratulations!**

If you've completed this testing guide successfully, your Expense Tracker application is fully functional and ready for daily use! 

You now have a robust personal finance management system that can:
- Track income and expenses
- Categorize transactions
- Generate detailed reports
- Create visualizations
- Export data for analysis
- Backup and restore data
- Handle errors gracefully

**Happy expense tracking!** 💰📊