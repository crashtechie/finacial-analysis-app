"""
URL configuration for API endpoints.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r"institutions", views.InstitutionViewSet, basename="institution")
router.register(r"accounts", views.AccountViewSet, basename="account")
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"transactions", views.TransactionViewSet, basename="transaction")
router.register(r"imports", views.ImportLogViewSet, basename="import")

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
    path("analytics/", include("api.analytics.urls")),
]
