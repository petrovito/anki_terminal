import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from anki_terminal.commons.config_manager import ConfigManager
from anki_terminal.ops.operation_factory import OperationFactory
from anki_terminal.ops.op_base import Operation, OperationArgument, OperationResult
from anki_terminal.ops.op_registry import OperationRegistry
from anki_terminal.commons.template_manager import TemplateManager


class MockOperation(Operation):
    """Mock operation for testing."""
    name = "mock-operation"
    description = "Mock operation for testing"
    readonly = True
    arguments = [
        OperationArgument(
            name="test_arg",
            description="Test argument",
            required=True
        )
    ]
    
    @classmethod
    def setup_subparser(cls, subparser):
        """Set up the subparser for this operation."""
        subparser.add_argument(
            "--test-arg",
            required=True,
            help="Test argument"
        )
    
    def _validate_impl(self):
        """Validate the operation."""
        if "test_arg" not in self.args:
            return ["Missing required argument: test_arg"]
        return []
    
    def _execute_impl(self):
        """Execute the operation."""
        return OperationResult(
            success=True,
            message=f"Mock operation executed with test_arg={self.args['test_arg']}",
            changes=[]
        )


@pytest.fixture
def mock_registry():
    """Create a mock registry with a test operation."""
    registry = OperationRegistry()
    registry._operations = {"mock-operation": MockOperation}
    return registry


@pytest.fixture
def mock_config_manager():
    """Create a mock config manager."""
    config_manager = MagicMock(spec=ConfigManager)
    config_manager.load_config.return_value = {"test_arg": "config_value"}
    return config_manager


@pytest.fixture
def mock_template_manager():
    """Create a mock template manager."""
    template_manager = MagicMock(spec=TemplateManager)
    template_manager.load_template.return_value = "template_content"
    return template_manager


def test_create_operation_from_args(mock_registry, mock_config_manager, mock_template_manager):
    """Test creating an operation from a dictionary of arguments."""
    factory = OperationFactory(
        registry=mock_registry,
        config_manager=mock_config_manager,
        template_manager=mock_template_manager
    )
    
    # Create args dictionary
    args_dict = {
        "operation": "mock-operation",
        "format": "human",
        "pretty": False,
        "test_arg": "arg_value",
        "config_file": None
    }
    
    # Create operation
    operation = factory.create_operation_from_args(args_dict)
    
    # Verify operation
    assert isinstance(operation, MockOperation)
    assert operation.args["test_arg"] == "arg_value"



def test_process_file_arguments(mock_registry, mock_template_manager):
    """Test processing arguments with file:// prefix."""
    factory = OperationFactory(
        registry=mock_registry,
        template_manager=mock_template_manager
    )
    
    # Test with file:// prefix
    args_dict = {
        "test_arg": "file://test_template.html",
        "normal_arg": "normal_value"
    }
    
    processed_args = factory._process_file_arguments(args_dict)
    
    # Verify processed arguments
    assert processed_args["test_arg"] == "template_content"
    assert processed_args["normal_arg"] == "normal_value"
    assert mock_template_manager.load_template.called_with("test_template.html") 