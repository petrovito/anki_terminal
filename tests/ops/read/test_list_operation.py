from typing import Type

from anki_terminal.ops.anki_path import AnkiPath
from anki_terminal.ops.op_base import Operation
from anki_terminal.ops.read.list_operation import ListOperation
from tests.ops.test_base import OperationTestBase


class TestListOperation(OperationTestBase):
    """Tests for the ListOperation."""
    
    operation_class: Type[Operation] = ListOperation
    
    def test_validation(self, mock_collection):
        """Test operation validation."""
        # Test valid paths
        for path_str in ["/notes", "/models"]:
            operation = self.operation_class(path=path_str, limit="10")
            operation.validate(mock_collection)
            assert True  # If we get here, validation passed
        
        # Test invalid model name
        path_str = "/models/NonExistent"
        operation = self.operation_class(path=path_str, limit="10")
        try:
            operation.validate(mock_collection)
            assert False, "Validation should have failed"
        except ValueError:
            assert True  # Expected exception
        
        # Test invalid limit - this will fail during execution, not validation
        # So we'll test it in the execution test
    
    def test_execution(self, mock_collection):
        """Test operation execution."""
        # Test listing all notes
        path_str = "/notes"
        operation = self.operation_class(path=path_str, limit="10")
        operation.validate(mock_collection)
        
        result = operation.execute()
        assert result.success
        assert "notes" in result.data
        assert len(result.data["notes"]) == 1
        assert result.data["notes"][0]["fields"]["Front"] == "test front"
        
        # Test listing notes for specific model
        path_str = "/notes/Basic"
        operation = self.operation_class(path=path_str, limit="10")
        operation.validate(mock_collection)
        
        result = operation.execute()
        assert result.success
        assert "notes" in result.data
        assert len(result.data["notes"]) == 1
        assert result.data["notes"][0]["fields"]["Front"] == "test front"
        
        # Test invalid limit
        path_str = "/notes"
        operation = self.operation_class(path=path_str, limit="invalid")
        operation.validate(mock_collection)
        
        try:
            result = operation.execute()
            assert False, "Execution should have failed with invalid limit"
        except ValueError:
            assert True  # Expected exception