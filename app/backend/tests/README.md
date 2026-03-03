# Test Suite Documentation

## Test Structure

The project has a two-tier test structure:

### Primary Test Suite (api/tests.py)
- **Location:** `app/backend/api/tests.py`
- **Framework:** Django TestCase
- **Status:** ✅ 29 tests - ALL PASSING
- **Coverage:** Models, serializers, and API endpoints

**Run with Django (`manage.py`):**
```bash
cd /workspaces/finacial-analysis-app/app/backend
python manage.py test api.tests --verbosity=2
```

**Or from workspace root:**
```bash
uv run python -m django test api.tests --verbosity=2 --settings=financial_analysis.settings
```

### Secondary Test Suite (tests/ directory)
- **Location:** `app/backend/tests/`
- **Framework:** pytest + pytest-django
- **Status:** ⚠️ Partially implemented (API endpoint tests working)
- **Run with pytest:**
```bash
cd app/backend
uv run pytest tests/ -v
```

## Test Organization

```
app/backend/
├── api/
│   └── tests.py              # ⭐ Main comprehensive test suite (29 tests)
│
└── tests/                     # Secondary pytest-based structure
    ├── conftest.py           # Pytest configuration
    ├── unit/
    │   └── test_models.py    # Model tests (use lazy imports)
    ├── integration/
    │   └── test_endpoints.py # API endpoint tests (✅ working)
    └── fixtures/
        └── factory.py        # Factory Boy factories
```

## Running Tests

**Recommended: Use Django test runner for most comprehensive results:**
```bash
uv run python -m django test api.tests --verbosity=2 --settings=financial_analysis.settings
```

**Alternative: Use pytest for specific endpoint tests:**
```bash
uv run pytest tests/integration/test_endpoints.py -v
```

**Check both:**
```bash
# Django tests
uv run python -m django test api.tests --verbosity=2 --settings=financial_analysis.settings

# Pytest
uv run pytest tests/ -v
```

## Test Coverage

### Main Test Suite (api/tests.py) - 29 Tests
- **Institution Model:** 4 tests (creation, uniqueness, string representation)
- **Account Model:** 5 tests (creation, balance calculation, constraints)
- **Category Model:** 5 tests (hierarchy, slug uniqueness, relationships)
- **Transaction Model:** 7 tests (hash generation, properties, duplicate prevention)
- **ImportLog Model:** 3 tests (creation, duration, string representation)
- **API Endpoints:** 5 tests (list, create, retrieve operations)

### Pytest Structure
- **integration/test_endpoints.py:** 4 endpoint tests (working)
- **unit/test_models.py:** 4 model tests (requires lazy imports within functions)

## Best Practices

1. **Use Django TestCase for model and API tests** (proven to work comprehensively)
2. **Use pytest for integration tests** (good for complex workflows)
3. **Lazy imports within test methods** to avoid Django initialization issues:
   ```python
   @pytest.mark.django_db
   def test_example():
       from api.models import Institution
       # Use model here
   ```
4. **Keep test files focused** on specific functionality
5. **Use factories for consistent test data** (Factory Boy available)

## Installation & Setup

All testing dependencies are already configured in `pyproject.toml`:
```bash
uv sync --all-extras
```

This installs:
- pytest
- pytest-django
- factory-boy
- Other dev tools

## Continuous Integration

For CI/CD pipelines, run both test suites:
```bash
# Primary suite (most comprehensive)
python manage.py test api.tests

# Secondary suite (endpoint integration)
pytest tests/
```

Expected result: ~33 tests passing, 0 failures

