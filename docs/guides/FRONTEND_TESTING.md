# Frontend Manual Testing Guide

This guide provides step-by-step instructions for manually testing the Financial Analysis frontend application. It covers all major features and pages.

## Prerequisites

Before testing, ensure:

- Backend API is running on `http://localhost:8000`
- Frontend is running on `http://localhost:5173` (dev) or `http://localhost:4173` (preview)
- Python virtual environment is activated
- All dependencies are installed (`npm install` in frontend directory)

### Starting the Servers

**Backend:**

```bash
cd /workspaces/finacial-analysis-app/app/backend
python manage.py runserver
```

**Frontend (Development):**

```bash
cd /workspaces/finacial-analysis-app/app/frontend
npm run dev
```

**Frontend (Production Preview):**

```bash
cd /workspaces/finacial-analysis-app/app/frontend
npm run preview -- --host 0.0.0.0 --port 4173
```

## Testing Checklist

### 1. Home Page (`/`)

**URL:** `http://localhost:5173/`

**Tests:**

- [ ] Page loads without errors
- [ ] Navigation bar displays all menu items: Institutions, Accounts, Categories, Transactions
- [ ] Displays four feature cards (Institutions, Accounts, Categories, Transactions)
- [ ] Each card has an icon and description
- [ ] Clicking each card navigates to the respective page
- [ ] Navigation links highlight when on their respective page

**Expected Result:** Clean dashboard with navigation and feature overview

---

### 2. Institutions Page (`/institutions`)

**URL:** `http://localhost:5173/institutions`

**Create Institution Tests:**

- [ ] Click "Add Institution" button
- [ ] Modal opens with form fields: Name, Identifier
- [ ] Enter Name: "Test Bank" and Identifier: "test-bank"
- [ ] Click "Create" button
- [ ] Institution appears in list with correct data
- [ ] Modal closes
- [ ] Success is reflected without page reload

**List/Display Tests:**

- [ ] All institutions display in table format
- [ ] Table shows columns: Name, Identifier, Created At, Actions
- [ ] Multiple institutions display correctly
- [ ] Created At dates format correctly (e.g., "Mar 4, 2026")
- [ ] Each row has Edit and Delete action buttons

**Edit Institution Tests:**

- [ ] Click Edit button on any institution
- [ ] Modal opens with current values pre-filled
- [ ] Modify Name and/or Identifier
- [ ] Click "Update" button
- [ ] Changes reflect in the list
- [ ] Modal closes

**Delete Institution Tests:**

- [ ] Click Delete button on any institution
- [ ] Confirmation dialog appears asking to confirm deletion
- [ ] Click "Delete" in confirmation
- [ ] Institution disappears from list
- [ ] Click Cancel in confirmation (if testing cancel flow)
- [ ] Institution remains in list

**Error Handling Tests:**

- [ ] Try creating institution without entering Name
- [ ] Form should not submit
- [ ] Try creating institution with duplicate name
- [ ] Should see error message

---

### 3. Accounts Page (`/accounts`)

**Pre-requisite:** At least one institution must exist

**Create Account Tests:**

- [ ] Click "Add Account" button
- [ ] Modal opens with form fields: Institution (dropdown), Account Name, Account Type (dropdown), Account Number
- [ ] Select an institution from dropdown
- [ ] Enter Account Name: "My Checking Account"
- [ ] Select Account Type: "Checking"
- [ ] Enter Account Number: "1234"
- [ ] Click "Create" button
- [ ] Account appears in list
- [ ] Account displays: Account Name, Institution Name, Type, Account Number, Balance, Actions

**List/Display Tests:**

- [ ] All accounts display in table format
- [ ] Balance displays as currency (e.g., "$1,234.56")
- [ ] Different account types display correctly (checking, savings, credit, investment)
- [ ] Institution names are shown (not just IDs)
- [ ] Created At dates format correctly

**Edit Account Tests:**

- [ ] Click Edit button on any account
- [ ] Modal pre-fills with current account data
- [ ] Modify account details
- [ ] Click "Update" button
- [ ] Changes reflect without page reload

**Delete Account Tests:**

- [ ] Click Delete button on any account
- [ ] Confirmation dialog appears
- [ ] Click Delete to confirm deletion
- [ ] Account disappears from list

**Warning Tests:**

- [ ] If no institutions exist, "Add Account" button should be disabled
- [ ] Yellow warning box should display about adding institution first

---

### 4. Categories Page (`/categories`)

**Create Category Tests:**

- [ ] Click "Add Category" button
- [ ] Modal opens with form fields: Category Name, Parent Category (dropdown/optional)
- [ ] Enter Name: "Groceries"
- [ ] Parent Category left empty (Top Level)
- [ ] Click "Create" button
- [ ] Category appears in list
- [ ] No error should occur (slug auto-generates)

