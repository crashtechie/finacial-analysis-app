"""
Additional comprehensive tests for importers, date helpers, and command line utilities.
"""

import csv
import tempfile
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase, override_settings
from io import StringIO

from api.importers import get_importer, list_importers
from api.importers.bank_1 import Bank1Importer
from api.importers.bank_5 import Bank5Importer
from api.models import Account, Category, ImportLog, Institution, Transaction
from api.utils.date_helpers import (
    format_period_label,
    get_date_range,
    get_previous_period,
    parse_date_param,
)


class DateHelperTests(TestCase):
    """Tests for date helper utilities"""

    def test_get_date_range_week(self):
        """Test getting weekly date range"""
        start, end = get_date_range(period="week")
        # Start should be Monday of current week
        self.assertEqual(start.weekday(), 0)
        # End should be Sunday
        self.assertEqual(end.weekday(), 6)
        # Duration should be 6 days
        self.assertEqual((end - start).days, 6)

    def test_get_date_range_month(self):
        """Test getting monthly date range"""
        start, end = get_date_range(period="month")
        # Start should be first day of month
        self.assertEqual(start.day, 1)
        # End should be last day of month
        next_month = start.replace(day=1) + timedelta(days=32)
        next_month = next_month.replace(day=1)
        last_day = (next_month - timedelta(days=1)).day
        self.assertEqual(end.day, last_day)

    def test_get_date_range_quarter(self):
        """Test getting quarterly date range"""
        start, end = get_date_range(period="quarter")
        # Start should be first day of a quarter
        self.assertIn(start.month, [1, 4, 7, 10])
        self.assertEqual(start.day, 1)

    def test_get_date_range_year(self):
        """Test getting yearly date range"""
        start, end = get_date_range(period="year")
        self.assertEqual(start.month, 1)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.month, 12)
        self.assertEqual(end.day, 31)

    def test_get_date_range_custom(self):
        """Test getting custom date range"""
        custom_start = date(2026, 2, 1)
        custom_end = date(2026, 2, 28)
        start, end = get_date_range(period="custom", start_date=custom_start, end_date=custom_end)
        self.assertEqual(start, custom_start)
        self.assertEqual(end, custom_end)

    def test_get_date_range_custom_missing_dates(self):
        """Test custom period without dates raises error"""
        with self.assertRaises(ValueError):
            get_date_range(period="custom")

    def test_get_date_range_invalid_period(self):
        """Test invalid period raises error"""
        with self.assertRaises(ValueError):
            get_date_range(period="invalid")

    def test_get_previous_period(self):
        """Test getting previous period"""
        start = date(2026, 2, 15)
        end = date(2026, 2, 20)
        prev_start, prev_end = get_previous_period(start, end)

        duration = (end - start).days
        self.assertEqual((prev_end - prev_start).days, duration)
        self.assertEqual(prev_end, start - timedelta(days=1))

    def test_parse_date_param_valid(self):
        """Test parsing valid date parameter"""
        result = parse_date_param("2026-02-15")
        self.assertEqual(result, date(2026, 2, 15))

    def test_parse_date_param_invalid_format(self):
        """Test parsing invalid date format"""
        with self.assertRaises(ValueError):
            parse_date_param("02-15-2026")

    def test_parse_date_param_none(self):
        """Test parsing None date parameter"""
        result = parse_date_param(None)
        self.assertIsNone(result)

    def test_parse_date_param_empty_string(self):
        """Test parsing empty string"""
        result = parse_date_param("")
        self.assertIsNone(result)

    def test_format_period_label_month(self):
        """Test formatting period label for month"""
        test_date = date(2026, 2, 15)
        result = format_period_label(test_date, period="month")
        self.assertIn("2026-02", result)

    def test_format_period_label_week(self):
        """Test formatting period label for week"""
        test_date = date(2026, 2, 15)
        result = format_period_label(test_date, period="week")
        self.assertIsNotNone(result)


