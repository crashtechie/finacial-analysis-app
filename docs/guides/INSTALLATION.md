# Installation and Setup Guide

Complete step-by-step guide to install and run the Financial Analysis API.

## Table of Contents
- [System Requirements](#system-requirements)
- [Quick Start (Dev Container)](#quick-start-dev-container)
- [Local Installation](#local-installation)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Dev Container (Recommended)
- Docker Desktop or Docker Engine
- VS Code with "Remote - Containers" extension
- 4GB RAM minimum, 10GB disk space

### Local Installation
- Python 3.14 or later
- Git
- SQLite3 (usually pre-installed)
- 2GB disk space

## Quick Start (Dev Container)

This is the recommended approach as it handles all setup automatically.

### Steps

1. **Install Prerequisites**
   - Install [Docker Desktop](https://www.docker.com/products/docker-desktop) for your OS
   - Install [VS Code](https://code.visualstudio.com/)
   - Install VS Code extension: "Remote - Containers"

2. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/financial-analysis-app.git
   cd financial-analysis-app
   ```

3. **Open in Container**
   - Open the folder in VS Code
   - Command Palette (Cmd/Ctrl + Shift + P)
   - Search for "Remote-Containers: Reopen in Container"
   - Wait 2-5 minutes for container to build

4. **Verify Installation**
   ```bash
   # Open VS Code terminal (Ctrl + `)
   cd app/backend
   python manage.py check
   ```

   You should see: `System check identified no issues (0 silenced).`

5. **Run Development Server**
   ```bash
   python manage.py runserver
   ```
   - Open http://localhost:8000 in your browser
   - API is at http://localhost:8000/api/

---

## Local Installation

For development without Docker.

### Prerequisites Installation

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.14
brew install python@3.14

# Install Git
brew install git

# Install uv package manager
brew install uv
```

#### Ubuntu/Debian
```bash
# Update package lists
sudo apt update

# Install Python 3.14
sudo apt install python3.14 python3.14-venv python3-pip

# Install Git
sudo apt install git

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows
1. Install [Python 3.14](https://www.python.org/downloads/) - Check "Add to PATH"
2. Install [Git for Windows](https://git-scm.com/download/win)
3. Install [uv](https://github.com/astral-sh/uv#windows) - Use installer or `pip install uv`

### Clone and Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/financial-analysis-app.git
   cd financial-analysis-app
   ```

2. **Create Virtual Environment**
   ```bash
   # Using uv (recommended)
   cd app/backend
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   # Install with uv
   uv sync --all-extras
   
   # Or using pip
   pip install -e ".[dev]"
   ```

4. **Verify Installation**
   ```bash
   python manage.py check
   ```

5. **Run Development Server**
   ```bash
   python manage.py runserver
   ```
   - API available at http://localhost:8000/api/

---

## Configuration

### Environment Variables

The application uses a `.env` file for configuration:

```bash
cd app/backend
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
# ENGINE options: sqlite, postgresql, mysql, mariadb
DATABASE_ENGINE=sqlite
DATABASE_NAME=db.sqlite3

# Required for postgresql, mysql, mariadb (ignored for sqlite)
# DATABASE_USER=your_db_user
# DATABASE_PASSWORD=your_db_password
# DATABASE_HOST=localhost
# DATABASE_PORT=5432

# CORS Settings
CORS_ALLOW_ALL_ORIGINS=True
```

### Database Setup

```bash
cd app/backend

# Run migrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser
```

### Load Sample Data (Optional)

```bash
# Load all fixtures (order matters for foreign key dependencies)
python manage.py loaddata institutions accounts categories transactions import_logs

# Or load individually
python manage.py loaddata api/fixtures/categories.json

# Run setup script
bash scripts/setup_dev_data.sh
```

---

## Verification

Confirm everything is working:

### 1. Check Django Configuration
```bash
cd app/backend
python manage.py check
```

Expected output:
```
System check identified no issues (0 silenced).
```

### 2. Run Tests
```bash
# Run all tests
python manage.py test api.tests

# Run with coverage report
pytest --cov=api api/tests.py
```

Expected: All tests pass (70+ tests)

### 3. Test API Endpoints
```bash
# In another terminal, start server
python manage.py runserver

# In another terminal, test endpoint
curl http://localhost:8000/api/institutions/
```

Expected: JSON response with empty list or institutions

### 4. Access Admin Panel
1. Create superuser (if not done): `python manage.py createsuperuser`
2. Visit: http://localhost:8000/admin/
3. Login with credentials
4. Browse models (Institutions, Accounts, Transactions, etc.)

---

## Development Tools

### Code Formatting
```bash
# Auto-format code
black api/

# Check import order
isort api/

# Run linter
flake8 api/
```

### Testing
```bash
# Run tests with verbose output
python manage.py test api.tests -v 2

# Run specific test
python manage.py test api.tests.InstitutionModelTests

# Run with coverage
pytest --cov=api --cov-report=html api/tests.py
```

### Database Management
```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

---

## Troubleshooting

### Container Build Issues

**Problem:** Container fails to build
```
Solution:
1. Delete container: docker system prune -a
2. Rebuild in VS Code: Remote-Containers: Rebuild Container
```

### Python Version Issues

**Problem:** Python version not 3.14
```bash
# Check version
python --version

# Solutions:
# - Update to Python 3.14 using system package manager
# - Or specify version when running: python3.14 manage.py runserver
```

### Database Errors

**Problem:** "no such table: api_transaction"
```bash
cd app/backend
python manage.py migrate
```

**Problem:** "UNIQUE constraint failed"
```bash
# Delete database and start fresh
rm db.sqlite3
python manage.py migrate
```

### Port Already in Use

**Problem:** Port 8000 already in use
```bash
# Change port
python manage.py runserver 8001

# Or find and kill process using port 8000
lsof -i :8000
kill -9 <PID>
```

### Import Errors

**Problem:** "ModuleNotFoundError: No module named 'django'"
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
uv sync --all-extras
```

### Permission Errors

**Problem:** "Permission denied" on Linux/macOS
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Ensure directory ownership
sudo chown -R $USER ./app/backend
```

---

## Next Steps

After successful installation:

1. **Read the [Architecture Guide](../architecture/SYSTEM_DESIGN.md)** - Understand how the project is structured
2. **Review the [API Reference](../API_REFERENCE.md)** - Learn available endpoints
3. **Check the [Developer Guide](../development/DEVELOPER_GUIDE.md)** - How to extend functionality
4. **Import Sample Data** - Use the import command to load transactions

---

## Getting Help

- Check [Troubleshooting Guide](TROUBLESHOOTING.md) for common issues
- Review [Architecture documentation](../architecture/) for system design
- Check existing [GitHub Issues](https://github.com/yourusername/financial-analysis-app/issues)
- See [Contributing Guide](../CONTRIBUTING.md) for community help
