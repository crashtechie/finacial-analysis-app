# Deployment Guide

Complete guide for deploying the Financial Analysis API to production.

## Table of Contents
- [Pre-deployment Checklist](#pre-deployment-checklist)
- [Environment Setup](#environment-setup)
- [Security Configuration](#security-configuration)
- [Database Configuration](#database-configuration)
- [Deployment Options](#deployment-options)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

---

## Pre-deployment Checklist

Before deploying to production, ensure:

### Code Quality
- [ ] All tests pass: `uv run python manage.py test api.tests`
- [ ] Code coverage >80%: `uv run pytest --cov=api api/tests.py`
- [ ] No linting errors: `flake8 api/`
- [ ] Code formatted: `black api/`
- [ ] No outstanding migrations: `uv run python manage.py makemigrations --check`

### Security
- [ ] `DEBUG = False` in settings
- [ ] `SECRET_KEY` is strong and never committed
- [ ] `ALLOWED_HOSTS` configured for your domain
- [ ] No test/dummy data in database
- [ ] CORS settings restricted to your domains

### Documentation
- [ ] README updated with deployment info
- [ ] API documentation current
- [ ] Operational runbooks created
- [ ] Backup procedures documented

### Infrastructure
- [ ] Database backups configured
- [ ] SSL/TLS certificate obtained
- [ ] Monitoring and alerting setup
- [ ] Log aggregation configured

---

## Environment Setup

### Production Environment Variables

Create `.env.production`:

```env
# Django Configuration
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@prod-db.example.com:5432/financial_analysis
DATABASE_TIMEOUT=30

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True

# CORS (restrict to your domain)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (for error notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO
```

### Generate Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Security Configuration

### Update Django Settings

Edit `financial_analysis/settings.py`:

```python
import os
from pathlib import Path

# Read environment
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Security for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
    }
    
    # HSTS
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/app.log',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': os.getenv('LOG_LEVEL', 'INFO'),
    },
}

# Authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### SSL/TLS Configuration

Using Let's Encrypt with certbot:

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Auto-renew
sudo certbot renew --dry-run
```

---

## Database Configuration

### Configurable Database Backend

The application supports multiple database backends via environment variables. Set these in your `.env` file (or production environment):

```env
# ENGINE options: sqlite, postgresql, mysql, mariadb
DATABASE_ENGINE=postgresql
DATABASE_NAME=financial_analysis
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

For SQLite (development default), only `DATABASE_ENGINE` and `DATABASE_NAME` are needed:

```env
DATABASE_ENGINE=sqlite
DATABASE_NAME=db.sqlite3
```

All database variables are required (no fallback defaults). Missing variables will cause Django to fail at startup with a `KeyError`.

You will also need the appropriate Python database driver installed:
- PostgreSQL: `psycopg2-binary`
- MySQL/MariaDB: `mysqlclient`

### Switch from SQLite to PostgreSQL

Update `settings.py`:

```python
import dj_database_url

# Production: PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Alternative: Direct config
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}
```

### Initialize Production Database

```bash
# Create database
createdb financial_analysis_prod

# Run migrations
uv run python manage.py migrate --database=production

# Create superuser
uv run python manage.py createsuperuser

# Load initial data
uv run python manage.py loaddata api/fixtures/categories.json

# Verify
uv run python manage.py check --deploy
```

### Database Backups

#### Automated Daily Backups

Create `scripts/backup_database.sh`:

```bash
#!/bin/bash

DB_NAME=financial_analysis_prod
DB_USER=postgres
BACKUP_DIR=/backups/database
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/backup_$DATE.sql.gz"
```

Add to cron:

```bash
# Run daily at 2 AM
0 2 * * * /root/financial-analysis-app/scripts/backup_database.sh
```

---

## Deployment Options

### Option 1: Heroku (Easiest)

#### Setup

1. **Install Heroku CLI**
   ```bash
   brew tap heroku/brew && brew install heroku
   heroku login
   ```

2. **Create Heroku app**
   ```bash
   heroku create financial-analysis-api
   ```

3. **Add PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:standard-0
   ```

4. **Configure environment**
   ```bash
   heroku config:set DEBUG=False
   heroku config:set SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Run migrations**
   ```bash
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### Option 2: AWS EC2

#### EC2 Setup

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.14 python3-pip python3-venv
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx certbot python3-certbot-nginx

# Clone repo
git clone https://github.com/yourrepo.git
cd financial-analysis-app/app/backend

# Create virtual environment
python3.14 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

#### Systemd Service

Create `/etc/systemd/system/financial-api.service`:

```ini
[Unit]
Description=Financial Analysis API
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/ubuntu/financial-analysis-app/app/backend
ExecStart=/home/ubuntu/financial-analysis-app/app/backend/.venv/bin/gunicorn \
          --workers 4 \
          --bind 127.0.0.1:8000 \
          financial_analysis.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable financial-api
sudo systemctl start financial-api
sudo systemctl status financial-api
```

#### Nginx Configuration

Create `/etc/nginx/sites-available/financial-analysis`:

```nginx
upstream financial_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 10M;

    location / {
        proxy_pass http://financial_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/ubuntu/financial-analysis-app/static/;
    }

    location /media/ {
        alias /home/ubuntu/financial-analysis-app/media/;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/financial-analysis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Docker / Docker Compose

Create `Dockerfile`:

```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml* ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -e ".[dev]" && \
    pip install gunicorn

# Copy application
COPY . .

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && gunicorn financial_analysis.wsgi:application --bind 0.0.0.0:8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.9'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: financial_analysis
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    command: gunicorn financial_analysis.wsgi --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      DEBUG: "False"
      SECRET_KEY: "your-secret-key"
      DATABASE_URL: "postgresql://postgres:secure_password@db:5432/financial_analysis"
    depends_on:
      - db

volumes:
  postgres_data:
```

Deploy:

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

## Monitoring and Maintenance

### Health Checks

Create status endpoint:

```python
# urls.py
path('health/', views.health_check, name='health'),

# views.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'timestamp': now(),
        'database': check_database(),
    })
```

Monitor:

```bash
# Check every minute
* * * * * curl https://yourdomain.com/health/ || alert
```

### Performance Monitoring

```python
# Add Django Debug Toolbar (dev only)
# Add New Relic / Datadog (production)

import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
```

### Logging

Centralize logs:

```python
# settings.py
LOGGING = {
    'handlers': {
        'syslog': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'address': '/dev/log',
        },
    },
}
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check logs
tail -f /var/log/django/app.log

# Test Django configuration
python manage.py check --deploy

# Verify database connection
python manage.py dbshell
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -h db.example.com -U postgres -d financial_analysis

# Check connection limits
psql -c "SELECT * FROM pg_stat_activity;"

# Increase pool size in settings
CONN_MAX_AGE: 600
```

### High Memory Usage

```bash
# Reduce worker processes
gunicorn --workers 2 --max-requests 1000

# Monitor memory
top -p $(pgrep -f gunicorn)
```

### Slow Queries

```python
# Enable query logging
LOGGING['loggers']['django.db.backends'] = {
    'level': 'DEBUG',
}

# Use select_related/prefetch_related
transactions = Transaction.objects.select_related(
    'account__institution'
).prefetch_related('category')
```

---

## Production Checklist

After deployment:

- [ ] Test all API endpoints
- [ ] Verify HTTPS is enforced
- [ ] Check error handling works
- [ ] Verify logging is enabled
- [ ] Test database backups
- [ ] Monitor error rate
- [ ] Load test application
- [ ] Document procedures
- [ ] Create runbooks for common issues
- [ ] Set up paging/alerts

---

## Further Reading

- [Installation Guide](../guides/INSTALLATION.md)
- [Security Guidelines](https://docs.djangoproject.com/en/stable/topics/security/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Configuration](https://nginx.org/en/docs/)
