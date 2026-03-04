# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Financial Analysis Application.

## Overview

The CI/CD pipeline is implemented using GitHub Actions and consists of three main components:

1. **CI Pipeline** ([.github/workflows/ci.yml](../../.github/workflows/ci.yml)) - Automated testing and quality checks
2. **Security Scanning** ([.github/workflows/security.yml](../../.github/workflows/security.yml)) - Security vulnerability detection
3. **Dependabot** ([.github/dependabot.yml](../../.github/dependabot.yml)) - Automated dependency updates

## CI Pipeline

### Triggers

The CI pipeline runs automatically on:

- **Push events** to `develop` and `main` branches
- **Pull requests** targeting `develop` and `main` branches

### Jobs

#### 1. Backend Tests & Coverage

**Purpose:** Validate backend functionality and enforce code coverage standards.

**Steps:**

1. Set up Python 3.14 environment
2. Install `uv` package manager
3. Install Python dependencies from [app/backend/pyproject.toml](../../app/backend/pyproject.toml)
4. Run database migrations
5. Load fixture data (categories)
6. Execute pytest with coverage analysis
7. Upload coverage report as artifact
8. **Enforcement:** Pipeline fails if coverage < 80%

**Local Testing:**

```bash
cd app/backend
uv run pytest --cov=api --cov-report=term --cov-fail-under=80 api/tests.py
```

#### 2. Backend Code Quality

**Purpose:** Ensure code follows style guidelines and best practices.

**Checks:**

- **Black:** Code formatting validation
- **Flake8:** PEP 8 compliance and code quality
- **isort:** Import statement organization

**Local Testing:**

```bash
cd app/backend
uv run black --check api/
uv run flake8 api/
uv run isort api/ --check-only
```

**Auto-fix locally:**

```bash
cd app/backend
uv run black api/
uv run isort api/
```

#### 3. Frontend Quality Checks

**Purpose:** Validate frontend code quality and build process.

**Checks:**

- **TypeScript Type Checking:** Validates type safety
- **ESLint:** Code quality and style validation
- **Production Build:** Ensures build completes successfully

**Local Testing:**

```bash
cd app/frontend
npm run type-check
npm run lint
npm run build
```

**Note:** Frontend unit tests will be added to CI once test files are implemented. The framework is configured in [app/frontend/vitest.config.ts](../../app/frontend/vitest.config.ts).

## Security Scanning

### Triggers

Security scans run on:

- **Push events** to `develop` and `main` branches
- **Pull requests** targeting `develop` and `main` branches
- **Weekly schedule:** Every Monday at 9:00 AM UTC

### Jobs

#### 1. CodeQL Security Analysis

**Purpose:** Detect security vulnerabilities and code quality issues using GitHub's semantic code analysis.

**Languages Scanned:**

- Python (backend code in [app/backend/api/](../../app/backend/api/))
- JavaScript/TypeScript (frontend code in [app/frontend/src/](../../app/frontend/src/))

**Queries:** Uses `security-extended` query suite for comprehensive scanning.

**Results:** Automatically uploaded to GitHub Security tab under "Code scanning alerts".

#### 2. Bandit Python Security Scan

**Purpose:** Identify common security issues in Python code using Bandit.

**Configuration:**

- Confidence level: Medium and High (-ll flag)
- Recursive scan of [app/backend/api/](../../app/backend/api/) directory
- Results uploaded to GitHub Security tab

**Local Testing:**

```bash
cd app/backend
pip install bandit
bandit -r api/ -ll
```

**Common Issues Detected:**

- Hardcoded passwords or secrets
- SQL injection vulnerabilities
- Use of insecure functions (eval, exec, pickle)
- Weak cryptographic algorithms

#### 3. npm Audit (Frontend Dependencies)

**Purpose:** Scan frontend dependencies for known vulnerabilities.

**Configuration:**

- Audit level: Moderate (for reporting), High (for failure)
- Scans packages in [app/frontend/package.json](../../app/frontend/package.json)

**Local Testing:**

```bash
cd app/frontend
npm audit
npm audit --audit-level=moderate
```

**Handling Vulnerabilities:**

1. Review vulnerability details in npm audit report
2. Update vulnerable packages: `npm update [package-name]`
3. If no fix available, assess risk and document in security review
4. Use `npm audit fix` for automatic fixes (test thoroughly after)

#### 4. Dependency Review

**Purpose:** Analyze dependency changes in pull requests.

**Features:**

- Runs only on pull requests
- Detects new vulnerabilities introduced by dependency changes
- Posts summary comment in PR
- Fails on moderate or higher severity vulnerabilities

## Dependabot Configuration

### Update Schedule

Dependabot checks for dependency updates **weekly on Mondays at 9:00 AM UTC**.

### Package Ecosystems

