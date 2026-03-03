# Documentation Index

Complete documentation for the Financial Analysis API project. Start here to find what you need.

## 📚 Quick Links

### For Users/New Developers
- **[Getting Started](guides/INSTALLATION.md)** - Install and run the project
- **[API Reference](reference/API_REFERENCE.md)** - Complete API endpoint documentation
- **[Troubleshooting](guides/TROUBLESHOOTING.md)** - Solutions to common issues

### For Developers
- **[Developer Guide](development/DEVELOPER_GUIDE.md)** - How to extend the project
- **[Testing Guide](development/TESTING.md)** - How to write and run tests
- **[System Design](architecture/SYSTEM_DESIGN.md)** - Architecture and design patterns
- **[Database Schema](architecture/DATABASE_SCHEMA.md)** - Complete database reference

### For DevOps/Operations
- **[Deployment Guide](deployment/DEPLOYMENT.md)** - Deploy to production
- **[Implementation Summary](reference/IMPLEMENTATION_SUMMARY.md)** - What was built

### For Security & Governance
- **[Security & Governance Guide](security/SECURITY_AND_GOVERNANCE.md)** - Security policies and compliance requirements
- **[Incident Response Plan](security/INCIDENT_RESPONSE.md)** - How to respond to security incidents

### For Contributors
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute code
- **[Changelog](CHANGELOG.md)** - Version history and changes

---

## 📖 Documentation Structure

```
docs/
├── README.md                          # Project overview and quick start
├── CHANGELOG.md                       # Version history
├── CONTRIBUTING.md                    # Contribution guidelines
├── INDEX.md                           # This file - documentation navigation
├── LICENSE                            # Project license
│
├── reference/                         # API and implementation reference
│   ├── API_REFERENCE.md              # Complete API documentation
│   └── IMPLEMENTATION_SUMMARY.md      # What was implemented
│
├── security/                          # Security and compliance documentation
│   ├── SECURITY_AND_GOVERNANCE.md    # Security policies and governance
│   ├── INCIDENT_RESPONSE.md          # Security incident response procedures
│   └── SECURITY_IMPLEMENTATION_SUMMARY.md # Implementation overview
│
├── guides/                            # Step-by-step guides
│   ├── INSTALLATION.md               # Install and setup
│   └── TROUBLESHOOTING.md            # Common issues and solutions
│
├── architecture/                      # System design documentation
│   ├── SYSTEM_DESIGN.md              # Architecture and design patterns
│   └── DATABASE_SCHEMA.md            # Database tables and relationships
│
├── development/                       # Developer documentation
│   ├── DEVELOPER_GUIDE.md            # Extending the project
│   └── TESTING.md                    # Testing guide
│
└── deployment/                        # Operations documentation
    └── DEPLOYMENT.md                 # Production deployment
```

---

## 🎯 Find What You Need

### "How do I..."

#### ...install the project?
→ [Installation Guide](guides/INSTALLATION.md)

