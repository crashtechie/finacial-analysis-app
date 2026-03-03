# Financial Analysis Django REST API

A Django REST API application for analyzing financial data from CSV and PDF documents, featuring spending trends, category breakdowns, and merchant patterns.

## Features

- **Multi-format Import**: Import financial data from CSV files (PDF support in Phase 2)
- **Multi-institution Support**: Extensible importer system for different banks
- **Transaction Management**: Store and manage transactions with automatic duplicate detection
- **Category Analysis**: Hierarchical categories with breakdown and comparison
- **Spending Trends**: Time-series analysis with daily/weekly/monthly aggregation
- **Merchant Insights**: Top merchants by frequency and spending patterns
- **REST API**: Full-featured API for programmatic access

## Tech Stack

- **Python 3.12+**
- **Django 5.x** - Web framework
- **Django REST Framework** - API framework
- **SQLite** - Database
- **uv** - Fast Python package manager
- **Pandas** - Data processing
- **VS Code Dev Containers** - Consistent development environment

## Getting Started

### Prerequisites

- Docker and VS Code with Remote - Containers extension (for dev container)
- OR Python 3.12+ and uv installed locally

### Setup with Dev Container (Recommended)

1. Open the project in VS Code
2. When prompted, click "Reopen in Container" (or use Command Palette: "Remote-Containers: Reopen in Container")
3. Wait for the container to build and dependencies to install
4. The application will be ready to use

### Setup Locally

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Run migrations**:
   ```bash
   uv run python manage.py migrate
   ```

4. **Load initial categories**:
   ```bash
   uv run python manage.py loaddata categories
   ```

5. **Import sample data** (optional):
   ```bash
   uv run python manage.py import_transactions finances/bank-1/bank-1-transactions-6057-202602.csv --format bank-1
   ```

6. **Start the development server**:
   ```bash
   uv run python manage.py runserver
   ```

**Note:** With `uv`, you don't need to manually activate virtual environments. Simply use `uv run` before Python commands.

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Core Resources

- `GET /api/accounts/` - List all accounts
- `GET /api/accounts/{id}/` - Get account details
- `GET /api/transactions/` - List transactions (supports filtering)
- `GET /api/transactions/{id}/` - Get transaction details
- `GET /api/categories/` - List categories
- `POST /api/imports/upload/` - Upload and import CSV file

### Analytics

- `GET /api/analytics/spending-trends/` - Time-series spending analysis
  - Query params: `period` (daily/weekly/monthly), `start_date`, `end_date`, `account`
  
- `GET /api/analytics/category-breakdown/` - Spending by category
  - Query params: `start_date`, `end_date`, `account`, `compare_period`
  
- `GET /api/analytics/merchants/` - Top merchants analysis
  - Query params: `start_date`, `end_date`, `account`, `limit`

### Query Parameters

- **Filtering**: `?category=groceries&date_after=2026-02-01`
- **Ordering**: `?ordering=-date,-amount`
- **Pagination**: `?page=2&page_size=50`
- **Search**: `?search=starbucks`

## Data Import

### CSV Format

Currently supports Bank-1 format with columns:
- Date (YYYY-MM-DD)
- Description
- Original Description
- Category
- Amount (negative for expenses, positive for income)
- Status

### Adding Support for Other Banks

1. Create a new importer in `api/importers/`
2. Extend `BaseImporter` class
3. Implement `parse_row()` and `get_format_name()` methods
4. Register in `api/importers/__init__.py`

Example:
```python
from .base import BaseImporter

class Bank5Importer(BaseImporter):
    def get_format_name(self):
        return "bank-5"
    
    def parse_row(self, row):
        # Parse row and return transaction dict
        pass
```

## Development

### Running Tests

```bash
uv run python manage.py test
```

### Code Formatting

```bash
black .
isort .
```

### Create Superuser

```bash
uv run python manage.py createsuperuser
```

### Access Django Admin

Visit `http://localhost:8000/admin/` (after creating superuser)

## Project Structure

```
financial-analysis-app/
├── .devcontainer/          # Dev container configuration
├── financial_analysis/     # Django project settings
├── api/                    # Main Django app
│   ├── models.py          # Data models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API viewsets
│   ├── importers/         # CSV/PDF import logic
│   ├── analytics/         # Analytics endpoints
│   └── management/        # Django commands
├── finances/              # Sample data
├── scripts/               # Utility scripts
└── manage.py             # Django management script
```

## Roadmap

### Phase 1 (Current)
- ✅ Dev container setup
- ✅ Django project structure
- ✅ Data models
- ✅ CSV import (Bank-1 format)
- ✅ REST API endpoints
- ✅ Analytics/reporting
- ✅ Documentation

### Phase 2 (Future)
- [ ] PDF parsing support
- [ ] Additional bank formats
- [ ] Budget tracking
- [ ] Recurring transaction detection
- [ ] Export functionality
- [ ] Advanced analytics (anomaly detection)
- [ ] Web frontend

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
