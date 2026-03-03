# Contributing Guide

Thank you for your interest in contributing to the Financial Analysis API! This guide explains how to contribute code, documentation, or other improvements.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Types of Contributions](#types-of-contributions)
- [Community](#community)

---

## Getting Started

### 1. Fork the Repository

Visit [GitHub repository](https://github.com/yourusername/financial-analysis-app) and click "Fork"

```bash
git clone https://github.com/your-username/financial-analysis-app.git
cd financial-analysis-app
git remote add upstream https://github.com/original-username/financial-analysis-app.git
```

### 2. Create Development Branch

```bash
# Update main branch
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number
```

Branch naming convention:
- `feature/description` - New feature
- `fix/issue-number` - Bug fix (reference issue)
- `docs/description` - Documentation update
- `test/description` - Test improvements
- `refactor/description` - Code refactoring

### 3. Setup Development Environment

```bash
cd app/backend

# Install with dev dependencies (uv manages the virtual environment)
uv sync --all-extras

# Verify setup
uv run python manage.py check
uv run pytest --cov=api api/tests.py
```

---

## Development Workflow

### Make Your Changes

```bash
# Make code changes
# Edit files in app/backend/api/

# Run the dev server locally
uv run python manage.py runserver

# Test in browser or with curl
curl http://localhost:8000/api/transactions/
```

### Keep Branch Updated

```bash
# Fetch latest changes
git fetch upstream

# Rebase on main
git rebase upstream/main

# If conflicts occur, resolve them
git status
# Edit conflicted files
git add .
git rebase --continue
```

### Before Committing

```bash
# 1. Format code
black app/
isort app/

# 2. Lint
flake8 app/ --max-line-length=100

# 3. Run tests
uv run python manage.py test api.tests -v 2

# 4. Check migrations
uv run python manage.py makemigrations --check

# 5. Verify no uncommitted changes
git status
```

All should pass before committing!

---

## Code Standards

### Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these settings:

**Line length:** 100 characters

```python
# Configure in pyproject.toml
[tool.black]
line-length = 100

[tool.isort]
line_length = 100
```

### Python Conventions

#### Imports

```python
# Order imports: standard library, third-party, local
import os
from decimal import Decimal
from datetime import date, datetime

import django
from django.db import models
from rest_framework import viewsets

from .models import Transaction
from .utils import formatters
```

#### Naming

```python
# Classes: PascalCase
class TransactionSerializer:
    pass

# Functions/variables: snake_case
def format_currency(amount):
    pass

total_spending = Decimal('100.00')

# Constants: UPPER_CASE
MAX_PAGE_SIZE = 1000
DEFAULT_PAGINATION = 50

# Private/internal: _leading_underscore
def _internal_helper():
    pass
```

#### Type Hints (Recommended)

```python
from typing import List, Optional, Dict
from decimal import Decimal

def calculate_total(
    amounts: List[Decimal],
    round_to_cents: bool = True
) -> Decimal:
    """Calculate total of amounts.
    
    Args:
        amounts: List of decimal amounts
        round_to_cents: Whether to round to 2 decimals
        
    Returns:
        Total as Decimal
    """
    return sum(amounts)
```

#### Documentation

```python
def get_transactions(
    account,
    start_date: date,
    end_date: date,
    category: Optional[Category] = None
) -> QuerySet:
    """Get transactions for account in date range.
    
    Filters transactions by account and date, optionally by category.
    Results are ordered by date descending.
    
    Args:
        account: Account instance
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        category: Optional category to filter by
        
    Returns:
        QuerySet of Transaction objects ordered by date
        
    Raises:
        ValueError: If start_date > end_date
        
    Example:
        >>> transactions = get_transactions(account, date(2026, 1, 1), date(2026, 3, 1))
        >>> len(transactions)
        145
    """
    if start_date > end_date:
        raise ValueError("start_date must be before end_date")
    
    qs = Transaction.objects.filter(
        account=account,
        date__gte=start_date,
        date__lte=end_date
    )
    
    if category:
        qs = qs.filter(category=category)
    
    return qs.order_by('-date')
```

---

## Testing Requirements

### Test Coverage Targets

- **Models:** 100% coverage
- **Views:** 90%+ coverage
- **Utilities:** 100% coverage
- **Overall:** 75%+ coverage

### Writing Tests

```python
from django.test import TestCase
from decimal import Decimal

class MyFeatureTests(TestCase):
    """Tests for new feature"""
    
    def setUp(self):
        """Create test data"""
        self.institution = Institution.objects.create(
            name="Test Bank",
            identifier="testbank"
        )
    
    def test_feature_success(self):
        """Test successful feature behavior"""
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
    
    def test_feature_edge_case(self):
        """Test edge case handling"""
        # Test boundary conditions, None values, empty results, etc.
        pass
    
    def test_feature_error_handling(self):
        """Test error handling"""
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            # Code that should raise error
            pass
```

### Run Tests Before Submitting

```bash
# All tests
uv run python manage.py test api.tests -v 2

# Specific test class/method
uv run python manage.py test api.tests.MyFeatureTests.test_feature_success

# With coverage
uv run pytest --cov=api --cov-report=term-missing api/tests.py

# All checks
black api/ && isort api/ && flake8 api/ && uv run pytest --cov=api api/tests.py
```

---

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Examples

```
feat(importers): add Bank-2 CSV importer

Add support for importing transactions from Bank-2 CSV format.
Includes parser for Bank-2-specific date and amount formatting.

Closes #42

---

fix(transactions): prevent duplicate imports

Use transaction hash to prevent duplicate transactions from being imported
multiple times. Hash based on account_id, date, description, and amount.

Fixes #38

---

docs(api): update endpoint documentation

Add missing parameter documentation for filtering and pagination.

---

test(models): increase coverage for Account model

Add tests for edge cases: zero balance, many transactions, etc.
Coverage increased from 85% to 98%.

---

refactor(utils): simplify date range calculation

Extract common date calculation logic to improve maintainability.
No functional changes.
```

### Types

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `test` - Test additions/improvements
- `refactor` - Code restructuring
- `perf` - Performance improvements
- `style` - Code style (formatting, linting)
- `chore` - Build, dependencies, etc.

### Scope (Optional)

- `models` - Data models
- `views` - API views
- `serializers` - DRF serializers
- `utils` - Utility functions
- `importers` - Transaction importers
- `analytics` - Analytics endpoints
- `tests` - Test suite
- `docs` - Documentation
- `ci` - CI/CD configuration

---

## Pull Request Process

### 1. Commit Your Changes

```bash
# Stage changes
git add app/backend/api/

# Commit with conventional message
git commit -m "feat(models): add budget tracking"

# Push to your fork
git push origin feature/your-feature-name
```

### 2. Create Pull Request

On GitHub:

1. Click "Compare & pull request"
2. Fill in PR template:

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues

Closes #123

## Testing

- [ ] Added tests for new code
- [ ] All tests pass locally
- [ ] Coverage maintained/improved

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No breaking changes
```

### 3. Respond to Feedback

1. Read reviewer comments
2. Make requested changes
3. Push new commits (don't force-push)
4. Comment when ready for re-review

```bash
# Make changes based on feedback
git add .
git commit -m "refactor: address review feedback"
git push origin feature/your-feature-name
```

### 4. Merge

Once approved, maintainer will merge with "Squash and merge" or "Rebase and merge"

---

## Types of Contributions

### Code Contributions

- Bug fixes (start with issue or discussion)
- New features (please open issue first)
- Performance improvements
- Refactoring

### Documentation Contributions

- Fix typos or unclear sections
- Add examples or clarifications
- Add API documentation
- Create deployment guides

### Test Contributions

- Add tests for uncovered code
- Add integration tests
- Add edge case tests

### Issue Contributions

- Report bugs with reproduction steps
- Suggest features with use cases
- Ask questions in issues (not PRs)

---

## Community

### Communication

- **Issues**: Report bugs, request features
- **Pull Requests**: Submit code changes
- **Discussions**: Ask questions, share ideas
- **Email**: Contact maintainers directly

### Code of Conduct

We follow a code of conduct based on the [Contributor Covenant](https://www.contributor-covenant.org/):

- Be respectful and inclusive
- Welcome diverse perspectives
- Accept constructive criticism
- Avoid harassment or discrimination
- Report concerns to maintainers

### Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Recognized in documentation

---

## Common Tasks

### Adding a New Bank Importer

1. Create `api/importers/yourbank.py`:

```python
from .base import BaseImporter, ImporterRegistry

@ImporterRegistry.register('yourbank')
class YourBankImporter(BaseImporter):
    """Import from YourBank CSV format"""
    
    EXPECTED_HEADERS = ['Date', 'Description', 'Amount']
    
    def parse_date(self, date_str):
        return datetime.strptime(date_str, '%m/%d/%Y').date()
    
    def import_transactions(self, file_handle, account):
        # Implementation
        pass
```

2. Write tests in `api/tests.py`:

```python
class YourBankImporterTests(TestCase):
    def test_parse_date(self):
        pass
    
    def test_import_csv(self):
        pass
```

3. Update `api/management/commands/import_transactions.py`
4. Add documentation to [Developer Guide](../development/DEVELOPER_GUIDE.md)
5. Create PR with detailed description

### Adding a New API Endpoint

1. Add model if needed in `api/models.py`
2. Create serializer in `api/serializers.py`
3. Create viewset in `api/views.py`
4. Register in `api/urls.py`
5. Write tests in `api/tests.py`
6. Update [API Reference](../API_REFERENCE.md)

### Writing Documentation

1. Choose appropriate location:
   - Setup guide → `/docs/guides/`
   - Architecture → `/docs/architecture/`
   - Development → `/docs/development/`
   - Deployment → `/docs/deployment/`

2. Follow markdown style:
   - Use clear headings
   - Include code examples
   - Link related docs
   - Add table of contents

3. Test links work:
   ```bash
   # Check links
   markdown-link-check docs/**/*.md
   ```

---

## Getting Help

- **Setup issues?** Check [Installation Guide](../guides/INSTALLATION.md)
- **Understanding code?** See [Developer Guide](../development/DEVELOPER_GUIDE.md)
- **API questions?** Read [API Reference](../API_REFERENCE.md)
- **Architecture?** See [System Design](../architecture/SYSTEM_DESIGN.md)
- **Still stuck?** Open an issue!

---

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Contributing Guide](https://docs.github.com/en/get-started/quickstart/contributing-to-projects)

---

## Thank You!

Your contributions make this project better. We appreciate your time and effort in improving the Financial Analysis API!

**Happy coding!** 🚀
