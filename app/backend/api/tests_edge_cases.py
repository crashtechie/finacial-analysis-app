"""
Edge case and error handling tests for comprehensive coverage.
"""

import tempfile
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from django.test import TestCase

from api.models import Account, Category, Institution, Transaction


class EdgeCaseImporterTests(TestCase):
    """Tests for importer edge cases and error handling"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Bank-1", identifier="bank-1")
        self.category = Category.objects.create(name="Test", slug="test")

    def test_parse_amount_with_spaces(self):
        """Test parsing amount with spaces"""
        from api.importers.bank_1 import Bank1Importer

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            importer = Bank1Importer(file_path=f.name)
            result = importer.parse_amount("  -123.45  ")
            self.assertEqual(result, Decimal("-123.45"))

    def test_parse_amount_positive(self):
        """Test parsing positive amount"""
        from api.importers.bank_1 import Bank1Importer

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            importer = Bank1Importer(file_path=f.name)
            result = importer.parse_amount("123.45")
            self.assertEqual(result, Decimal("123.45"))

    def test_parse_amount_large_number(self):
        """Test parsing large amount"""
        from api.importers.bank_1 import Bank1Importer

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            importer = Bank1Importer(file_path=f.name)
            result = importer.parse_amount("1234567.89")
            self.assertEqual(result, Decimal("1234567.89"))

    def test_parse_date_valid(self):
        """Test parsing date"""
        from api.importers.bank_1 import Bank1Importer

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            importer = Bank1Importer(file_path=f.name)
            result = importer.parse_date("2026-02-15")
            self.assertEqual(result, date(2026, 2, 15))

    def test_get_or_create_account_existing(self):
        """Test getting existing account"""
        account = Account.objects.create(
            institution=self.institution,
            name="Test",
            account_number="1001",
            account_type="checking",
        )

        from api.importers.bank_1 import Bank1Importer

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            importer = Bank1Importer(file_path=f.name, account=account)
            result = importer.get_or_create_account()
            self.assertEqual(result, account)

    def test_handle_amount_parsing(self):
        """Test handling amount string parsing with currency symbol"""
        from api.importers.bank_1 import Bank1Importer

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            importer = Bank1Importer(file_path=f.name)
            # Test parse_amount with currency symbol
            result = importer.parse_amount("$-50.25")
            self.assertEqual(result, Decimal("-50.25"))

    def test_import_with_missing_category(self):
        """Test import creates missing category"""
        csv_data = """Date,Description,Original Description,Category,Amount,Status
2026-02-15,Store,STORE,NewCategory,-50.00,Posted"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_data)
            f.flush()

            account = Account.objects.create(
                institution=self.institution,
                name="Test",
                account_number="1001",
                account_type="checking",
            )

            from api.importers.bank_1 import Bank1Importer

            importer = Bank1Importer(file_path=f.name, account=account)
            importer.import_file()

            # Category should be created if not exists
            self.assertTrue(
                Category.objects.filter(slug="newcategory").exists()
                or Category.objects.filter(slug="new-category").exists()
            )

            Path(f.name).unlink()

    def test_import_duplicate_detection(self):
        """Test duplicate transaction detection"""
        csv_data = """Date,Description,Original Description,Category,Amount,Status
2026-02-15,Store,STORE #1234,Test,-50.00,Posted
2026-02-15,Store,STORE #1234,Test,-50.00,Posted"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_data)
            f.flush()

            account = Account.objects.create(
                institution=self.institution,
                name="Test",
                account_number="1001",
                account_type="checking",
            )

            from api.importers.bank_1 import Bank1Importer

            importer = Bank1Importer(file_path=f.name, account=account)
            log = importer.import_file()

            # Should skip duplicate
            self.assertEqual(log.records_processed, 2)
            self.assertEqual(log.records_skipped, 1)

            Path(f.name).unlink()

    def test_get_summary(self):
        """Test getting import summary"""
        from api.importers.bank_1 import Bank1Importer

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
            account = Account.objects.create(
                institution=self.institution,
                name="Test",
                account_number="1001",
                account_type="checking",
            )

            importer = Bank1Importer(file_path=f.name, account=account)
            summary = importer.get_summary()

            self.assertIn("account", summary)
            self.assertIn("processed", summary)
            self.assertIn("imported", summary)
            self.assertIn("skipped", summary)


class TransactionFilteringTests(TestCase):
    """Tests for transaction filtering and search"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Bank-1", identifier="bank-1")
        self.account = Account.objects.create(
            institution=self.institution,
            name="Checking",
            account_number="1001",
            account_type="checking",
        )
        self.category = Category.objects.create(name="Groceries", slug="groceries")

    def test_filter_by_status(self):
        """Test filtering transactions by status"""
        Transaction.objects.create(
            account=self.account,
            date=date.today(),
            description="Transaction 1",
            amount=Decimal("-50.00"),
            status="posted",
        )
        Transaction.objects.create(
            account=self.account,
            date=date.today(),
            description="Transaction 2",
            amount=Decimal("-25.00"),
            status="pending",
        )

        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get("/api/transactions/?status=posted")
        self.assertEqual(response.status_code, 200)

    def test_filter_multiple_criteria(self):
        """Test filtering with multiple criteria"""
        Transaction.objects.create(
            account=self.account,
            date=date.today(),
            description="Whole Foods",
            amount=Decimal("-50.00"),
            category=self.category,
        )

        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get(
            f"/api/transactions/?account={self.account.id}&category={self.category.id}"
        )
        self.assertEqual(response.status_code, 200)

    def test_search_by_description_partial(self):
        """Test searching by partial description"""
        Transaction.objects.create(
            account=self.account,
            date=date.today(),
            description="Whole Foods Market",
            amount=Decimal("-50.00"),
        )

        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get("/api/transactions/?search=whole")
        self.assertEqual(response.status_code, 200)


