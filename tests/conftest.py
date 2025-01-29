import sys
from pathlib import Path
import pytest

# Add the project root directory to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]

def pytest_addoption(parser):
    """Add --run-api option to run API tests."""
    parser.addoption(
        "--run-api",
        action="store_true",
        default=False,
        help="run tests that require API access"
    )

def pytest_configure(config):
    """Add api marker."""
    config.addinivalue_line(
        "markers",
        "api: mark test as requiring API access (deselect with '-m \"not api\"')"
    )

def pytest_collection_modifyitems(config, items):
    """Skip API tests unless --run-api flag is used."""
    if not config.getoption("--run-api"):
        skip_api = pytest.mark.skip(reason="need --run-api option to run API tests")
        for item in items:
            if "api" in item.keywords:
                item.add_marker(skip_api) 