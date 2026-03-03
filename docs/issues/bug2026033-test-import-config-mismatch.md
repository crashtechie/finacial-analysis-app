# Bug: Pytest model tests fail due to Django import/configuration mismatch

## Summary
`pytest` fails in model tests because Django app registration and import paths are inconsistent across project configuration files.

## Environment
- Date observed: 2026-03-02
- OS: Linux (Debian GNU/Linux 13 / dev container)
- Working directory: `app/backend`
- Command: `uv run pytest -q`

## Steps to Reproduce
1. Change directory to `app/backend`.
2. Run:
   ```bash
   uv run pytest -q
   ```

## Expected Behavior
All tests execute with Django apps correctly registered.

## Actual Behavior
Model tests fail with:

```text
RuntimeError: Model class api.models.Institution doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.
```

## Root Cause
Project files reference two conflicting module styles:

- Local style used by tests/pytest:
  - `DJANGO_SETTINGS_MODULE = financial_analysis.settings`
  - imports like `from api.models import ...`
- Prefixed style used in settings/urls/app config:
  - `app.backend.api`
  - `app.backend.financial_analysis.*`

This mismatch causes Django to not treat `api.models` as part of an installed app during tests.

## Proposed Fix
Normalize Django configuration to local package layout consistently:
- `INSTALLED_APPS`: use `api`
- `ROOT_URLCONF`: `financial_analysis.urls`
- `WSGI_APPLICATION`: `financial_analysis.wsgi.application`
- ASGI/WSGI `DJANGO_SETTINGS_MODULE`: `financial_analysis.settings`
- URL includes: `api.urls` and `api.analytics.urls`
- `api.apps.ApiConfig.name = 'api'`

## Acceptance Criteria
- `uv run pytest -q` exits with code `0`
- No `app_label`/`INSTALLED_APPS` runtime error in model tests
- Integration and unit tests both pass

## Status
**✅ RESOLVED**

## Verification Evidence

### Django Check
```bash
$ cd app/backend && uv run python manage.py check
System check identified no issues (0 silenced).
```

### Test Suite
```bash
$ cd app/backend && uv run pytest -q
============================= test session starts ==============================
collected 8 items

tests/integration/test_endpoints.py ....
tests/unit/test_models.py ....

============================== 8 passed in 0.41s ===============================
```

## Files Updated to Fix Issue
- `app/backend/api/apps.py`
- `app/backend/financial_analysis/settings.py`
- `app/backend/financial_analysis/asgi.py`
- `app/backend/financial_analysis/wsgi.py`
- `app/backend/financial_analysis/urls.py`
- `app/backend/api/urls.py`
- `app/backend/api/analytics/views.py`
- `app/backend/api/management/commands/import_transactions.py`
- `app/backend/api/importers/base.py`
- `app/backend/manage.py`