#### 1. Python (Backend)

**Directory:** `/app/backend`  
**Target Branch:** `develop`

**Grouped Updates:**

- **django-ecosystem:** Django core and Django REST Framework
- **dev-tools:** Black, Flake8, isort, pytest
- **data-processing:** pandas, python-dateutil

#### 2. npm (Frontend)

**Directory:** `/app/frontend`  
**Target Branch:** `develop`

**Grouped Updates:**

- **react-ecosystem:** React and React type definitions
- **build-tools:** Vite, TypeScript
- **testing-tools:** Vitest, Testing Library
- **linting-tools:** ESLint and TypeScript ESLint

#### 3. GitHub Actions

**Directory:** `/`  
**Target Branch:** `develop`

Updates action versions in workflow files to latest releases.

### Managing Dependabot PRs

1. **Review the PR:** Check changelog and breaking changes
2. **Wait for CI:** Ensure all tests pass
3. **Test locally if needed:**

   ```bash
   # Backend
   cd app/backend
   uv sync --extra dev
   uv run pytest

   # Frontend
   cd app/frontend
   npm install
   npm run build
   ```

4. **Merge to develop:** After validation
5. **Monitor:** Watch for issues in develop before promoting to main

## Running Checks Locally

### Before Committing

Run these commands to catch issues before pushing:

```bash
# Backend - Full validation
cd app/backend
uv run black api/                                    # Format code
uv run isort api/                                    # Sort imports
uv run flake8 api/                                   # Lint code
uv run pytest --cov=api --cov-fail-under=80         # Run tests with coverage

# Frontend - Full validation
cd app/frontend
npm run type-check                                   # Check types
npm run lint                                         # Lint code
npm run build                                        # Build production bundle

# Security - Optional local scans
cd app/backend
bandit -r api/ -ll                                   # Python security scan

cd app/frontend
npm audit --audit-level=moderate                     # npm vulnerability scan
```

### Quick Pre-Push Check

```bash
# Backend quick check
cd app/backend && uv run pytest && uv run black --check api/ && cd ../..

# Frontend quick check
cd app/frontend && npm run lint && npm run type-check && cd ../..
```

## CI/CD Pipeline Artifacts

### Coverage Reports

- **Location:** GitHub Actions → Workflow run → Artifacts section
- **Format:** XML (Cobertura format)
- **Retention:** 30 days
- **Usage:** Download for detailed coverage analysis or integration with coverage services

### Security Scan Results

- **Location:** GitHub Security tab → Code scanning alerts
- **Sources:** CodeQL, Bandit SARIF uploads
- **Persistence:** Permanent until resolved
- **Notifications:** Configurable in repository settings

## Troubleshooting

### Common CI Failures

#### Backend Tests Failing

**Symptom:** Test suite fails in CI but passes locally

**Possible Causes:**

1. **Missing migrations:** Run `python manage.py makemigrations --check` locally
2. **Missing fixtures:** Ensure [app/backend/api/fixtures/categories.json](../../app/backend/api/fixtures/categories.json) exists
3. **Environment differences:** Check Python version (requires 3.14+)
4. **Database state:** CI uses fresh SQLite DB, ensure tests don't depend on existing data

**Solution:**

```bash
cd app/backend
rm -f db.sqlite3  # Start fresh
uv run python manage.py migrate
uv run python manage.py loaddata api/fixtures/categories.json
uv run pytest
```

#### Coverage Below Threshold

**Symptom:** `FAIL Required test coverage of 80% not reached. Total coverage: XX.XX%`

**Solution:**

1. Identify untested code: `uv run pytest --cov=api --cov-report=html`
2. Open `app/backend/htmlcov/index.html` in browser
3. Add tests for uncovered lines
4. See [TESTING.md](TESTING.md) for testing guidelines

#### Black/isort Formatting Issues

**Symptom:** `Files would be reformatted` or `Imports are incorrectly sorted`

**Solution:**

```bash
cd app/backend
uv run black api/      # Auto-format
uv run isort api/      # Auto-sort imports
git add api/
git commit --amend --no-edit  # Amend your commit
git push --force-with-lease    # Force push if already pushed
```

#### Flake8 Linting Errors

**Symptom:** Flake8 reports style violations

**Common Issues:**

- Line too long (E501): Break into multiple lines
- Unused imports (F401): Remove unused imports
- Undefined names (F821): Fix variable/function names

**Solution:**

```bash
cd app/backend
uv run flake8 api/  # See detailed errors
# Fix issues manually
```

#### Frontend Build Failures

**Symptom:** `npm run build` fails in CI

**Possible Causes:**

1. **TypeScript errors:** Run `npm run type-check` locally
2. **Missing dependencies:** Ensure `package-lock.json` is committed
3. **Environment variables:** Vite build uses `VITE_` prefixed vars

