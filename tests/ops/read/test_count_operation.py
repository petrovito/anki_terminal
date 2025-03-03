from typing import Type
from anki_terminal.ops.base import Operation
from anki_terminal.ops.read.count_operation import CountOperation
from anki_terminal.ops.anki_path import AnkiPath
from tests.ops.test_base import OperationTestBase

class TestCountOperation(OperationTestBase):
    """Tests for the CountOperation."""
    
    operation_class: Type[Operation] = CountOperation
    
    def test_validation(self, mock_collection):
        """Test operation validation."""
        # Test valid paths
        for path_str in ["/notes", "/models"]:
            operation = self.operation_class(path=path_str)
            operation.validate(mock_collection)
            assert True  # If we get here, validation passed
        
        # Test invalid model name
        path_str = "/models/NonExistent"
        operation = self.operation_class(path=path_str)
        try:
            operation.validate(mock_collection)
            assert False, "Validation should have failed"
        except ValueError:
            assert True  # Expected exception
    
    def test_execution(self, mock_collection):
        """Test operation execution."""
        # Test counting all models
        path_str = "/models"
        operation = self.operation_class(path=path_str)
        operation.validate(mock_collection)
        
        result = operation.execute()
        assert result.success
        assert "count" in result.data
        assert result.data["count"] == 2  # Basic and Advanced models
        
        # Test counting fields for a model
        path_str = "/models/Basic/fields"
        operation = self.operation_class(path=path_str)
        operation.validate(mock_collection)
        
        result = operation.execute()
        assert result.success
        assert "count" in result.data
        assert result.data["count"] == 2  # Front and Back fields
        
        # Test counting templates for a model
        path_str = "/models/Basic/templates"
        operation = self.operation_class(path=path_str)
        operation.validate(mock_collection)
        
        result = operation.execute()
        assert result.success
        assert "count" in result.data
        assert result.data["count"] == 0  # No templates in the mock
        
        # Test counting all cards
        path_str = "/cards"
        operation = self.operation_class(path=path_str)
        operation.validate(mock_collection)
        
        result = operation.execute()
        assert result.success
        assert "count" in result.data
        assert result.data["count"] == 0  # No cards in the mock
        
        # Test counting notes for specific model
        path_str = "/notes/Basic"
        operation = self.operation_class(path=path_str)
        operation.validate(mock_collection)
        
        result = operation.execute()
        assert result.success
        assert "count" in result.data
        assert result.data["count"] == 1
        
        # Test counting all notes (returns total and by_model)
        path_str = "/notes"
        operation = self.operation_class(path=path_str)
        operation.validate(mock_collection)
        
        result = operation.execute()
        assert result.success
        assert "total" in result.data
        assert "by_model" in result.data
        assert result.data["total"] == 1
        assert "Basic" in result.data["by_model"]
        assert result.data["by_model"]["Basic"] == 1
        assert "Advanced" in result.data["by_model"]
        assert result.data["by_model"]["Advanced"] == 0 