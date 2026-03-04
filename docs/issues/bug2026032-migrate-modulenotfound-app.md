# Bug: `uv run python manage.py migrate` fails with `ModuleNotFoundError: No module named 'app'`

## Summary
Running Django migrations from `app/backend` with `uv run python manage.py migrate` fails during Django settings import with:

```text
ModuleNotFoundError: No module named 'app'
```

## Environment
- Date observed: 2026-03-02
- OS: Linux (Debian GNU/Linux 13 / dev container)
- Working directory: `app/backend`
- Command: `uv run python manage.py migrate`

## Steps to Reproduce
1. Open a terminal.
2. Change directory to `app/backend`.
3. Run:
   ```bash
   uv run python manage.py migrate
   ```

## Expected Behavior
`migrate` applies pending migrations (or reports that no migrations are pending).

## Actual Behavior
Command exits with code `1` and traceback ending in:

```text
ModuleNotFoundError: No module named 'app'
```

## Full Error (tail)
```text
File "<frozen importlib._bootstrap>", line 1335, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'app'
```

## Notes / Initial Analysis
- Failure occurs while Django initializes settings and imports modules.
- The import path appears to reference `app` as a top-level package, which is not resolvable from the current runtime `PYTHONPATH`/working directory context.

## Root Cause
**`app/backend/manage.py` adds the wrong directory to `sys.path`.**

- `manage.py` computes `PROJECT_ROOT = Path(__file__).resolve().parent` = `/app/backend`
- It adds only `/app/backend` to `sys.path`
- But `DJANGO_SETTINGS_MODULE = 'app.backend.financial_analysis.settings'` tries to import `app` as a top-level package
- Since `app` is a parent directory (not a child of `/app/backend`), the import fails

## Solution Applied
**Updated `app/backend/manage.py`** to add the workspace root to `sys.path` instead:

```python
# Old (broken):
PROJECT_ROOT = Path(__file__).resolve().parent  # /app/backend
sys.path.insert(0, str(PROJECT_ROOT))

# New (fixed):
BACKEND_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = BACKEND_DIR.parent.parent  # /workspaces/finacial-analysis-app
sys.path.insert(0, str(WORKSPACE_ROOT))
```

Now the `app` package is importable from the workspace root, and Django settings imports resolve correctly.

## Status
**✅ RESOLVED** — Migrations now run successfully:
```bash
$ cd app/backend && uv run python manage.py migrate
Operations to perform:
  Apply all migrations: admin, api, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ... (all migrations applied successfully)
```

## Lessons Learned

### 1. Package Path Resolution
- When Django settings are referenced with dotted paths (e.g., `app.backend.financial_analysis.settings`), the root of that path must be in `sys.path`.
- The `manage.py` script is responsible for ensuring the correct Python path setup before importing any Django modules.
- Using relative path calculations (`Path(__file__).resolve().parent`) must account for the actual module structure, not just the file system organization.

### 2. Django Project Structure Constraints
- For a Django project where the `manage.py` resides in a subdirectory (`app/backend`), the DJANGO_SETTINGS_MODULE must be compatible with the sys.path configuration.
- Options:
  - Add workspace root to sys.path + use `app.backend.financial_analysis.settings` (chosen)
  - Add backend dir to sys.path + use `financial_analysis.settings`
  - Current choice maintains full package hierarchy and clarity.

### 3. Testing Impact
- All Django management commands (makemigrations, runserver, test, shell) will use the same sys.path setup.
- Environment-specific overrides or path adjustments should be centralized in `manage.py` or development documentation.

## Next Steps

### Verification
- [x] Verify that other Django management commands work correctly with the fix (e.g., `runserver`, `shell`, `createsuperuser`).
- [x] Test import paths from other entry points (e.g., `wsgi.py`, test runners) to ensure consistency.

### Documentation Updates
- [x] Update CHANGELOG with fix details and version bump to 0.1.1
- [x] Update DEVELOPER_GUIDE with `manage.py` environment setup requirements
- [x] Add troubleshooting section to TROUBLESHOOTING guide

### Release
- [x] Merge `bug/migrate-modulenotfound-app` branch to main.
- [x] Tag release as `v0.1.1`.
- [x] Update version in `pyproject.toml` to `0.1.1`.

## Related Changes
- **Fixed**: [app/backend/manage.py](app/backend/manage.py)
- **Documentation**: 
  - [docs/CHANGELOG.md](docs/CHANGELOG.md)
  - [docs/development/DEVELOPER_GUIDE.md](docs/development/DEVELOPER_GUIDE.md)
  - [docs/guides/TROUBLESHOOTING.md](docs/guides/TROUBLESHOOTING.md)

## Metadata
- **Bug ID**: 2026032
- **Severity**: High (blocks all Django management commands)
- **Impact**: Development workflow (migrations, testing, local execution)
- **Fix Version**: 0.1.1
- **Date Fixed**: 2026-03-02
- **Commit**: 72cd3ad
