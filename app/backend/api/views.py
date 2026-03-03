"""
Django REST Framework viewsets for financial analysis API.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Account, Category, ImportLog, Institution, Transaction
from .serializers import (
    AccountSerializer,
    CategorySerializer,
    ImportLogSerializer,
    InstitutionSerializer,
    TransactionListSerializer,
    TransactionSerializer,
)


class InstitutionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for financial institutions.

    list: Get all institutions
    retrieve: Get a specific institution
    create: Create a new institution
    update: Update an institution
    destroy: Delete an institution
    """

    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "identifier"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


class AccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint for accounts.

    list: Get all accounts with balances
    retrieve: Get a specific account with details
    create: Create a new account
    update: Update an account
    destroy: Delete an account
    """

    queryset = Account.objects.select_related("institution").all()
    serializer_class = AccountSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["institution", "account_type"]
    search_fields = ["name", "account_number"]
    ordering_fields = ["name", "created_at"]
    ordering = ["institution__name", "name"]

    @action(detail=True, methods=["get"])
    def transactions(self, request, pk=None):
        """Get all transactions for this account"""
        account = self.get_object()
        transactions = account.transactions.all()

        # Apply pagination
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = TransactionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TransactionListSerializer(transactions, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for categories.

    list: Get all categories
    retrieve: Get a specific category
    create: Create a new category
    update: Update a category
    destroy: Delete a category
    """

    queryset = Category.objects.select_related("parent").all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["parent"]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    @action(detail=True, methods=["get"])
    def transactions(self, request, pk=None):
        """Get all transactions for this category"""
        category = self.get_object()
        transactions = category.transactions.all()

        # Apply pagination
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = TransactionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TransactionListSerializer(transactions, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for transactions.

    list: Get all transactions (paginated, supports filtering)
    retrieve: Get a specific transaction
    create: Create a new transaction
    update: Update a transaction
    partial_update: Partially update a transaction
    destroy: Delete a transaction

    Filters:
    - account: Filter by account ID
    - category: Filter by category ID
    - date_after: Filter transactions after date (YYYY-MM-DD)
    - date_before: Filter transactions before date (YYYY-MM-DD)
    - amount_min: Minimum amount
    - amount_max: Maximum amount
    - status: Transaction status

    Search: Search in description and original_description
    Ordering: date, amount, -date, -amount
    """

    queryset = Transaction.objects.select_related(
        "account", "account__institution", "category"
    ).all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["description", "original_description"]
    ordering_fields = ["date", "amount", "created_at"]
    ordering = ["-date", "-created_at"]

    # Custom filter fields with lookups
    filterset_fields = {
        "account": ["exact"],
        "category": ["exact", "isnull"],
        "date": ["exact", "gte", "lte", "gt", "lt"],
        "amount": ["exact", "gte", "lte", "gt", "lt"],
        "status": ["exact"],
    }

    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == "list":
            return TransactionListSerializer
        return TransactionSerializer


class ImportLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for import logs (read-only).

    list: Get all import logs
    retrieve: Get a specific import log
    """

    queryset = ImportLog.objects.select_related("account").all()
    serializer_class = ImportLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["account", "format_type", "status"]
    ordering_fields = ["started_at", "completed_at"]
    ordering = ["-started_at"]
