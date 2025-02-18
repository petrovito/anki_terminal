import pytest
from typing import Dict, Any

from ops.write.rename_field import RenameFieldOperation
from tests.ops.test_base import OperationTestBase
from anki_types import Collection, Model, Field, Note

class TestRenameFieldOperation(OperationTestBase):
    """Unit tests for RenameFieldOperation."""
    
    operation_class = RenameFieldOperation
    valid_args = {
        "old_field_name": "Front",
        "new_field_name": "Question",
        "model_name": "Basic"
    }
    
    def test_validation(self, mock_collection):
        """Test operation validation.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Test with valid arguments
        op = RenameFieldOperation(**self.valid_args)
        op.validate(mock_collection)
        
        # Test with non-existent field
        op = RenameFieldOperation(
            old_field_name="NonExistent",
            new_field_name="Question",
            model_name="Basic"
        )
        with pytest.raises(ValueError, match="Field 'NonExistent' not found"):
            op.validate(mock_collection)
        
        # Test with duplicate field name
        op = RenameFieldOperation(
            old_field_name="Front",
            new_field_name="Back",  # Back already exists
            model_name="Basic"
        )
        with pytest.raises(ValueError, match="Field 'Back' already exists"):
            op.validate(mock_collection)
        
        # Test with non-existent model
        op = RenameFieldOperation(
            old_field_name="Front",
            new_field_name="Question",
            model_name="NonExistent"
        )
        with pytest.raises(ValueError, match="Model not found"):
            op.validate(mock_collection)
    
    def test_execution(self, mock_collection):
        """Test operation execution.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Create and validate operation
        op = RenameFieldOperation(**self.valid_args)
        op.validate(mock_collection)
        
        # Execute operation
        result = op.execute()
        
        # Verify result
        assert result.success
        assert result.changes  # Should have recorded changes
        
        # Verify field was renamed in model
        model = mock_collection.models[1]  # Basic model
        assert any(f.name == "Question" for f in model.fields)
        assert not any(f.name == "Front" for f in model.fields)
        
        # Verify field was renamed in notes
        for note in mock_collection.notes.values():
            if note.model_id == model.id:
                assert "Question" in note.fields
                assert "Front" not in note.fields 