**Hierarchical Category Tests:**

- [ ] Create a parent category: "Food"
- [ ] Create a child category: "Fast Food"
- [ ] Select "Food" as parent category
- [ ] Click "Create" button
- [ ] Child category saves successfully
- [ ] Parent category name displays in list

**List/Display Tests:**

- [ ] All categories display in table format
- [ ] Table shows: Name, Slug, Parent Category, Transaction Count, Actions
- [ ] Slug field shows auto-generated slugs (e.g., "groceries" from "Groceries")
- [ ] Parent category column shows parent name or "-" for top-level
- [ ] Transaction count displays (0 for new categories)

**Edit Category Tests:**

- [ ] Click Edit button on any category
- [ ] Modal pre-fills with current data
- [ ] Modify category name
- [ ] Click "Update" button
- [ ] Changes reflect in list
- [ ] Slug updates accordingly

**Delete Category Tests:**

- [ ] Click Delete button
- [ ] Confirmation dialog appears
- [ ] Confirm deletion
- [ ] Category disappears from list

---

### 5. Transactions Page (`/transactions`)

**Pre-requisite:** At least one account and category must exist

**Create Transaction Tests:**

- [ ] Click "Add Transaction" button
- [ ] Modal opens with form fields: Account (dropdown), Date, Description, Amount, Category (dropdown), Status (dropdown)
- [ ] Select an account
- [ ] Enter Date: today's date
- [ ] Enter Description: "Grocery Shopping"
- [ ] Enter Amount: "-50.25" (negative for expense)
- [ ] Select Category: "Groceries"
- [ ] Select Status: "Posted"
- [ ] Click "Create" button
- [ ] Transaction appears in list
- [ ] Amount displays in correct color (red for negative/expenses, green for positive/income)

**List/Display Tests:**

- [ ] All transactions display in table format
- [ ] Table shows: Date, Description, Account, Category, Status, Amount, Actions
- [ ] Dates format correctly (e.g., "Mar 4, 2026")
- [ ] Amounts display as currency with correct colors
- [ ] Status displays properly (Pending, Posted, Cleared)
- [ ] Negative amounts are red, positive amounts are green

**Filter Tests:**

- [ ] Click in Search field, enter "Grocery"
- [ ] Results filter to matching transactions
- [ ] Click in Account dropdown, select specific account
- [ ] Results filter to account transactions
- [ ] Click in Category dropdown, select specific category
- [ ] Results filter to category transactions
- [ ] Multiple filters work together
- [ ] Click "Clear" to reset all filters
- [ ] All transactions show again

**Edit Transaction Tests:**

- [ ] Click Edit button on any transaction
- [ ] Modal pre-fills with current data
- [ ] Modify description or amount
- [ ] Click "Update" button
- [ ] Changes reflect in list
- [ ] Amount color updates if changed

**Delete Transaction Tests:**

- [ ] Click Delete button
- [ ] Confirmation dialog appears
- [ ] Confirm deletion
- [ ] Transaction disappears from list
- [ ] Count updates

**Pagination Tests:**

- [ ] Ensure there are more than 50 transactions (check with backend if needed)
- [ ] Look for pagination controls (Previous/Next buttons)
- [ ] Click "Next" to view next page
- [ ] Page number updates
- [ ] Click "Previous" to go back
- [ ] Works correctly through multiple pages

**Warning Tests:**

- [ ] If no accounts exist, "Add Transaction" button should be disabled
- [ ] Yellow warning box should display about adding account first

---

### 6. Navigation Tests

**Menu Navigation:**

- [ ] Click on "Financial Analysis" logo/home link
- [ ] Navigate to home page
- [ ] Click "Institutions" in navigation
- [ ] Navigate to institutions page
- [ ] Click "Accounts" in navigation
- [ ] Navigate to accounts page
- [ ] Click "Categories" in navigation
- [ ] Navigate to categories page
- [ ] Click "Transactions" in navigation
- [ ] Navigate to transactions page
- [ ] Active page is highlighted in navigation bar

**URL Direct Navigation:**

- [ ] Type URL directly: `http://localhost:5173/institutions`
- [ ] Page loads correctly
- [ ] Type `http://localhost:5173/accounts`
- [ ] Page loads correctly
- [ ] Type `http://localhost:5173/invalid-page`
- [ ] Redirects to home page
- [ ] Type `http://localhost:5173/transactions`
- [ ] Page loads correctly

---

### 7. Error Handling Tests

**API Timeout Scenarios:**

- [ ] Stop backend server while frontend is loaded
- [ ] Try creating/fetching data
- [ ] Should see error message (timeout after 15 seconds)
- [ ] Error message should be user-friendly
- [ ] "Try Again" button should be available
- [ ] Click "Try Again" to retry operation

**Form Validation Tests:**