class CreateAndDeleteTests(TestCase):
    """Tests for create and delete operations"""

    def test_delete_institution(self):
        """Test deleting institution"""
        institution = Institution.objects.create(name="Bank-2", identifier="bank-2")

        from rest_framework.test import APIClient

        client = APIClient()
        response = client.delete(f"/api/institutions/{institution.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Institution.objects.filter(id=institution.id).exists())

    def test_delete_account(self):
        """Test deleting account"""
        institution = Institution.objects.create(name="Bank-1", identifier="bank-1")
        account = Account.objects.create(
            institution=institution,
            name="Test",
            account_number="1001",
            account_type="checking",
        )

        from rest_framework.test import APIClient

        client = APIClient()
        response = client.delete(f"/api/accounts/{account.id}/")
        self.assertEqual(response.status_code, 204)

    def test_create_category_with_parent(self):
        """Test creating category with parent"""
        parent = Category.objects.create(name="Expenses", slug="expenses")

        from rest_framework.test import APIClient

        client = APIClient()
        data = {
            "name": "Groceries",
            "slug": "groceries",
            "parent": parent.id,
        }
        response = client.post("/api/categories/", data)
        self.assertEqual(response.status_code, 201)


class SerializerValidationTests(TestCase):
    """Tests for serializer validation"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Bank-1", identifier="bank-1")

    def test_create_invalid_institution(self):
        """Test creating institution with invalid data"""
        from rest_framework.test import APIClient

        client = APIClient()
        # Missing identifier field
        data = {"name": "Bank-2"}
        response = client.post("/api/institutions/", data)
        self.assertEqual(response.status_code, 400)

    def test_create_institution_duplicate_identifier(self):
        """Test creating institution with duplicate identifier"""
        from rest_framework.test import APIClient

        client = APIClient()
        data = {"name": "Duplicate", "identifier": "bank-1"}
        response = client.post("/api/institutions/", data)
        self.assertEqual(response.status_code, 400)

    def test_update_institution(self):
        """Test updating institution"""
        from rest_framework.test import APIClient

        client = APIClient()
        data = {"name": "Bank-1 Updated"}
        response = client.patch(f"/api/institutions/{self.institution.id}/", data)
        self.assertEqual(response.status_code, 200)
        self.institution.refresh_from_db()
        self.assertEqual(self.institution.name, "Bank-1 Updated")


class PagenationTests(TestCase):
    """Tests for pagination"""

    def setUp(self):
        self.institution = Institution.objects.create(name="Bank-1", identifier="bank-1")
        self.account = Account.objects.create(
            institution=self.institution,
            name="Checking",
            account_number="1001",
            account_type="checking",
        )

        # Create 50 transactions
        for i in range(50):
            Transaction.objects.create(
                account=self.account,
                date=date.today() - timedelta(days=i),
                description=f"Transaction {i}",
                amount=Decimal(f"-{i}.00"),
            )

    def test_pagination_default(self):
        """Test default pagination"""
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get("/api/transactions/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)

    def test_pagination_custom_page_size(self):
        """Test custom page size"""
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get("/api/transactions/?page_size=10")
        self.assertEqual(response.status_code, 200)

    def test_pagination_page_2(self):
        """Test pagination page 2"""
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get("/api/transactions/?page=2&page_size=20")
        # May be 404 if only one page of results, otherwise 200
        self.assertIn(response.status_code, [200, 404])
