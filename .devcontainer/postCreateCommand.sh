#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting post-create setup..."

# Ensure uv is in PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Check if pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found"
    exit 1
fi

echo "📦 Installing Python dependencies with uv..."
uv sync

# Check if virtual environment was created
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not created"
    exit 1
fi

echo "✨ Activating virtual environment..."
source .venv/bin/activate

# Check if Django project exists in app/backend
if [ ! -f "app/backend/manage.py" ]; then
    echo "⚠️  Warning: app/backend/manage.py not found. Skipping Django setup."
else
    echo "🗄️  Running Django migrations..."
    python manage.py migrate --noinput 2>/dev/null || echo "ℹ️  Note: Migrations skipped or not yet available"
    
    echo "📊 Loading initial data..."
    python manage.py loaddata categories 2>/dev/null || echo "ℹ️  Note: Category fixtures not available"
    
    echo "🔍 Running Django checks..."
    python manage.py check || echo "⚠️  Some checks did not pass"
fi

echo "📦 Installing frontend dependencies..."
if [ -f "app/frontend/package.json" ]; then
    cd app/frontend
    echo "  Installing npm packages..."
    npm install
    cd ../..
    echo "✅ Frontend dependencies installed!"
else
    echo "⚠️  Warning: app/frontend/package.json not found. Skipping frontend setup."
fi

echo ""
echo "✅ Post-create setup complete!"
echo ""
echo "📚 Quick start:"
echo "  Backend:"
echo "    1. Activate venv: source .venv/bin/activate"
echo "    2. Start server: cd app/backend && python manage.py runserver"
echo "    3. API available at: http://127.0.0.1:8000/api/"
echo ""
echo "  Frontend:"
echo "    1. Navigate: cd app/frontend"
echo "    2. Start dev server: npm run dev"
echo "    3. App available at: http://localhost:5173"
echo ""