#### ...run the API locally?
→ [Installation Guide - Quick Start](guides/INSTALLATION.md#quick-start-dev-container)

#### ...run the tests?
→ [Testing Guide - Running Tests](development/TESTING.md#running-tests)

#### ...use the API?
→ [API Reference](reference/API_REFERENCE.md)

#### ...add a new feature?
→ [Developer Guide](development/DEVELOPER_GUIDE.md)

#### ...add a new bank importer?
→ [Developer Guide - Adding New Importers](development/DEVELOPER_GUIDE.md#adding-new-importers)

#### ...create a new API endpoint?
→ [Developer Guide - Creating New API Endpoints](development/DEVELOPER_GUIDE.md#creating-new-api-endpoints)

#### ...write tests?
→ [Testing Guide - Writing Tests](development/TESTING.md#writing-tests)

#### ...deploy to production?
→ [Deployment Guide](deployment/DEPLOYMENT.md)

#### ...understand the architecture?
→ [System Design](architecture/SYSTEM_DESIGN.md)

#### ...see what the database looks like?
→ [Database Schema](architecture/DATABASE_SCHEMA.md)

#### ...contribute code?
→ [Contributing Guide](CONTRIBUTING.md)

#### ...fix an issue?
→ [Troubleshooting Guide](guides/TROUBLESHOOTING.md)

#### ...handle a security incident?
→ [Incident Response Plan](security/INCIDENT_RESPONSE.md)

#### ...understand security policies?
→ [Security & Governance Guide](security/SECURITY_AND_GOVERNANCE.md)

#### ...protect sensitive data?
→ [Security & Governance Guide - Financial Data Protection](security/SECURITY_AND_GOVERNANCE.md#financial-data-protection)

---

## 🔗 Navigation

### Installation & Setup
1. Start with [Installation Guide](guides/INSTALLATION.md)
2. Choose setup method (Dev Container recommended)
3. Run tests to verify: `uv run python manage.py test api.tests`
4. See [Troubleshooting](guides/TROUBLESHOOTING.md) if issues

### Using the API
1. Read [API Reference](reference/API_REFERENCE.md) for endpoint documentation
2. Try endpoints locally: `curl http://localhost:8000/api/institutions/`
3. Access admin panel: `http://localhost:8000/admin/`

### Development & Contribution
1. Read [Developer Guide](development/DEVELOPER_GUIDE.md) to understand codebase
2. Review [System Design](architecture/SYSTEM_DESIGN.md) for architecture
3. Check [Database Schema](architecture/DATABASE_SCHEMA.md) for data models
4. Follow [Contributing Guide](CONTRIBUTING.md) for PR process
5. Use [Testing Guide](development/TESTING.md) to write tests

### Deployment
1. Review [Pre-deployment Checklist](deployment/DEPLOYMENT.md#pre-deployment-checklist)
2. Choose deployment option (Heroku, AWS EC2, Docker)
3. Follow [Security Configuration](deployment/DEPLOYMENT.md#security-configuration)
4. Monitor and maintain using [Monitoring section](deployment/DEPLOYMENT.md#monitoring-and-maintenance)

### Security & Governance
1. Review [Security & Governance Guide](security/SECURITY_AND_GOVERNANCE.md) for policies
2. Understand [Financial Data Protection](security/SECURITY_AND_GOVERNANCE.md#financial-data-protection) requirements
3. Follow [Secure Coding Practices](security/SECURITY_AND_GOVERNANCE.md#code-security-practices)
4. Review [Access Control](security/SECURITY_AND_GOVERNANCE.md#access-control-and-authentication)
5. Familiarize with [Incident Response](security/INCIDENT_RESPONSE.md) procedures

---

## 📋 Popular Topics

### API Endpoints
- List, create, retrieve, update, delete institutions, accounts, categories, transactions
- Import logs and tracking
- Advanced analytics (spending trends, category breakdown, merchant analysis)
- See [API Reference](reference/API_REFERENCE.md) for complete list with examples

### Data Models
- Institution (bank/credit card company)
- Account (checking, savings, credit, investment)
- Category (transaction categories with hierarchy)
- Transaction (individual transactions with duplicate detection)
- ImportLog (transaction import tracking)

See [Database Schema](architecture/DATABASE_SCHEMA.md) for complete details.

### Key Features
- Multi-bank support with extensible importer system
- CSV import with duplicate detection
- Hierarchical transaction categories
- Spending analysis and trends
- REST API with pagination and filtering

See [Implementation Summary](reference/IMPLEMENTATION_SUMMARY.md) for complete feature list.

### Tech Stack
- **Python 3.14+** - Programming language
- **Django 5.2+** - Web framework
- **Django REST Framework 3.14+** - API framework
- **PostgreSQL/SQLite** - Database
- **pytest/Django TestCase** - Testing

---

## 🧪 Development Checklist

Creating a new feature?

- [ ] Read [System Design](architecture/SYSTEM_DESIGN.md) to understand architecture
- [ ] Check [Database Schema](architecture/DATABASE_SCHEMA.md) for relevant tables
- [ ] Follow steps in [Developer Guide](development/DEVELOPER_GUIDE.md)
- [ ] Write tests using [Testing Guide](development/TESTING.md)
- [ ] Run all tests: `pytest --cov=api api/tests.py`
- [ ] Format code: `black api/ && isort api/`
- [ ] Lint code: `flake8 api/`
- [ ] Follow [Contributing Guide](CONTRIBUTING.md) for PR

---

## 🚀 Deployment Checklist

Deploying to production?

- [ ] Review [Pre-deployment Checklist](deployment/DEPLOYMENT.md#pre-deployment-checklist)
- [ ] Configure [Security Settings](deployment/DEPLOYMENT.md#security-configuration)
- [ ] Set up [Database](deployment/DEPLOYMENT.md#database-configuration)
- [ ] Choose [Deployment Option](deployment/DEPLOYMENT.md#deployment-options)
- [ ] Configure [Monitoring](deployment/DEPLOYMENT.md#monitoring-and-maintenance)
- [ ] Complete [Post-deployment Checklist](deployment/DEPLOYMENT.md#production-checklist)

---

## 🔒 Security Checklist

Before deployment or handling sensitive data:

- [ ] Review [Security & Governance Guide](security/SECURITY_AND_GOVERNANCE.md)
- [ ] Verify [Financial Data Protection](security/SECURITY_AND_GOVERNANCE.md#financial-data-protection) compliance
- [ ] Check .gitignore (no secrets, PDFs, CSVs exposed)
- [ ] Implement [Access Control](security/SECURITY_AND_GOVERNANCE.md#access-control-and-authentication)
- [ ] Review [Secure Coding Practices](security/SECURITY_AND_GOVERNANCE.md#code-security-practices)
- [ ] Set up [Credential Management](security/SECURITY_AND_GOVERNANCE.md#credential-and-secret-management)
- [ ] Understand [Incident Response Procedures](security/INCIDENT_RESPONSE.md)
- [ ] Complete [Deployment Security Checklist](security/SECURITY_AND_GOVERNANCE.md#deployment-security-checklist)

---

## 🆘 Troubleshooting

Common issues and solutions:
→ [Troubleshooting Guide](guides/TROUBLESHOOTING.md)

### Installation Issues
- Port 8000 already in use
- Python version mismatch
- ModuleNotFoundError
- Permission denied on scripts

### Runtime Errors
- Django SystemCheckError
- ImportError issues
- IntegrityError/UNIQUE constraints
- Database locked

### API Issues
- CORS errors
- 404 Not Found
- 403 Forbidden
- Pagination not working

### Testing Problems
- Tests not discovering
- ImportError in tests
- Database state bleeding
- Slow tests

---

## 📞 Getting Help

### First Steps
1. Check [Troubleshooting Guide](guides/TROUBLESHOOTING.md)
2. Search for your issue
3. Check [GitHub Issues](https://github.com/yourusername/financial-analysis-app/issues)

### Read Documentation
- [Installation Guide](guides/INSTALLATION.md) - Setup help
- [API Reference](API_REFERENCE.md) - API usage
- [Developer Guide](development/DEVELOPER_GUIDE.md) - Code structure
- [System Design](architecture/SYSTEM_DESIGN.md) - Architecture

### Still Need Help?
- Open a [GitHub Issue](https://github.com/yourusername/financial-analysis-app/issues/new)
- Include reproduction steps, error messages, and expected behavior
- Read [Contributing Guide](CONTRIBUTING.md) for community expectations

---

## 📝 Documentation Info

- **Last Updated**: March 2, 2026
- **Python Version**: 3.14+
- **Django Version**: 5.2+
- **Coverage**: 75% (70+ tests)

### See Also
- [README](README.md) - Project overview
- [Changelog](CHANGELOG.md) - Version history
- [License](LICENSE) - Licensing information

---

**Happy learning!** 📚

Start with the [Installation Guide](guides/INSTALLATION.md) to get up and running quickly.
