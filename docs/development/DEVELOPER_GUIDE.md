# Developer Guide

Guide for extending and contributing to the Financial Analysis API.

## Table of Contents
- [Project Structure](#project-structure)
- [Adding New Data Models](#adding-new-data-models)
- [Creating New API Endpoints](#creating-new-api-endpoints)
- [Adding New Importers](#adding-new-importers)
- [Writing Tests](#writing-tests)
- [Code Style and Quality](#code-style-and-quality)
- [Common Development Tasks](#common-development-tasks)

---

## Project Structure

```
app/backend/
├── manage.py                      # Django management script
├── pyproject.toml                 # Project configuration and dependencies
├── pytest.ini                     # Pytest configuration
├── db.sqlite3                     # Development database
├── .env                          # Environment variables (create from .env.example)
├── .env.example                  # Example environment configuration
│
├── financial_analysis/            # Django project settings
│   ├── settings.py               # Django configuration
│   ├── urls.py                   # Main URL routing
│   ├── asgi.py                   # ASGI config for production
│   └── wsgi.py                   # WSGI config for production
│
├── api/                          # Main application
│   ├── models.py                 # Data models (Institution, Account, etc.)
│   ├── views.py                  # API views
│   ├── serializers.py            # DRF serializers
│   ├── admin.py                  # Django admin configuration
│   ├── urls.py                   # API URL routing
│   ├── tests.py                  # Comprehensive test suite (70+ tests)
│   │
│   ├── utils/                    # Utility modules
│   │   ├── formatters.py         # Currency, percentage formatting
│   │   └── date_helpers.py       # Date range, period calculations
│   │
│   ├── importers/                # CSV/PDF import handlers
│   │   ├── base.py               # Abstract base importer
│   │   └── bank_1.py             # Bank-1 format importer
│   │
│   ├── analytics/                # Analytics endpoints
│   │   ├── views.py              # Analytics API views
│   │   ├── serializers.py        # Analytics data serializers
│   │   └── urls.py               # Analytics routing
│   │
│   ├── management/               # CLI management commands
│   │   └── commands/
│   │       └── import_transactions.py  # Import CLI command
│   │
│   ├── fixtures/                 # Initial data
│   │   ├── categories.json      # Default categories
│   │   ├── institutions.json    # Sample institutions
│   │   ├── accounts.json        # Sample accounts
│   │   ├── transactions.json    # Sample transactions
│   │   └── import_logs.json     # Sample import logs
│   │
│   └── migrations/               # Database migrations
│       └── 0001_initial.py
│
├── tests/                        # Pytest-based testing (supplementary)
│   ├── conftest.py              # Pytest configuration
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data factories
│
└── scripts/                      # Utility scripts
    └── setup_dev_data.sh         # Setup development data
```

---

## Adding New Data Models

### Step 1: Define the Model

Edit `api/models.py`:

```python
from django.db import models
from django.contrib.auth.models import User

class BudgetCategory(models.Model):
    """User-defined budget limits for categories"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    monthly_limit = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'category')
        verbose_name_plural = "Budget Categories"
        indexes = [
            models.Index(fields=['user', 'category']),
        ]
    
    def __str__(self):
        return f"{self.category.name} - ${self.monthly_limit}"
```

### Step 2: Create and Run Migration

```bash
# Create migration file
python manage.py makemigrations

# Apply to database
python manage.py migrate

# Verify
python manage.py showmigrations
```

### Step 3: Register in Admin (if needed)

Edit `api/admin.py`:

```python
@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ['category', 'user', 'monthly_limit', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['user__username', 'category__name']
    readonly_fields = ['created_at', 'updated_at']
```

### Step 4: Write Model Tests

Add to `api/tests.py`:

```python
class BudgetCategoryModelTests(TestCase):
    """Tests for BudgetCategory model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.category = Category.objects.create(
            name='Groceries',
            slug='groceries'
        )
    
    def test_budget_creation(self):
        """Test creating a budget category"""
        budget = BudgetCategory.objects.create(
            user=self.user,
            category=self.category,
            monthly_limit=Decimal('500.00')
        )
        self.assertEqual(budget.monthly_limit, Decimal('500.00'))
    
    def test_unique_constraint(self):
        """Test duplicate user-category combinations are rejected"""
        BudgetCategory.objects.create(
            user=self.user,
            category=self.category,
            monthly_limit=Decimal('500.00')
        )
        with self.assertRaises(IntegrityError):
            BudgetCategory.objects.create(
                user=self.user,
                category=self.category,
                monthly_limit=Decimal('600.00')
            )
```

---

## Creating New API Endpoints

### Step 1: Create Serializer

Edit `api/serializers.py`:

```python
from rest_framework import serializers
from .models import BudgetCategory

class BudgetCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = BudgetCategory
        fields = ['id', 'category', 'category_name', 'monthly_limit', 'created_at']
        read_only_fields = ['created_at']
```

### Step 2: Create ViewSet

Edit `api/views.py`:

```python
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

class BudgetCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for budget categories.
    
    list - Get all budgets for current user
    create - Create new budget
    retrieve - Get specific budget
    update - Update budget
    destroy - Delete budget
    """
    serializer_class = BudgetCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only return budgets for current user"""
        return BudgetCategory.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Automatically set user to current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def exceeded(self, request):
        """Get budgets exceeded this month"""
        from datetime import date
        from django.db.models import Sum
        
        budgets = self.get_queryset()
        exceeded = []
        
        for budget in budgets:
            spent = budget.category.transactions.filter(
                date__month=date.today().month
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            if abs(spent) > budget.monthly_limit:
                exceeded.append({
                    'budget_id': budget.id,
                    'category': budget.category.name,
                    'limit': str(budget.monthly_limit),
                    'spent': str(spent),
                    'over_by': str(abs(spent) - budget.monthly_limit)
                })
        
        return Response(exceeded)
```

### Step 3: Register in Router

Edit `api/urls.py`:

```python
from rest_framework.routers import DefaultRouter
from .views import (
    InstitutionViewSet,
    AccountViewSet,
    CategoryViewSet,
    TransactionViewSet,
    ImportLogViewSet,
    BudgetCategoryViewSet,  # Add this
)

router = DefaultRouter()
router.register('institutions', InstitutionViewSet, basename='institution')
router.register('accounts', AccountViewSet, basename='account')
router.register('categories', CategoryViewSet, basename='category')
router.register('transactions', TransactionViewSet, basename='transaction')
router.register('import-logs', ImportLogViewSet, basename='import-log')
router.register('budgets', BudgetCategoryViewSet, basename='budget')  # Add this

urlpatterns = router.urls
```

### Step 4: Test the Endpoint

```bash
# Start server
python manage.py runserver

# In another terminal
curl -X GET http://localhost:8000/api/budgets/
```

---

## Adding New Importers

Bank-specific importers handle different CSV/PDF formats.

### Step 1: Create Importer Class

Create `api/importers/bank_2.py`:

```python
from decimal import Decimal
from datetime import datetime
from .base import BaseImporter, ImporterRegistry

@ImporterRegistry.register('bank-2')
class Bank2Importer(BaseImporter):
    """Import transactions from Bank-2 CSV format"""
    
    EXPECTED_HEADERS = ['Transaction Date', 'Post Date', 'Description', 'Amount']
    
    def parse_date(self, date_str):
        """Parse Bank-2 date format: MM/DD/YYYY"""
        return datetime.strptime(date_str, '%m/%d/%Y').date()
    
    def import_transactions(self, file_handle, account):
        """Import transactions from Bank-2 CSV"""
        import csv
        
        reader = csv.DictReader(file_handle)
        
        # Validate headers
        if not all(h in reader.fieldnames for h in self.EXPECTED_HEADERS):
            raise ValueError(f"Invalid headers. Expected: {self.EXPECTED_HEADERS}")
        
        transactions = []
        for row in reader:
            # Parse transaction data
            date = self.parse_date(row['Transaction Date'])
            description = row['Description'].strip()
            amount = Decimal(row['Amount'])
            
            # Create transaction
            from ..models import Transaction
            transaction = Transaction(
                account=account,
                date=date,
                description=description,
                amount=amount,
                status='pending'
            )
            transactions.append(transaction)
        
        return self.create_transactions(transactions, account)
```

### Step 2: Register and Test

The registry decorator automatically registers it:

```python
# Use the importer
from api.importers.bank_2 import Bank2Importer

with open('bank-2.csv') as f:
    importer = Bank2Importer()
    result = importer.import_transactions(f, account)
    print(f"Imported: {result['imported']}, Skipped: {result['skipped']}")
```

### Step 3: Add to Management Command

Edit `api/management/commands/import_transactions.py`:

```python
# Add Bank-2 to available formats
IMPORTERS = ['bank-1', 'bank-2', 'bank-4']  # Add 'bank-2'
```

### Step 4: Write Tests

```python
class Bank2ImporterTests(TestCase):
    """Tests for Bank-2 importer"""
    
    def setUp(self):
        self.institution = Institution.objects.create(
            name="Bank-2",
            identifier="bank-2"
        )
        self.account = Account.objects.create(
            institution=self.institution,
            name="Bank-2 Checking",
            account_number="1234567890"
        )
    
    def test_parse_date(self):
        """Test date parsing"""
        importer = Bank2Importer()
        date = importer.parse_date('03/01/2026')
        self.assertEqual(date.month, 3)
        self.assertEqual(date.year, 2026)
    
    def test_import_csv(self):
        """Test importing Bank-2 CSV"""
        from io import StringIO
        
        csv_data = StringIO(
            "Transaction Date,Post Date,Description,Amount\n"
            "03/01/2026,03/01/2026,STARBUCKS #12345,5.50\n"
            "03/02/2026,03/02/2026,TARGET #5678,-49.99\n"
        )
        
        importer = Bank2Importer()
        result = importer.import_transactions(csv_data, self.account)
        
        self.assertEqual(result['imported'], 2)
        self.assertEqual(result['skipped'], 0)
```

---

## Writing Tests

### Test Structure

All tests are in `api/tests.py` using Django TestCase:

```python
from django.test import TestCase
from decimal import Decimal

class MyFeatureTests(TestCase):
    """Tests for my new feature"""
    
    def setUp(self):
        """Run before each test"""
        self.institution = Institution.objects.create(
            name="Test Bank",
            identifier="testbank"
        )
    
    def tearDown(self):
        """Run after each test (optional)"""
        pass
    
    def test_something(self):
        """Test description"""
        # Arrange
        account = Account.objects.create(
            institution=self.institution,
            name="Test",
            account_number="1234"
        )
        
        # Act
        result = account.get_balance()
        
        # Assert
        self.assertEqual(result, Decimal('0.00'))
```

### Common Test Patterns

```python
# Model tests
def test_model_creation(self):
    item = MyModel.objects.create(name="test")
    self.assertEqual(item.name, "test")

# Relationship tests
def test_foreign_key(self):
    item = MyModel.objects.create(parent=self.parent)
    self.assertEqual(item.parent, self.parent)

# Validation tests
def test_field_validation(self):
    with self.assertRaises(ValidationError):
        MyModel.objects.create(invalid_field="")

# Database constraints
def test_unique_constraint(self):
    MyModel.objects.create(unique_field="value")
    with self.assertRaises(IntegrityError):
        MyModel.objects.create(unique_field="value")

# API endpoint tests
def test_api_list(self):
    response = self.client.get('/api/items/')
    self.assertEqual(response.status_code, 200)

def test_api_create(self):
    response = self.client.post('/api/items/', {
        'name': 'new item',
        'value': 100
    })
    self.assertEqual(response.status_code, 201)
```

### Run Tests

```bash
# All tests
python manage.py test api.tests

# Specific test class
python manage.py test api.tests.InstitutionModelTests

# Specific test method
python manage.py test api.tests.InstitutionModelTests.test_institution_creation

# With coverage
pytest --cov=api --cov-report=html api/tests.py

# Verbose output
python manage.py test api.tests -v 2
```

---

## Code Style and Quality

### Code Formatting

```bash
# Auto-format code
black api/

# Check import order
isort api/

# Lint code
flake8 api/

# All together
black api/ && isort api/ && flake8 api/
```

### Pre-commit Checks

Before committing:

```bash
# Format
black api/
isort api/

# Check for issues
flake8 api/ --max-line-length=100

# Run tests
python manage.py test api.tests

# Check for migrations
python manage.py makemigrations --check
```

### Type Hints (Optional but Recommended)

```python
from typing import List, Optional
from decimal import Decimal

def calculate_total(amounts: List[Decimal]) -> Decimal:
    """Calculate total of amounts"""
    return sum(amounts)

def get_optional_account(account_id: int) -> Optional[Account]:
    """Get account or None if not found"""
    return Account.objects.filter(id=account_id).first()
```

---

## Common Development Tasks

### Run Development Server

```bash
cd app/backend
python manage.py runserver

# Custom port
python manage.py runserver 0.0.0.0:8001
```

### Interactive Shell

```bash
python manage.py shell

>>> from api.models import *
>>> institutions = Institution.objects.all()
>>> for i in institutions:
...     print(i.name)
>>> exit()
```

### Database Operations

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Rollback migration
python manage.py migrate api 0001
```

### Django Management Commands - Environment Setup

All Django management commands (`manage.py`) must be executed from the correct directory with the proper Python path configuration.

**Working Directory:**
```bash
# Always run from the backend directory
cd app/backend

# Then execute any management command
python manage.py <command>
# Or with uv:
uv run python manage.py <command>
```

**Why This Matters:**
- The `manage.py` script automatically adds the workspace root to `sys.path` to make the `app` package importable
- This is required for Django to resolve the settings module path: `financial_analysis.settings`
- Running from a different directory may cause `ModuleNotFoundError`

**Common Management Commands:**
```bash
python manage.py runserver          # Start dev server
python manage.py makemigrations     # Create migrations
python manage.py migrate            # Apply migrations
python manage.py test api           # Run tests
python manage.py shell              # Interactive shell
python manage.py createsuperuser    # Create admin user
python manage.py import_transactions # Import CSV transactions
```

For details on troubleshooting Django command issues, see [TROUBLESHOOTING.md](../guides/TROUBLESHOOTING.md#django-management-commands).

### Create Django Admin User

```bash
python manage.py createsuperuser
# Then visit http://localhost:8000/admin/
```

### Load Fixtures

```bash
# Load all fixtures (order matters for foreign key dependencies)
python manage.py loaddata institutions accounts categories transactions import_logs

# Load individual fixtures
python manage.py loaddata api/fixtures/categories.json

# Create custom fixture
python manage.py dumpdata api.Category > my_categories.json
python manage.py loaddata my_categories.json
```

### Generate Fake Data

```bash
from factory_boy import Factory
from api.models import Institution

# Create using factories
from api.factories import InstitutionFactory

institutions = [InstitutionFactory() for _ in range(10)]
```

---

## Deploy Your Changes

1. **Test locally:**
   ```bash
   python manage.py test api.tests
   pytest --cov=api api/tests.py
   ```

2. **Format code:**
   ```bash
   black api/ && isort api/ && flake8 api/
   ```

3. **Commit changes:**
   ```bash
   git add api/
   git commit -m "Add BudgetCategory feature"
   ```

4. **Push to GitHub:**
   ```bash
   git push origin feature/budget-category
   ```

5. **Create Pull Request** on GitHub

---

## Further Reading

- [Project Architecture](../architecture/SYSTEM_DESIGN.md)
- [Database Schema](../architecture/DATABASE_SCHEMA.md)
- [API Reference](../API_REFERENCE.md)
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
