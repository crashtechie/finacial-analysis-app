"""
Financial data importers registry.
"""

from .bank_1 import Bank1Importer
from .bank_5 import Bank5Importer
from .base import BaseImporter

__all__ = ["BaseImporter", "Bank1Importer", "Bank5Importer", "get_importer", "list_importers"]


# Registry of available importers
IMPORTERS = {
    "bank-1": Bank1Importer,
    "bank-5": Bank5Importer,
    # Add more importers here as they're created
    # 'bank-2': Bank2Importer,
}


def get_importer(format_name):
    """
    Get an importer class by format name.

    Args:
        format_name: Format identifier (e.g., 'bank-1')

    Returns:
        Importer class

    Raises:
        KeyError: If format is not supported
    """
    if format_name not in IMPORTERS:
        available = ", ".join(IMPORTERS.keys())
        raise KeyError(
            f"Unsupported import format: '{format_name}'. " f"Available formats: {available}"
        )

    return IMPORTERS[format_name]


def list_importers():
    """
    Get list of available importer formats.

    Returns:
        List of format names
    """
    return list(IMPORTERS.keys())
