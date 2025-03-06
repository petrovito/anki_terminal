from typing import Type

from anki_terminal.ops.anki_path import AnkiPath
from anki_terminal.ops.op_base import Operation
from anki_terminal.ops.read.get_operation import GetOperation
from tests.ops.test_base import OperationTestBase


class TestGetOperation(OperationTestBase):
    """Tests for the GetOperation."""
    
    operation_class: Type[Operation] = GetOperation
    
    def test_validation(self, mock_collection):
        """Test operation validation."""
        # Test valid path
        path_str = "/models/Basic/example"
        operation = self.operation_class(path=path_str)
        operation.validate(mock_collection)
        assert True  # If we get here, validation passed
        
        # Test invalid model name
        path_str = "/models/NonExistent/example"
        operation = self.operation_class(path=path_str)
        try:
            operation.validate(mock_collection)
            assert False, "Validation should have failed"
        except ValueError:
            assert True  # Expected exception
    
    def test_execution(self, mock_collection):
        """Test operation execution."""
        path_str = "/models/Basic/example"
        operation = self.operation_class(path=path_str)
        operation.validate(mock_collection)
        
        result = operation.execute()
        assert result.success
        assert "example" in result.data
        assert result.data["example"]["Front"] == "test front"
        assert result.data["example"]["Back"] == "test back" 