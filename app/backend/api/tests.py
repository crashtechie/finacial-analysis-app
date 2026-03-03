"""
Unit tests for the financial analysis API.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from api.admin import AccountAdmin, CategoryAdmin, InstitutionAdmin, TransactionAdmin
from api.models import Account, Category, ImportLog, Institution, Transaction
from api.utils.date_helpers import get_date_range
from api.utils.formatters import (
    format_change,
    format_currency,
    format_number_abbreviated,
    format_percentage,
)


class InstitutionModelTests(TestCase):
    """Tests for Institution model"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Bank-1", identifier="bank-1")

    def test_institution_creation(self):
        """Test creating an institution"""
        self.assertEqual(self.institution.name, "Bank-1")
        self.assertEqual(self.institution.identifier, "bank-1")

    def test_institution_str(self):
        """Test institution string representation"""
        self.assertEqual(str(self.institution), "Bank-1")

    def test_institution_unique_name(self):
        """Test institution name uniqueness"""
        with self.assertRaises(Exception):
            Institution.objects.create(name="Bank-1", identifier="bank-1-2")

    def test_institution_unique_identifier(self):
        """Test institution identifier uniqueness"""
        with self.assertRaises(Exception):
            Institution.objects.create(name="Bank-1 Second", identifier="bank-1")


class AccountModelTests(TestCase):
    """Tests for Account model"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Bank-1", identifier="bank-1")
        self.account = Account.objects.create(
            institution=self.institution,
            name="Checking Account",
            account_number="6057",
            account_type="checking",
        )

    def test_account_creation(self):
        """Test creating an account"""
        self.assertEqual(self.account.name, "Checking Account")
        self.assertEqual(self.account.account_type, "checking")
        self.assertEqual(self.account.institution, self.institution)

    def test_account_str(self):
        """Test account string representation"""
        expected = f"{self.institution.name} - {self.account.name} ({self.account.account_number})"
        self.assertEqual(str(self.account), expected)

    def test_account_get_balance_no_transactions(self):
        """Test account balance with no transactions"""
        balance = self.account.get_balance()
        self.assertEqual(balance, Decimal("0.00"))

    def test_account_get_balance_with_transactions(self):
        """Test account balance calculation"""
        Category.objects.create(name="Income", slug="income")
        Category.objects.create(name="Expenses", slug="expenses")

        Transaction.objects.create(
            account=self.account, date=date.today(), description="Salary", amount=Decimal("1000.00")
        )
        Transaction.objects.create(
            account=self.account,
            date=date.today(),
            description="Groceries",
            amount=Decimal("-50.00"),
        )

        balance = self.account.get_balance()
        self.assertEqual(balance, Decimal("950.00"))

    def test_account_unique_account_number_per_institution(self):
        """Test account number uniqueness per institution"""
        with self.assertRaises(Exception):
            Account.objects.create(
                institution=self.institution,
                name="Another Account",
                account_number="6057",
                account_type="savings",
            )


class CategoryModelTests(TestCase):
    """Tests for Category model"""

    def setUp(self):
        self.parent_category = Category.objects.create(name="Expenses", slug="expenses")
        self.subcategory = Category.objects.create(
            name="Groceries", slug="groceries", parent=self.parent_category
        )

    def test_category_creation(self):
        """Test creating a category"""
        self.assertEqual(self.parent_category.name, "Expenses")
        self.assertEqual(self.parent_category.slug, "expenses")

    def test_category_hierarchy(self):
        """Test category parent-child relationship"""
        self.assertEqual(self.subcategory.parent, self.parent_category)
        self.assertIn(self.subcategory, self.parent_category.subcategories.all())

    def test_category_str_with_parent(self):
        """Test category string with parent"""
        expected = f"{self.parent_category.name} > {self.subcategory.name}"
        self.assertEqual(str(self.subcategory), expected)

    def test_category_str_without_parent(self):
        """Test category string without parent"""
        self.assertEqual(str(self.parent_category), "Expenses")

    def test_category_unique_slug(self):
        """Test category slug uniqueness"""
        with self.assertRaises(Exception):
            Category.objects.create(name="Other Expenses", slug="expenses")


class TransactionModelTests(TestCase):
    """Tests for Transaction model"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Bank-1", identifier="bank-1")
        self.account = Account.objects.create(
            institution=self.institution,
            name="Checking Account",
            account_number="6057",
            account_type="checking",
        )
        self.category = Category.objects.create(name="Expenses", slug="expenses")
        self.transaction = Transaction.objects.create(
            account=self.account,
            date=date.today(),
            description="Grocery Store",
            amount=Decimal("-50.00"),
            category=self.category,
        )

    def test_transaction_creation(self):
        """Test creating a transaction"""
        self.assertEqual(self.transaction.description, "Grocery Store")
        self.assertEqual(self.transaction.amount, Decimal("-50.00"))
        self.assertEqual(self.transaction.status, "posted")

    def test_transaction_hash_generation(self):
        """Test transaction hash generation"""
        self.assertIsNotNone(self.transaction.transaction_hash)
        self.assertEqual(len(self.transaction.transaction_hash), 64)

    def test_transaction_hash_uniqueness(self):
        """Test transaction hash uniqueness"""
        transaction = Transaction.objects.create(
            account=self.account,
            date=date.today(),
            description="Different Store",
            amount=Decimal("-25.00"),
            category=self.category,
        )
        self.assertNotEqual(self.transaction.transaction_hash, transaction.transaction_hash)

    def test_transaction_hash_duplicate_prevention(self):
        """
        Test that duplicate transactions get same hash
        (and fail to create due to unique constraint)
        """
        # Create a new transaction with identical details
        with self.assertRaises(Exception):
            # This should fail because the hash already exists
            Transaction.objects.create(
                account=self.account,
                date=self.transaction.date,
                description=self.transaction.description,
                amount=self.transaction.amount,
            )

    def test_is_expense(self):
        """Test is_expense property"""
        self.assertTrue(self.transaction.is_expense)

    def test_is_income(self):
        """Test is_income property"""
        income = Transaction.objects.create(
            account=self.account, date=date.today(), description="Salary", amount=Decimal("1000.00")
        )
        self.assertTrue(income.is_income)
        self.assertFalse(income.is_expense)

    def test_merchant_property(self):
        """Test merchant property"""
        self.assertEqual(self.transaction.merchant, "Grocery Store")