- [ ] Try submitting form with required field empty
- [ ] Form should not submit
- [ ] Try entering invalid date format
- [ ] Try entering non-numeric amount value
- [ ] Try selecting no account when creating transaction
- [ ] All validation should prevent form submission

**Duplicate/Conflict Tests:**

- [ ] Try creating institution with duplicate name
- [ ] Should see error from backend
- [ ] Try creating category with duplicate name
- [ ] Should see error from backend

---

### 8. Performance Tests

**Page Load Speed:**

- [ ] Open DevTools (F12)
- [ ] Go to Network tab
- [ ] Navigate to each page
- [ ] Check load time (should be < 2 seconds)
- [ ] Large transactions list should load within reasonable time

**Memory/Resource Usage:**

- [ ] Open DevTools
- [ ] Go to Performance/Memory tab
- [ ] Perform CRUD operations
- [ ] No excessive memory leaks
- [ ] Smooth scrolling in data tables

---

### 9. UI/UX Tests

**Responsive Design:**

- [ ] Test on desktop (1920x1080)
- [ ] Tables display correctly
- [ ] Buttons are properly sized
- [ ] Modals are centered and readable
- [ ] Resize browser window to tablet size (768px width)
- [ ] Layout adapts appropriately
- [ ] Buttons and forms remain functional

**Visual Consistency:**

- [ ] All pages use same color scheme
- [ ] Buttons have consistent styling
- [ ] Tables format consistently
- [ ] Font sizes are readable
- [ ] Colors follow design system

**Modal Behavior:**

- [ ] Modal appears with overlay
- [ ] Can close by clicking X button
- [ ] Can close by pressing Escape key
- [ ] Can close by clicking background overlay
- [ ] Form data persists while modal is open (before submit)
- [ ] Modal clears after successful submission

---

### 10. Data Integrity Tests

**Transaction Data Consistency:**

- [ ] Create transaction with specific amount
- [ ] Refresh page
- [ ] Amount remains the same
- [ ] Description remains the same
- [ ] Account and category associations maintained

**Concurrent Operations:**

- [ ] Open app in two browser tabs
- [ ] Create institution in tab 1
- [ ] Refresh tab 2
- [ ] New institution appears in tab 2
- [ ] Delete category in tab 1
- [ ] Create transaction in tab 2 (ensure category is gone)
- [ ] Data stays consistent

---

## Common Issues to Watch For

| Issue                    | Observable Symptom        | Resolution                            |
| ------------------------ | ------------------------- | ------------------------------------- |
| API not running          | 503 error or timeout      | Start Django backend server           |
| CORS errors              | Network errors in console | Backend CORS settings                 |
| Frontend not reloading   | Stale data on page        | Hard refresh (Ctrl+Shift+R)           |
| Form submission fails    | 400 bad request           | Check required fields                 |
| Infinite loading spinner | Page never loads          | Check API proxy, backend connectivity |
| Date formatting wrong    | Invalid date display      | Check browser locale, date format     |
| Colors not showing       | Always default color      | Check CSS loading, browser cache      |

---

## Test Data Setup

To most efficiently test the application:

1. **Create 3 institutions:**
   - Bank-1 (identifier: bank-1)
   - Bank-5 (identifier: bank-5)
   - Credit Union (identifier: credit-union)

2. **Create 5+ accounts:**
   - Mix of checking, savings, credit accounts
   - Assign to different institutions

3. **Create 10+ categories:**
   - Both parent and child categories
   - Examples: Food > Groceries, Entertainment > Movies

4. **Import sample transactions:**
   - Use provided demo CSV files
   - Or create manually through UI

---

## Test Execution Tips

1. **Clear browser cache** before testing new versions: Ctrl+Shift+Delete
2. **Use browser DevTools** to check console for errors
3. **Test in different browsers** (Chrome, Firefox, Safari Edge)
4. **Test with different data volumes** (empty, small, large)
5. **Perform smoke tests** frequently during development
6. **Document any new issues** found
7. **Test both happy path and error cases** for each feature

---

## Regression Testing Checklist

After each significant change, run through:

- [ ] Home page loads
- [ ] Can create/read/update/delete institutions
- [ ] Can create/read/update/delete accounts
- [ ] Can create/read/update/delete categories
- [ ] Can create/read/update/delete transactions
- [ ] Filtering works
- [ ] No console errors
- [ ] API errors display gracefully
- [ ] Navigation works

---

## Browser Compatibility

Test on:

- [ ] Chrome/Chromium (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

## Notes

- API base URL can be configured in `.env.local` with `VITE_API_URL`
- Default is `/api` which proxies through Vite dev server
- For production, ensure `VITE_API_URL` is set to actual API endpoint
- Frontend timeout is 15 seconds per request
- All dates use browser locale for formatting
