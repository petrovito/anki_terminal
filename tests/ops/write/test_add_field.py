import pytest
from typing import Dict, Any

from anki_terminal.ops.write.add_field import AddFieldOperation
from tests.ops.test_base import OperationTestBase
from tests.ops.base_write_test import BaseWriteTest
from anki_terminal.anki_types import Collection, Model, Field, Note
from tests.fixtures.test_data_fixtures import apkg_v2_path, apkg_v21_path

class TestAddFieldOperation(OperationTestBase):
    """Unit tests for AddFieldOperation."""
    
    operation_class = AddFieldOperation
    valid_args = {
        "model_name": "Basic",
        "field_name": "Notes"
    }
    
    def test_validation(self, mock_collection):
        """Test operation validation.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Test with valid arguments
        op = AddFieldOperation(**self.valid_args)
        op.validate(mock_collection)
        
        # Test with duplicate field name
        op = AddFieldOperation(
            model_name="Basic",
            field_name="Front"  # Front already exists
        )
        with pytest.raises(ValueError, match="Field 'Front' already exists"):
            op.validate(mock_collection)
        
        # Test with non-existent model
        op = AddFieldOperation(
            model_name="NonExistent",
            field_name="Notes"
        )
        with pytest.raises(ValueError, match="Model not found"):
            op.validate(mock_collection)
    
    def test_execution(self, mock_collection):
        """Test operation execution.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Create and validate operation
        op = AddFieldOperation(**self.valid_args)
        op.validate(mock_collection)
        
        # Execute operation
        result = op.execute()
        
        # Verify result
        assert result.success
        assert result.changes  # Should have recorded changes
        
        # Verify field was added to model
        model = mock_collection.models[1]  # Basic model
        assert any(f.name == "Notes" for f in model.fields)
        
        # Verify field was added to notes
        for note in mock_collection.notes.values():
            if note.model_id == model.id:
                assert "Notes" in note.fields
                assert note.fields["Notes"] == ""  # Should be empty

class TestAddFieldIntegration(BaseWriteTest):
    """Integration tests for AddFieldOperation using real Anki packages."""
    
    # Test both v2 and v21
    versions_to_test = ["v2", "v21"]
    
    # Test parameters
    model_name = "subs2srs"
    field_name = "CustomNotes"
    model_id = None
    initial_field_count = 0
    
    def setup_before_operation(self, context):
        """Get original field count for verification."""
        collection = self.get_collection(context)
        
        # Find the model by name
        for mid, model in collection.models.items():
            if model.name == self.model_name:
                self.model_id = mid
                self.initial_field_count = len(model.fields)
                break
        
        assert self.model_id is not None, f"Model {self.model_name} not found"
        
        # Verify the field doesn't already exist
        model = collection.models[self.model_id]
        field_names = [field.name for field in model.fields]
        assert self.field_name not in field_names, f"Field {self.field_name} already exists in model"
    
    def get_operation(self):
        """Return the add field operation."""
        return AddFieldOperation(
            model_name=self.model_name,
            field_name=self.field_name
        )
    
    def verify_changes(self, context):
        """Verify that the field was added."""
        collection = self.get_collection(context)
        
        # Find the model by name
        model_id = None
        for mid, model in collection.models.items():
            if model.name == self.model_name:
                model_id = mid
                break
        
        assert model_id is not None, f"Model {self.model_name} not found"
        
        # Verify field was added
        model = collection.models[model_id]
        field_names = [field.name for field in model.fields]
        assert self.field_name in field_names, f"Field {self.field_name} should exist"
        assert len(model.fields) == self.initial_field_count + 1, "Field count should have increased by 1"
        
        # Verify notes were updated
        for note in collection.notes.values():
            if note.model_id == model_id:
                assert self.field_name in note.fields, f"Field {self.field_name} should exist in note"
                assert note.fields[self.field_name] == "", f"Field {self.field_name} should be empty" 