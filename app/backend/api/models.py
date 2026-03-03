"""
Data models for financial analysis API.
"""

import hashlib
from decimal import Decimal

from django.db import models
from django.utils import timezone


class Institution(models.Model):
    """Financial institution (bank, credit card company, etc.)"""

    name = models.CharField(max_length=255, unique=True)
    identifier = models.CharField(
        max_length=100, unique=True, help_text="Short identifier (e.g., 'bank-1', 'bank-5')"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Institutions"

    def __str__(self):
        return self.name


class Account(models.Model):
    """Bank account or credit card"""

    ACCOUNT_TYPES = [
        ("checking", "Checking Account"),
        ("savings", "Savings Account"),
        ("credit", "Credit Card"),
        ("investment", "Investment Account"),
        ("other", "Other"),
    ]

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="accounts")
    name = models.CharField(max_length=255)
    account_number = models.CharField(
        max_length=100, help_text="Last 4 digits or account identifier"
    )
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default="checking")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["institution", "name"]
        unique_together = [["institution", "account_number"]]

    def __str__(self):
        return f"{self.institution.name} - {self.name} ({self.account_number})"

    def get_balance(self):
        """Calculate current balance from all transactions"""
        total = self.transactions.aggregate(balance=models.Sum("amount"))["balance"] or Decimal(
            "0.00"
        )
        return total


class Category(models.Model):
    """Transaction category with optional hierarchy"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subcategories"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Transaction(models.Model):
    """Individual financial transaction"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("posted", "Posted"),
        ("cleared", "Cleared"),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    date = models.DateField()
    description = models.CharField(max_length=255)
    original_description = models.CharField(max_length=500, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions"
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Negative for expenses, positive for income"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="posted")
    transaction_hash = models.CharField(max_length=64, unique=True, editable=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["account", "date"]),
            models.Index(fields=["category"]),
            models.Index(fields=["amount"]),
            models.Index(fields=["transaction_hash"]),
        ]

    def __str__(self):
        return f"{self.date} - {self.description} (${self.amount})"

    def save(self, *args, **kwargs):
        """Generate transaction hash for duplicate detection"""
        if not self.transaction_hash:
            self.transaction_hash = self.generate_hash()
        super().save(*args, **kwargs)

    def generate_hash(self):
        """Generate unique hash from transaction details"""
        hash_string = f"{self.account_id}|{self.date}|{self.description}|{self.amount}"
        return hashlib.sha256(hash_string.encode()).hexdigest()

    @property
    def is_expense(self):
        """Check if transaction is an expense"""
        return self.amount < 0

    @property
    def is_income(self):
        """Check if transaction is income"""
        return self.amount > 0

    @property
    def merchant(self):
        """Extract merchant name from description"""
        # Simple implementation - can be enhanced
        return self.description.strip()


class ImportLog(models.Model):
    """Track CSV/PDF import operations"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("partial", "Partial Success"),
    ]

    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, blank=True)
    account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name="imports"
    )
    format_type = models.CharField(
        max_length=50, help_text="Import format (e.g., 'bank-1', 'bank-5')"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    records_processed = models.IntegerField(default=0)
    records_imported = models.IntegerField(default=0)
    records_skipped = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name_plural = "Import Logs"

    def __str__(self):
        return f"{self.file_name} - {self.status} ({self.records_imported} imported)"

    @property
    def duration(self):
        """Calculate import duration"""
        if self.completed_at:
            return self.completed_at - self.started_at
        return None
