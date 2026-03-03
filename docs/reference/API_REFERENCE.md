# Financial Analysis API Reference

Complete API documentation for the Financial Analysis Django REST API.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

Currently using `AllowAny` permission for development. Update `REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES']` in settings.py for production.

## Response Format

All responses return JSON with the following structure:

**Success Response:**
```json
{
  "data": { ... },
  "count": 100,  // For paginated lists
  "next": "...",  // Next page URL
  "previous": "..."  // Previous page URL
}
```

**Error Response:**
```json
{
  "detail": "Error message"
}
```

## Pagination

- Default page size: 50 items
- Use `?page=2` for next pages
- Use `?page_size=100` to customize page size (max: 100)

---

## Endpoints

### Institutions

#### List Institutions
```
GET /api/institutions/
```

**Query Parameters:**
- `search` - Search in name and identifier
- `ordering` - Order by: `name`, `created_at`, `-name`, `-created_at`

**Response:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "Bank-1",
      "identifier": "bank-1",
      "account_count": 1,
      "created_at": "2026-03-01T12:00:00Z"
    }
  ]
}
```

#### Get Institution
```
GET /api/institutions/{id}/
```

#### Create Institution
```
POST /api/institutions/
Content-Type: application/json

{
  "name": "Bank-2",
  "identifier": "bank-2"
}
```

---

### Accounts

#### List Accounts
```
GET /api/accounts/
```

**Query Parameters:**
- `institution` - Filter by institution ID
- `account_type` - Filter by type: `checking`, `savings`, `credit`, `investment`, `other`
- `search` - Search in name and account number
- `ordering` - Order by: `name`, `created_at`

**Response:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "institution": 1,
      "institution_name": "Bank-1",
      "name": "Bank-1 Account",
      "account_number": "0000",
      "account_type": "checking",
      "transaction_count": 76,
      "balance": -1234.56,
      "created_at": "2026-03-01T12:00:00Z"
    }
  ]
}
```

#### Get Account
```
GET /api/accounts/{id}/
```

#### Get Account Transactions
```
GET /api/accounts/{id}/transactions/
```

Returns paginated list of transactions for the account.

---

### Categories

#### List Categories
```
GET /api/categories/
```

**Query Parameters:**
- `parent` - Filter by parent category ID (use `parent__isnull=true` for root categories)
- `search` - Search in name and slug
- `ordering` - Order by: `name`, `created_at`

**Response:**
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "name": "Groceries",
      "slug": "groceries",
      "parent": null,
      "parent_name": null,
      "transaction_count": 15,
      "created_at": "2026-03-01T12:00:00Z"
    }
  ]
}
```

#### Get Category
```
GET /api/categories/{id}/
```

#### Get Category Transactions
```
GET /api/categories/{id}/transactions/
```

---

### Transactions

#### List Transactions
```
GET /api/transactions/
```

**Query Parameters:**
- `account` - Filter by account ID
- `category` - Filter by category ID
- `category__isnull` - Filter uncategorized: `true` or `false`
- `date` - Exact date (YYYY-MM-DD)
- `date__gte` - Date greater than or equal
- `date__lte` - Date less than or equal
- `date__gt` - Date greater than
- `date__lt` - Date less than
- `amount` - Exact amount
- `amount__gte` - Amount ≥
- `amount__lte` - Amount ≤
- `amount__gt` - Amount >
- `amount__lt` - Amount <
- `status` - Filter by status: `pending`, `posted`, `cleared`
- `search` - Search in description and original description
- `ordering` - Order by: `date`, `amount`, `-date`, `-amount`

**Example:**
```
GET /api/transactions/?date__gte=2026-02-01&date__lte=2026-02-28&category=1&ordering=-amount
```

**Response:**
```json
{
  "count": 76,
  "results": [
    {
      "id": 1,
      "account_name": "Bank-1 Account",
      "date": "2026-02-15",
      "description": "Starbucks",
      "category_name": "Restaurants",
      "amount": "-5.25",
      "status": "posted"
    }
  ]
}
```

#### Get Transaction
```
GET /api/transactions/{id}/
```

**Response:**
```json
{
  "id": 1,
  "account": 1,
  "account_name": "Bank-1 Account",
  "date": "2026-02-15",
  "description": "Starbucks",
  "original_description": "STARBUCKS STORE #12345",
  "category": 4,
  "category_name": "Restaurants",
  "amount": "-5.25",
  "status": "posted",
  "is_expense": true,
  "is_income": false,
  "merchant": "Starbucks",
  "notes": "",
  "created_at": "2026-03-01T12:00:00Z",
  "updated_at": "2026-03-01T12:00:00Z"
}
```

#### Update Transaction
```
PATCH /api/transactions/{id}/
Content-Type: application/json

