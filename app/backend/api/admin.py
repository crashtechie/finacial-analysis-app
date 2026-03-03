"""
Django admin configuration for financial analysis models.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Account, Category, ImportLog, Institution, Transaction


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ["name", "identifier", "account_count", "created_at"]
    search_fields = ["name", "identifier"]
    readonly_fields = ["created_at"]

    def account_count(self, obj):
        return obj.accounts.count()

    account_count.short_description = "Accounts"


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "institution",
        "account_number",
        "account_type",
        "transaction_count",
        "balance",
        "created_at",
    ]
    list_filter = ["institution", "account_type"]
    search_fields = ["name", "account_number"]
    readonly_fields = ["created_at", "balance"]

    def transaction_count(self, obj):
        return obj.transactions.count()

    transaction_count.short_description = "Transactions"

    def balance(self, obj):
        balance = obj.get_balance()
        color = "green" if balance >= 0 else "red"
        formatted_balance = f"${balance:,.2f}"
        return format_html('<span style="color: {};">{}</span>', color, formatted_balance)

    balance.short_description = "Balance"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "parent", "transaction_count", "created_at"]
    list_filter = ["parent"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at"]

    def transaction_count(self, obj):
        return obj.transactions.count()

    transaction_count.short_description = "Transactions"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["date", "description", "category", "amount_display", "account", "status"]
    list_filter = ["account", "category", "status", "date"]
    search_fields = ["description", "original_description"]
    date_hierarchy = "date"
    readonly_fields = ["transaction_hash", "created_at", "updated_at"]
    list_per_page = 100

    fieldsets = (
        (
            "Transaction Details",
            {
                "fields": (
                    "account",
                    "date",
                    "description",
                    "original_description",
                    "amount",
                    "status",
                )
            },
        ),
        ("Categorization", {"fields": ("category", "notes")}),
        (
            "Metadata",
            {"fields": ("transaction_hash", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def amount_display(self, obj):
        color = "green" if obj.amount > 0 else "red" if obj.amount < 0 else "black"
        return format_html('<span style="color: {};">${:,.2f}</span>', color, obj.amount)

    amount_display.short_description = "Amount"
    amount_display.admin_order_field = "amount"


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = [
        "file_name",
        "account",
        "format_type",
        "status",
        "records_imported",
        "records_skipped",
        "started_at",
        "duration_display",
    ]
    list_filter = ["status", "format_type", "account"]
    search_fields = ["file_name", "file_path"]
    readonly_fields = ["started_at", "completed_at", "duration_display"]
    date_hierarchy = "started_at"

    fieldsets = (
        ("File Information", {"fields": ("file_name", "file_path", "format_type", "account")}),
        (
            "Import Statistics",
            {
                "fields": (
                    "status",
                    "records_processed",
                    "records_imported",
                    "records_skipped",
                    "error_message",
                )
            },
        ),
        ("Timing", {"fields": ("started_at", "completed_at", "duration_display")}),
    )

    def duration_display(self, obj):
        duration = obj.duration
        if duration:
            total_seconds = int(duration.total_seconds())
            if total_seconds < 60:
                return f"{total_seconds}s"
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        return "In progress..."

    duration_display.short_description = "Duration"
