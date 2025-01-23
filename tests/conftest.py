import sys
from pathlib import Path
import pytest

# Add the project root directory to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]

def pytest_addoption(parser):
    """Add pytest command line options."""
    parser.addini(
        "asyncio_mode",
        "run async tests in async mode",
        default="strict"
    )
    parser.addini(
        "asyncio_default_fixture_loop_scope",
        "default event loop scope for async fixtures",
        default="function"
    ) 