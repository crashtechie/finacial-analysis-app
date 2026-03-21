"""
Integration tests for API endpoints.
"""

from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestAPIEndpoints:
    """API endpoint integration tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.client = APIClient()

    def test_institution_endpoints(self):
        """Test Institution CRUD endpoints."""
        # Create
        response = self.client.post(
            "/api/institutions/", {"name": "Test Bank", "identifier": "testbank"}
        )
        assert response.status_code == status.HTTP_201_CREATED

        inst_id = response.data["id"]

        # List
        response = self.client.get("/api/institutions/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

        # Retrieve
        response = self.client.get(f"/api/institutions/{inst_id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Bank"

        # Update
        response = self.client.patch(f"/api/institutions/{inst_id}/", {"name": "Updated Bank"})
        assert response.status_code == status.HTTP_200_OK

        # Delete
        response = self.client.delete(f"/api/institutions/{inst_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_account_endpoints(self):
        """Test Account CRUD endpoints."""
        # Create institution first
        inst_response = self.client.post(
            "/api/institutions/", {"name": "Test Bank", "identifier": "testbank"}
        )
        inst_id = inst_response.data["id"]

        # Create account
        response = self.client.post(
            "/api/accounts/",
            {
                "institution": inst_id,
                "name": "Checking",
                "account_number": "5678",
                "account_type": "checking",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_category_endpoints(self):
        """Test Category endpoints."""
        response = self.client.post(
            "/api/categories/", {"name": "Entertainment", "slug": "entertainment"}
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_transaction_endpoints(self):
        """Test Transaction endpoints."""
        # Set up institution, account, category
        inst_resp = self.client.post("/api/institutions/", {"name": "Bank", "identifier": "bank"})
        inst_id = inst_resp.data["id"]

        acc_resp = self.client.post(
            "/api/accounts/", {"institution": inst_id, "name": "Checking", "account_number": "1234"}
        )
        acc_id = acc_resp.data["id"]

        cat_resp = self.client.post("/api/categories/", {"name": "Groceries", "slug": "groceries"})
        cat_id = cat_resp.data["id"]

        # Create transaction
        response = self.client.post(
            "/api/transactions/",
            {
                "account": acc_id,
                "date": str(date.today()),
                "description": "Groceries",
                "amount": "-50.00",
                "category": cat_id,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
