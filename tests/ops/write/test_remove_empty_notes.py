from datetime import datetime

import pytest

from anki_terminal.commons.anki_types import Card, Collection, Field, Model, Note
from anki_terminal.ops.write.remove_empty_notes import RemoveEmptyNotesOperation
from tests.ops.test_base import OperationTestBase


class TestRemoveEmptyNotesOperation(OperationTestBase):
    """Unit tests for RemoveEmptyNotesOperation."""
    
    operation_class = RemoveEmptyNotesOperation
    valid_args = {
        "model": "Basic",
        "field": "Front"
    }
    
    def test_validation(self, mock_collection):
        """Test operation validation.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Test with valid arguments
        op = RemoveEmptyNotesOperation(**self.valid_args)
        op.validate(mock_collection)
        
        # Test with non-existent model
        op = RemoveEmptyNotesOperation(
            model="NonExistent",
            field="Front"
        )
        with pytest.raises(ValueError, match="Model not found"):
            op.validate(mock_collection)
        
        # Test with non-existent field
        op = RemoveEmptyNotesOperation(
            model="Basic",
            field="NonExistent"
        )
        with pytest.raises(ValueError, match="Field 'NonExistent' not found"):
            op.validate(mock_collection)
    
    def test_auto_detect_model(self, mock_collection):
        """Test auto-detection of model when not specified.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Create operation without specifying model
        op = RemoveEmptyNotesOperation(field="Front")
        op.validate(mock_collection)
        
        # Verify model was auto-detected
        assert op.args["model"] == "Basic"  # Should have detected the Basic model
    
    def test_execution_no_empty_notes(self, mock_collection):
        """Test operation execution when there are no empty notes.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Create operation
        op = RemoveEmptyNotesOperation(**self.valid_args)
        op.validate(mock_collection)
        
        # Execute operation
        result = op.execute()
        
        # Verify result
        assert result.success
        assert "No notes found with empty" in result.message
        assert not result.changes
    
    def test_execution_with_empty_notes(self):
        """Test operation execution when there are empty notes."""
        # Create a test collection with empty notes
        model = Model(
            id=1,
            name="Basic",
            fields=[
                Field(name="Front", ordinal=0),
                Field(name="Back", ordinal=1)
            ],
            templates=[],
            css="",
            modified=int(datetime.now().timestamp())
        )
        
        # Create notes with empty fields
        notes = {
            1: Note(
                id=1,
                model_id=1,
                fields={"Front": "", "Back": "Back content"},  # Empty Front
                tags=[],
                modified=int(datetime.now().timestamp())
            ),
            2: Note(
                id=2,
                model_id=1,
                fields={"Front": "   ", "Back": "Back content"},  # Whitespace Front
                tags=[],
                modified=int(datetime.now().timestamp())
            ),
            3: Note(
                id=3,
                model_id=1,
                fields={"Front": "Front content", "Back": "Back content"},  # Non-empty Front
                tags=[],
                modified=int(datetime.now().timestamp())
            )
        }
        
        # Create cards associated with these notes
        cards = {
            1: Card(
                id=1,
                note_id=1,
                deck_id=1,
                template_id=1,
                modified=int(datetime.now().timestamp())
            ),
            2: Card(
                id=2,
                note_id=2,
                deck_id=1,
                template_id=1,
                modified=int(datetime.now().timestamp())
            ),
            3: Card(
                id=3,
                note_id=3,
                deck_id=1,
                template_id=1,
                modified=int(datetime.now().timestamp())
            )
        }
        
        # Create collection
        collection = Collection(
            id=1,
            models={1: model},
            notes=notes,
            cards=cards,
            decks={},
            tags=[],
            modified=int(datetime.now().timestamp())
        )
        
        # Create operation
        op = RemoveEmptyNotesOperation(
            model="Basic",
            field="Front"
        )
        op.validate(collection)
        
        # Execute operation
        result = op.execute()
        
        # Verify result
        assert result.success
        assert "Removed 2 notes and 2 cards" in result.message
        assert len(result.changes) == 4  # 2 notes + 2 cards
        
        # Verify notes and cards were removed
        assert len(collection.notes) == 1
        assert 3 in collection.notes  # Only note 3 should remain
        assert len(collection.cards) == 1
        assert 3 in collection.cards  # Only card 3 should remain
    
    def test_execution_with_auto_detected_model(self):
        """Test operation execution with auto-detected model."""
        # Create a test collection with empty notes
        model = Model(
            id=1,
            name="Basic",
            fields=[
                Field(name="Front", ordinal=0),
                Field(name="Back", ordinal=1)
            ],
            templates=[],
            css="",
            modified=int(datetime.now().timestamp())
        )
        
        # Create notes with empty fields
        notes = {
            1: Note(
                id=1,
                model_id=1,
                fields={"Front": "", "Back": "Back content"},  # Empty Front
                tags=[],
                modified=int(datetime.now().timestamp())
            ),
            2: Note(
                id=2,
                model_id=1,
                fields={"Front": "Front content", "Back": "Back content"},  # Non-empty Front
                tags=[],
                modified=int(datetime.now().timestamp())
            )
        }
        
        # Create cards associated with these notes
        cards = {
            1: Card(
                id=1,
                note_id=1,
                deck_id=1,
                template_id=1,
                modified=int(datetime.now().timestamp())
            ),
            2: Card(
                id=2,
                note_id=2,
                deck_id=1,
                template_id=1,
                modified=int(datetime.now().timestamp())
            )
        }
        
        # Create collection
        collection = Collection(
            id=1,
            models={1: model},
            notes=notes,
            cards=cards,
            decks={},
            tags=[],
            modified=int(datetime.now().timestamp())
        )
        
        # Create operation without specifying model
        op = RemoveEmptyNotesOperation(field="Front")
        op.validate(collection)
        
        # Execute operation
        result = op.execute()
        
        # Verify result
        assert result.success
        assert "Removed 1 notes and 1 cards" in result.message
        assert len(result.changes) == 2  # 1 note + 1 card
        
        # Verify notes and cards were removed
        assert len(collection.notes) == 1
        assert 2 in collection.notes  # Only note 2 should remain
        assert len(collection.cards) == 1
        assert 2 in collection.cards  # Only card 2 should remain 