class Bank1ImporterTests(TestCase):
    """Tests for Bank-1 importer"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Bank-1", identifier="bank-1")
        self.account = Account.objects.create(
            institution=self.institution,
            name="Checking",
            account_number="1001",
            account_type="checking",
        )
        Category.objects.create(name="Groceries", slug="groceries")
        Category.objects.create(name="Restaurants", slug="restaurants")

    def test_importer_initialization(self):
        """Test importer initialization"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            importer = Bank1Importer(file_path=f.name, account=self.account)
            self.assertEqual(importer.account, self.account)
            self.assertIsNotNone(importer.file_path)

    def test_get_format_name(self):
        """Test format name"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            importer = Bank1Importer(file_path=f.name, account=self.account)
            self.assertEqual(importer.get_format_name(), "bank-1")

    def test_parse_row(self):
        """Test parsing CSV row"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            importer = Bank1Importer(file_path=f.name, account=self.account)
            row = {
                "Date": "2026-02-15",
                "Description": "Whole Foods",
                "Original Description": "WF MKT #1234",
                "Category": "Groceries",
                "Amount": "-50.25",
                "Status": "Posted",
            }
            parsed = importer.parse_row(row)
            self.assertEqual(parsed["date"], date(2026, 2, 15))
            self.assertEqual(parsed["description"], "Whole Foods")
            self.assertEqual(parsed["amount"], Decimal("-50.25"))
            self.assertEqual(parsed["status"], "posted")

    def test_parse_row_with_missing_fields(self):
        """Test parsing row with missing optional fields"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            importer = Bank1Importer(file_path=f.name, account=self.account)
            row = {
                "Date": "2026-02-15",
                "Description": "Transaction",
                "Amount": "100.00",
            }
            parsed = importer.parse_row(row)
            self.assertEqual(parsed["original_description"], "")
            self.assertEqual(parsed["status"], "posted")

    def test_full_import_process(self):
        """Test full import process with real CSV"""
        csv_data = """Date,Description,Original Description,Category,Amount,Status
2026-02-15,Whole Foods,WF MKT #1234,Groceries,-50.25,Posted
2026-02-14,Chipotle,CHIPOTLE #5678,Restaurants,-12.50,Posted"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_data)
            f.flush()

            importer = Bank1Importer(file_path=f.name, account=self.account)
            log = importer.import_file()

            self.assertIsNotNone(log)
            self.assertEqual(log.records_processed, 2)
            self.assertEqual(log.records_imported, 2)
            self.assertEqual(Transaction.objects.filter(account=self.account).count(), 2)

            Path(f.name).unlink()


class Bank5ImporterTests(TestCase):
    """Tests for Bank-5 importer"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Bank-5", identifier="bank-5")
        self.account = Account.objects.create(
            institution=self.institution,
            name="Savings",
            account_number="5001",
            account_type="savings",
        )
        Category.objects.create(name="Utilities", slug="utilities")

    def test_get_format_name(self):
        """Test Bank-5 format name"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            importer = Bank5Importer(file_path=f.name, account=self.account)
            self.assertEqual(importer.get_format_name(), "bank-5")

    def test_full_import_process(self):
        """Test full Bank-5 import"""
        csv_data = """Date,Description,Original Description,Category,Amount,Status
2026-02-18,Power Company,POWER BILL,Utilities,-145.67,Posted
2026-02-17,Interest Income,INTEREST,Income,5.25,Posted"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_data)
            f.flush()

            importer = Bank5Importer(file_path=f.name, account=self.account)
            log = importer.import_file()

            self.assertEqual(log.records_processed, 2)
            self.assertEqual(log.records_imported, 2)

            Path(f.name).unlink()


class ImporterRegistryTests(TestCase):
    """Tests for importer registry"""

    def test_list_importers(self):
        """Test listing available importers"""
        importers = list_importers()
        self.assertIn("bank-1", importers)
        self.assertIn("bank-5", importers)

    def test_get_importer_bank1(self):
        """Test getting Bank-1 importer"""
        ImporterClass = get_importer("bank-1")
        self.assertEqual(ImporterClass, Bank1Importer)

    def test_get_importer_bank5(self):
        """Test getting Bank-5 importer"""
        ImporterClass = get_importer("bank-5")
        self.assertEqual(ImporterClass, Bank5Importer)

    def test_get_importer_invalid(self):
        """Test getting invalid importer"""
        with self.assertRaises(KeyError):
            get_importer("bank-99")


class ManagementCommandTests(TestCase):
    """Tests for management commands"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Bank-1", identifier="bank-1")
        self.account = Account.objects.create(
            institution=self.institution,
            name="Checking",
            account_number="1001",
            account_type="checking",
        )
        Category.objects.create(name="Groceries", slug="groceries")

    def test_import_transactions_command_basic(self):
        """Test import_transactions management command"""
        csv_data = """Date,Description,Original Description,Category,Amount,Status
2026-02-15,Store,STORE #1234,Groceries,-50.00,Posted"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_data)
            f.flush()

            out = StringIO()
            call_command(
                "import_transactions",
                f.name,
                "--format",
                "bank-1",
                "--account-id",
                str(self.account.id),
                stdout=out,
            )

            output = out.getvalue()
            self.assertIn("Import completed", output)

            Path(f.name).unlink()

    def test_import_transactions_command_auto_create(self):
        """Test import with auto-create account"""
        csv_data = """Date,Description,Original Description,Category,Amount,Status
