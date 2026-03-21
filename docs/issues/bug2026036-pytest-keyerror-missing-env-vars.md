# Bug: Pytest fails with KeyError for database environment variables

## Summary
`pytest` fails on all tests with `KeyError` exceptions because `conftest.py` does not load the `.env` file before Django settings are imported. After updating `settings.py` to require database configuration via `os.environ[]` (no fallback defaults), the test environment lacks the necessary environment variables.

## Environment
- Date observed: 2026-03-20
- OS: Linux (Debian GNU/Linux 13 / dev container)
- Working directory: `app/backend`
- Command: `uv run pytest`

## Steps to Reproduce
1. Change directory to `app/backend`.
2. Ensure `settings.py` uses `os.environ[]` (strict, no defaults) for `DATABASE_ENGINE`, `DATABASE_NAME`, etc.
3. Run:
   ```bash
   uv run pytest
   ```

## Expected Behavior
All tests execute successfully, reading database configuration from the `.env` file.

## Actual Behavior
All tests fail immediately during Django settings initialization with:

```text
KeyError: 'DATABASE_ENGINE'
```

## Full Error (tail)
```text
tests/unit/test_models.py::TestModels::test_institution_can_be_created FAILED
tests/unit/test_models.py::TestModels::test_account_balance_calculation FAILED
tests/integration/test_endpoints.py::TestAPIEndpoints::test_institution_endpoints FAILED

E   KeyError: 'DATABASE_ENGINE'
```

## Notes / Initial Analysis
- The `.env` file contains all required variables (`DATABASE_ENGINE`, `DATABASE_NAME`, etc.).
- Django's `settings.py` loads `.env` via `load_dotenv()` when accessed through `manage.py`, but pytest does not trigger that code path early enough.
- `conftest.py` set `DJANGO_SETTINGS_MODULE` but never called `load_dotenv()`, so the `.env` values were absent from `os.environ` when `settings.py` was imported.

## Root Cause
`tests/conftest.py` was missing a `load_dotenv()` call. When `settings.py` was updated to use `os.environ[]` instead of `os.getenv()` with fallback defaults, the test runner had no way to populate the required environment variables before Django settings were loaded.

The previous `settings.py` used `os.getenv('DATABASE_ENGINE', 'sqlite')` which silently fell back to defaults. The new strict version uses `os.environ['DATABASE_ENGINE']` which raises `KeyError` when the variable is missing.

## Solution Applied
**Added `load_dotenv()` to `tests/conftest.py` before Django settings are imported.**

### Updated `tests/conftest.py`
```python
# Old (broken):
import os
import sys
from pathlib import Path

import pytest

backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_analysis.settings')
```

```python
# New (fixed):
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load .env before Django settings are imported
load_dotenv(backend_dir / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_analysis.settings')
```

## Status
**✅ RESOLVED** — `load_dotenv()` added to `conftest.py`; all tests pass.

## Verification Evidence

### Test Suite
```bash
$ cd app/backend && uv run pytest -q
```

## Lessons Learned

### 1. Strict Environment Configuration Requires Consistent Loading
- When switching from `os.getenv()` with defaults to `os.environ[]` (strict), every entry point that triggers Django settings must load the `.env` file.
- `manage.py` → `settings.py` works because `settings.py` calls `load_dotenv()` itself, but pytest imports settings before that call completes in some configurations.
- `conftest.py` is the earliest reliable hook for pytest and must handle env setup.

### 2. Test Runner Entry Points Differ from Application Entry Points
- Django's `manage.py` and `wsgi.py` both load `.env` as part of their startup.
- Pytest uses `conftest.py` → `DJANGO_SETTINGS_MODULE` → `settings.py`, and if `conftest.py` doesn't load `.env` first, the environment is incomplete.
- Any new entry point (scripts, CLI tools, cron jobs) must also load `.env` or set variables explicitly.

## Related Changes
- **Fixed**:
  - [app/backend/tests/conftest.py](app/backend/tests/conftest.py) — Added `load_dotenv()` call
- **Context** (prior change that exposed this bug):
  - [app/backend/financial_analysis/settings.py](app/backend/financial_analysis/settings.py) — Switched database config from `os.getenv()` with defaults to strict `os.environ[]`

## Metadata
- **Bug ID**: 2026036
- **Severity**: Critical (blocks all test execution)
- **Impact**: Development workflow (testing, CI/CD)
- **Date Observed**: 2026-03-20
- **Date Fixed**: 2026-03-20
