"""
URL configuration for analytics endpoints.
"""

from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("spending-trends/", views.SpendingTrendsView.as_view(), name="spending-trends"),
    path("category-breakdown/", views.CategoryBreakdownView.as_view(), name="category-breakdown"),
    path("merchants/", views.MerchantAnalysisView.as_view(), name="merchants"),
    path("summary/", views.AnalyticsSummaryView.as_view(), name="summary"),
]