**Solution:**

```bash
cd app/frontend
npm ci                    # Clean install
npm run type-check       # Check types
npm run build            # Test build
```

#### npm Audit Failures

**Symptom:** Security vulnerabilities detected

**Solution:**

1. Review vulnerabilities: `npm audit`
2. Update packages: `npm update`
3. For unfixable issues:
   - Assess risk (is vulnerable code path used?)
   - Document in security review
   - Create issue to track
   - If critical, consider alternative package

### Python 3.14 Availability

**Issue:** Python 3.14 may not be available in all CI runners yet.

**Temporary Solution:** Update [.github/workflows/ci.yml](../../.github/workflows/ci.yml) and [.github/workflows/security.yml](../../.github/workflows/security.yml) to use Python 3.13 or 3.12 if 3.14 setup fails:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.13" # or '3.12'
```

## Branch Protection Rules

### Recommended Settings

#### For `main` branch:

- ✅ Require pull request reviews before merging (1 reviewer minimum)
- ✅ Require status checks to pass before merging
  - `Backend Tests & Coverage`
  - `Backend Code Quality`
  - `Frontend Quality Checks`
  - `CodeQL Security Analysis`
  - `Bandit Python Security Scan`
  - `npm Audit (Frontend Dependencies)`
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings

#### For `develop` branch:

- ✅ Require status checks to pass before merging (same as main)
- ⚠️ Optional: Require pull request reviews (0 or 1 reviewer)

### How to Configure

1. Go to GitHub repository → Settings → Branches
2. Click "Add rule" or edit existing rule
3. Set "Branch name pattern": `main` or `develop`
4. Enable protections as listed above
5. Click "Create" or "Save changes"

## GitHub Secrets (Future Use)

Currently, no secrets are required for the CI/CD pipeline. When deploying or integrating external services, add secrets in:

**GitHub Repository → Settings → Secrets and variables → Actions**

Common secrets to add later:

- `DJANGO_SECRET_KEY` - Production Django secret key
- `DATABASE_URL` - Production database connection string
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` - For S3 or ECS deployment
- `CODECOV_TOKEN` - For coverage reporting to Codecov (optional)

## Monitoring and Notifications

### Email Notifications

Configure in: **GitHub → Settings → Notifications**

Options:

- Email on workflow run failure
- Email on security alert
- Email on Dependabot PR

### GitHub Security Advisories

Enable in: **Repository → Settings → Security & analysis**

Features:

- Dependabot alerts
- Dependabot security updates
- Code scanning alerts
- Secret scanning alerts

## Performance Optimization

### Caching Strategy

The CI pipeline uses caching to speed up builds:

- **uv dependencies:** Cached based on `pyproject.toml` and `uv.lock` hashes
- **npm packages:** Cached automatically by `actions/setup-node` using `package-lock.json`

**Expected Build Times:**

- Backend tests: 1-2 minutes (with cache)
- Backend lint: 30-60 seconds (with cache)
- Frontend quality: 2-3 minutes (with cache)
- Security scans: 3-5 minutes

### Reducing CI Time

If CI becomes slow:

1. **Parallelize more:** Jobs already run in parallel, but steps within jobs are sequential
2. **Skip frontend build on backend-only changes:** Use path filters in workflow
3. **Split tests:** Run unit and integration tests as separate jobs
4. **Use pre-built Docker images:** Create base image with dependencies pre-installed

## Related Documentation

- [TESTING.md](TESTING.md) - Comprehensive testing guide
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Development setup and workflows
- [DEPLOYMENT.md](../deployment/DEPLOYMENT.md) - Production deployment procedures
- [SECURITY_AND_GOVERNANCE.md](../security/SECURITY_AND_GOVERNANCE.md) - Security policies
- [API_REFERENCE.md](../reference/API_REFERENCE.md) - API documentation

## Changelog

### 2026-03-04 - Initial CI/CD Implementation

**Added:**

- GitHub Actions CI workflow with backend tests (80% coverage enforcement)
- GitHub Actions security scanning workflow (CodeQL, Bandit, npm audit)
- Dependabot configuration for Python, npm, and GitHub Actions
- Comprehensive CI/CD documentation

**Pipeline Features:**

- Automated testing on push to develop/main branches
- Code quality enforcement (Black, Flake8, isort, ESLint)
- Security vulnerability scanning with multiple tools
- Weekly dependency update PRs via Dependabot
- Test coverage reporting and artifact uploads

## Support

For CI/CD issues or questions:

1. Check this documentation first
2. Review [TROUBLESHOOTING.md](../guides/TROUBLESHOOTING.md)
3. Check GitHub Actions logs for detailed error messages
4. Create an issue with the `ci` label for persistent problems