{
  "category": 5,
  "notes": "Business expense"
}
```

---

### Import Logs

#### List Import Logs
```
GET /api/imports/
```

**Query Parameters:**
- `account` - Filter by account ID
- `format_type` - Filter by format: `bank-1`, etc.
- `status` - Filter by status: `pending`, `processing`, `success`, `failed`, `partial`
- `ordering` - Order by: `started_at`, `completed_at`

**Response:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "file_name": "bank-1-transactions-6057-202602.csv",
      "file_path": "finances/bank-1/bank-1-transactions-6057-202602.csv",
      "account": 1,
      "account_name": "Bank-1 Account",
      "format_type": "bank-1",
      "status": "success",
      "records_processed": 76,
      "records_imported": 76,
      "records_skipped": 0,
      "error_message": "",
      "started_at": "2026-03-01T12:00:00Z",
      "completed_at": "2026-03-01T12:00:05Z",
      "duration": 5.0
    }
  ]
}
```

---

## Analytics Endpoints

### Spending Trends

Analyze spending over time with different aggregation periods.

```
GET /api/analytics/spending-trends/
```

**Query Parameters:**
- `period` - Aggregation period: `daily`, `weekly`, `monthly` (default: `monthly`)
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)
- `account` - Filter by account ID

**Example:**
```
GET /api/analytics/spending-trends/?period=weekly&start_date=2026-02-01&end_date=2026-02-29
```

**Response:**
```json
[
  {
    "period": "2026-02-03",
    "total_expenses": 450.75,
    "total_income": 2000.00,
    "net": 1549.25,
    "transaction_count": 15
  },
  {
    "period": "2026-02-10",
    "total_expenses": 523.50,
    "total_income": 0.00,
    "net": -523.50,
    "transaction_count": 18
  }
]
```

---

### Category Breakdown

Analyze spending by category with percentages.

```
GET /api/analytics/category-breakdown/
```

**Query Parameters:**
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)
- `account` - Filter by account ID
- `expense_only` - Show only expenses: `true` (default) or `false`

**Example:**
```
GET /api/analytics/category-breakdown/?start_date=2026-02-01&end_date=2026-02-29
```

**Response:**
```json
[
  {
    "category_id": 1,
    "category_name": "Groceries",
    "total": 450.25,
    "percentage": 35.50,
    "transaction_count": 8,
    "avg_transaction": 56.28
  },
  {
    "category_id": 2,
    "category_name": "Gas",
    "total": 180.00,
    "percentage": 14.20,
    "transaction_count": 4,
    "avg_transaction": 45.00
  }
]
```

---

### Merchant Analysis

Analyze spending patterns by merchant.

```
GET /api/analytics/merchants/
```

**Query Parameters:**
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)
- `account` - Filter by account ID
- `limit` - Number of top merchants (default: 20)

**Example:**
```
GET /api/analytics/merchants/?limit=10
```

**Response:**
```json
[
  {
    "merchant": "Target",
    "total_spent": 350.75,
    "transaction_count": 5,
    "avg_transaction": 70.15,
    "first_transaction": "2026-02-05",
    "last_transaction": "2026-02-25"
  },
  {
    "merchant": "Shell Gas Station",
    "total_spent": 180.00,
    "transaction_count": 4,
    "avg_transaction": 45.00,
    "first_transaction": "2026-02-08",
    "last_transaction": "2026-02-22"
  }
]
```

---

### Analytics Summary

Get overall summary statistics.

```
GET /api/analytics/summary/
```

**Query Parameters:**
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)
- `account` - Filter by account ID

**Response:**
```json
{
  "total_transactions": 76,
  "total_expenses": 2350.50,
  "total_income": 2000.00,
  "net": -350.50,
  "period_start": "2026-02-02",
  "period_end": "2026-02-27",
  "accounts": ["Bank-1 Account"]
}
```

---

## Common Use Cases

### 1. Get all transactions for February 2026
```
GET /api/transactions/?date__gte=2026-02-01&date__lte=2026-02-29
```

### 2. Get monthly spending by category
```
GET /api/analytics/category-breakdown/?start_date=2026-02-01&end_date=2026-02-29
```

### 3. Find all uncategorized transactions
```
GET /api/transactions/?category__isnull=true
```

### 4. Get largest expenses
```
GET /api/transactions/?amount__lt=0&ordering=amount&page_size=10
```

### 5. Search for specific merchant
```
GET /api/transactions/?search=starbucks
```

### 6. Weekly spending trends
```
GET /api/analytics/spending-trends/?period=weekly&start_date=2026-02-01&end_date=2026-02-29
```

### 7. Top 5 merchants by spending
```
GET /api/analytics/merchants/?limit=5
```

---

## Error Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success with no response body
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Testing with cURL

### List transactions
```bash
curl http://localhost:8000/api/transactions/
```

### Get spending trends
```bash
curl "http://localhost:8000/api/analytics/spending-trends/?period=monthly"
```

### Update transaction category
```bash
curl -X PATCH http://localhost:8000/api/transactions/1/ \
  -H "Content-Type: application/json" \
  -d '{"category": 5}'
```

---

## Browsable API

Visit endpoints in your browser for an interactive interface:
- http://localhost:8000/api/
- http://localhost:8000/api/transactions/
- http://localhost:8000/api/analytics/spending-trends/

---

## Rate Limiting

Currently no rate limiting in development. Consider adding rate limiting for production.

## CORS

CORS is enabled for all origins in development. Configure `CORS_ALLOWED_ORIGINS` in settings.py for production.
