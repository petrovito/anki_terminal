import pytest
from typing import Dict, Any

from ops.write.rename_field import RenameFieldOperation
from tests.ops.test_base import OperationTestBase
from tests.ops.base_write_test import BaseWriteTest
from anki_types import Collection, Model, Field, Note
from tests.fixtures.test_data_fixtures import apkg_v2_path, apkg_v21_path

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

class TestRenameFieldIntegration(BaseWriteTest):
    """Integration tests for RenameFieldOperation using real Anki packages."""
    
    # Test both v2 and v21
    versions_to_test = ["v2", "v21"]
    
    # Test parameters
    old_field_name = "Expression"
    new_field_name = "Sentence"
    model_name = "subs2srs"
    model_id = None
    
    def setup_before_operation(self, context):
        """Get original fields for verification."""
        collection = self.get_collection(context)
        
        # Find the model by name
        for mid, model in collection.models.items():
            if model.name == self.model_name:
                self.model_id = mid
                break
        
        assert self.model_id is not None, f"Model {self.model_name} not found"
        
        # Verify the field exists
        model = collection.models[self.model_id]
        field_names = [field.name for field in model.fields]
        assert self.old_field_name in field_names, f"Field {self.old_field_name} not found in model"
    
    def get_operation(self):
        """Return the rename field operation."""
        return RenameFieldOperation(
            old_field_name=self.old_field_name,
            new_field_name=self.new_field_name,
            model_name=self.model_name
        )
    
    def verify_changes(self, context):
        """Verify that the field was renamed."""
        collection = self.get_collection(context)
        
        # Find the model by name
        model_id = None
        for mid, model in collection.models.items():
            if model.name == self.model_name:
                model_id = mid
                break
        
        assert model_id is not None, f"Model {self.model_name} not found"
        
        # Verify field was renamed
        model = collection.models[model_id]
        field_names = [field.name for field in model.fields]
        assert self.old_field_name not in field_names, f"Old field name {self.old_field_name} should not exist"
        assert self.new_field_name in field_names, f"New field name {self.new_field_name} should exist"
        
        # Verify notes were updated
        for note in collection.notes.values():
            if note.model_id == model_id:
                assert self.old_field_name not in note.fields, f"Old field name {self.old_field_name} should not exist in note"
                assert self.new_field_name in note.fields, f"New field name {self.new_field_name} should exist in note" 