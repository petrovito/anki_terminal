from typing import Any, Dict

import pytest

from anki_terminal.commons.anki_types import Collection, Model, Note
from anki_terminal.ops.write.rename_model import RenameModelOperation
from tests.fixtures.test_data_fixtures import apkg_v2_path, apkg_v21_path
from tests.ops.base_write_test import BaseWriteTest
from tests.ops.test_base import OperationTestBase


class TestRenameModelOperation(OperationTestBase):
    """Unit tests for RenameModelOperation."""
    
    operation_class = RenameModelOperation
    valid_args = {
        "old_model_name": "Basic",
        "new_model_name": "Basic Note"
    }
    
    def test_validation(self, mock_collection):
        """Test operation validation.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Test with valid arguments
        op = RenameModelOperation(**self.valid_args)
        op.validate(mock_collection)
        
        # Test with non-existent model
        op = RenameModelOperation(
            old_model_name="NonExistent",
            new_model_name="Basic Note"
        )
        with pytest.raises(ValueError, match="Model 'NonExistent' not found"):
            op.validate(mock_collection)
        
        # Test with duplicate model name
        op = RenameModelOperation(
            old_model_name="Basic",
            new_model_name="Basic"  # Already exists
        )
        with pytest.raises(ValueError, match="Model 'Basic' already exists"):
            op.validate(mock_collection)
    
    def test_execution(self, mock_collection):
        """Test operation execution.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Create and validate operation
        op = RenameModelOperation(**self.valid_args)
        op.validate(mock_collection)
        
        # Execute operation
        result = op.execute()
        
        # Verify result
        assert result.success
        assert result.changes  # Should have recorded changes
        
        # Verify model was renamed
        assert not any(m.name == "Basic" for m in mock_collection.models.values())
        new_model = next(m for m in mock_collection.models.values() 
                        if m.name == "Basic Note")
        
        # Verify notes were updated
        for note in mock_collection.notes.values():
            if note.model_id == new_model.id:
                # Verify the note is still associated with the renamed model
                assert note.model_id == new_model.id


class TestRenameModelIntegration(BaseWriteTest):
    """Integration tests for RenameModelOperation using real Anki packages."""
    
    # Test both v2 and v21
    versions_to_test = ["v2", "v21"]
    
    # Test parameters
    old_model_name = "subs2srs"
    new_model_name = "Sentence to Subs2SRS"
    model_id = None
    
    def setup_before_operation(self, context):
        """Get original model for verification."""
        collection = self.get_collection(context)
        
        # Find the model by name
        for mid, model in collection.models.items():
            if model.name == self.old_model_name:
                self.model_id = mid
                break
        
        assert self.model_id is not None, f"Model {self.old_model_name} not found"
    
    def get_operation(self):
        """Get the operation to test."""
        return RenameModelOperation(
            old_model_name=self.old_model_name,
            new_model_name=self.new_model_name
        )
    
    def verify_changes(self, context):
        """Verify that the model was renamed."""
        collection = self.get_collection(context)
        
        # Find the model by name
        model_id = None
        for mid, model in collection.models.items():
            if model.name == self.new_model_name:
                model_id = mid
                break
        
        assert model_id is not None, f"Model {self.new_model_name} not found"
        
        # Verify old model name doesn't exist
        assert not any(m.name == self.old_model_name for m in collection.models.values()), \
            f"Old model name {self.old_model_name} should not exist"
        
        # Verify notes were updated
        for note in collection.notes.values():
            if note.model_id == model_id:
                # Verify the note is still associated with the renamed model
                assert note.model_id == model_id 