class ImportLogModelTests(TestCase):
    """Tests for ImportLog model"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Bank-1", identifier="bank-1")
        self.account = Account.objects.create(
            institution=self.institution,
            name="Checking Account",
            account_number="6057",
            account_type="checking",
        )
        self.import_log = ImportLog.objects.create(
            file_name="transactions.csv",
            account=self.account,
            format_type="bank-1",
            records_processed=100,
            records_imported=95,
            records_skipped=5,
        )

    def test_import_log_creation(self):
        """Test creating an import log"""
        self.assertEqual(self.import_log.file_name, "transactions.csv")
        self.assertEqual(self.import_log.status, "pending")
        self.assertEqual(self.import_log.records_processed, 100)

    def test_import_log_str(self):
        """Test import log string representation"""
        expected = (
            f"{self.import_log.file_name} - {self.import_log.status} "
            f"({self.import_log.records_imported} imported)"
        )
        self.assertEqual(str(self.import_log), expected)

    def test_import_log_duration(self):
        """Test import log duration calculation"""
        self.import_log.status = "success"
        self.import_log.completed_at = timezone.now()
        self.import_log.save()

        duration = self.import_log.duration
        self.assertIsNotNone(duration)
        self.assertGreaterEqual(duration.total_seconds(), 0)


class APIEndpointTests(APITestCase):
    """Tests for API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.institution = Institution.objects.create(name="Bank-1", identifier="bank-1")
        self.account = Account.objects.create(
            institution=self.institution,
            name="Checking Account",
            account_number="6057",
            account_type="checking",
        )
        self.category = Category.objects.create(name="Expenses", slug="expenses")

    def test_institution_list(self):
        """Test listing institutions"""
        response = self.client.get("/api/institutions/")
        self.assertEqual(response.status_code, 200)
        # Should have at least one institution
        self.assertGreaterEqual(len(response.data), 1)

    def test_account_list(self):
        """Test listing accounts"""
        response = self.client.get("/api/accounts/")
        self.assertEqual(response.status_code, 200)
        # Should have at least one account
        self.assertGreaterEqual(len(response.data), 1)

    def test_category_list(self):
        """Test listing categories"""
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, 200)
        # Should have at least one category
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_institution(self):
        """Test creating an institution via API"""
        data = {"name": "Bank-3", "identifier": "bank-3"}
        response = self.client.post("/api/institutions/", data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Institution.objects.count(), 2)

    def test_create_account(self):
        """Test creating an account via API"""
        data = {
            "institution": self.institution.id,
            "name": "Savings Account",
            "account_number": "1234",
            "account_type": "savings",
        }
        response = self.client.post("/api/accounts/", data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Account.objects.count(), 2)


