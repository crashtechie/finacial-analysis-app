"""
Bank-5 CSV importer.
"""

from .base import BaseImporter


class Bank5Importer(BaseImporter):
    """Importer for Bank-5 CSV format"""

    def get_format_name(self):
        """Return format identifier"""
        return "bank-5"

    def parse_row(self, row):
        """
        Parse Bank-5 CSV row format.

        Expected columns:
        - Date (YYYY-MM-DD)
        - Description
        - Original Description
        - Category
        - Amount (negative for expenses, positive for income)
        - Status

        Args:
            row: CSV row dictionary

        Returns:
            Dictionary with parsed transaction data
        """
        # Parse date
        date = self.parse_date(row["Date"])

        # Parse amount
        amount = self.parse_amount(row["Amount"])

        # Clean description
        description = row["Description"].strip()
        original_description = row.get("Original Description", "").strip()

        # Get category
        category = row.get("Category", "").strip()

        # Get status
        status = row.get("Status", "Posted").strip().lower()

        return {
            "date": date,
            "description": description,
            "original_description": original_description,
            "category": category,
            "amount": amount,
            "status": status,
        }
