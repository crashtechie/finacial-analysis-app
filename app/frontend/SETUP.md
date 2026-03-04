# Frontend Setup Instructions

## Prerequisites

The frontend requires Node.js and npm to run. Follow these steps to set up your environment.

## Installing Node.js (if not installed)

### Option 1: Using apt (Debian/Ubuntu)

```bash
# Update package list
sudo apt update

# Install Node.js (version 20.x LTS recommended)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### Option 2: Using nvm (Node Version Manager) - Recommended

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# Reload shell configuration
source ~/.bashrc  # or source ~/.zshrc

# Install Node.js LTS
nvm install --lts
nvm use --lts

# Verify installation
node --version
npm --version
```

### Option 3: Manual Download

Visit https://nodejs.org/ and download the LTS version for your platform.

## Setting Up the Frontend

Once Node.js is installed:

1. **Navigate to the frontend directory:**
   ```bash
   cd /workspaces/finacial-analysis-app/app/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```
   
   This will install all packages defined in `package.json`:
   - React & React DOM
   - Vite (build tool)
   - TypeScript
   - Tailwind CSS
   - Zustand (state management)
   - React Router
   - Development tools (ESLint, testing libraries)

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The frontend will be available at: `http://localhost:5173`

4. **Make sure the backend is running:**
   
   In a separate terminal:
   ```bash
   cd /workspaces/finacial-analysis-app/app/backend
   source ../.venv/bin/activate  # if using venv
   python manage.py runserver
   ```
   
   The backend should be running at: `http://localhost:8000`

## Available Commands

After installation, you can use these npm scripts:

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Run tests
npm test

# Run TypeScript type checking
npm run type-check

# Run ESLint
npm run lint
```

## Verifying the Setup

1. **Check if dependencies installed:**
   ```bash
   ls node_modules/ | wc -l
   ```
   Should show hundreds of packages.

2. **Check TypeScript compilation:**
   ```bash
   npm run type-check
   ```
   Should complete with no errors.

3. **Open in browser:**
   - Navigate to `http://localhost:5173`
   - You should see the Financial Analysis homepage
   - Check browser console for any errors

## Troubleshooting

### Port Already in Use

If port 5173 is already in use:
```bash
# Kill the process using port 5173
lsof -ti:5173 | xargs kill -9

# Or specify a different port
npm run dev -- --port 3000
```

### CORS Issues

If you get CORS errors:
1. Ensure backend CORS settings allow `http://localhost:5173`
2. Check that `corsheaders` is in Django's `INSTALLED_APPS`
3. Verify `CORS_ALLOWED_ORIGINS` includes your frontend URL

### Module Not Found Errors

If you see TypeScript path alias errors:
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### API Connection Errors

1. Verify backend is running: `curl http://localhost:8000/api/institutions/`
2. Check `.env.local` has correct `VITE_API_URL`
3. Open browser DevTools Network tab to inspect requests

## Next Steps

After the frontend is running:

1. **Add an institution** - Navigate to Institutions page
2. **Create an account** - Navigate to Accounts page
3. **Add categories** - Navigate to Categories page
4. **Record transactions** - Navigate to Transactions page

For more details, see [README.md](README.md)