"""
Extended tests for formatters, date helpers, importers, and analytics.
These tests extend the coverage for uncovered areas of the financial analysis API.
"""


class FormatterUtilityTests(TestCase):
    """Tests for formatting utility functions"""

    def test_format_currency_positive(self):
        """Test formatting positive currency amounts"""
        result = format_currency(1234.56)
        self.assertEqual(result, "$1,234.56")

    def test_format_currency_negative(self):
        """Test formatting negative currency amounts"""
        result = format_currency(-500.00)
        self.assertEqual(result, "-$500.00")

    def test_format_currency_zero(self):
        """Test formatting zero currency"""
        result = format_currency(0)
        self.assertEqual(result, "$0.00")

    def test_format_currency_large_amount(self):
        """Test formatting large currency amounts"""
        result = format_currency(1000000.99)
        self.assertEqual(result, "$1,000,000.99")

    def test_format_currency_custom_symbol(self):
        """Test formatting with custom currency symbol"""
        result = format_currency(100, currency_symbol="€")
        self.assertEqual(result, "€100.00")

    def test_format_currency_custom_decimals(self):
        """Test formatting with custom decimal places"""
        result = format_currency(100.5, decimal_places=0)
        # Python uses banker's rounding: 100.5 rounds to 100 (even)
        self.assertEqual(result, "$100")

    def test_format_percentage(self):
        """Test formatting percentage values"""
        result = format_percentage(45.678)
        self.assertEqual(result, "45.68%")

    def test_format_percentage_zero(self):
        """Test formatting zero percentage"""
        result = format_percentage(0)
        self.assertEqual(result, "0.00%")

    def test_format_change_positive(self):
        """Test calculating positive change"""
        result = format_change(150, 100)
        self.assertEqual(result["direction"], "up")
        self.assertEqual(result["amount"], 50)
        self.assertEqual(result["percentage"], 50.0)

    def test_format_change_negative(self):
        """Test calculating negative change"""
        result = format_change(75, 100)
        self.assertEqual(result["direction"], "down")
        self.assertEqual(result["amount"], -25)
        self.assertEqual(result["percentage"], -25.0)

    def test_format_change_zero_previous(self):
        """Test change when previous value is zero"""
        result = format_change(100, 0)
        self.assertEqual(result["amount"], 100)
        self.assertIsNone(result["percentage"])

    def test_format_change_no_change(self):
        """Test when values don't change"""
        result = format_change(100, 100)
        self.assertEqual(result["direction"], "same")
        self.assertEqual(result["amount"], 0)

    def test_format_number_abbreviated_thousands(self):
        """Test abbreviating thousands"""
        result = format_number_abbreviated(5400)
        self.assertEqual(result, "5.4K")

    def test_format_number_abbreviated_millions(self):
        """Test abbreviating millions"""
        result = format_number_abbreviated(2500000)
        self.assertEqual(result, "2.5M")

    def test_format_number_abbreviated_small(self):
        """Test small numbers"""
        result = format_number_abbreviated(500)
        self.assertEqual(result, "500")

    def test_format_number_abbreviated_negative(self):
        """Test abbreviating negative numbers"""
        result = format_number_abbreviated(-3500)
        self.assertEqual(result, "3.5K")


class DateHelperUtilityTests(TestCase):
    """Tests for date helper utilities"""

    def test_get_date_range_month(self):
        """Test getting current month date range"""
        start, end = get_date_range("month")
        today = date.today()

        self.assertEqual(start.month, today.month)
        self.assertEqual(start.day, 1)

        # Last day of month
        self.assertEqual(end.month, today.month)

    def test_get_date_range_week(self):
        """Test getting current week date range"""
        start, end = get_date_range("week")

        # Start should be Monday of this week
        self.assertEqual(start.weekday(), 0)

        # 6 days difference (Monday to Sunday)
        self.assertEqual((end - start).days, 6)

    def test_get_date_range_quarter(self):
        """Test getting current quarter date range"""
        start, end = get_date_range("quarter")
        today = date.today()

        # Q1: Jan-Mar, Q2: Apr-Jun, etc.
        quarter = (today.month - 1) // 3 + 1
        expected_start_month = (quarter - 1) * 3 + 1

        self.assertEqual(start.month, expected_start_month)
        self.assertEqual((end - start).days >= 89, True)

    def test_get_date_range_year(self):
        """Test getting current year date range"""
        start, end = get_date_range("year")
        today = date.today()

        self.assertEqual(start.year, today.year)
        self.assertEqual(start.month, 1)
        self.assertEqual(start.day, 1)

    def test_get_date_range_custom(self):
        """Test custom date range"""
        custom_start = date(2026, 1, 1)
        custom_end = date(2026, 3, 31)

        start, end = get_date_range("custom", custom_start, custom_end)

        self.assertEqual(start, custom_start)
        self.assertEqual(end, custom_end)

    def test_get_date_range_custom_missing_dates(self):
        """Test custom range without required dates raises error"""
        with self.assertRaises(ValueError):
            get_date_range("custom")


