import pytest
from datetime import datetime
from ops.write.migrate_notes import MigrateNotesOperation
from tests.ops.test_base import OperationTestBase
from anki_types import Collection, Model, Field, Note

class TestMigrateNotesOperation(OperationTestBase):
    """Unit tests for MigrateNotesOperation."""
    
    operation_class = MigrateNotesOperation
    valid_args = {
        "model_name": "Basic",  # Source model
        "target_model_name": "Advanced",  # Target model
        "field_mapping": {
            "Front": "Question",  # Map Front field to Question
            "Back": "Answer"      # Map Back field to Answer
        }
    }
    
    def test_validation(self, mock_collection):
        """Test operation validation.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Test with valid arguments
        op = MigrateNotesOperation(**self.valid_args)
        op.validate(mock_collection)
        
        # Test with non-existent source model
        op = MigrateNotesOperation(
            **{**self.valid_args, "model_name": "NonExistent"}
        )
        with pytest.raises(ValueError, match="Source model not found"):
            op.validate(mock_collection)
        
        # Test with non-existent target model
        op = MigrateNotesOperation(
            **{**self.valid_args, "target_model_name": "NonExistent"}
        )
        with pytest.raises(ValueError, match="Target model not found"):
            op.validate(mock_collection)
        
        # Test with non-dict field mapping
        op = MigrateNotesOperation(
            **{**self.valid_args, "field_mapping": "not a dict"}
        )
        with pytest.raises(ValueError, match="Field mapping must be a dictionary"):
            op.validate(mock_collection)
        
        # Test with non-existent source field
        op = MigrateNotesOperation(
            **{**self.valid_args, "field_mapping": {"NonExistent": "Question"}}
        )
        with pytest.raises(ValueError, match="Source field not found"):
            op.validate(mock_collection)
        
        # Test with non-existent target field
        op = MigrateNotesOperation(
            **{**self.valid_args, "field_mapping": {"Front": "NonExistent"}}
        )
        with pytest.raises(ValueError, match="Target field not found"):
            op.validate(mock_collection)
    
    def test_execution(self, mock_collection):
        """Test operation execution.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Add a test note to the Basic model
        test_note = Note(
            id=2,  # Different from the existing note
            guid="test_guid_2",
            model_id=1,  # Basic model ID
            modification_time=datetime.fromtimestamp(0),
            usn=-1,
            tags=[],
            fields={"Front": "Test Question", "Back": "Test Answer"},
            sort_field=0,
            checksum=0,
            flags=0
        )
        mock_collection.notes[2] = test_note
        
        # Create and validate operation
        op = MigrateNotesOperation(**self.valid_args)
        op.validate(mock_collection)
        
        # Get initial note counts
        initial_basic_notes = len([n for n in mock_collection.notes.values() if n.model_id == 1])
        initial_advanced_notes = len([n for n in mock_collection.notes.values() if n.model_id == 2])
        
        # Execute operation
        result = op.execute()
        
        # Verify result
        assert result.success
        assert result.changes  # Should have recorded changes
        
        # Verify note counts changed
        final_basic_notes = len([n for n in mock_collection.notes.values() if n.model_id == 1])
        final_advanced_notes = len([n for n in mock_collection.notes.values() if n.model_id == 2])
        assert final_basic_notes == 0  # All notes should be moved
        assert final_advanced_notes == initial_basic_notes  # Should have all the notes
        
        # Verify note content was mapped correctly
        migrated_note = mock_collection.notes[2]  # Get our test note
        assert migrated_note.model_id == 2  # Advanced model ID
        assert migrated_note.fields["Question"] == "Test Question"
        assert migrated_note.fields["Answer"] == "Test Answer"
        assert migrated_note.fields["Notes"] == ""  # Unmapped field should be empty
        assert migrated_note.usn == -1  # Should be marked for sync
    
    def test_execution_no_notes(self, mock_collection):
        """Test operation execution when no notes exist for the source model.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Remove all notes from the Basic model
        mock_collection.notes = {
            k: v for k, v in mock_collection.notes.items()
            if v.model_id != 1  # Remove Basic model notes
        }
        
        # Create and validate operation
        op = MigrateNotesOperation(**self.valid_args)
        op.validate(mock_collection)
        
        # Execute operation
        result = op.execute()
        
        # Verify result
        assert result.success
        assert not result.changes  # Should not have any changes
        assert "No notes found" in result.message 