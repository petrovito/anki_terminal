import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from anki_terminal.arg_parser import (create_operation_subparser, create_parser,
                                      get_printer, parse_args)
from anki_terminal.ops.op_base import Operation, OperationArgument
from anki_terminal.ops.operation_factory import OperationFactory


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
        return []
    
    def _execute_impl(self):
        """Execute the operation."""
        pass


def test_create_operation_subparser():
    """Test creating a subparser for an operation."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="operation")
    
    # Create subparser
    create_operation_subparser(subparsers, "mock-operation", MockOperation)
    
    # Parse args to verify subparser
    args = parser.parse_args(["mock-operation", "--test-arg", "test_value"])
    assert args.operation == "mock-operation"
    assert args.test_arg == "test_value"
    assert hasattr(args, "config_file")


@patch('anki_terminal.arg_parser.OperationRegistry')
def test_create_parser(mock_registry_class):
    """Test creating the argument parser."""
    # Set up mock registry
    mock_registry = MagicMock()
    mock_registry.list_operations.return_value = {"mock-operation": {}}
    mock_registry.get.return_value = MockOperation
    mock_registry_class.return_value = mock_registry
    
    # Create parser
    parser = create_parser()
    
    # Verify parser has common arguments
    actions = {action.dest: action for action in parser._actions}
    assert "apkg_file" in actions
    assert "output_file" in actions
    assert "format" in actions
    assert "pretty" in actions
    assert "config_file" in actions
    
    # Verify subparsers were created
    assert mock_registry.list_operations.called
    assert mock_registry.get.called_with("mock-operation") 