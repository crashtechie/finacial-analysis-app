"""
Base importer class for financial data import.
"""

import csv
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from api.models import Account, Category, ImportLog, Institution, Transaction


class BaseImporter(ABC):
    """Abstract base class for importing financial data from CSV files"""

    def __init__(self, file_path, account=None, auto_create_account=True):
        """
        Initialize the importer.

        Args:
            file_path: Path to the CSV file to import
            account: Account instance to associate transactions with (optional)
            auto_create_account: Whether to auto-create account if not provided
        """
        self.file_path = Path(file_path)
        self.account = account
        self.auto_create_account = auto_create_account
        self.import_log = None
        self.stats = {
            "processed": 0,
            "imported": 0,
            "skipped": 0,
            "errors": [],
        }

    @abstractmethod
    def get_format_name(self):
        """Return the format name identifier (e.g., 'bank-1', 'bank-5')"""
        pass

    @abstractmethod
    def parse_row(self, row):
        """
        Parse a CSV row and return transaction data dictionary.

        Args:
            row: CSV row as dictionary

        Returns:
            Dictionary with keys: date, description, original_description,
                                  category, amount, status
        """
        pass

    def get_or_create_account(self):
        """Get or create the account for this import"""
        if self.account:
            return self.account

        if not self.auto_create_account:
            raise ValueError("Account must be provided or auto_create_account must be True")

        # Create default institution and account
        institution, _ = Institution.objects.get_or_create(
            identifier=self.get_format_name(), defaults={"name": self.get_format_name().upper()}
        )

        account, _ = Account.objects.get_or_create(
            institution=institution,
            account_number="0000",
            defaults={
                "name": f"{institution.name} Account",
                "account_type": "checking",
            },
        )

        return account

    def get_or_create_category(self, category_name):
        """Get or create a category from name"""
        if not category_name:
            return None

        slug = slugify(category_name)
        category, _ = Category.objects.get_or_create(slug=slug, defaults={"name": category_name})
        return category

    def parse_date(self, date_string, formats=None):
        """Parse date string with multiple format support"""
        if formats is None:
            formats = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%Y%m%d"]

        for fmt in formats:
            try:
                return datetime.strptime(date_string.strip(), fmt).date()
            except ValueError:
                continue

        raise ValueError(f"Could not parse date: {date_string}")

    def parse_amount(self, amount_string):
        """Parse amount string to Decimal"""
        # Remove currency symbols, commas, spaces
        cleaned = amount_string.replace("$", "").replace(",", "").replace(" ", "").strip()
        return Decimal(cleaned)

    @transaction.atomic
    def import_file(self):
        """
        Import transactions from the CSV file.

        Returns:
            ImportLog instance with import statistics
        """
        # Get/create account
        self.account = self.get_or_create_account()

        # Create import log
        self.import_log = ImportLog.objects.create(
            file_name=self.file_path.name,
            file_path=str(self.file_path),
            account=self.account,
            format_type=self.get_format_name(),
            status="processing",
            started_at=timezone.now(),
        )

        try:
            with open(self.file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
                    self.stats["processed"] += 1

                    try:
                        transaction_data = self.parse_row(row)
                        self.import_transaction(transaction_data)
                        self.stats["imported"] += 1

                    except Transaction.DoesNotExist:
                        # Duplicate transaction (hash already exists)
                        self.stats["skipped"] += 1

                    except Exception as e:
                        error_msg = f"Row {row_num}: {str(e)}"
                        self.stats["errors"].append(error_msg)
                        self.stats["skipped"] += 1

            # Update import log with success
            self.import_log.status = "success" if not self.stats["errors"] else "partial"
            self.import_log.records_processed = self.stats["processed"]
            self.import_log.records_imported = self.stats["imported"]
            self.import_log.records_skipped = self.stats["skipped"]
            self.import_log.error_message = "\n".join(
                self.stats["errors"][:10]
            )  # Store first 10 errors
            self.import_log.completed_at = timezone.now()
            self.import_log.save()

            return self.import_log

        except Exception as e:
            # Import failed
            self.import_log.status = "failed"
            self.import_log.error_message = str(e)
            self.import_log.completed_at = timezone.now()
            self.import_log.save()
            raise

    def import_transaction(self, transaction_data):
        """
        Import a single transaction.

        Args:
            transaction_data: Dictionary with transaction details

        Raises:
            Transaction.DoesNotExist: If transaction already exists (duplicate)
        """
        # Get or create category
        category = None
        if transaction_data.get("category"):
            category = self.get_or_create_category(transaction_data["category"])

        # Create transaction
        transaction = Transaction(
            account=self.account,
            date=transaction_data["date"],
            description=transaction_data["description"],
            original_description=transaction_data.get("original_description", ""),
            category=category,
            amount=transaction_data["amount"],
            status=transaction_data.get("status", "posted").lower(),
        )

        # Generate hash for duplicate detection
        transaction.transaction_hash = transaction.generate_hash()

        # Check if transaction already exists
        if Transaction.objects.filter(transaction_hash=transaction.transaction_hash).exists():
            raise Transaction.DoesNotExist("Duplicate transaction")

        transaction.save()
        return transaction

    def get_summary(self):
        """Get import summary statistics"""
        return {
            "file": self.file_path.name,
            "format": self.get_format_name(),
            "account": str(self.account) if self.account else None,
            "processed": self.stats["processed"],
            "imported": self.stats["imported"],
            "skipped": self.stats["skipped"],
            "errors": len(self.stats["errors"]),
        }
