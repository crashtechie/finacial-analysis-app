# Testing Guide

Comprehensive guide to testing the Financial Analysis API.

## Table of Contents
- [Overview](#overview)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Writing Tests](#writing-tests)
- [Coverage Analysis](#coverage-analysis)
- [Advanced Testing](#advanced-testing)

---

## Overview

The project uses **two testing frameworks**:

1. **Django TestCase** (Primary) - Best for model and view testing
2. **pytest** (Secondary) - Supports additional features and integration tests

### Test Coverage

- **Current Coverage: 75%** (1,028 statements, 1028 lines tested)
- **70+ tests** covering:
  - Models (Institution, Account, Category, Transaction, ImportLog)
  - API endpoints (C RUD operations)
  - Utilities (formatting, date calculations)
  - Admin interface
  - Edge cases
  - Analytics endpoints

---

## Running Tests

### Quick Start

```bash
cd app/backend

# Run all tests
uv run python manage.py test api.tests

# Run with pytest (shows coverage)
uv run pytest --cov=api api/tests.py

# Quick summary
uv run pytest api/tests.py -q
```

### Run Specific Tests

```bash
# Run specific test class
uv run python manage.py test api.tests.InstitutionModelTests

# Run specific test method
uv run python manage.py test api.tests.InstitutionModelTests.test_institution_creation

# Run tests matching pattern
uv run python manage.py test api.tests -k FormatterUtilityTests
```

### Test Output Options

```bash
# Verbose output (level 2 = very detailed)
uv run python manage.py test api.tests -v 2

# Quiet output
uv run python manage.py test api.tests -q

# Show test discovery
uv run python manage.py test api.tests --debug-mode
```

### Pass/Fail Summary

```
======================================================================
Ran 70 tests in 0.088s

OK
```

---

## Test Structure

### Main Test File: `api/tests.py`

```
InstitutionModelTests (4 tests)
├── test_institution_creation
├── test_institution_str
├── test_institution_delete
└── test_institution_duplicate_identifier

AccountModelTests (5 tests)
├── test_account_creation
├── test_account_with_institution
├── test_account_str
├── test_account_balance_calculation
└── test_account_number_uniqueness_per_institution

... [and 60+ more tests]

FormatterUtilityTests (14 tests)
├── test_format_currency_positive
├── test_format_currency_negative
├── test_format_percentage
└── [11 more tests]

TransactionEdgeCasesTests (11 tests)
├── test_transaction_with_zero_amount
├── test_transaction_with_large_amount
└── [9 more tests]
```

### Pytest Structure: `tests/` (Supplementary)

```
tests/
├── conftest.py           # Pytest configuration
├── unit/                 # Unit test modules
│   ├── test_models.py
│   ├── test_serializers.py
│   └── test_utils.py
├── integration/          # Integration tests
│   └── test_api.py
└── fixtures/            # Test data factories
    └── factory.py
```

---

## Writing Tests

### Basic Model Test

```python
from django.test import TestCase
from decimal import Decimal
from .models import Institution, Account

class AccountModelTests(TestCase):
    """Tests for Account model"""
    
    def setUp(self):
        """Create test data before each test"""
        self.institution = Institution.objects.create(
            name="Test Bank",
            identifier="testbank"
        )
    
    def test_account_creation(self):
        """Test creating an account"""
        account = Account.objects.create(
            institution=self.institution,
            name="Checking",
            account_number="1234",
            account_type="checking"
        )
        
        self.assertEqual(account.name, "Checking")
        self.assertEqual(account.account_type, "checking")
        self.assertEqual(account.institution, self.institution)
    
    def test_account_balance_calculation(self):
        """Test balance calculation from transactions"""
        account = Account.objects.create(
            institution=self.institution,
            name="Checking",
            account_number="1234"
        )
        
        # Add transactions
        Category.objects.create(name="Test", slug="test")
        category = Category.objects.get(slug="test")
        
        Transaction.objects.create(
            account=account,
            date=timezone.now().date(),
            description="Deposit",
            amount=Decimal("100.00"),
            category=category,
            status="cleared"
        )
        
        # Check balance
        self.assertEqual(account.get_balance(), Decimal("100.00"))
```

### API Endpoint Test

```python
from rest_framework.test import APITestCase

class InstitutionAPITests(APITestCase):
    """Tests for Institution API endpoints"""
    
    def setUp(self):
        self.institution = Institution.objects.create(
            name="Bank-1",
            identifier="bank-1"
        )
    
    def test_list_institutions(self):
        """Test listing institutions"""
        response = self.client.get('/api/institutions/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Bank-1')
    
    def test_create_institution(self):
        """Test creating an institution"""
        response = self.client.post('/api/institutions/', {
            'name': 'Bank-2',
            'identifier': 'bank-2'
        })
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Institution.objects.count(), 2)
    
    def test_retrieve_institution(self):
        """Test retrieving single institution"""
        response = self.client.get(f'/api/institutions/{self.institution.id}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Bank-1')
```

### Test Model Methods

```python
def test_transaction_is_expense(self):
    """Test expense detection"""
    expense = Transaction(amount=Decimal("-50.00"))
    income = Transaction(amount=Decimal("100.00"))
    
    self.assertTrue(expense.is_expense)
    self.assertFalse(income.is_expense)
    self.assertFalse(expense.is_income)
    self.assertTrue(income.is_income)
```

### Test Validation

```python
def test_unique_constraint_violation(self):
    """Test that unique constraints are enforced"""
    Institution.objects.create(
        name="Bank-1",
        identifier="bank-1"
    )
    
    from django.db import IntegrityError
    with self.assertRaises(IntegrityError):
        Institution.objects.create(
            name="Bank-1 Second",
            identifier="bank-1"  # Duplicate identifier
        )
```

### Test Filtering and Search

```python
def test_filter_transactions_by_category(self):
    """Test filtering transactions by category"""
    category1 = Category.objects.create(name="Food", slug="food")
    category2 = Category.objects.create(name="Gas", slug="gas")
    
    food_trans = Transaction.objects.create(
        account=self.account,
        date=timezone.now().date(),
        description="Restaurant",
        amount=Decimal("-25.00"),
        category=category1,
        status="cleared"
    )
    
    gas_trans = Transaction.objects.create(
        account=self.account,
        date=timezone.now().date(),
        description="Shell",
        amount=Decimal("-40.00"),
        category=category2,
        status="cleared"
    )
    
    # Filter
    response = self.client.get('/api/transactions/?category=food')
    
    self.assertEqual(len(response.data['results']), 1)
    self.assertEqual(response.data['results'][0]['description'], 'Restaurant')
```

---

## Coverage Analysis

### Generate Coverage Report

```bash
# Generate HTML report
uv run pytest --cov=api --cov-report=html api/tests.py

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Terminal report with missing lines
uv run pytest --cov=api --cov-report=term-missing api/tests.py
```

### Current Coverage Status

| Module | Coverage | Status |
|--------|----------|--------|
| api/models.py | 98% | ✅ Excellent |
| api/serializers.py | 92% | ✅ Excellent |
| api/formatters.py | 100% | ✅ Perfect |
| api/utils/formatters.py | 100% | ✅ Perfect |
| api/analytics/views.py | 71% | 🟡 Good |
| api/views.py | 72% | 🟡 Good |
| api/admin.py | 80% | ✅ Excellent |
| api/utils/date_helpers.py | 58% | 🟡 Fair |
| api/importers/*.py | 0% | ❌ None |

### Improve Coverage

```bash
# Identify missing coverage
uv run pytest --cov=api --cov-report=term-missing api/tests.py | grep -A2 "Missing"

# Add tests for missing lines
# Edit api/tests.py and add test methods
# Re-run to verify improvement
uv run pytest --cov=api api/tests.py
```

---

## Advanced Testing

### Mocking External Calls

```python
from unittest.mock import patch
import requests

@patch('requests.get')
def test_external_api_call(self, mock_get):
    """Test with mocked external API"""
    # Setup mock
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'data': 'value'}
    
    # Test code that calls requests.get
    result = external_function()
    
    # Verify
    mock_get.assert_called_once_with('http://api.example.com')
    self.assertEqual(result['data'], 'value')
```

### Testing Database Transactions

```python
from django.test import TransactionTestCase

class DatabaseTransactionTests(TransactionTestCase):
    """Tests requiring transaction support"""
    
    def test_transaction_rollback(self):
        """Test transaction behavior"""
        from django.db import transaction
        
        try:
            with transaction.atomic():
                Institution.objects.create(name="test")
                raise Exception("Simulated error")
        except Exception:
            pass
        
        # Transaction rolled back
        self.assertEqual(Institution.objects.count(), 0)
```

### Testing Celery Tasks (if added)

```python
@override_settings(CELERY_ALWAYS_EAGER=True)
def test_async_task(self):
    """Test Celery task executes immediately"""
    from myapp.tasks import process_data
    
    result = process_data.delay(arg1, arg2)
    
    self.assertEqual(result.status, 'SUCCESS')
```

### Parameterized Tests

```python
import pytest

@pytest.mark.parametrize("amount,expected_sign", [
    ("100.00", "+"),
    ("-50.00", "-"),
    ("0.00", " "),
])
def test_sign_formatting(amount, expected_sign):
    """Test sign formatting for various amounts"""
    result = format_with_sign(amount)
    assert expected_sign in result
```

### Test Fixtures and Factories

```python
# Using factory_boy (if configured)
from factory import Factory, SubFactory
from api.models import Institution, Account

class InstitutionFactory(Factory):
    class Meta:
        model = Institution
    
    name = "Test Bank"
    identifier = "testbank"

class AccountFactory(Factory):
    class Meta:
        model = Account
    
    institution = SubFactory(InstitutionFactory)
    name = "Checking"
    account_number = "1234567890"

# Use in tests
def test_with_factory(self):
    account = AccountFactory()
    self.assertEqual(account.name, "Checking")
```

---

## Best Practices

### ✅ Do

```python
# Clear test names describing what's tested
def test_transaction_with_negative_amount_is_expense(self):
    pass

# Use setUp for common test data
def setUp(self):
    self.institution = Institution.objects.create(...)

# Test one thing per test method
def test_account_creation(self):
    # Only test account creation, not balance calculation

# Use assertions clearly
self.assertEqual(account.balance, Decimal("100.00"))
self.assertTrue(transaction.is_expense)

# Test edge cases and errors
def test_invalid_date_format(self):
    with self.assertRaises(ValueError):
        parse_date("invalid")
```

### ❌ Avoid

```python
# Generic test names
def test_model(self):  # ✗ Too vague
    pass

# Testing multiple things
def test_account(self):  # Tests creation, balance, and delete

# Creating unnecessary test data in each test
def setUp(self):
    for i in range(100):
        Institution.objects.create(...)

# Ignoring test failures
def test_something(self):
    result = dangerous_operation()  # What if this fails?

# Testing implementation details
def test_balance_uses_sum_queryset(self):  # Implementation detail
    pass
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.14
      
      - name: Install dependencies
        run: |
          pip install uv
          cd app/backend && uv sync --all-extras
      
      - name: Run tests
        run: |
          cd app/backend
          python manage.py test api.tests
```

---

## Continuous Testing

### Watch Mode (Run tests on file changes)

```bash
# Using pytest-watch
pip install pytest-watch

# Run tests on any file change
ptw -- --cov=api api/tests.py
```

### Run Tests Before Commit

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
cd app/backend
uv run python manage.py test api.tests
if [ $? -ne 0 ]; then
  echo "Tests failed. Commit aborted."
  exit 1
fi
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Debugging Tests

### Run Test with Full Output

```bash
uv run python manage.py test api.tests -v 2

# Get SQL queries
uv run python manage.py test api.tests --debug-mode
```

### Add Breakpoints

```python
def test_something(self):
    result = calculate()
    breakpoint()  # Pauses execution
    self.assertEqual(result, expected)
```

Run with:
```bash
uv run python manage.py test api.tests --failfast --pdb
```

### Print Debug Information

```python
def test_transaction_creation(self):
    transaction = Transaction.objects.create(...)
    
    # Debug prints
    print(f"Transaction ID: {transaction.id}")
    print(f"Amount: {transaction.amount}")
    print(f"Hash: {transaction.transaction_hash}")
    
    self.assertEqual(transaction.amount, Decimal("100.00"))
```

---

## Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [pytest Documentation](https://docs.pytest.org/)
- [Project Tests](../../api/tests.py)
