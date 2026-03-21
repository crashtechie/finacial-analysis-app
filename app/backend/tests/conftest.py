"""
Pytest configuration and fixtures.
"""

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Add backend dir to path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load .env before Django settings are imported
load_dotenv(backend_dir / ".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "financial_analysis.settings")


@pytest.fixture
def factory_boy_fixture():
    """Placeholder pytest-factory-boy fixture usage."""
    pass