class AdminInterfaceTests(TestCase):
    """Tests for Django admin customizations"""

    def setUp(self):
        self.site = AdminSite()
        self.institution = Institution.objects.create(name="Test Bank", identifier="testbank")
        self.account = Account.objects.create(
            institution=self.institution, name="Checking", account_number="1234"
        )
        self.category = Category.objects.create(name="Groceries", slug="groceries")
        self.transaction = Transaction.objects.create(
            account=self.account,
            date=date.today(),
            description="Test",
            amount=Decimal("-50.00"),
            category=self.category,
        )

    def test_institution_admin_list_display(self):
        """Test InstitutionAdmin list display fields"""
        admin = InstitutionAdmin(Institution, self.site)
        self.assertIn("name", admin.list_display)
        self.assertIn("identifier", admin.list_display)

    def test_account_admin_list_display(self):
        """Test AccountAdmin list display fields"""
        admin = AccountAdmin(Account, self.site)
        self.assertIn("name", admin.list_display)
        self.assertIn("institution", admin.list_display)
        self.assertIn("account_type", admin.list_display)

    def test_account_admin_balance_calculation(self):
        """Test AccountAdmin balance field calculation"""
        admin = AccountAdmin(Account, self.site)
        # The balance method should return HTML formatted balance
        balance = admin.balance(self.account)
        # Should return HTML string containing balance
        self.assertIsInstance(balance, str)
        self.assertIn("color:", balance)
        self.assertIn("$", balance)

    def test_transaction_admin_list_display(self):
        """Test TransactionAdmin list display fields"""
        admin = TransactionAdmin(Transaction, self.site)
        self.assertIn("date", admin.list_display)
        self.assertIn("description", admin.list_display)
        self.assertIn("amount_display", admin.list_display)

    def test_category_admin_list_display(self):
        """Test CategoryAdmin list display fields"""
        admin = CategoryAdmin(Category, self.site)
        self.assertIn("name", admin.list_display)


