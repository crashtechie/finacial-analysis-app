# Database Schema Reference

Complete reference for all database tables, fields, relationships, and constraints.

## Table of Contents
- [Overview](#overview)
- [Institutions Table](#institutions-table)
- [Accounts Table](#accounts-table)
- [Categories Table](#categories-table)
- [Transactions Table](#transactions-table)
- [Import Logs Table](#import-logs-table)
- [Relationships Diagram](#relationships-diagram)
- [Indexes and Constraints](#indexes-and-constraints)

---

## Overview

The database contains 5 main tables representing financial data entities:

| Table | Purpose | Records | Example Data |
|-------|---------|---------|--------------|
| `api_institution` | Banks and financial institutions | ~5-10 | Bank-1, Bank-2, Bank-4 |
| `api_account` | Individual accounts | ~20-50 | Checking, Savings, Credit Cards |
| `api_category` | Transaction categories (hierarchical) | ~30-50 | Food, Gas, Utilities |
| `api_transaction` | Individual transactions | ~10K-100K | Grocery stores, restaurant, ATM |
| `api_importlog` | Import job history | ~100-1000 | CSV import logs, status |

---

## Institutions Table

**Table Name:** `api_institution`

**Purpose:** Store financial institutions (banks, credit card companies)

### Schema

```sql
CREATE TABLE api_institution (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  name            VARCHAR(200) NOT NULL UNIQUE,
  identifier      VARCHAR(50) NOT NULL UNIQUE,
  created_at      DATETIME NOT NULL
);
```

### Column Details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-incrementing unique identifier |
| `name` | VARCHAR(200) | NOT NULL, UNIQUE | Institution display name (e.g., "Bank-1") |
| `identifier` | VARCHAR(50) | NOT NULL, UNIQUE | Machine-readable ID (e.g., "bank-1") - used by importers |
| `created_at` | DATETIME | NOT NULL | Record creation timestamp |

### Example Records

```sql
INSERT INTO api_institution VALUES
(1, 'Bank-1', 'bank-1', '2026-03-01 10:00:00'),
(2, 'Bank-2', 'bank-2', '2026-03-01 10:00:00'),
(3, 'Bank-4', 'bank-4', '2026-03-01 10:00:00');
```

### Relationships

- **One Institution** → **Many Accounts** (1:N)
- Referenced by: `api_account.institution_id`

### Usage

```python
# Get institution
institution = Institution.objects.get(identifier='bank-1')

# Get all accounts for institution
accounts = institution.accounts.all()

# Count accounts
account_count = institution.accounts.count()
```

---

## Accounts Table

**Table Name:** `api_account`

**Purpose:** Store individual financial accounts (checking, savings, credit cards)

### Schema

```sql
CREATE TABLE api_account (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  institution_id  INTEGER NOT NULL,
  name            VARCHAR(200) NOT NULL,
  account_number  VARCHAR(50) NOT NULL,
  account_type    VARCHAR(20) NOT NULL,
  created_at      DATETIME NOT NULL,
  updated_at      DATETIME NOT NULL,
  FOREIGN KEY (institution_id) REFERENCES api_institution(id),
  UNIQUE (institution_id, account_number)
);
```

### Column Details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-incrementing unique identifier |
| `institution_id` | INTEGER | FK, NOT NULL | References api_institution.id |
| `name` | VARCHAR(200) | NOT NULL | User-friendly name ("My Checking", "Business CC") |
| `account_number` | VARCHAR(50) | NOT NULL | Account identifier (last 4 digits or full number) |
| `account_type` | VARCHAR(20) | NOT NULL | Type: checking, savings, credit, investment, other |
| `created_at` | DATETIME | NOT NULL | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL | Last modification timestamp |

### Account Types

```python
ACCOUNT_TYPES = (
    ('checking', 'Checking Account'),
    ('savings', 'Savings Account'),
    ('credit', 'Credit Card'),
    ('investment', 'Investment Account'),
    ('other', 'Other'),
)
```

### Example Records

```sql
INSERT INTO api_account VALUES
(1, 1, 'Bank-1 Checking', '0000', 'checking', '2026-03-01 10:00:00', '2026-03-01 10:00:00'),
(2, 1, 'Bank-1 Savings', '0000', 'savings', '2026-03-01 10:00:00', '2026-03-01 10:00:00'),
(3, 2, 'Bank-2 Credit', '0000', 'credit', '2026-03-01 10:00:00', '2026-03-01 10:00:00');
```

### Constraints

- **Composite Unique**: `(institution_id, account_number)` must be unique
  - Prevents duplicate accounts for same institution
  - Allows same account_number across different institutions

### Computed Fields

```python
def get_balance(self):
    """Calculate balance from all transactions"""
    total = self.transactions.aggregate(
        balance=models.Sum('amount')
    )['balance'] or Decimal('0.00')
    return total
```

### Relationships

- **Many Accounts** ← **One Institution** (N:1)
  - Uses: `account.institution`
- **One Account** → **Many Transactions** (1:N)
  - Referenced by: `api_transaction.account_id`

### Usage

```python
# Get account
account = Account.objects.get(id=1)

# Get all transactions
transactions = account.transactions.all()

# Get balance
balance = account.get_balance()  # Decimal('-1234.56')

# Filter by institution
accounts = Account.objects.filter(
    institution__identifier='bank-1',
    account_type='checking'
)
```

---

## Categories Table

**Table Name:** `api_category`

**Purpose:** Store transaction categories with hierarchical structure

### Schema

```sql
CREATE TABLE api_category (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        VARCHAR(100) NOT NULL UNIQUE,
  slug        VARCHAR(100) NOT NULL UNIQUE,
  parent_id   INTEGER,
  created_at  DATETIME NOT NULL,
  FOREIGN KEY (parent_id) REFERENCES api_category(id)
);
```

### Column Details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-incrementing unique identifier |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE | Display name ("Groceries", "Restaurants") |
| `slug` | VARCHAR(100) | NOT NULL, UNIQUE | URL-friendly identifier ("groceries") |
| `parent_id` | INTEGER | FK (self), NULL | Parent category for hierarchies |
| `created_at` | DATETIME | NOT NULL | Record creation timestamp |

### Example Hierarchy

```
Food (parent=NULL)
  ├─ Groceries (parent=Food)
  ├─ Restaurants (parent=Food)
  └─ Coffee Shops (parent=Food)

Transportation (parent=NULL)
  ├─ Gas (parent=Transportation)
  ├─ Auto Maintenance (parent=Transportation)
  └─ Parking (parent=Transportation)

Utilities (parent=NULL)
  ├─ Electric (parent=Utilities)
  ├─ Water (parent=Utilities)
  └─ Internet (parent=Utilities)
```

### Example Records

```sql
INSERT INTO api_category VALUES
(1, 'Food', 'food', NULL, '2026-03-01 10:00:00'),
(2, 'Groceries', 'groceries', 1, '2026-03-01 10:00:00'),
(3, 'Restaurants', 'restaurants', 1, '2026-03-01 10:00:00'),
(4, 'Transportation', 'transportation', NULL, '2026-03-01 10:00:00'),
(5, 'Gas', 'gas', 4, '2026-03-01 10:00:00');
```

### Relationships

- **One Category** ← **One Parent Category** (N:1 self-referential)
  - Uses: `category.parent`
- **One Category** → **Many Transactions** (1:N)
  - Referenced by: `api_transaction.category_id`
- **One Category** → **Many Child Categories** (1:N)
  - Uses: `category.subcategories.all()` (reverse relation)

### Usage

```python
# Get category
category = Category.objects.get(slug='groceries')

# Get parent
parent = category.parent  # Food

# Get children
children = category.subcategories.all()

# Get all transactions in category
transactions = category.transactions.all()

# Get spending by category
from django.db.models import Sum
spending = category.transactions.aggregate(
    total=Sum('amount')
)  # {'total': Decimal('-1234.56')}
```

---

## Transactions Table

**Table Name:** `api_transaction`

**Purpose:** Store individual financial transactions

### Schema

```sql
CREATE TABLE api_transaction (
  id                  INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id          INTEGER NOT NULL,
  date                DATE NOT NULL,
  description         VARCHAR(500) NOT NULL,
  original_description VARCHAR(500),
  amount              DECIMAL(12, 2) NOT NULL,
  category_id         INTEGER,
  status              VARCHAR(20) NOT NULL DEFAULT 'pending',
  notes               TEXT,
  transaction_hash    VARCHAR(64) NOT NULL UNIQUE,
  created_at          DATETIME NOT NULL,
  updated_at          DATETIME NOT NULL,
  FOREIGN KEY (account_id) REFERENCES api_account(id),
  FOREIGN KEY (category_id) REFERENCES api_category(id)
);

CREATE INDEX idx_account_date ON api_transaction(account_id, date);
CREATE INDEX idx_amount ON api_transaction(amount);
CREATE INDEX idx_transaction_hash ON api_transaction(transaction_hash);
```

### Column Details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-incrementing identifier |
| `account_id` | INTEGER | FK, NOT NULL | References api_account.id |
| `date` | DATE | NOT NULL | Transaction date |
| `description` | VARCHAR(500) | NOT NULL | Transaction description ("Starbucks #1234") |
| `original_description` | VARCHAR(500) | NULL | Original description from bank CSV |
| `amount` | DECIMAL(12,2) | NOT NULL | Amount (negative for expenses, positive for income) |
| `category_id` | INTEGER | FK, NULL | References api_category.id (NULL if uncategorized) |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT | pending, posted, cleared, failed |
| `notes` | TEXT | NULL | User notes about transaction |
| `transaction_hash` | VARCHAR(64) | NOT NULL, UNIQUE | SHA-256 hash for duplicate detection |
| `created_at` | DATETIME | NOT NULL | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL | Last modification timestamp |

### Transaction Statuses

```python
TRANSACTION_STATUSES = (
    ('pending', 'Pending'),        # Awaiting post
    ('posted', 'Posted'),          # Posted but not cleared
    ('cleared', 'Cleared'),        # Money moved
    ('failed', 'Failed'),          # Failed transaction
)
```

### Example Records

```sql
INSERT INTO api_transaction VALUES
(1, 1, '2026-03-01', 'STARBUCKS #1234', 'COFFEE SHOP', -5.50, 4, 'cleared', NULL, 'hash1', '2026-03-01 10:00:00', '2026-03-01 10:00:00'),
(2, 1, '2026-03-02', 'WHOLE FOODS #5678', 'GROCERY STORE', -87.43, 2, 'cleared', NULL, 'hash2', '2026-03-02 10:00:00', '2026-03-02 10:00:00'),
(3, 1, '2026-03-03', 'SALARY DEPOSIT', 'EMPLOYER', 2500.00, NULL, 'cleared', 'Monthly salary', 'hash3', '2026-03-03 10:00:00', '2026-03-03 10:00:00');
```

### Computed Fields

```python
@property
def is_expense(self):
    """Check if transaction is expense (negative)"""
    return self.amount < 0

@property
def is_income(self):
    """Check if transaction is income (positive)"""
    return self.amount > 0

@property
def merchant(self):
    """Extract merchant name from description"""
    # First word up to special characters
    match = re.match(r'([A-Z\s&]+)', self.description)
    return match.group(1).strip() if match else self.description
```

### Duplicate Detection

```python
def generate_hash(self):
    """Generate unique hash from transaction details"""
    hash_string = f"{self.account_id}|{self.date}|{self.description}|{self.amount}"
    return hashlib.sha256(hash_string.encode()).hexdigest()

# Hash = SHA-256 of: account_id|date|description|amount
# Identical transactions on same account → same hash → duplicates prevented
```

### Relationships

- **Many Transactions** ← **One Account** (N:1)
  - Uses: `transaction.account`
- **Many Transactions** ← **One Category** (N:1)
  - Uses: `transaction.category` (can be NULL)

### Indexes

- `(account_id, date)` - For monthly/yearly reports
- `(amount)` - For spending analysis
- `(transaction_hash)` - For duplicate detection

### Usage

```python
# Get transaction
transaction = Transaction.objects.get(id=1)

# Filter by date range
from django.utils import timezone
from datetime import timedelta

start_date = timezone.now().date() - timedelta(days=30)
recent = Transaction.objects.filter(date__gte=start_date)

# Filter by category and account
groceries = Transaction.objects.filter(
    account=account,
    category__slug='groceries',
    status='cleared'
)

# Get total spending
from django.db.models import Sum
total = Transaction.objects.filter(
    account=account,
    date__month=3
).aggregate(Sum('amount'))  # {'amount__sum': Decimal('-1234.56')}

# Check if expense
if transaction.is_expense:
    print(f"Spent: ${abs(transaction.amount)}")
```

---

## Import Logs Table

**Table Name:** `api_importlog`

**Purpose:** Track transaction import operations

### Schema

```sql
CREATE TABLE api_importlog (
  id                  INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id          INTEGER NOT NULL,
  file_name           VARCHAR(255) NOT NULL,
  file_path           VARCHAR(500),
  format_type         VARCHAR(20) NOT NULL,
  status              VARCHAR(20) NOT NULL DEFAULT 'pending',
  records_processed   INTEGER DEFAULT 0,
  records_imported    INTEGER DEFAULT 0,
  records_skipped     INTEGER DEFAULT 0,
  error_message       TEXT,
  started_at          DATETIME NOT NULL,
  completed_at        DATETIME,
  created_at          DATETIME NOT NULL,
  updated_at          DATETIME NOT NULL,
  FOREIGN KEY (account_id) REFERENCES api_account(id)
);

CREATE INDEX idx_account_started ON api_importlog(account_id, started_at);
```

### Column Details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-incrementing identifier |
| `account_id` | INTEGER | FK, NOT NULL | Account being imported to |
| `file_name` | VARCHAR(255) | NOT NULL | Original filename |
| `file_path` | VARCHAR(500) | NULL | Full path to file |
| `format_type` | VARCHAR(20) | NOT NULL | Format: csv, pdf, ofx, etc. |
| `status` | VARCHAR(20) | NOT NULL | pending, successful, failed |
| `records_processed` | INTEGER | DEFAULT 0 | Total records in file |
| `records_imported` | INTEGER | DEFAULT 0 | Successfully imported |
| `records_skipped` | INTEGER | DEFAULT 0 | Skipped (duplicates, errors) |
| `error_message` | TEXT | NULL | Error details if failed |
| `started_at` | DATETIME | NOT NULL | Import start time |
| `completed_at` | DATETIME | NULL | Import completion time (NULL if in progress) |
| `created_at` | DATETIME | NOT NULL | Record creation |
| `updated_at` | DATETIME | NOT NULL | Last update |

### Example Records

```sql
INSERT INTO api_importlog VALUES
(1, 1, 'bank-1-2026-03-01.csv', '/uploads/bank-1-2026-03-01.csv', 'csv', 'successful', 142, 140, 2, NULL, '2026-03-01 10:00:00', '2026-03-01 10:05:00', '2026-03-01 10:00:00', '2026-03-01 10:05:00'),
(2, 1, 'bank-1-2026-02-01.csv', '/uploads/bank-1-2026-02-01.csv', 'csv', 'successful', 156, 155, 1, NULL, '2026-03-01 11:00:00', '2026-03-01 11:03:00', '2026-03-01 11:00:00', '2026-03-01 11:03:00');
```

### Computed Fields

```python
@property
def duration(self):
    """Get import duration"""
    if self.completed_at:
        return self.completed_at - self.started_at
    return None

def success_rate(self):
    """Calculate success percentage"""
    if self.records_processed == 0:
        return 0
    return (self.records_imported / self.records_processed) * 100
```

### Relationships

- **Many ImportLogs** ← **One Account** (N:1)
  - Uses: `importlog.account`

### Usage

```python
# Get import history
from api.models import ImportLog

logs = ImportLog.objects.filter(
    account=account,
    status='successful'
).order_by('-completed_at')

# Get latest import
latest = ImportLog.objects.filter(
    account=account
).latest('completed_at')

# Check import success rate
success_pct = latest.success_rate()  # 98.6%

# Get failed imports
failed = ImportLog.objects.filter(status='failed')
```

---

## Relationships Diagram

```
Institution (1)
    │
    ├────────────────────► (N) Account
    │                           │
    │                           ├──────────────────► (N) Transaction
    │                           │                        │
    │                           │                        ├─ has amount
    │                           │                        ├─ has date
    │                           │                        └─ has Category (FK)
    │                           │
    │                           └──────────────────► (N) ImportLog
    │
    │
    ├──────────────────────────────────────────────┐
    │                                              │
Category (1)                                        │
    │                                              │
    ├─ has parent_id (self-referential)            │
    │   └─► (N) Category (children)                │
    │                                              │
    └──────────────────► (N) Transaction ◄────────┘
```

---

## Indexes and Constraints

### Primary Keys
- All tables have auto-incrementing INTEGER primary key

### Foreign Keys
- `api_account.institution_id` → `api_institution.id`
- `api_transaction.account_id` → `api_account.id`
- `api_transaction.category_id` → `api_category.id` (NULLABLE)
- `api_category.parent_id` → `api_category.id` (NULLABLE, self-referential)
- `api_importlog.account_id` → `api_account.id`

### Unique Constraints
- `api_institution(name)`
- `api_institution(identifier)`
- `api_account(institution_id, account_number)` - Composite unique
- `api_category(name)`
- `api_category(slug)`
- `api_transaction(transaction_hash)`

### Indexes for Performance

```sql
-- Transaction querying
CREATE INDEX idx_transaction_account_date 
  ON api_transaction(account_id, date);
CREATE INDEX idx_transaction_amount 
  ON api_transaction(amount);
CREATE INDEX idx_transaction_category 
  ON api_transaction(category_id);
CREATE INDEX idx_transaction_status 
  ON api_transaction(status);

-- Import tracking
CREATE INDEX idx_importlog_account_started 
  ON api_importlog(account_id, started_at);
CREATE INDEX idx_importlog_status 
  ON api_importlog(status);
```

---

## Sample Queries

### Monthly Spending by Category
```python
from django.db.models import Sum
from datetime import date, timedelta

# Last 30 days
thirty_days_ago = date.today() - timedelta(days=30)

spending = Transaction.objects.filter(
    account=account,
    date__gte=thirty_days_ago
).values('category__name').annotate(
    total=Sum('amount')
).order_by('total')

# Result: [{'category__name': 'Groceries', 'total': -234.56}, ...]
```

### Account Balance
```python
account.get_balance()  # Decimal('-1234.56')
```

### Top 10 Merchants
```python
transactions = Transaction.objects.filter(
    account=account,
    amount__lt=0  # Expenses only
)[:10]

merchants = [t.merchant for t in transactions]
```

### Last Import Status
```python
latest_import = ImportLog.objects.filter(
    account=account
).latest('completed_at')

print(f"Imported {latest_import.records_imported} transactions")
print(f"Success rate: {latest_import.success_rate():.1f}%")
```

---

## Data Constraints and Validation

### Transaction Hash Generation
- Prevents duplicate transactions
- Hash = SHA-256(`account_id|date|description|amount`)
- Unique constraint on hash column

### Amount Precision
- Decimal(12, 2) = 12 digits with 2 decimal places
- Range: -9,999,999.99 to 9,999,999.99
- Sufficient for personal finances

### Status Workflows
- ImportLog: pending → successful/failed
- Transaction: pending → posted → cleared/failed

---

## Further Reading

- [System Design](SYSTEM_DESIGN.md)
- [API Reference](../API_REFERENCE.md)
- [Developer Guide](../development/DEVELOPER_GUIDE.md)
