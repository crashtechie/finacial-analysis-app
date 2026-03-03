# Manual Testing Guide

Complete guide for manually testing the Financial Analysis API backend endpoints and functionality.

## Table of Contents
- [Setup & Prerequisites](#setup--prerequisites)
- [Starting the Server](#starting-the-server)
- [Testing Tools & Methods](#testing-tools--methods)
- [API Endpoint Testing](#api-endpoint-testing)
- [Data Import Testing](#data-import-testing)
- [Analytics Testing](#analytics-testing)
- [Error Handling Testing](#error-handling-testing)
- [Admin Interface Testing](#admin-interface-testing)
- [Performance Testing](#performance-testing)

---

## Setup & Prerequisites

### 1. Environment Setup

```bash
# Navigate to backend directory
cd app/backend

# Sync dependencies with uv (if needed)
uv sync

# Note: With uv, you don't need to manually activate virtual environments.
# Use 'uv run' prefix for all Python commands (shown below).
```

### 2. Database Setup

```bash
# Run migrations
uv run python manage.py migrate

# Load sample categories
uv run python manage.py loaddata api/fixtures/categories.json

# Create superuser (for admin testing)
uv run python manage.py createsuperuser
# Follow prompts for username, email, password
```

### 3. Sample Data Setup (Optional)

```bash
# Create institutions and accounts via Django shell
uv run python manage.py shell << 'EOF'
from api.models import Institution, Account

# Create institutions
bank1, _ = Institution.objects.get_or_create(
    identifier='bank-1',
    defaults={'name': 'Bank-1'}
)
bank5, _ = Institution.objects.get_or_create(
    identifier='bank-5',
    defaults={'name': 'Bank-5'}
)

# Create accounts
Account.objects.get_or_create(
    institution=bank1,
    account_number='1001',
    defaults={'name': 'Checking Account', 'account_type': 'checking'}
)
Account.objects.get_or_create(
    institution=bank5,
    account_number='5001',
    defaults={'name': 'Savings Account', 'account_type': 'savings'}
)
print('✅ Institutions and accounts created!')
EOF

# Import sample transactions
uv run python manage.py import_transactions ../../finances/bank-1/test-transactions-demo.csv --format bank-1 --account-id 1
uv run python manage.py import_transactions ../../finances/bank-5/test-transactions-demo.csv --format bank-5 --account-id 2
```

---

## Starting the Server

### Development Server

```bash
# Start the development server
uv run python manage.py runserver

# Server will be available at: http://localhost:8000
# Admin: http://localhost:8000/admin
# API: http://localhost:8000/api
```

### In Another Terminal

Keep the server running and use another terminal for testing commands:

```bash
cd app/backend
# With uv, no activation needed - just use 'uv run' for Python commands
```

---

## Testing Tools & Methods

### Using cURL

Simple command-line HTTP requests:

```bash
# Basic GET request
curl http://localhost:8000/api/institutions/

# With pretty JSON output
curl http://localhost:8000/api/institutions/ | python -m json.tool

# POST request with data
curl -X POST http://localhost:8000/api/institutions/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Bank-2", "identifier": "bank-2"}'

# With authentication (if required)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/institutions/
```

### Using Python Requests

More flexible testing:

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# List institutions
response = requests.get(f"{BASE_URL}/institutions/")
print(json.dumps(response.json(), indent=2))

# Create institution
data = {"name": "Bank-2", "identifier": "bank-2"}
response = requests.post(f"{BASE_URL}/institutions/", json=data)
print(response.status_code)
print(response.json())

# Get specific institution
response = requests.get(f"{BASE_URL}/institutions/1/")
print(response.json())
```

### Using Postman

1. Download and install [Postman](https://www.postman.com/downloads/)
2. Create new collection: "Financial API"
3. Add requests for each endpoint
4. Save and reuse

### Using Django Shell

Direct Python access to models:

```bash
uv run python manage.py shell
```

```python
from api.models import Institution, Account, Transaction, Category

# List all institutions
institutions = Institution.objects.all()
for inst in institutions:
    print(f"{inst.id}: {inst.name} ({inst.identifier})")

# Create new institution
inst = Institution.objects.create(name="Bank-4", identifier="bank-4")
print(f"Created: {inst}")

# Query transactions
transactions = Transaction.objects.all()[:5]
for t in transactions:
    print(f"{t.date}: {t.description} - {t.amount}")

# Filter by date range
from datetime import datetime
feb = Transaction.objects.filter(date__month=2)
print(f"February transactions: {feb.count()}")

# Calculate totals
expenses = Transaction.objects.filter(amount__lt=0)
total_expenses = sum(t.amount for t in expenses)
print(f"Total expenses: ${abs(total_expenses):.2f}")
```

---

## API Endpoint Testing

### Institutions Endpoint

```bash
# List all institutions
curl http://localhost:8000/api/institutions/

# Create new institution
curl -X POST http://localhost:8000/api/institutions/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Bank-3", "identifier": "bank-3"}'

# Get specific institution
curl http://localhost:8000/api/institutions/1/

# Update institution
curl -X PATCH http://localhost:8000/api/institutions/1/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Bank-3 Updated"}'

# Delete institution
curl -X DELETE http://localhost:8000/api/institutions/1/
```

### Accounts Endpoint

```bash
# List accounts
curl http://localhost:8000/api/accounts/

# Filter by institution
curl "http://localhost:8000/api/accounts/?institution=1"

# Filter by account type
curl "http://localhost:8000/api/accounts/?account_type=checking"

# Create account
curl -X POST http://localhost:8000/api/accounts/ \
  -H "Content-Type: application/json" \
  -d '{
    "institution": 1,
    "name": "Checking Account",
    "account_number": "1234",
    "account_type": "checking"
  }'

# Get account details (includes balance)
curl http://localhost:8000/api/accounts/1/

# Get account transactions
curl http://localhost:8000/api/accounts/1/transactions/
```

### Categories Endpoint

```bash
# List all categories
curl http://localhost:8000/api/categories/

# List root categories only
curl "http://localhost:8000/api/categories/?parent__isnull=true"

# Search categories
curl "http://localhost:8000/api/categories/?search=groceries"

# Get category details
curl http://localhost:8000/api/categories/1/

# Get category transactions
curl http://localhost:8000/api/categories/1/transactions/
```

### Transactions Endpoint

```bash
# List all transactions
curl http://localhost:8000/api/transactions/

# Filter by date range
curl "http://localhost:8000/api/transactions/?date__gte=2026-02-01&date__lte=2026-02-28"

# Filter by amount (expenses only)
curl "http://localhost:8000/api/transactions/?amount__lt=0"

# Filter by account
curl "http://localhost:8000/api/transactions/?account=1"

# Filter by category
curl "http://localhost:8000/api/transactions/?category=5"

# Find uncategorized transactions
curl "http://localhost:8000/api/transactions/?category__isnull=true"

# Search by description
curl "http://localhost:8000/api/transactions/?search=starbucks"

# Sort by amount (descending)
curl "http://localhost:8000/api/transactions/?ordering=-amount"

# Paginate results
curl "http://localhost:8000/api/transactions/?page=1&page_size=10"

# Get transaction details
curl http://localhost:8000/api/transactions/1/

# Update transaction category
curl -X PATCH http://localhost:8000/api/transactions/1/ \
  -H "Content-Type: application/json" \
  -d '{"category": 5, "notes": "lunch"}'
```

### Import Logs Endpoint

```bash
# List all imports
curl http://localhost:8000/api/imports/

# Filter by status
curl "http://localhost:8000/api/imports/?status=success"

# Get import details
curl http://localhost:8000/api/imports/1/
```

---

## Data Import Testing

All commands below assume you are in `app/backend`.

Available test files in `finances` subdirectories with 1000+ transactions spanning September 2025 - March 2026:

```bash
ls -la ../../finances/bank-1/test-transactions-demo.csv  # 690 transactions
ls -la ../../finances/bank-5/test-transactions-demo.csv  # 706 transactions
```

Supported importers: `bank-1`, `bank-5`

### Manual CSV Import

```bash
# Import Bank-1 test data (690 transactions)
uv run python manage.py import_transactions \
  ../../finances/bank-1/test-transactions-demo.csv \
  --format bank-1 \
  --account-id 1

# Import Bank-5 test data (706 transactions)
uv run python manage.py import_transactions \
  ../../finances/bank-5/test-transactions-demo.csv \
  --format bank-5 \
  --account-id 2

# Alternative (auto-create account for Bank-1)
uv run python manage.py import_transactions \
  ../../finances/bank-1/test-transactions-demo.csv \
  --format bank-1

# Expected output:
# ✓ Account: Bank-1 - Checking Account (1001)
# ✓ Processed: 690
# ✓ Imported: 690
# ✓ Skipped: 0 (duplicates)
# ✓ Import Log ID: #
```

### Test Import Error Handling

```bash
# Try importing to non-existent account (should fail)
uv run python manage.py import_transactions \
  ../../finances/bank-1/test-transactions-demo.csv \
  --format bank-1 \
  --account-id 999  # Non-existent account ID
# Expected: CommandError: Account with ID 999 not found

# Try importing with invalid format (should fail)
uv run python manage.py import_transactions \
  ../../finances/bank-1/test-transactions-demo.csv \
  --format invalid_format \
  --account-id 1
# Expected: CommandError: Unsupported import format: 'invalid_format'. Available formats: bank-1, bank-5

# Try importing non-existent file (should fail)
uv run python manage.py import_transactions \
  nonexistent.csv \
  --format bank-1 \
  --account-id 1
# Expected: CommandError: File not found: nonexistent.csv

# Successfully import Bank-5 test file (now supported!)
uv run python manage.py import_transactions \
  ../../finances/bank-5/test-transactions-demo.csv \
  --format bank-5 \
  --account-id 2
# Expected: ✅ Import completed with 706 transactions
```

### Verify Import Results

```bash
# Check import log via API
curl http://localhost:8000/api/imports/

# Count total transactions imported
uv run python manage.py shell
>>> from api.models import Transaction
>>> print(f"Total transactions: {Transaction.objects.count()}")
>>> print(f"February transactions: {Transaction.objects.filter(date__month=2).count()}")
```

---

## Analytics Testing

### Spending Trends

```bash
# Monthly trending
curl "http://localhost:8000/api/analytics/spending-trends/?period=monthly"

# Weekly trending
curl "http://localhost:8000/api/analytics/spending-trends/?period=weekly&start_date=2026-02-01&end_date=2026-02-28"

# Daily trending
curl "http://localhost:8000/api/analytics/spending-trends/?period=daily&start_date=2026-02-15&end_date=2026-02-20"

# Filter by account
curl "http://localhost:8000/api/analytics/spending-trends/?account=1&period=weekly"

# Expected response format:
# [
#   {
#     "period": "2026-02-01",
#     "total_expenses": 123.45,
#     "total_income": 1000.00,
#     "net": 876.55,
#     "transaction_count": 5
#   },
#   ...
# ]
```

### Category Breakdown

```bash
# Spending by category (February)
curl "http://localhost:8000/api/analytics/category-breakdown/?start_date=2026-02-01&end_date=2026-02-28"

# All transactions (including income)
curl "http://localhost:8000/api/analytics/category-breakdown/?expense_only=false"

# By specific account
curl "http://localhost:8000/api/analytics/category-breakdown/?account=1"

# Expected response:
# [
#   {
#     "category_id": 1,
#     "category_name": "Groceries",
#     "total": 450.25,
#     "percentage": 35.50,
#     "transaction_count": 8,
#     "avg_transaction": 56.28
#   },
#   ...
# ]
```

### Merchant Analysis

```bash
# Top 20 merchants (default)
curl http://localhost:8000/api/analytics/merchants/

# Top 5 merchants
curl "http://localhost:8000/api/analytics/merchants/?limit=5"

# Merchants for specific date range
curl "http://localhost:8000/api/analytics/merchants/?start_date=2026-02-01&end_date=2026-02-28"

# Expected response:
# [
#   {
#     "merchant": "Target",
#     "total_spent": 350.75,
#     "transaction_count": 5,
#     "avg_transaction": 70.15,
#     "first_transaction": "2026-02-05",
#     "last_transaction": "2026-02-25"
#   },
#   ...
# ]
```

### Summary Statistics

```bash
# Overall summary
curl http://localhost:8000/api/analytics/summary/

# Summary for specific month
curl "http://localhost:8000/api/analytics/summary/?start_date=2026-02-01&end_date=2026-02-28"

# By account
curl "http://localhost:8000/api/analytics/summary/?account=1"

# Expected response:
# {
#   "total_transactions": 76,
#   "total_expenses": 2350.50,
#   "total_income": 2000.00,
#   "net": -350.50,
#   "period_start": "2026-02-02",
#   "period_end": "2026-02-27",
#   "accounts": ["Bank-1 Account"]
# }
```

---

## Error Handling Testing

### Test 404 Errors

```bash
# Non-existent institution
curl http://localhost:8000/api/institutions/999/

# Expected: 404 Not Found
# {
#   "detail": "Not found."
# }
```

### Test 400 Errors

```bash
# Missing required field
curl -X POST http://localhost:8000/api/institutions/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Bank"}'

# Invalid pagination
curl "http://localhost:8000/api/transactions/?page=invalid"

# Invalid date format
curl "http://localhost:8000/api/transactions/?date__gte=02-28-2026"
```

### Test 400 Errors (continued)

```bash
# Malformed JSON (invalid syntax)
curl -X POST http://localhost:8000/api/institutions/ \
  -H "Content-Type: application/json" \
  -d '{invalid json}'

# Expected: 400 Bad Request
# The API correctly validates JSON and returns a 400 error for malformed requests
```

### Test 500 Errors

500 errors are server-side failures caused by unhandled exceptions. Here's how to simulate a real-world database connection failure:

```bash
# Step 1: Stop the development server (Ctrl+C in server terminal)

# Step 2: Rename the database file to simulate database unavailability
cd app/backend
mv db.sqlite3 db.sqlite3.bck

# Step 3: Restart the development server
uv run python manage.py runserver

# Step 4: In another terminal, make any API request
curl http://localhost:8000/api/institutions/

# Expected: 500 Internal Server Error
# {
#   "detail": "Internal Server Error"
# }

# Step 5: Check the server terminal - you'll see detailed error logs:
# ERROR:django.request: Internal Server Error: /api/institutions/
# Traceback shows: OperationalError - no such table: ...

# Step 6: Restore the database
mv db.sqlite3.bck db.sqlite3

# Step 7: Reload your browser or make a new request
curl http://localhost:8000/api/institutions/
# Expected: 200 OK (normal response)
```

**Why This Simulates Real Issues:**
- Database unavailability is a common production problem
- Ensures your error handling works for unrecoverable failures
- Tests API resilience and error logging
- Helps verify 500 errors are properly communicated to clients
```

### Database Constraint Testing

```bash
# Try creating duplicate identifier
curl -X POST http://localhost:8000/api/institutions/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Bank-1", "identifier": "bank-1"}'

# Expected: 400 Bad Request (or 409 Conflict)
# Should not create duplicate
```

---

## Admin Interface Testing

### Access Admin Panel

1. Navigate to: `http://localhost:8000/admin/`
2. Login with superuser credentials created earlier

### Test Admin Features

#### Institutions
- [ ] List all institutions
- [ ] Search by name or identifier
- [ ] Create new institution
- [ ] Edit existing institution
- [ ] Delete institution

#### Accounts
- [ ] List all accounts
- [ ] Filter by institution
- [ ] View account details (name, number, balance)
- [ ] Edit account information
- [ ] Delete account

#### Categories
- [ ] View category hierarchy
- [ ] Create new category
- [ ] Edit category
- [ ] Delete category
- [ ] Verify parent-child relationships

#### Transactions
- [ ] View all transactions
- [ ] Filter by date range
- [ ] Search by description
- [ ] View transaction details
- [ ] Edit category assignment
- [ ] Add notes to transaction

#### Import Logs
- [ ] View all imports
- [ ] Filter by status (success/failed)
- [ ] View import details (records processed, skipped)
- [ ] Check error messages

### Color-Coded Status Indicators

Look for color coding in admin:
- 🟢 Green: Income/Success
- 🔴 Red: Expenses/Errors
- 🟡 Yellow: Pending/Neutral

---

## Performance Testing

### Load Testing - Simple

```bash
# Test endpoint response time
time curl http://localhost:8000/api/institutions/

# Test with large result set
curl "http://localhost:8000/api/transactions/?page_size=100" | wc -l

# Monitor memory/CPU
# In another terminal:
watch -n 1 'ps aux | grep python'
```

### Pagination Performance

```bash
# Test different page sizes
curl "http://localhost:8000/api/transactions/?page_size=10"
curl "http://localhost:8000/api/transactions/?page_size=50"
curl "http://localhost:8000/api/transactions/?page_size=100"

# Performance should be similar
```

### Complex Query Performance

```bash
# Date range + category + sorting
time curl "http://localhost:8000/api/transactions/?date__gte=2026-02-01&date__lte=2026-02-28&category=1&ordering=-amount"

# Should complete in < 200ms for typical datasets
```

### Database Query Analysis

```bash
# Use Django Debug Toolbar (if installed)
# Or check SQL logs with:
uv run python manage.py shell
>>> from django.db import connection
>>> from api.models import Transaction
>>> Transaction.objects.filter(date__month=2)
>>> print(connection.queries[-1]['sql'])
```

---

## Testing Checklist

Use this checklist to ensure all functionality works:

### Core API
- [ ] Institutions - CRUD operations
- [ ] Accounts - CRUD operations
- [ ] Categories - CRUD operations
- [ ] Transactions - CRUD operations
- [ ] Import Logs - Read operations

### Filtering & Searching
- [ ] Date range filtering
- [ ] Amount filtering
- [ ] Category filtering
- [ ] Account filtering
- [ ] Text search
- [ ] Uncategorized filtering

### Sorting & Pagination
- [ ] Ascending/descending sort
- [ ] Multiple page sizes
- [ ] Next/previous links
- [ ] Total count accuracy

### Analytics
- [ ] Spending trends (daily/weekly/monthly)
- [ ] Category breakdown
- [ ] Merchant analysis
- [ ] Summary statistics
- [ ] Date range filtering

### Data Import
- [ ] CSV import success
- [ ] Duplicate detection
- [ ] Category auto-mapping
- [ ] Error handling
- [ ] Import log creation

### Admin Interface
- [ ] Login/logout
- [ ] Model viewing
- [ ] Create/edit/delete
- [ ] Filtering and search
- [ ] Bulk actions

### Error Cases
- [ ] 404 on non-existent resources
- [ ] 400 on invalid input
- [ ] 500 error handling
- [ ] Validation error messages
- [ ] Constraint violations

---

## Common Issues & Troubleshooting

### Server Won't Start

```bash
# Check for port conflicts
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process using port 8000 and restart
# Or use different port:
uv run python manage.py runserver 8001
```

### Import Fails

```bash
# Could be file not found
ls -la ../../finances/bank-1/
ls -la ../../finances/bank-5/

# Could be account doesn't exist
uv run python manage.py shell
>>> from api.models import Account
>>> Account.objects.all()

# Check for encoding issues
file ../../finances/bank-1/test-transactions-demo.csv
```

### API Returns Empty Results

```bash
# Check if data was imported
uv run python manage.py shell
>>> from api.models import Transaction
>>> print(Transaction.objects.count())

# Run import command if needed
uv run python manage.py import_transactions ../../finances/bank-1/test-transactions-demo.csv --format bank-1 --account-id 1
```

### Database Locked

```bash
# Close all connections and restart server
ps aux | grep python  # Find process ID
kill -9 <PID>

# Remove lock files if needed
rm -f db.sqlite3-journal

# Start fresh
uv run python manage.py migrate
uv run python manage.py loaddata api/fixtures/categories.json
```

---

## Next Steps

After manual testing:

1. **Automated Testing** - Run full test suite:
   ```bash
   uv run pytest --cov=api api/tests.py
   ```

2. **Code Quality** - Check formatting and linting:
   ```bash
   uv run black api/
   uv run flake8 api/
   uv run isort api/
   ```

3. **Security** - Run security checks:
   ```bash
   uv run python manage.py check --deploy
   ```

4. **Documentation** - Update API docs based on findings

5. **Deployment** - Follow deployment guide for production

---

## Reference

- [API Reference](../reference/API_REFERENCE.md) - Complete endpoint documentation
- [Developer Guide](../development/DEVELOPER_GUIDE.md) - How to extend the project
- [Testing Guide](../development/TESTING.md) - Automated testing details
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions

---

**Last Updated:** March 3, 2026  
**Status:** Updated with Bank-5 importer and enhanced test data (1000+ transactions)

