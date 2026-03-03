"""
Serializers for analytics API responses.
"""

from rest_framework import serializers


class SpendingTrendSerializer(serializers.Serializer):
    """Serializer for spending trend data"""

    period = serializers.CharField(help_text="Time period (date or week/month label)")
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    net = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()


class CategoryBreakdownSerializer(serializers.Serializer):
    """Serializer for category breakdown data"""

    category_id = serializers.IntegerField(allow_null=True)
    category_name = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    percentage = serializers.FloatField()
    transaction_count = serializers.IntegerField()
    avg_transaction = serializers.DecimalField(max_digits=12, decimal_places=2)


class MerchantAnalysisSerializer(serializers.Serializer):
    """Serializer for merchant analysis data"""

    merchant = serializers.CharField()
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()
    avg_transaction = serializers.DecimalField(max_digits=12, decimal_places=2)
    first_transaction = serializers.DateField()
    last_transaction = serializers.DateField()


class AnalyticsSummarySerializer(serializers.Serializer):
    """Serializer for overall analytics summary"""

    total_transactions = serializers.IntegerField()
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    net = serializers.DecimalField(max_digits=12, decimal_places=2)
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    accounts = serializers.ListField(child=serializers.CharField())
