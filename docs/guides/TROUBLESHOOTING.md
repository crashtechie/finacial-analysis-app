# Troubleshooting Guide

Solutions to common issues encountered when working with the Financial Analysis API.

## Table of Contents
- [Installation Issues](#installation-issues)
- [Runtime Errors](#runtime-errors)
- [Database Problems](#database-problems)
- [API Issues](#api-issues)
- [Testing Problems](#testing-problems)
- [Performance Issues](#performance-issues)
- [Getting Additional Help](#getting-additional-help)

---

## Installation Issues

### Port 8000 Already in Use

**Error:**
```
Address already in use ('0.0.0.0', 8000)
```

**Solutions:**

1. **Use a different port:**
   ```bash
   python manage.py runserver 8001
   ```

2. **Kill process using port 8000:**
   ```bash
   # macOS/Linux
   lsof -i :8000
   kill -9 <PID>
   
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

3. **Check running processes:**
   ```bash
   ps aux | grep runserver  # Find and kill stray processes
   ```

---

### Python Version Mismatch

**Error:**
```
python: No module named django
# OR
SyntaxError: invalid syntax (Python 3.13 trying to run 3.14 code)
```

**Solutions:**

1. **Verify Python version:**
   ```bash
   python --version  # Should be 3.14.x
   ```

2. **Use explicit Python version:**
   ```bash
   python3.14 manage.py runserver
   ```

3. **Update Python:**
   ```bash
   # macOS
   brew install python@3.14
   
   # Ubuntu
   sudo apt install python3.14
   
   # Windows - Download from python.org
   ```

4. **Verify virtual environment:**
   ```bash
   which python  # Should point to .venv/bin/python
   python -m venv --help  # If this fails, Python is misconfigured
   ```

---

### ModuleNotFoundError: No module named 'django'

**Error:**
```
ModuleNotFoundError: No module named 'django'
```

**Solutions:**

1. **Activate virtual environment:**
   ```bash
   cd app/backend
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```

2. **Reinstall dependencies:**
   ```bash
   uv sync --all-extras
   # OR
   pip install -e ".[dev]"
   ```

3. **Check installation:**
   ```bash
   pip list | grep -i django
   python -c "import django; print(django.__version__)"
   ```

4. **For Dev Container issues:**
   ```bash
   # Rebuild container
   Command Palette > Remote-Containers: Rebuild Container
   ```

---

### Permission Denied on Scripts

**Error:**
```
bash: ./scripts/setup_dev_data.sh: Permission denied
```

**Solution:**
```bash
chmod +x scripts/*.sh
./scripts/setup_dev_data.sh
```

---

## Runtime Errors

### Django SystemCheckError

**Error:**
```
django.core.management.base.SystemCheckError: SystemCheckError: System check identified some issues
```

**Solutions:**

1. **Run system check:**
   ```bash
   python manage.py check --deploy
   ```

2. **Check settings.py:** Ensure `INSTALLED_APPS` includes all required apps
   ```python
   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       # ... all apps must be listed
       'api',
       'api.analytics',
   ]
   ```

3. **Verify SECRET_KEY:** Should not have spaces or special characters
   ```env
   SECRET_KEY=your-secret-key-without-spaces
   ```

---

### ImportError: Cannot import name 'X' from 'api'

**Error:**
```
ImportError: cannot import name 'Institution' from 'api.models'
```

**Solutions:**

1. **Ensure migrations are applied:**
   ```bash
   python manage.py migrate
   ```

2. **Check model definition:** Verify model exists in `api/models.py`
   ```python
   from api.models import Institution, Account, Category
   ```

3. **Rebuild migrations if needed:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **In tests, use relative imports:**
   ```python
   from .models import Institution  # Not: from api.models import Institution
   ```

---

### IntegrityError: UNIQUE constraint failed

**Error:**
```
django.db.utils.IntegrityError: UNIQUE constraint failed: api_institution.identifier
```

**Causes:**
- Duplicate identifier when creating Institution
- Duplicate transaction hash
- Duplicate category slug

**Solutions:**

1. **Check existing records:**
   ```bash
   python manage.py shell
   >>> from api.models import Institution
   >>> Institution.objects.all()
   ```

2. **Delete duplicates:**
   ```python
   Institution.objects.filter(identifier='duplicate').delete()
   ```

3. **Fresh database (development only):**
   ```bash
   rm db.sqlite3
   python manage.py migrate
   ```

---

## Database Problems

### "no such table: api_transaction"

**Error:**
```
_sqlite3.OperationalError: no such table: api_transaction
```

**Cause:** Migrations not applied

**Solution:**
```bash
python manage.py migrate

# Verify all tables exist
python manage.py dbshell
.tables  # Shows all tables
```

---

### Database Locked

**Error:**
```
database is locked
```

**Causes:**
- Multiple processes accessing database
- Long-running transaction not completed
- Corrupted database file

**Solutions:**

1. **Kill running processes:**
   ```bash
   # Find processes using database
   lsof | grep db.sqlite3
   kill -9 <PID>
   ```

2. **Restart dev server:**
   ```bash
   # Stop with Ctrl+C
   python manage.py runserver
   ```

3. **Clear database (dev only):**
   ```bash
   rm db.sqlite3
   python manage.py migrate
   ```

4. **Check file permissions:**
   ```bash
   ls -la db.sqlite3
   chmod 644 db.sqlite3  # Ensure readable/writable
   ```

---

### Migration Conflicts

**Error:**
```
Conflicting migrations detected; multiple leaf nodes in the migration graph
```

**Solutions:**

1. **Show migration status:**
   ```bash
   python manage.py showmigrations
   ```

2. **Merge migrations:**
   ```bash
   python manage.py makemigrations --merge
   python manage.py migrate
   ```

3. **Last resort (dev only):**
   ```bash
   rm db.sqlite3
   rm api/migrations/0*.py  # Keep only __init__.py
   python manage.py makemigrations
   python manage.py migrate
   ```

---

## API Issues

### CORS Errors

**Error:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:** In `settings.py`:
```python
---

### Django Management Commands: ModuleNotFoundError

**Error:**
```
ModuleNotFoundError: No module named 'app'
```

**When This Occurs:**
- Running `python manage.py migrate`
- Running `python manage.py makemigrations`
- Running any other `manage.py` command
- Running from the wrong directory or with incorrect Python path

**Root Cause:**
The Django settings module is referenced as `financial_analysis.settings`. If commands are run from the wrong directory, imports and Python path resolution can fail. The `manage.py` script configures the path correctly when run from `app/backend`.

**Solutions:**

1. **Run from `app/backend` directory (REQUIRED):**
   ```bash
   cd app/backend
   python manage.py migrate
   # OR
   uv run python manage.py migrate
   ```
   
   ❌ **DO NOT run from workspace root:**
   ```bash
   cd /workspaces/finacial-analysis-app
   python manage.py migrate  # This will fail!
   ```

2. **Check working directory:**
   ```bash
   pwd  # Should output: /path/to/app/backend
   ls -la manage.py  # Should find manage.py in current directory
   ```

3. **Verify Python path configuration:** The `manage.py` script should add workspace root automatically:
   ```bash
   python -c "import manage; import sys; print(sys.path[:2])"
   ```

4. **For virtual environment issues:**
   ```bash
   # Ensure venv is activated
   which python  # Should show .venv/bin/python
   
   # If not activated:
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

**Related Documentation:**
- See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#django-management-commands---environment-setup) for detailed setup information
- See [bug2026032](../issues/bug2026032-migrate-modulenotfound-app.md) for full technical details

# For development - allow all origins
CORS_ALLOW_ALL_ORIGINS = True

# For production - specify allowed origins
CORS_ALLOWED_ORIGINS = [
    "https://myapp.com",
    "https://www.myapp.com",
]
```

---

### 404 Not Found on Endpoints

**Error:**
```
HTTP 404: Not found
GET /api/transactions/
```

**Solutions:**

1. **Verify URL patterns:** Check `urls.py`:
   ```python
   path('api/', include(api_urls)),
   path('api/analytics/', include(analytics_urls)),
   ```

2. **Check routers are registered:**
   ```python
   from rest_framework.routers import DefaultRouter
   router = DefaultRouter()
   router.register('institutions', InstitutionViewSet)
   # ... etc
   ```

3. **Test endpoint:**
   ```bash
   curl -v http://localhost:8000/api/institutions/
   ```

4. **Restart server** after URL changes:
   ```bash
   # Stop with Ctrl+C
   python manage.py runserver
   ```

---

### 403 Forbidden

**Error:**
```
HTTP 403: Forbidden
```

**Cause:** Permission classes restricting access

**Solution:** In `settings.py` (for development):
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}
```

---

### Pagination Not Working

**Issue:** `page` parameter ignored, all results returned

**Solution:**

1. **Ensure paginator is set:**
   ```python
   # settings.py
   REST_FRAMEWORK = {
       'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
       'PAGE_SIZE': 50
   }
   ```

2. **Test pagination:**
   ```bash
   curl "http://localhost:8000/api/transactions/?page=2"
   ```

---

## Testing Problems

### Tests Not Discovering

**Error:**
```
Ran 0 tests
```

**Solutions:**

1. **Check test discovery:**
   ```bash
   python manage.py test --help | grep -A 5 "test labels"
   ```

2. **Run specific test file:**
   ```bash
   python manage.py test api.tests.InstitutionModelTests
   ```

3. **Ensure test methods start with `test_`:**
   ```python
   def test_institution_creation(self):  # ✓ Discovered
       pass
   
   def institution_creation(self):  # ✗ Not discovered
       pass
   ```

---

### ImportError in Tests

**Error:**
```
ImportError: Failed to import test module: tests
ModuleNotFoundError: No module named 'api'
```

**Cause:** Test using absolute imports instead of relative imports

**Solution:**
```python
# ✗ Wrong
from api.models import Institution

# ✓ Correct (in tests.py)
from .models import Institution
```

---

### Database State Bleeding Between Tests

**Issue:** Test data from one test affects another test

**Cause:** Not using Django TestCase or test database not rolling back

**Solution:**

```python
from django.test import TestCase

class MyTests(TestCase):  # Use TestCase, not unittest.TestCase
    def setUp(self):
        # This runs before each test
        self.institution = Institution.objects.create(...)
    
    # Database is rolled back after each test automatically
```

---

### Slow Tests

**Issue:** Tests taking 30+ seconds

**Cause:** Database operations or external API calls

**Solutions:**

1. **Use transaction rollback:**
   ```python
   from django.test import TransactionTestCase
   
   class MyTests(TransactionTestCase):
       # Slower than TestCase but supports transactions
       pass
   ```

2. **Mock external calls:**
   ```python
   from unittest.mock import patch
   
   @patch('api.importers.bank_1.requests.get')
   def test_importer(self, mock_get):
       mock_get.return_value.json.return_value = {...}
   ```

3. **Run tests in parallel:**
   ```bash
   pytest -n auto api/tests.py
   ```

---

## Performance Issues

### Slow API Responses

**Issue:** Endpoint takes 5+ seconds to respond

**Solutions:**

1. **Check for N+1 queries:** Use `select_related()` and `prefetch_related()`
   ```python
   # Slow
   transactions = Transaction.objects.all()
   for t in transactions:
       print(t.account.institution.name)  # Query per transaction
   
   # Fast
   transactions = Transaction.objects.select_related(
       'account__institution'
   ).all()
   ```

2. **Add database indexes:**
   ```python
   class Meta:
       indexes = [
           models.Index(fields=['account', 'date']),
           models.Index(fields=['category']),
       ]
   ```

3. **Use pagination:**
   ```bash
   # Instead of fetching all: /api/transactions/
   curl "http://localhost:8000/api/transactions/?page_size=50&page=1"
   ```

4. **Cache results:**
   ```python
   from django.views.decorators.cache import cache_page
   
   @cache_page(60 * 15)  # Cache for 15 minutes
   def get_analytics(request):
       pass
   ```

---

### High Memory Usage

**Issue:** Process consuming 500MB+ RAM

**Solutions:**

1. **Use iterators for large queries:**
   ```python
   # Instead of loading all into memory
   for transaction in Transaction.objects.all():  # Loads all at once
       process(transaction)
   
   # Use iterator()
   for transaction in Transaction.objects.iterator(chunk_size=1000):
       process(transaction)
   ```

2. **Close unnecessary connections:**
   ```python
   from django.db import connection
   connection.close()
   ```

3. **Monitor with:**
   ```bash
   top -p $(pgrep -f "manage.py runserver")
   ```

---

## Getting Additional Help

### Check Logs

1. **Django logs:**
   ```bash
   # Enable debug logging
   # settings.py
   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'handlers': {
           'console': {'class': 'logging.StreamHandler'},
       },
       'loggers': {
           'django': {'handlers': ['console'], 'level': 'DEBUG'},
       },
   }
   ```

2. **Server output:** Watch VS Code terminal for errors

3. **Database logs:**
   ```bash
   # Enable query logging
   # settings.py
   LOGGING = {
       'loggers': {
           'django.db.backends': {'level': 'DEBUG'},
       },
   }
   ```

### Run Diagnostics

```bash
# System check
python manage.py check --deploy

# Show environment
python -m django --version

# Test database connection
python manage.py dbshell
.quit

# Verify imports
python -c "from api.models import *; print('OK')"
```

### Documentation References

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Project Architecture](../architecture/SYSTEM_DESIGN.md)
- [API Reference](../API_REFERENCE.md)

### Get Community Help

1. Check [GitHub Issues](https://github.com/yourusername/financial-analysis-app/issues)
2. Search [Django Forum](https://forum.djangoproject.com/)
3. Ask on [Stack Overflow](https://stackoverflow.com/questions/tagged/django) with tag `django`
4. Check [Contributing Guide](../CONTRIBUTING.md) for project-specific help
