"""
Django REST Framework serializers for financial analysis API.
"""

from rest_framework import serializers

from .models import Account, Category, ImportLog, Institution, Transaction


class InstitutionSerializer(serializers.ModelSerializer):
    """Serializer for Institution model"""

    account_count = serializers.IntegerField(source="accounts.count", read_only=True)

    class Meta:
        model = Institution
        fields = ["id", "name", "identifier", "account_count", "created_at"]
        read_only_fields = ["created_at"]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""

    parent_name = serializers.CharField(source="parent.name", read_only=True, allow_null=True)
    transaction_count = serializers.IntegerField(source="transactions.count", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "parent_name", "transaction_count", "created_at"]
        read_only_fields = ["created_at"]


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for Account model"""

    institution_name = serializers.CharField(source="institution.name", read_only=True)
    transaction_count = serializers.IntegerField(source="transactions.count", read_only=True)
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            "id",
            "institution",
            "institution_name",
            "name",
            "account_number",
            "account_type",
            "transaction_count",
            "balance",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def get_balance(self, obj):
        """Calculate and return account balance"""
        return float(obj.get_balance())


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""

    account_name = serializers.CharField(source="account.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, allow_null=True)
    is_expense = serializers.BooleanField(read_only=True)
    is_income = serializers.BooleanField(read_only=True)
    merchant = serializers.CharField(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "account_name",
            "date",
            "description",
            "original_description",
            "category",
            "category_name",
            "amount",
            "status",
            "is_expense",
            "is_income",
            "merchant",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["transaction_hash", "created_at", "updated_at"]


class TransactionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for transaction lists"""

    account_name = serializers.CharField(source="account.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, allow_null=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "account_name",
            "date",
            "description",
            "category_name",
            "amount",
            "status",
        ]


class ImportLogSerializer(serializers.ModelSerializer):
    """Serializer for ImportLog model"""

    account_name = serializers.CharField(source="account.name", read_only=True, allow_null=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = ImportLog
        fields = [
            "id",
            "file_name",
            "file_path",
            "account",
            "account_name",
            "format_type",
            "status",
            "records_processed",
            "records_imported",
            "records_skipped",
            "error_message",
            "started_at",
            "completed_at",
            "duration",
        ]
        read_only_fields = [
            "records_processed",
            "records_imported",
            "records_skipped",
            "started_at",
            "completed_at",
        ]

    def get_duration(self, obj):
        """Get duration in seconds"""
        duration = obj.duration
        if duration:
            return duration.total_seconds()
        return None
