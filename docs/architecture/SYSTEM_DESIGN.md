# System Design and Architecture

Comprehensive documentation of the Financial Analysis API architecture, design patterns, and system structure.

## Table of Contents
- [High-Level Architecture](#high-level-architecture)
- [System Components](#system-components)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Directory Structure](#directory-structure)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client Applications                         │
│              (Web Frontend, Mobile, Third-party Apps)          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REST API Gateway                             │
│              (Django REST Framework DRF)                        │
│  • Request routing and serialization                            │
│  • CORS headers and authentication                              │
│  • Pagination and filtering                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
        ┌──────────────┐ ┌──────────┐ ┌─────────┐
        │ Transaction  │ │Analytics │ │Importer │
        │ Management   │ │ Engine   │ │ System  │
        └─────┬────────┘ └────┬─────┘ └────┬────┘
              │               │            │
              └───────────┬───┴────┬───────┘
                          ▼        ▼
        ┌─────────────────────────────────────────┐
        │      Django ORM / SQLAlchemy Layer      │
        │        • Model validation                │
        │        • Query optimization              │
        │        • Relationship management         │
        └──────────────────┬──────────────────────┘
                           ▼
        ┌─────────────────────────────────────────┐
        │      SQLite Database                    │
        │    (Can be replaced with PostgreSQL)    │
        │                                         │
        │  institution, account, category,       │
        │  transaction, import_log tables        │
        └─────────────────────────────────────────┘
```

---

## System Components

### 1. API Layer (REST Framework)

**File:** `api/views.py`, `api/urls.py`

Handles HTTP requests and returns JSON responses.

```python
# Endpoint structure
/api/
  ├── institutions/          # CRUD: banks, credit card companies
  ├── accounts/              # CRUD: checking, savings, credit accounts
  ├── categories/            # CRUD: expense categories
  ├── transactions/          # CRUD: individual transactions
  ├── import-logs/           # READ: import operation history
  └── analytics/
      ├── spending-trends/   # Time-series spending data
      ├── category-breakdown/ # Spending by category
      ├── merchant-analysis/ # Top merchants
      └── spending-trends/   # Period-based comparisons
```

**Key Features:**
- Pagination (50 items/page default)
- Filtering (date range, amount, category)
- Search (descriptions, merchants)
- Ordering (date, amount, institution)
- Browsable API interface

### 2. Data Models Layer

**File:** `api/models.py`

Core domain models representing financial entities.

```
Institution
  ├── name: str              • Bank or credit company name
  ├── identifier: str        • Unique identifier (bank-1, bank-2, bank-4)
  └── accounts: FK[]         • Related accounts
      │
      └─→ Account
          ├── name: str      • Account nickname
          ├── account_number • Account identifier
          ├── account_type   • checking, savings, credit, etc.
          ├── balance        • Calculated from transactions
          └── transactions: FK[]
              │
              └─→ Transaction
                  ├── date: date
                  ├── description: str
                  ├── amount: Decimal
                  ├── category: FK → Category
                  ├── status: pending/posted/cleared
                  ├── transaction_hash: unique hash for deduplication
                  └── ImportLog relationship

Category
  ├── name: str
  ├── slug: str
  ├── parent: FK (self)      • For hierarchical categories
  └── transactions: FK[]

ImportLog
  ├── account: FK
  ├── file_name: str
  ├── format_type: str       • csv, pdf, ofx, etc.
  ├── status: pending/successful/failed
  ├── records_processed/imported/skipped
  ├── started_at, completed_at timestamps
  └── error_message: str (if failed)
```

### 3. Serializers Layer

**File:** `api/serializers.py`

Converts between Python objects and JSON.

```python
InstitutionSerializer
  ├── id, name, identifier (read-only: account_count)
  
AccountSerializer
  ├── id, institution, name, account_number, account_type
  ├── read-only: balance, transaction_count
  
TransactionSerializer
  ├── id, account, date, description, amount, category, status
  ├── merchant (extracted from description)
  
AnalyticsSerializer (for complex responses)
  └── Aggregated spending data
```

### 4. Utility Functions

**Directory:** `api/utils/`

#### Formatters (`formatters.py`)
```python
format_currency(100.50)           # → "$100.50"
format_percentage(45.678)         # → "45.68%"
format_change(150, 100)           # → {'direction': 'up', 'amount': 50, 'pct': 50%}
format_number_abbreviated(1500)   # → "1.5K"
```

#### Date Helpers (`date_helpers.py`)
```python
get_date_range('week')            # → (start_date, end_date)
get_date_range('month')
get_date_range('quarter')
get_date_range('year')
get_date_range('custom', start, end)
```

### 5. Importer System

**Directory:** `api/importers/`

Extensible architecture for importing transactions from various bank formats.

```python
BaseImporter (Abstract)
  ├── parse_date()
  ├── import_transactions()
  └── create_transactions()
      
└─→ ConcreteImporters:
    ├── Bank1Importer
    ├── Bank2Importer (future)
    ├── Bank4Importer (future)
    └── [Add more as needed]
```

**Design Pattern Used:** Registry Pattern

```python
@ImporterRegistry.register('bank-1')
class Bank1Importer(BaseImporter):
    # Implementation
    pass

# Usage
importer = ImporterRegistry.get('bank-1')
result = importer.import_transactions(file, account)
```

### 6. Analytics Engine

**Directory:** `api/analytics/`

Computes advanced financial metrics.

```
ViewSets (api/analytics/views.py)
  ├── SpendingTrendsView
  │   ├── Daily aggregation
  │   ├── Weekly aggregation
  │   └── Monthly aggregation
  │
  ├── CategoryBreakdownView
  │   ├── Total by category
  │   ├── Percentage of total
  │   └── Trend comparison
  │
  ├── MerchantAnalysisView
  │   ├── Top merchants by frequency
  │   ├── Top merchants by spending
  │   └── Merchant patterns
  │
  └── SpendingComparisonView
      ├── Period-over-period comparison
      ├── Category trends
      └── Variance analysis
```

---

## Data Flow

### 1. Transaction Import Flow

```
CSV File
   ↓
[FileUpload or CLI]
   ↓
ImporterRegistry.get('institution_type')
   ↓
Parser (institution-specific format)
   ├── Validate format/headers
   ├── Parse each row
   ├── Generate transaction_hash
   └── Check for duplicates
   ↓
Transaction Validation
   ├── Required fields
   ├── Data type conversion
   └── Amount validation
   ↓
Database Storage
   ├── INSERT transactions
   ├── Update ImportLog
   └── Calculate account balance
   ↓
Response
   └── {"imported": 1542, "skipped": 12, "errors": [...]}
```

### 2. API Request/Response Flow

```
Client Request
   ↓
URL Router (urls.py)
   └─→ Route to correct ViewSet
   ↓
Permission.check()
   └─→ Check authentication/permissions
   ↓
Query Database
   ├── Filter (if parameters provided)
   ├── Order (if requested)
   └── Paginate (if applicable)
   ↓
Serialize Data (Serializer)
   ├── Convert QuerySet → dict
   ├── Include related objects
   └── Add computed fields
   ↓
JSON Response
   ├── 200: Success with data
   ├── 400: Bad request
   ├── 401: Unauthorized
   └── 500: Server error
```

### 3. Analytics Calculation Flow

```
Request: /api/analytics/spending-trends/?period=monthly
   ↓
Parse Parameters
   ├── period, start_date, end_date
   ├── category_filter
   └── account_filter
   ↓
Database Query
   └─→ SELECT SUM(amount) BY DATE for each period
   ↓
Aggregate Results
   ├── Group by category
   ├── Calculate totals
   └── Format for display
   ↓
Serialize Analytics Response
   └─→ Include charts, percentages, comparisons
   ↓
JSON Response
   └─→ {
         "periods": [
           {"date": "2026-03", "total": -1234.56, "by_category": {...}},
           ...
         ]
       }
```

---

## Design Patterns

### 1. Registry Pattern (Importers)

```python
# Define registry
class ImporterRegistry:
    _importers = {}
    
    @classmethod
    def register(cls, name):
        def decorator(importer_class):
            cls._importers[name] = importer_class
            return importer_class
        return decorator
    
    @classmethod
    def get(cls, name):
        return cls._importers[name]

# Register implementations
@ImporterRegistry.register('bank-1')
class Bank1Importer(BaseImporter):
    pass

# Use
importer_class = ImporterRegistry.get('bank-1')
importer = importer_class()
```

**Benefits:**
- Easy to add new importers
- No changes to existing code needed
- Runtime selection of importer

### 2. Factory Pattern (Model Creation)

```python
# In tests, use factories to create test data
from factory import Factory

class InstitutionFactory(Factory):
    class Meta:
        model = Institution
    
    name = "Test Bank"
    identifier = "testbank"

# Usage
institution = InstitutionFactory()
```

### 3. Query Optimization Pattern

```python
# Use select_related for ForeignKey relationships
accounts = Account.objects.select_related('institution')

# Use prefetch_related for reverse ForeignKey and M2M
accounts = Account.objects.prefetch_related('transactions')

# Combined
transactions = Transaction.objects.select_related(
    'account__institution',
    'category'
).prefetch_related('import_logs')
```

### 4. Pagination Pattern

```python
# REST Framework handles automatically
class PaginationSettings(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000
```

---

## Directory Structure

```
app/backend/
├── manage.py                      # Django CLI
├── pyproject.toml                 # Dependencies and config
├── pytest.ini                     # Pytest configuration
├── .env                          # Environment variables
├── .env.example                  # Example environment
├── db.sqlite3                    # Development database
│
├── financial_analysis/            # Project settings
│   ├── settings.py               # Django configuration
│   │   ├── INSTALLED_APPS
│   │   ├── MIDDLEWARE
│   │   ├── DATABASES
│   │   ├── REST_FRAMEWORK settings
│   │   └── CORS settings
│   ├── urls.py                   # Main URL routing
│   ├── asgi.py                   # Async server config
│   └── wsgi.py                   # WSGI server config
│
├── api/                          # Main app
│   ├── models.py                 # 5 data models (98% test coverage)
│   ├── views.py                  # 5 ViewSets (72% coverage)
│   ├── serializers.py            # 7 Serializers (92% coverage)
│   ├── admin.py                  # Admin configuration (80% coverage)
│   ├── urls.py                   # URL routing
│   ├── tests.py                  # 70+ comprehensive tests
│   │
│   ├── utils/
│   │   ├── formatters.py         # Currency/percent formatting (100% coverage)
│   │   └── date_helpers.py       # Date calculations (58% coverage)
│   │
│   ├── importers/                # Bank import handlers
│   │   ├── base.py               # Abstract base importer
│   │   └── bank_1.py             # Bank-1 CSV importer
│   │
│   ├── analytics/                # Advanced analytics
│   │   ├── views.py              # Analytics endpoints (71% coverage)
│   │   ├── serializers.py        # Analytics data formatting
│   │   └── urls.py               # Analytics routing
│   │
│   ├── management/               # CLI commands
│   │   └── commands/
│   │       └── import_transactions.py  # Import command
│   │
│   ├── fixtures/                 # Initial data
│   │   ├── categories.json      # Default transaction categories
│   │   ├── institutions.json    # Sample institutions
│   │   ├── accounts.json        # Sample accounts
│   │   ├── transactions.json    # Sample transactions
│   │   └── import_logs.json     # Sample import logs
│   │
│   └── migrations/               # Database migrations
│       └── 0001_initial.py       # Initial schema
│
├── tests/                        # Pytest-based testing (supplementary)
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data factories
│
└── scripts/                      # Utility scripts
    └── setup_dev_data.sh         # Development data setup
```

---

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.14.3 | Core runtime |
| **Web Framework** | Django | 5.2+ | Web server and ORM |
| **API Framework** | Django REST Framework | 3.14+ | REST API implementation |
| **Database** | SQLite | 3.x | Data persistence (default; PostgreSQL, MySQL, MariaDB also supported) |
| **Package Manager** | uv | Latest | Fast dependency management |
| **Testing** | pytest, Django TestCase | Latest | Test execution and validation |
| **Code Quality** | black, flake8, isort | Latest | Code formatting and linting |
| **Data Processing** | pandas | 2.2+ | CSV parsing, data analysis |
| **Data Format** | python-dateutil | 2.8+ | Date/time parsing |
| **Config Management** | python-dotenv | 1.0+ | Environment configuration |
| **CORS Support** | django-cors-headers | 4.3+ | Cross-origin requests |
| **Filtering** | django-filter | 24.0+ | Advanced query filtering |

---

## API Design Principles

1. **RESTful**: Standard HTTP methods (GET, POST, PUT, DELETE)
2. **Stateless**: No session data stored server-side
3. **Versioned**: API can be versioned in URLs or headers
4. **Consistent**: Standard response format for all endpoints
5. **Discoverable**: Browsable API with schema
6. **Paginated**: Large result sets automatically paginated
7. **Filterable**: Query parameters for filtering and search
8. **Documented**: Inline code documentation and API reference

---

## Security Considerations

### Current Development Setup

```python
# In settings.py
DEBUG = True                               # Only for development
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # For development
    ]
}

CORS_ALLOW_ALL_ORIGINS = True  # For development only
```

### Production Recommendations

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'strong-random-key'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
]

# Add authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}
```

---

## Deployment Architecture (Future)

```
┌─────────────────┐
│   Users/Clients │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  Load Balancer      │
│  (nginx)            │
└────────┬────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Gunicorn│ │Gunicorn│ (Multiple instances)
│ App 1   │ │ App 2  │
└────┬───┘ └────┬───┘
     │         │
     └────┬────┘
          ▼
    ┌──────────────┐
    │ PostgreSQL   │ (Production database)
    │ Database     │
    └──────────────┘
    
    ┌──────────────┐
    │ Redis Cache  │ (Optional)
    └──────────────┘
```

---

## Scalability Considerations

### Current Limitations (SQLite)
- Single connection (good for dev)
- File locking (OK for <100 concurrent users)
- No distributed transactions

### Scaling to PostgreSQL

1. **Database**: SQLite → PostgreSQL
2. **Caching**: Add Redis for query caching
3. **Async**: Add Celery for long-running imports
4. **Load Balancing**: Multiple app instances behind nginx
5. **API Gateway**: Kong or API Gateway for rate limiting

---

## Further Reading

- [Database Schema](DATABASE_SCHEMA.md)
- [API Reference](../API_REFERENCE.md)
- [Developer Guide](../development/DEVELOPER_GUIDE.md)
- [Django Architecture](https://docs.djangoproject.com/en/stable/intro/overview/)