2026-02-15,Store,STORE,Groceries,-50.00,Posted"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_data)
            f.flush()

            out = StringIO()
            call_command(
                "import_transactions",
                f.name,
                "--format",
                "bank-1",
                stdout=out,
            )

            output = out.getvalue()
            self.assertIn("Import completed", output)

            Path(f.name).unlink()

    def test_import_transactions_invalid_format(self):
        """Test import with invalid format"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            f.write("test")
            f.flush()

            with self.assertRaises(Exception):
                call_command(
                    "import_transactions",
                    f.name,
                    "--format",
                    "invalid",
                    "--account-id",
                    str(self.account.id),
                )

    def test_import_transactions_nonexistent_account(self):
        """Test import with nonexistent account ID"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            f.write("test")
            f.flush()

            with self.assertRaises(Exception):
                call_command(
                    "import_transactions",
                    f.name,
                    "--format",
                    "bank-1",
                    "--account-id",
                    "999",
                )


class AdditionalViewTests(TestCase):
    """Additional tests for API views"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Bank-1", identifier="bank-1")
        self.account = Account.objects.create(
            institution=self.institution,
            name="Checking",
            account_number="1001",
            account_type="checking",
        )

    def test_update_transaction_category(self):
        """Test updating transaction category"""
        category1 = Category.objects.create(name="Groceries", slug="groceries")
        category2 = Category.objects.create(name="Restaurants", slug="restaurants")

        transaction = Transaction.objects.create(
            account=self.account,
            date=date.today(),
            description="Test",
            amount=Decimal("-50.00"),
            category=category1,
        )

        from rest_framework.test import APIClient

        client = APIClient()
        url = f"/api/transactions/{transaction.id}/"
        data = {"category": category2.id}
        response = client.patch(url, data)

        self.assertEqual(response.status_code, 200)
        transaction.refresh_from_db()
        self.assertEqual(transaction.category, category2)


class AdditionalAnalyticsTests(TestCase):
    """Additional tests for analytics endpoints"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Bank-1", identifier="bank-1")
        self.account = Account.objects.create(
            institution=self.institution,
            name="Checking",
            account_number="1001",
            account_type="checking",
        )
        self.category = Category.objects.create(name="Groceries", slug="groceries")

        # Create test transactions
        for i in range(10):
            Transaction.objects.create(
                account=self.account,
                date=date.today() - timedelta(days=i),
                description=f"Store {i}",
                amount=Decimal("-50.00") if i % 2 == 0 else Decimal("25.00"),
                category=self.category,
            )

    def test_spending_trends_weekly(self):
        """Test spending trends with weekly period"""
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get("/api/analytics/spending-trends/?period=weekly")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_spending_trends_daily(self):
        """Test spending trends with daily period"""
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get("/api/analytics/spending-trends/?period=daily")
        self.assertEqual(response.status_code, 200)

    def test_category_breakdown_expense_only(self):
        """Test category breakdown for expenses only"""
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get("/api/analytics/category-breakdown/?expense_only=true")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_category_breakdown_all(self):
        """Test category breakdown for all transactions"""
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get("/api/analytics/category-breakdown/?expense_only=false")
        self.assertEqual(response.status_code, 200)

    def test_merchant_analysis(self):
        """Test merchant analysis"""
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get("/api/analytics/merchants/?limit=5")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_summary_statistics(self):
        """Test summary statistics"""
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get("/api/analytics/summary/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_transactions", response.data)
        self.assertIn("total_expenses", response.data)
        self.assertIn("total_income", response.data)
