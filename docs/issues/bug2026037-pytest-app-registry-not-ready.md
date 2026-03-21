# Bug: Pytest collection fails with AppRegistryNotReady on all api/ test files

## Summary
`pytest` fails during collection of all three test files in `api/` (`tests.py`, `tests_coverage.py`, `tests_edge_cases.py`) with `django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.` The Django app registry is never initialized because `pytest-django` is not installed in the main dependency group — it is only listed under `[project.optional-dependencies] dev`. Without `pytest-django`, the `DJANGO_SETTINGS_MODULE` config option in `pytest.ini` is ignored, Django is never bootstrapped, and top-level model imports in the test files fail at collection time.

## Environment
- Date observed: 2026-03-21
- OS: Linux (Debian GNU/Linux 13 / dev container)
- Python: 3.14.3
- pytest: 9.0.2
- Working directory: `app/backend`
- Command: `uv run pytest`

## Steps to Reproduce
1. Set up the dev container or run `uv sync` (without `--extra dev`).
2. Change directory to `app/backend`.
3. Run:
   ```bash
   uv run pytest
   ```

## Expected Behavior
All tests are collected and executed. Django initializes before test modules are imported.

## Actual Behavior
All three test files under `api/` fail during collection with `AppRegistryNotReady`. Pytest also emits a warning confirming the root cause:

```text
PytestConfigWarning: Unknown config option: DJANGO_SETTINGS_MODULE
```

3 errors, 0 tests collected from `api/`.

## Full Error Output
```text
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
testpaths: tests, api
plugins: cov-7.0.0
collecting ... collected 8 items / 3 errors

==================================== ERRORS ====================================
________________________ ERROR collecting api/tests.py _________________________
api/tests.py:13: in <module>
    from api.admin import AccountAdmin, CategoryAdmin, InstitutionAdmin, TransactionAdmin
api/admin.py:8: in <module>
    from .models import Account, Category, ImportLog, Institution, Transaction
api/models.py:12: in <module>
    class Institution(models.Model):
E   django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.

____________________ ERROR collecting api/tests_coverage.py ____________________
api/tests_coverage.py:14: in <module>
    from api.importers import get_importer, list_importers
api/importers/__init__.py:5: in <module>
    from .bank_1 import Bank1Importer
api/importers/bank_1.py:5: in <module>
    from .base import BaseImporter
api/importers/base.py:15: in <module>
    from api.models import Account, Category, ImportLog, Institution, Transaction
api/models.py:12: in <module>
    class Institution(models.Model):
E   django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.

___________________ ERROR collecting api/tests_edge_cases.py ___________________
api/tests_edge_cases.py:12: in <module>
    from api.models import Account, Category, Institution, Transaction
api/models.py:12: in <module>
    class Institution(models.Model):
E   django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.

=============================== warnings summary ===============================
PytestConfigWarning: Unknown config option: DJANGO_SETTINGS_MODULE

=========================== short test summary info ============================
ERROR api/tests.py - django.core.exceptions.AppRegistryNotReady: Apps aren't ...
ERROR api/tests_coverage.py - django.core.exceptions.AppRegistryNotReady: App...
ERROR api/tests_edge_cases.py - django.core.exceptions.AppRegistryNotReady: A...
!!!!!!!!!!!!!!!!!!! Interrupted: 3 errors during collection !!!!!!!!!!!!!!!!!!!!
========================= 1 warning, 3 errors in 5.20s =========================
```

## Notes / Initial Analysis
- The warning `Unknown config option: DJANGO_SETTINGS_MODULE` is the key indicator. This means `pytest-django` is not loaded as a plugin, so pytest does not recognize the setting and never calls `django.setup()`.
- All three test files (`api/tests.py`, `api/tests_coverage.py`, `api/tests_edge_cases.py`) perform top-level imports of Django models. When pytest collects these files, Python executes the imports immediately. Without `django.setup()` having been called first, the Django app registry is not initialized and model class creation fails.
- The test files under `tests/` (`tests/unit/test_models.py`, `tests/integration/test_endpoints.py`) use lazy imports inside test methods, so they are not affected.
- `pytest.ini` takes precedence over `pyproject.toml` (`WARNING: ignoring pytest config in pyproject.toml!`), and `pytest.ini` includes `api` in `testpaths`, which is why these files are collected at all.

## Root Cause
Two contributing factors:

### 1. `pytest-django` is not in main dependencies
In `pyproject.toml`, `pytest-django` is only listed under `[project.optional-dependencies] dev`:

```toml
[project.optional-dependencies]
dev = [
    ...
    "pytest-django>=4.7.0,<5.0",
    ...
]
```

Running `uv sync` without `--extra dev` does not install `pytest-django`. Without this plugin, pytest has no knowledge of Django and never calls `django.setup()`.

### 2. Test files use top-level Django model imports
All three `api/` test files import Django models at module level:

- `api/tests.py` → `from api.admin import ...` → `from .models import ...`
- `api/tests_coverage.py` → `from api.importers import ...` → `from api.models import ...`
- `api/tests_edge_cases.py` → `from api.models import ...`

These imports trigger Django model metaclass registration, which requires the app registry to be ready. Since `pytest-django` never called `django.setup()`, the registry is uninitialized.

## Affected Files
- `api/tests.py` — fails at collection due to top-level import of `api.admin`
- `api/tests_coverage.py` — fails at collection due to top-level import of `api.importers`
- `api/tests_edge_cases.py` — fails at collection due to top-level import of `api.models`

## Solution Options

### Option A: Move `pytest-django` to main dependencies (recommended)
Move `pytest-django` from `[project.optional-dependencies] dev` into `[project] dependencies` so it is always installed when the project is synced:

```toml
[project]
dependencies = [
    ...
    "pytest-django>=4.7.0,<5.0",
    ...
]
```

Then re-sync:
```bash
uv sync
```

### Option B: Always sync with `--extra dev`
Ensure the dev container and all development environments run:

```bash
uv sync --extra dev
```

The `postCreateCommand.sh` already runs `uv sync --extra dev`, but if the container was set up manually or the script was modified, this step may have been missed.

### Option C: Add `django.setup()` to `conftest.py` as a safety net
Add an explicit `django.setup()` call in `tests/conftest.py` so Django is initialized even without `pytest-django`:

```python
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_analysis.settings')
django.setup()
```

Note: This only helps if `conftest.py` is loaded before the `api/` test files. Since `testpaths` includes both `tests` and `api`, and `conftest.py` lives in `tests/`, this may not reliably execute first for `api/` test files.

## Status
**🔴 OPEN**

## Metadata
- **Bug ID**: 2026037
- **Severity**: Critical (blocks test collection for all api/ test files)
- **Impact**: Development workflow (testing, CI/CD)
- **Date Observed**: 2026-03-21
- **Related Config Files**:
  - [app/backend/pyproject.toml](app/backend/pyproject.toml) — `pytest-django` in optional deps only
  - [app/backend/pytest.ini](app/backend/pytest.ini) — `DJANGO_SETTINGS_MODULE` config, `testpaths` includes `api`
  - [app/backend/tests/conftest.py](app/backend/tests/conftest.py) — current test setup
