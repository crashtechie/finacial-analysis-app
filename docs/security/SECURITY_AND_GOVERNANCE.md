# Security & Governance Guide

Comprehensive security, financial governance, software development, and IT best practices for the Financial Analysis API project.

## Table of Contents
- [Security Overview](#security-overview)
- [Financial Data Protection](#financial-data-protection)
- [Credential & Secret Management](#credential--secret-management)
- [Access Control](#access-control)
- [Code Security](#code-security)
- [Deployment Security](#deployment-security)
- [Audit & Compliance](#audit--compliance)
- [Incident Response](#incident-response)
- [Development Best Practices](#development-best-practices)

---

## Security Overview

### Security Principles

This project adheres to the following core security principles:

1. **Principle of Least Privilege** - Users and systems have minimal necessary permissions
2. **Defense in Depth** - Multiple layers of security controls
3. **Fail Secure** - When a control fails, it defaults to secure state
4. **Separation of Duties** - Critical functions separated across multiple people/systems
5. **Transparency** - Security practices are open and documented

### Security Levels

```
Level 1: Development
├── Debug enabled
├── SQLite database
├── CORS: All origins
└── Permissions: AllowAny

Level 2: Staging
├── Debug disabled
├── PostgreSQL database
├── CORS: Specific domains
└── Permissions: Authenticated

Level 3: Production
├── All security hardened
├── Full encryption
├── Comprehensive monitoring
└── Full audit logging
```

---

## Financial Data Protection

### CRITICAL: Never Commit Sensitive Data

**NEVER commit the following to version control:**

❌ Bank statements (PDF files)
❌ Transaction export files (CSV files)
❌ Account numbers or full card numbers
❌ Database files with real data (*.sqlite3, *.db)
❌ Environment files with secrets (.env)
❌ API keys or credentials
❌ Personal financial information

### Protected File Categories

Your `.gitignore` protects against committing:

#### 1. Financial Documents
```
finances/              # Entire financial documents directory
*.pdf                 # All PDF files (statements)
*.csv                 # All CSV files (transactions)
*.xlsx, *.xls        # Spreadsheets with data
*.ofx, *.qbo         # Bank export formats
*statement*          # Anything with "statement" in name
*transaction*        # Transaction files
*bank*               # Bank documents
```

#### 2. Database Files with Data
```
*.sqlite3            # SQLite databases
*.db                 # All database files
db.sqlite3-journal   # Database journals
*.backup             # Database backups
/backups/            # Backup directories
```

#### 3. Environment & Secrets
```
.env                 # Actual environment variables
.env.local           # Local environment overrides
.env.production      # Production environment file
.env.staging         # Staging environment file
*.pem, *.key         # Private keys
*.p12, *.jks         # Certificate files
```

### Data Classification

**Public** - Committed to repository
- Code and documentation
- Structure and architecture
- API design and patterns
- Configuration templates

**Confidential** - Never committed
- Environment variables
- API keys and tokens
- Database credentials
- Private certificates

**Restricted** - Manual secure storage
- Financial documents
- Real transaction data
- Personal financial information
- User data dumps

### Safe Development with Real Data

If you must work with real financial data locally:

```bash
# 1. Create local-only .env
cp .env.example .env.local
# Edit with local database path

# 2. Use local database (separate from version control)
export DATABASE_PATH=./db.local.sqlite3

# 3. Add to .gitignore:
db.local.sqlite3
db.*.sqlite3

# 4. Never add .gitignore to commits
git update-index --assume-unchanged .gitignore
```

---

## Credential & Secret Management

### Secret Hierarchy

```
Development (Least Sensitive)
  ├── Generic test secrets
  ├── Public API keys (if any)
  └── Non-critical database credentials

Staging (Medium)
  ├── Staging API keys
  ├── Staging database credentials
  └── Staging deployment keys

Production (Most Sensitive)
  ├── Production SECRET_KEY
  ├── Production database credentials
  ├── Production API keys
  └── Production deployment keys
```

### Managing Secrets

#### Development
```bash
# Copy template
cp .env.example .env

# Edit with development values
nano .env

# NEVER commit this file
# Verify it's in .gitignore
grep "^\.env$" .gitignore
```

#### Production / Staging
```bash
# Use environment variable 
# service (Heroku, AWS Secrets Manager, GitLab CI Secrets)

# Example: Heroku
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG="False"
heroku config:set ALLOWED_HOSTS="yourdomain.com"

# Example: AWS Secrets Manager
aws secretsmanager create-secret \
  --name prod/financial-api \
  --secret-string '{"SECRET_KEY":"...","DB_PASSWORD":"..."}'

# Example: GitLab CI
# Set in: Settings > CI/CD > Variables
PRODUCTION_SECRET_KEY = "your-secret-key"
DATABASE_PASSWORD = "secure-password"
```

### Secret Rotation

```bash
# Rotate secrets regularly (quarterly minimum)

# 1. Generate new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 2. Update in secret management system
heroku config:set SECRET_KEY="new-secure-key"

# 3. Deploy application
git push heroku main

# 4. Document rotation
# Add to AUDIT_LOG.md:
# - Rotation date
# - Keys affected
# - New expiry date (3 months)
```

### Credential Audit

```bash
# Check for exposed secrets in git history
git log -p --all -S 'password' | head -50
git log -p --all -S 'SECRET_KEY' | head -50
git log -p --all -S 'api_key' | head -50

# Use tools to detect secrets
# uv tool install detect-secrets
detect-secrets scan --all-files

# GitLab: Enable secret detection
# Settings > Security & Compliance > Enable Secret Detection
```

---

## Access Control

### Authentication & Authorization

#### Development
```python
# settings.py - Development
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}
DEBUG = True
```

#### Production
```python
# settings.py - Production
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}
DEBUG = False

# Require SSL
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### User Roles & Permissions

```python
# Define roles for multi-user future
ROLES = {
    'viewer': {
        'permissions': ['view_transactions', 'view_reports'],
        'description': 'Read-only access to transactions'
    },
    'editor': {
        'permissions': ['view_transactions', 'edit_transactions', 'import_transactions'],
        'description': 'Can edit transactions and import'
    },
    'admin': {
        'permissions': ['*'],  # All permissions
        'description': 'Full system access'
    }
}
```

### Password Policy

```python
# Django settings for password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Minimum 12 characters
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

---

## Code Security

### Secure Coding Practices

#### 1. Input Validation
```python
# ✓ Validate all user input
from django.core.exceptions import ValidationError

def import_csv_file(file):
    if not file.name.endswith('.csv'):
        raise ValidationError("Only CSV files allowed")
    
    if file.size > 10 * 1024 * 1024:  # 10MB limit
        raise ValidationError("File too large")
    
    return parse_csv(file)
```

#### 2. SQL Injection Prevention
```python
# ✓ Use ORM queries (never raw SQL)
# Good
transactions = Transaction.objects.filter(
    account=account,
    date__gte=start_date
)

# ✗ Bad - vulnerable to SQL injection
from django.db import connection
cursor = connection.cursor()
cursor.execute(f"SELECT * FROM transactions WHERE account_id = {account_id}")

# If raw SQL necessary, use parameterized queries
cursor.execute(
    "SELECT * FROM transactions WHERE account_id = %s",
    [account_id]
)
```

#### 3. Cross-Site Scripting (XSS) Prevention
```python
# ✓ Escape output (Django templates do this automatically)
# template.html
{{ transaction.description }}  <!-- Automatically escaped -->

# ✓ Explicit escaping if needed
from django.utils.html import escape
safe_description = escape(user_input)

# ✗ Never use |safe without verification
{{ user_input|safe }}  <!-- Vulnerable! -->
```

#### 4. Cross-Site Request Forgery (CSRF) Prevention
```python
# ✓ Django includes CSRF protection by default
# In templates, include CSRF token
{% csrf_token %}

# In API, use CSRF middleware
MIDDLEWARE = [
    ...
    'django.middleware.csrf.CsrfViewMiddleware',
    ...
]
```

#### 5. Sensitive Data Handling
```python
# ✗ Don't log sensitive data
logger.error(f"Failed to import: {password}")  # Bad!

# ✓ Log securely
logger.error(f"Failed to import transaction")  # Good

# ✓ Mask sensitive data in logs
def mask_account_number(account_number):
    if len(account_number) > 4:
        return f"****{account_number[-4:]}"
    return account_number

logger.info(f"Imported to account {mask_account_number(acc_num)}")
```

#### 6. Dependency Security
```bash
# Install safety tool (one time)
uv tool install safety

# Check for vulnerable dependencies
safety check

# Update dependencies regularly
uv sync

# Lock dependencies (pyproject.toml already defines versions)
# uv automatically locks versions in uv.lock
```

---

## Deployment Security

### Pre-deployment Checklist

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` is strong and random
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] HTTPS/SSL certificates valid
- [ ] Database credentials rotated
- [ ] API keys rotated
- [ ] Backups configured and tested
- [ ] Monitoring and alerts enabled
- [ ] Security headers set
- [ ] CORS restricted to expected domains
- [ ] No test data in production database
- [ ] All dependencies up to date

### Security Headers

```python
# settings.py - Production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),
    'style-src': ("'self'", "'unsafe-inline'"),
}

# HSTS - Force HTTPS
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Database Security

```python
# Production database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),  # Never hardcode
        'HOST': os.getenv('DB_HOST'),
        'PORT': '5432',
        
        # Security options
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'require',  # Require SSL
            'connect_timeout': 10,
        }
    }
}

# Backup strategy
# Daily encrypted backups to secure storage
# Retention: 30 days
# Test restore quarterly
```

---

## Audit & Compliance

### Audit Logging

```python
# Log all important actions
import logging

audit_logger = logging.getLogger('audit')

# Log successful imports
audit_logger.info(
    f"Import completed",
    extra={
        'user': request.user.username,
        'action': 'import_transactions',
        'file': filename,
        'records': count,
        'account': account_id,
        'timestamp': timezone.now().isoformat(),
    }
)

# Log failed security operations
audit_logger.warning(
    f"Unauthorized access attempt",
    extra={
        'user': request.user.username,
        'resource': resource,
        'timestamp': timezone.now().isoformat(),
        'ip_address': get_client_ip(request),
    }
)
```

### Compliance Requirements

This project handles financial data and should comply with:

1. **Personal Financial Information (PFI) Protection**
   - Limit access, encrypt at rest and in transit
   - Regular access reviews
   - Incident reporting procedures

2. **Data Privacy (GDPR if EU users)**
   - Right to access
   - Right to erasure
   - Data portability
   - Breach notification

3. **SOC 2 Type II (if SaaS)**
   - Security controls
   - Availability
   - Processing integrity
   - Confidentiality
   - Privacy

4. **Internal Controls**
   - Segregation of duties
   - Approval workflows
   - Change management
   - Exception handling

---

## Incident Response

### Incident Response Plan

See [Incident Response Plan](../INCIDENT_RESPONSE.md) for detailed procedures.

#### 1. Detection

```bash
# Monitor for suspicious activity
- Unusual failed login attempts
- Large data exports
- 500 server errors
- Database connection failures
- Suspicious file downloads
```

#### 2. Assessment

```
Severity Levels:
- Critical: Data breach, ransomware, system down
- High: Security vulnerability, unauthorized access
- Medium: Minor vulnerability, policy violation
- Low: Configuration warning, update available
```

#### 3. Containment

```bash
if Critical:
    1. Take system offline
    2. Notify stakeholders immediately
    3. Preserve evidence
    4. Engage security team
    
if High:
    1. Isolate affected systems
    2. Block attacker IP
    3. Reset potentially compromised credentials
    
if Medium:
    1. Apply temporary mitigation
    2. Schedule patching
    
if Low:
    1. Document issue
    2. Schedule for next maintenance window
```

#### 4. Communication

```markdown
Incident Notification:
- To: Security team, management, affected users (if needed)
- Include: What happened, when, impact, mitigation
- Template in: INCIDENT_RESPONSE.md
```

#### 5. Recovery

```bash
# Restore from clean backup
1. Verify backup integrity
2. Test restore on staging
3. Plan downtime window
4. Execute restore
5. Verify functionality
6. Monitor closely post-recovery
```

#### 6. Post-Incident

```bash
# After incident resolution:
1. Complete Root Cause Analysis (RCA)
2. Identify preventive measures
3. Update security controls
4. Document lessons learned
5. Update procedures/runbooks
6. Share knowledge with team
```

---

## Development Best Practices

### Secure Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make code changes
# - Follow secure coding practices
# - No hardcoded secrets
# - Validate all input
# - Use parameterized queries

# 3. Add tests (including security tests)
def test_sql_injection_prevented(self):
    malicious_input = "'; DROP TABLE transactions; --"
    response = self.client.get(f'/api/transactions/?description={malicious_input}')
    self.assertEqual(response.status_code, 200)
    # Verify table still exists
    self.assertTrue(Transaction.objects.exists())

# 4. Security review checklist
# [ ] No hardcoded secrets
# [ ] All input validated
# [ ] Output escaped
# [ ] SQL injection prevented
# [ ] No debug code
# [ ] Logging doesn't expose PII
# [ ] Crypto used correctly
# [ ] Third-party libraries updated

# 5. Create pull request
git push origin feature/new-feature

# 6. Code review by peer
# - Security review mandatory
# - Approve only if secure

# 7. Merge to main
git merge --no-ff feature/new-feature
```

### Security Code Review Checklist

```markdown
## Security Review Checklist

### Secrets & Credentials
- [ ] No API keys in code
- [ ] No database passwords in code
- [ ] No SECRET_KEY hardcoded
- [ ] Environment variables used for secrets

### Input & Output
- [ ] User input validated
- [ ] Output properly escaped
- [ ] No SQL injection possible
- [ ] No XSS vulnerabilities

### Authentication & Authorization
- [ ] Permissions checked
- [ ] Role-based access enforced
- [ ] Session management secure

### Data Protection
- [ ] Sensitive data not logged
- [ ] HTTPS/TLS used
- [ ] Passwords hashed properly
- [ ] No PII in comments

### Dependencies
- [ ] All dependencies up to date
- [ ] No known vulnerabilities
- [ ] Dependencies from trusted sources

### Error Handling
- [ ] No sensitive info in error messages
- [ ] Proper logging without PII
- [ ] Graceful failure
```

---

## Security Documentation

### Keep Updated

- **SECURITY_AND_GOVERNANCE.md** - This file
- **deployment/DEPLOYMENT.md** - Deployment security
- **guides/TROUBLESHOOTING.md** - Incident handling
- **CHANGELOG.md** - Security fixes noted
- **AUDIT_LOG.md** - Security audit trail (not in repo)

### Incident Response Plan

See `INCIDENT_RESPONSE.md` for detailed procedures.

### Third-Party Assessment

Consider annual:
- Code security audit
- Penetration testing
- SOC 2 Type II audit
- OWASP top 10 assessment

---

## Security Contacts

In case of security issue:

1. **Do NOT create public GitHub issue**
2. **Email security team or maintainers**
3. **Use security-sensitive subject line**
4. **Describe issue clearly**
5. **Provide reproduction steps**
6. **Allow time for patch before disclosure**

---

## References & Standards

### Security Standards
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework/)

### Django Security
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

### Financial Industry Standards
- [PCI DSS](https://www.pcisecuritystandards.org/) - Payment Card Security
- [FFIEC Guidelines](https://www.ffiec.gov/) - Federal banking standards
- [SOC 2](https://www.aicpa.org/interestareas/informationmanagement/socsforserviceorganizations.html) - Service organization controls

### Tools & Services
- `uv tool install safety` - Check dependencies
- `uv tool install bandit` - Code security analysis
- [GitHub Security](https://docs.github.com/en/security) - Built-in scanning
- [OWASP ZAP](https://www.zaproxy.org/) - Security testing

---

## Compliance Verification

```bash
# Run security checks regularly
safety check                    # Check dependencies
python -m bandit -r api/       # Check code
flake8 api/                     # Code quality
uv run pytest api/tests.py            # Run tests
uv run python manage.py check --deploy  # Django checks

# Generate security report
echo "=== Dependency Audit ===" > security_report.md
safety check >> security_report.md
echo "=== Code Security ===" >> security_report.md
python -m bandit -r api/ >> security_report.md
```

---

## Questions & Support

For security concerns:
1. Check this document
2. Review deployment guide
3. Check [Troubleshooting Guide](../../guides/TROUBLESHOOTING.md)
4. Contact security team via email (not GitHub issues)

---

**Last Updated:** March 2, 2026
**Version:** 1.0
**Status:** Active & Current
