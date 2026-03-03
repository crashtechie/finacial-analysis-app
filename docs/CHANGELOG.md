# Changelog

All notable changes to the Financial Analysis API project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- PDF statement parsing support (Bank-2, Bank-4 formats)
- Budget tracking and alerts
- Recurring transaction detection
- Transaction export (CSV/Excel)
- Advanced analytics (anomaly detection, spending predictions)
- Web frontend (React/Vue)
- User authentication and multi-user support
- API rate limiting

---

## [0.2.0] - 2026-03-03

### Added
- **Bank-5 CSV Importer**: Fully functional importer for Bank-5 format CSV files.
  - Supports standard Bank-5 CSV columns: Date, Description, Original Description, Category, Amount, Status
  - Registered in importer registry and available via `import_transactions` management command
  - Includes comprehensive test coverage in `tests_coverage.py` and `tests_edge_cases.py`
- **Enhanced Test Data**: Added Bank-5 demo transaction file with 706 transactions spanning September 2025 - March 2026 in `finances/bank-5/`

### Documentation
- Updated manual testing guide to include Bank-5 importer usage examples and test scenarios
- Added Bank-5 format support documentation across API reference and developer guides
- Updated importer registry documentation to reflect both bank-1 and bank-5 support

---

## [0.1.2] - 2026-03-02

### Fixed
- **Analytics Daily Aggregation**: Fixed daily spending trend aggregation to annotate directly from the transaction `date` field instead of using an incorrect truncation class reference.
  - Ensures `/api/analytics/spending-trends/?period=daily` returns consistent daily buckets.
  - Prevents aggregation annotation errors when using explicit date filters.

### Added
- **Regression Test for Daily Trends**: Added coverage for daily spending trends with an explicit date range in `api/tests.py`.

### Changed
- **Codebase Formatting Consistency**: Standardized string quoting and formatting across API modules, serializers, model definitions, importer code, and URL configuration.
- **Developer Tooling**: Updated development dependency `black` to `>=25.0.0,<26.0` in `pyproject.toml`.

### Documentation
- Updated test command examples to use the correct Django settings module path (`financial_analysis.settings`).
- Updated manual testing/linting commands to consistently use `uv run`.
- Clarified troubleshooting guidance for command execution from `app/backend`.

---

## [0.1.1] - 2026-03-02

### Fixed
- **Module Import Error in Django Management**: Fixed `ModuleNotFoundError: No module named 'app'` when running `uv run python manage.py migrate` and other management commands from `app/backend` directory.
  - Updated `manage.py` to correctly add workspace root to `sys.path` instead of just the backend directory
  - This ensures the `app` package is properly importable for Django settings module resolution
  - Affects all Django management commands: `migrate`, `makemigrations`, `runserver`, etc.
  - **Related Issue**: [bug2026032](docs/issues/bug2026032-migrate-modulenotfound-app.md)

---

## [0.1.0] - 2026-03-01

### Added

#### Development Environment
- VS Code dev container configuration with Python 3.12
- Docker setup with automatic dependency installation
- Environment variable configuration via .env
- Python package management with uv

#### Core Data Models
- Institution model - Financial institutions management
- Account model - Multiple account support with balance calculation
- Category model - Hierarchical category structure
- Transaction model - Individual transaction storage with duplicate detection via SHA-256 hashing
- ImportLog model - Import operation tracking and statistics

#### CSV Import System
- Base importer class for extensible import architecture
- Bank-1 CSV format importer (fully functional)
- Import registry pattern for easy addition of new formats
- Management command: `uv run python manage.py import_transactions`
- Automatic category mapping from CSV data
- Duplicate transaction detection and prevention
- Comprehensive import statistics and error reporting

#### REST API Endpoints
- Institution CRUD endpoints
- Account CRUD endpoints with balance calculation
- Category CRUD endpoints with hierarchy support
- Transaction CRUD endpoints with:
  - Date range filtering (exact, gte, lte, gt, lt)
  - Amount filtering and comparison
  - Category and account filtering
  - Full-text search in descriptions
  - Flexible ordering options
  - Pagination (default 50 items/page)
- ImportLog read-only endpoints

#### Analytics Endpoints
- Spending Trends (`/api/analytics/spending-trends/`)
  - Daily, weekly, and monthly aggregation
  - Expense vs income tracking
  - Customizable date ranges
  - Account filtering
  
- Category Breakdown (`/api/analytics/category-breakdown/`)
  - Category-wise expense analysis
  - Percentage calculations
  - Transaction counts and averages
  - Expense-only or all transactions mode
  
- Merchant Analysis (`/api/analytics/merchants/`)
  - Top merchants by spending amount
  - Transaction frequency analysis
  - Average transaction calculations
  - First/last transaction dates
  - Configurable result limits
  
- Summary Statistics (`/api/analytics/summary/`)
  - Total transaction counts
  - Expense and income totals
  - Net amount calculation
  - Period date ranges
  - Account listings

#### Admin Interface
- Full Django admin customization
- Transaction admin with color-coded amounts
- Account admin with balance display
- Category hierarchy display
- Import log statistics
- Advanced filtering and search
- Responsive design

#### Utilities
- Date helper functions (period calculations, date parsing)
- Currency and number formatting utilities
- Date range calculations (week, month, quarter, year)
- Period label formatting

#### Documentation
- Comprehensive README with setup instructions
- Detailed API reference with examples
- Implementation summary
- Auto-generated category fixtures
- Setup automation script

#### Configuration & Settings
- Django REST Framework configuration
- CORS headers setup
- Filter backend configuration
- Environment-based settings
- Database configuration (SQLite)

### Technical Specifications

- **Language:** Python 3.12
- **Framework:** Django 5.2.11
- **API Framework:** Django REST Framework 3.16.1
- **Database:** SQLite3
- **Package Manager:** uv
- **Dependencies:** pandas, django-cors-headers, django-filter, python-dateutil

### Test Data

- **Sample Transactions:** 76 Bank-1 transactions (February 2026)
- **Categories:** 20 pre-loaded categories
- **Date Range:** February 2-27, 2026
- **Total Expenses:** $3,242.15
- **Total Income:** $3,000.01
- **Net:** -$242.14

### Known Limitations

- PDF file parsing not yet implemented
- Single user only (no authentication)
- No rate limiting
- Development environment uses SQLite (PostgreSQL recommended for production)
- CORS set to allow all origins (restrict for production)

### Breaking Changes

None (initial release)

### Security Notes

- Uses Django's default security middleware
- CSRF protection enabled
- SQL injection prevention via Django ORM
- XSS protection disabled for browsable API (enable for production)
- No authentication layer (add for production)

---

## Migration Guide

### From 0.0.0 (Initial Setup)

No migration needed - this is the initial release.

To set up for the first time:

```bash
# Install dependencies
uv sync

# Create database
uv run python manage.py migrate

# Load fixture data
uv run python manage.py loaddata categories

# Import sample transactions
uv run python manage.py import_transactions finances/bank-1/bank-1-transactions-6057-202602.csv --format bank-1

# Start development server
uv run python manage.py runserver
```

---

## Contributors

- Initial implementation: March 1, 2026

---

## Support & Feedback

For questions, issues, or feature requests:
1. Check the [README.md](README.md) for setup instructions
2. Review [API_REFERENCE.md](API_REFERENCE.md) for API documentation
3. Examine [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for technical details

---

## Links

- [Issues](#)
- [Pull Requests](#)
- [Releases](../../releases)
- [License](LICENSE)
