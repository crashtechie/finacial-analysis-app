#!/bin/bash

# Setup script for development environment with sample data

set -e

echo "🚀 Setting up Financial Analysis Application..."
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🔄 Activating virtual environment..."
    source .venv/bin/activate
fi

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Create superuser (optional)
echo ""
read -p "Create superuser for Django admin? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# Load category fixtures
echo ""
echo "📊 Loading category fixtures..."
python manage.py loaddata categories

# Import sample data
echo ""
read -p "Import sample Bank-1 transactions? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📥 Importing sample transactions..."
    python manage.py import_transactions finances/bank-1/bank-1-transactions-6057-202602.csv --format bank-1
fi

# Show summary
echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Start the development server:"
echo "     python manage.py runserver"
echo ""
echo "  2. Access the API at:"
echo "     http://localhost:8000/api/"
echo ""
echo "  3. Access Django admin at:"
echo "     http://localhost:8000/admin/"
echo ""
echo "  4. View API documentation in README.md"
echo ""
