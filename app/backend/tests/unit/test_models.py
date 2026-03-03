"""
Unit tests for models and core functionality.
"""
from datetime import date
from decimal import Decimal

import pytest


@pytest.mark.django_db
class TestModels:
    """Model tests using lazy imports."""

    def test_institution_can_be_created(self):
        """Test Institution model creation."""
        from api.models import Institution
        
        inst = Institution.objects.create(
            name="Test Bank",
            identifier="testbank"
        )
        assert inst.name == "Test Bank"
        assert str(inst) == "Test Bank"

    def test_account_balance_calculation(self):
        """Test Account balance calculation."""
        from api.models import Institution, Account, Category, Transaction
        
        inst = Institution.objects.create(name="Bank", identifier="bank")
        account = Account.objects.create(
            institution=inst,
            name="Checking",
            account_number="1234",
            account_type="checking"
        )
        category = Category.objects.create(name="Test", slug="test")
        
        # Add transactions
        Transaction.objects.create(
            account=account,
            date=date.today(),
            description="Deposit",
            amount=Decimal('500.00'),
            category=category
        )
        Transaction.objects.create(
            account=account,
            date=date.today(),
            description="Withdrawal",
            amount=Decimal('-100.00'),
            category=category
        )
        
        balance = account.get_balance()
        assert balance == Decimal('400.00')

    def test_category_hierarchy(self):
        """Test Category parent-child relationships."""
        from api.models import Category
        
        parent = Category.objects.create(name="Expenses", slug="expenses")
        child = Category.objects.create(
            name="Groceries",
            slug="groceries",
            parent=parent
        )
        
        assert child.parent == parent
        assert str(child) == "Expenses > Groceries"
        assert child in parent.subcategories.all()

    def test_transaction_properties(self):
        """Test Transaction properties."""
        from api.models import Institution, Account, Category, Transaction
        
        inst = Institution.objects.create(name="Bank", identifier="bank")
        account = Account.objects.create(
            institution=inst,
            name="Checking",
            account_number="1234"
        )
        category = Category.objects.create(name="Test", slug="test")
        
        # Expense
        expense = Transaction.objects.create(
            account=account,
            date=date.today(),
            description="Coffee",
            amount=Decimal('-5.50'),
            category=category
        )
        assert expense.is_expense
        assert not expense.is_income
        
        # Income
        income = Transaction.objects.create(
            account=account,
            date=date.today(),
            description="Salary",
            amount=Decimal('2000.00'),
            category=category
        )
        assert income.is_income
        assert not income.is_expense
