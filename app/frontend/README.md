# Financial Analysis Frontend

React-based frontend application for the Financial Analysis system. Built with Vite, TypeScript, and Tailwind CSS.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - State management
- **React Router** - Client-side routing
- **date-fns** - Date manipulation

## Project Structure

```
src/
├── api/                    # API client and endpoint handlers
│   ├── client.ts          # Base API client with fetch wrapper
│   ├── institutions.ts    # Institution endpoints
│   ├── accounts.ts        # Account endpoints
│   ├── categories.ts      # Category endpoints
│   └── transactions.ts    # Transaction endpoints
├── components/            # Reusable UI components
│   ├── Layout.tsx        # Main layout with navigation
│   ├── Modal.tsx         # Modal dialog component
│   ├── DeleteConfirmation.tsx  # Delete confirmation dialog
│   ├── LoadingSpinner.tsx     # Loading indicator
│   └── ErrorMessage.tsx  # Error display component
├── pages/                # Page-level components
│   ├── HomePage.tsx      # Landing page
│   ├── InstitutionsPage.tsx   # Institutions CRUD
│   ├── AccountsPage.tsx       # Accounts CRUD
│   ├── CategoriesPage.tsx     # Categories CRUD
│   └── TransactionsPage.tsx   # Transactions CRUD with filters
├── store/                # Zustand state management
│   ├── institutionStore.ts
│   ├── accountStore.ts
│   ├── categoryStore.ts
│   └── transactionStore.ts
├── types/                # TypeScript type definitions
│   ├── models.ts         # Backend model types
│   └── index.ts          # Utility types
├── utils/                # Utility functions
│   └── formatters.ts     # Currency, date, and display formatters
├── test/                 # Test configuration
│   └── setup.ts
├── App.tsx               # Main app with routing
├── main.tsx              # App entry point
└── index.css             # Global styles and Tailwind imports
```

## Getting Started

### Prerequisites

- Node.js 18+ or higher
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd app/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment file (already created):
   ```bash
   # .env.local
   VITE_API_URL=http://localhost:8000/api
   ```

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Building for Production

```bash
npm run build
```

Build output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Features

### Phase 1 (Current Implementation)

- ✅ **Institutions Management** - Create, read, update, delete financial institutions
- ✅ **Accounts Management** - Manage accounts with live balance calculations
- ✅ **Categories Management** - Hierarchical category organization
- ✅ **Transactions Management** - Full CRUD with filtering, search, and pagination
- ✅ **Responsive Design** - Mobile-friendly interface with Tailwind CSS
- ✅ **Type Safety** - Full TypeScript coverage
- ✅ **Error Handling** - User-friendly error messages and retry mechanisms

### Future Enhancements

- [ ] Dashboard with analytics visualizations
- [ ] CSV import interface
- [ ] Transaction bulk operations
- [ ] Dark mode support
- [ ] Export functionality
- [ ] Advanced filtering (date ranges, amount ranges)
- [ ] User authentication
- [ ] Keyboard shortcuts

## Component Architecture

### State Management (Zustand)

Each domain resource has its own store with CRUD operations:

```typescript
const useInstitutionStore = create<InstitutionState>((set, get) => ({
  institutions: [],
  loading: false,
  error: null,
  fetchInstitutions: async () => { /* ... */ },
  createInstitution: async (data) => { /* ... */ },
  updateInstitution: async (id, data) => { /* ... */ },
  deleteInstitution: async (id) => { /* ... */ },
}));
```

### API Client Pattern

Consistent API wrapper with typed responses:

```typescript
// Base client
apiClient.get<T>(endpoint, params)
apiClient.post<T>(endpoint, data)
apiClient.put<T>(endpoint, data)
apiClient.delete<T>(endpoint)

// Resource-specific endpoints
institutionsAPI.list()
institutionsAPI.get(id)
institutionsAPI.create(data)
institutionsAPI.update(id, data)
institutionsAPI.delete(id)
```

### Component Patterns

All CRUD pages follow a consistent structure:

1. Fetch data on component mount
2. Display data in a table with sorting
3. Modal dialogs for create/edit forms
4. Confirmation dialogs for delete operations
5. Loading states and error handling
6. Form validation

## API Integration

### Backend Endpoints

The frontend consumes these backend REST API endpoints:

- `GET/POST/PUT/DELETE /api/institutions/`
- `GET/POST/PUT/DELETE /api/accounts/`
- `GET/POST/PUT/DELETE /api/categories/`
- `GET/POST/PUT/DELETE /api/transactions/`

### Proxy Configuration

Vite dev server proxies API requests to avoid CORS issues:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

## Styling

### Tailwind CSS

Utility classes are used throughout with custom component classes defined in `index.css`:

- `.btn-primary` - Primary action buttons
- `.btn-secondary` - Secondary action buttons
- `.btn-danger` - Destructive actions
- `.input-field` - Form input styling
- `.card` - Card container styling

### Responsive Design

- Mobile-first approach
- Breakpoints: `sm:`, `md:`, `lg:`, `xl:` (Tailwind defaults)
- Navigation adapts to screen size
- Tables scroll horizontally on mobile

## Testing

Test configuration is set up with Vitest and React Testing Library:

```bash
npm test
```

*Note: Tests are currently minimal. Expand coverage as needed.*

## TypeScript

Strict mode is enabled for maximum type safety:

```json
{
  "strict": true,
  "noUnusedLocals": true,
  "noUnusedParameters": true,
  "noFallthroughCasesInSwitch": true
}
```

All API responses and component props are fully typed.

## Code Quality

### Linting

```bash
npm run lint
```

ESLint is configured with React and TypeScript rules.

### Type Checking

```bash
npm run type-check
```

Runs TypeScript compiler without emitting files.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Troubleshooting

### API Connection Issues

If the frontend can't connect to the backend:

1. Ensure the backend is running on `http://localhost:8000`
2. Check `.env.local` has the correct `VITE_API_URL`
3. Verify CORS is enabled in backend settings
4. Check browser console for specific error messages

### Build Issues

If you encounter build errors:

1. Clear node_modules and reinstall: `rm -rf node_modules && npm install`
2. Clear Vite cache: `rm -rf node_modules/.vite`
3. Check Node.js version: `node --version` (should be 18+)

## Contributing

When adding new features:

1. Create types in `src/types/models.ts` matching backend models
2. Add API endpoints in `src/api/`
3. Create Zustand store in `src/store/`
4. Build page component in `src/pages/`
5. Add route in `src/App.tsx`
6. Update navigation in `src/components/Layout.tsx`

## License

See main project LICENSE file.