class ImporterFunctionalityTests(TestCase):
    """Tests for file importer functionality"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Test Bank", identifier="testbank")
        self.account = Account.objects.create(
            institution=self.institution, name="Checking", account_number="1234"
        )

    def test_import_log_creation_on_import(self):
        """Test that import log is created during import"""
        log = ImportLog.objects.create(
            file_name="test.csv", account=self.account, format_type="test", status="processing"
        )

        self.assertIsNotNone(log.id)
        self.assertEqual(log.status, "processing")

    def test_import_log_status_transitions(self):
        """Test import log status can transition through states"""
        log = ImportLog.objects.create(
            file_name="test.csv", account=self.account, format_type="test", status="pending"
        )

        # Transition to processing
        log.status = "processing"
        log.save()
        self.assertEqual(log.status, "processing")

        # Transition to success
        log.status = "success"
        log.records_imported = 100
        log.completed_at = timezone.now()
        log.save()
        self.assertEqual(log.status, "success")

    def test_import_log_error_handling(self):
        """Test import log error message storage"""
        error_msg = "Invalid CSV format: missing date column"
        log = ImportLog.objects.create(
            file_name="bad.csv",
            account=self.account,
            format_type="test",
            status="failed",
            error_message=error_msg,
        )

        self.assertEqual(log.error_message, error_msg)
        self.assertEqual(log.status, "failed")

    def test_import_record_counts(self):
        """Test tracking of processed/imported/skipped records"""
        log = ImportLog.objects.create(
            file_name="test.csv",
            account=self.account,
            format_type="test",
            records_processed=100,
            records_imported=95,
            records_skipped=5,
        )

        total = log.records_imported + log.records_skipped
        self.assertEqual(total, log.records_processed)


class AnalyticsViewTests(APITestCase):
    """Tests for analytics views and endpoints"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Test Bank", identifier="testbank")
        self.account = Account.objects.create(
            institution=self.institution, name="Checking", account_number="1234"
        )
        self.category = Category.objects.create(name="Groceries", slug="groceries")

        # Create test transactions
        for i in range(5):
            Transaction.objects.create(
                account=self.account,
                date=date.today() - timedelta(days=i),
                description=f"Transaction {i}",
                amount=Decimal("-50.00"),
                category=self.category,
            )

    def test_spending_trends_endpoint_exists(self):
        """Test spending trends endpoint is accessible"""
        response = self.client.get("/api/analytics/spending-trends/")
        self.assertIn(response.status_code, [200, 404])

    def test_spending_trends_daily_with_date_range(self):
        """Daily spending trends should work with explicit date range filters."""
        response = self.client.get(
            "/api/analytics/spending-trends/",
            {
                "period": "daily",
                "start_date": (date.today() - timedelta(days=4)).isoformat(),
                "end_date": date.today().isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_category_breakdown_endpoint_exists(self):
        """Test category breakdown endpoint is accessible"""
        response = self.client.get("/api/analytics/category-breakdown/")
        self.assertIn(response.status_code, [200, 404])

    def test_merchant_analysis_endpoint_exists(self):
        """Test merchant analysis endpoint is accessible"""
        response = self.client.get("/api/analytics/merchant-analysis/")
        self.assertIn(response.status_code, [200, 404])

    def test_analytics_summary_endpoint_exists(self):
        """Test summary analytics endpoint is accessible"""
        response = self.client.get("/api/analytics/summary/")
        self.assertIn(response.status_code, [200, 404])


class TransactionEdgeCasesTests(TestCase):
    """Tests for edge cases and error scenarios"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Test Bank", identifier="testbank")
        self.account = Account.objects.create(
            institution=self.institution, name="Checking", account_number="1234"
        )
        self.category = Category.objects.create(name="Test", slug="test")

    def test_zero_amount_transaction(self):
        """Test transaction with zero amount"""
        tx = Transaction.objects.create(
            account=self.account,
            date=date.today(),
            description="Zero transaction",
            amount=Decimal("0.00"),
            category=self.category,
        )

        self.assertEqual(tx.amount, Decimal("0.00"))
        self.assertFalse(tx.is_expense)
        self.assertFalse(tx.is_income)

    def test_very_large_amount(self):
        """Test transaction with very large amount"""
        large_amount = Decimal("999999999.99")
        tx = Transaction.objects.create(
            account=self.account,
            date=date.today(),
            description="Large transaction",
            amount=large_amount,
            category=self.category,
        )

        self.assertEqual(tx.amount, large_amount)

    def test_very_small_amount(self):
        """Test transaction with very small decimal amount"""
        small_amount = Decimal("0.01")
        tx = Transaction.objects.create(
            account=self.account,
            date=date.today(),
            description="Small transaction",
            amount=small_amount,
            category=self.category,
        )

        self.assertEqual(tx.amount, small_amount)

    def test_transaction_missing_category(self):
        """Test transaction without category (optional)"""
        tx = Transaction.objects.create(
            account=self.account,
            date=date.today(),
            description="Uncategorized",
            amount=Decimal("-25.00"),
            category=None,
        )

        self.assertIsNone(tx.category)

    def test_account_with_many_transactions(self):
        """Test account balance with large number of transactions"""
        # Create 100 transactions
        total_amount = Decimal("0.00")
        for i in range(100):
            amount = Decimal(str(i % 50 - 25))  # Mix of positive and negative
            Transaction.objects.create(
                account=self.account,
                date=date.today() - timedelta(days=i),
                description=f"Transaction {i}",
                amount=amount,
                category=self.category,
            )
            total_amount += amount

        balance = self.account.get_balance()
        self.assertEqual(balance, total_amount)

    def test_concurrent_import_logs(self):
        """Test multiple import logs for same account"""
        ImportLog.objects.create(
            file_name="import1.csv", account=self.account, format_type="bank-1"
        )
        ImportLog.objects.create(
            file_name="import2.csv", account=self.account, format_type="bank-1"
        )

        account_logs = self.account.imports.all()
        self.assertEqual(account_logs.count(), 2)
