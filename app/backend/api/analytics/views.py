"""
Analytics views for financial data analysis.
"""

from decimal import Decimal

from django.db.models import Avg, Count, F, Max, Min, Q, Sum
from django.db.models.functions import TruncMonth, TruncWeek
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Transaction

from .serializers import (
    AnalyticsSummarySerializer,
    CategoryBreakdownSerializer,
    MerchantAnalysisSerializer,
    SpendingTrendSerializer,
)


class SpendingTrendsView(APIView):
    """
    Analyze spending trends over time.

    Query Parameters:
    - period: 'daily', 'weekly', or 'monthly' (default: 'monthly')
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - account: Filter by account ID
    """

    def get(self, request):
        # Get query parameters
        period = request.query_params.get("period", "monthly")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        account_id = request.query_params.get("account")

        # Build queryset
        queryset = Transaction.objects.all()

        if account_id:
            queryset = queryset.filter(account_id=account_id)

        if start_date:
            queryset = queryset.filter(date__gte=start_date)

        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Determine period annotation
        if period == "daily":
            period_annotation = F("date")
        elif period == "weekly":
            period_annotation = TruncWeek("date")
        else:  # monthly
            period_annotation = TruncMonth("date")

        # Aggregate by period
        trends = (
            queryset.annotate(period_date=period_annotation)
            .values("period_date")
            .annotate(
                total_expenses=Sum("amount", filter=Q(amount__lt=0)),
                total_income=Sum("amount", filter=Q(amount__gt=0)),
                net=Sum("amount"),
                transaction_count=Count("id"),
            )
            .order_by("period_date")
        )

        # Format results
        results = []
        for trend in trends:
            # Handle None values
            expenses = trend["total_expenses"] or Decimal("0")
            income = trend["total_income"] or Decimal("0")
            net = trend["net"] or Decimal("0")

            results.append(
                {
                    "period": trend["period_date"].strftime("%Y-%m-%d"),
                    "total_expenses": abs(expenses),  # Make expenses positive for display
                    "total_income": income,
                    "net": net,
                    "transaction_count": trend["transaction_count"],
                }
            )

        serializer = SpendingTrendSerializer(results, many=True)
        return Response(serializer.data)


class CategoryBreakdownView(APIView):
    """
    Analyze spending by category.

    Query Parameters:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - account: Filter by account ID
    - expense_only: Show only expenses (default: true)
    """

    def get(self, request):
        # Get query parameters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        account_id = request.query_params.get("account")
        expense_only = request.query_params.get("expense_only", "true").lower() == "true"

        # Build queryset
        queryset = Transaction.objects.all()

        if account_id:
            queryset = queryset.filter(account_id=account_id)

        if start_date:
            queryset = queryset.filter(date__gte=start_date)

        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        if expense_only:
            queryset = queryset.filter(amount__lt=0)

        # Calculate total for percentage
        total_amount = queryset.aggregate(total=Sum("amount"))["total"] or Decimal("0")
        if expense_only:
            total_amount = abs(total_amount)

        # Aggregate by category
        breakdown = (
            queryset.values("category_id", "category__name")
            .annotate(
                total=Sum("amount"),
                transaction_count=Count("id"),
                avg_transaction=Avg("amount"),
            )
            .order_by("-total")
        )

        # Format results
        results = []
        for item in breakdown:
            total = abs(item["total"]) if expense_only else item["total"]
            percentage = float(total / abs(total_amount) * 100) if total_amount != 0 else 0

            results.append(
                {
                    "category_id": item["category_id"],
                    "category_name": item["category__name"] or "Uncategorized",
                    "total": total,
                    "percentage": round(percentage, 2),
                    "transaction_count": item["transaction_count"],
                    "avg_transaction": (
                        abs(item["avg_transaction"]) if expense_only else item["avg_transaction"]
                    ),
                }
            )

        serializer = CategoryBreakdownSerializer(results, many=True)
        return Response(serializer.data)


class MerchantAnalysisView(APIView):
    """
    Analyze spending by merchant.

    Query Parameters:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - account: Filter by account ID
    - limit: Number of top merchants to return (default: 20)
    """

    def get(self, request):
        # Get query parameters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        account_id = request.query_params.get("account")
        limit = int(request.query_params.get("limit", 20))

        # Build queryset (expenses only)
        queryset = Transaction.objects.filter(amount__lt=0)

        if account_id:
            queryset = queryset.filter(account_id=account_id)

        if start_date:
            queryset = queryset.filter(date__gte=start_date)

        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Aggregate by merchant (description)
        merchants = (
            queryset.values("description")
            .annotate(
                total_spent=Sum("amount"),
                transaction_count=Count("id"),
                avg_transaction=Avg("amount"),
                first_transaction=Min("date"),
                last_transaction=Max("date"),
            )
            .order_by("total_spent")[:limit]  # Smallest (most negative) first
        )

        # Format results
        results = []
        for merchant in merchants:
            results.append(
                {
                    "merchant": merchant["description"],
                    "total_spent": abs(merchant["total_spent"]),
                    "transaction_count": merchant["transaction_count"],
                    "avg_transaction": abs(merchant["avg_transaction"]),
                    "first_transaction": merchant["first_transaction"],
                    "last_transaction": merchant["last_transaction"],
                }
            )

        serializer = MerchantAnalysisSerializer(results, many=True)
        return Response(serializer.data)


class AnalyticsSummaryView(APIView):
    """
    Get overall analytics summary.

    Query Parameters:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - account: Filter by account ID
    """

    def get(self, request):
        # Get query parameters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        account_id = request.query_params.get("account")

        # Build queryset
        queryset = Transaction.objects.all()

        if account_id:
            queryset = queryset.filter(account_id=account_id)

        if start_date:
            queryset = queryset.filter(date__gte=start_date)

        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Calculate summary statistics
        summary = queryset.aggregate(
            total_transactions=Count("id"),
            total_expenses=Sum("amount", filter=Q(amount__lt=0)),
            total_income=Sum("amount", filter=Q(amount__gt=0)),
            net=Sum("amount"),
            period_start=Min("date"),
            period_end=Max("date"),
        )

        # Get account names
        if account_id:
            accounts = list(queryset.values_list("account__name", flat=True).distinct())
        else:
            from api.models import Account

            accounts = list(Account.objects.values_list("name", flat=True))

        # Format result
        result = {
            "total_transactions": summary["total_transactions"],
            "total_expenses": abs(summary["total_expenses"] or Decimal("0")),
            "total_income": summary["total_income"] or Decimal("0"),
            "net": summary["net"] or Decimal("0"),
            "period_start": summary["period_start"],
            "period_end": summary["period_end"],
            "accounts": accounts,
        }

        serializer = AnalyticsSummarySerializer(result)
        return Response(serializer.data)
