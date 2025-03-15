import pytest

from anki_terminal.commons.anki_types import Collection, Deck, Field, Model, Note, Template
from anki_terminal.ops.write.tag_notes import TagNotesOperation
from tests.fixtures.test_data_fixtures import apkg_v21_path
from tests.ops.base_write_test import BaseWriteTest
from tests.ops.test_base import OperationTestBase


class TestTagNotesOperation(OperationTestBase):
    """Test the tag notes operation."""
    
    operation_class = TagNotesOperation
    
    def test_validation(self, mock_collection):
        """Test operation validation."""
        self.collection = mock_collection
        
        # Create a test model
        self.model = Model(
            id=1,
            name="Test Model",
            fields=[
                Field(name="Front", ordinal=0),
                Field(name="Back", ordinal=1),
                Field(name="ID", ordinal=2)
            ],
            templates=[
                Template(name="Card 1", question_format="{{Front}}", answer_format="{{Back}}", ordinal=0)
            ],
            css="",
            deck_id=1,
            modification_time=mock_collection.modification_time,
            type=0,
            usn=0,
            version=0
        )
        
        # Create test notes
        self.notes = [
            Note(
                id=1,
                guid="guid1",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=[],
                fields={
                    "Front": "Front 1",
                    "Back": "Back 1",
                    "ID": "Monster_25_06180_0.13.40.487"
                },
                sort_field=0,
                checksum=0
            ),
            Note(
                id=2,
                guid="guid2",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=[],
                fields={
                    "Front": "Front 2",
                    "Back": "Back 2",
                    "ID": "Monster_25_06181_0.13.41.593"
                },
                sort_field=0,
                checksum=0
            ),
            Note(
                id=3,
                guid="guid3",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=[],
                fields={
                    "Front": "Front 3",
                    "Back": "Back 3",
                    "ID": "Attack_On_Titan_S03_12_06182_0.13.42.698"
                },
                sort_field=0,
                checksum=0
            )
        ]
        
        # Add model and notes to collection
        self.collection.models[self.model.id] = self.model
        for note in self.notes:
            self.collection.notes[note.id] = note
        
        # Test with valid arguments
        operation = TagNotesOperation(
            model="Test Model",
            source_field="ID",
            pattern=r"([^_]+_\d+)"
        )
        operation.validate(self.collection)
        
        # Test with non-existent model
        with pytest.raises(ValueError, match="Model not found"):
            operation = TagNotesOperation(
                model="Non-existent Model",
                source_field="ID",
                pattern=r"([^_]+_\d+)"
            )
            operation.validate(self.collection)
        
        # Test with non-existent field
        with pytest.raises(ValueError, match="Source field 'Non-existent Field' not found in model"):
            operation = TagNotesOperation(
                model="Test Model",
                source_field="Non-existent Field",
                pattern=r"([^_]+_\d+)"
            )
            operation.validate(self.collection)
        
        # Test with invalid pattern (no capture groups)
        with pytest.raises(ValueError, match="Pattern must contain at least one capture group"):
            operation = TagNotesOperation(
                model="Test Model",
                source_field="ID",
                pattern=r"[^_]+_\d+"
            )
            operation.validate(self.collection)
        
        # Test with invalid regex pattern
        with pytest.raises(ValueError, match="Invalid regular expression pattern"):
            operation = TagNotesOperation(
                model="Test Model",
                source_field="ID",
                pattern=r"([^_]+_\d+"
            )
            operation.validate(self.collection)
    
    def test_execution(self, mock_collection):
        """Test operation execution."""
        self.collection = mock_collection
        
        # Create a test model
        self.model = Model(
            id=1,
            name="Test Model",
            fields=[
                Field(name="Front", ordinal=0),
                Field(name="Back", ordinal=1),
                Field(name="ID", ordinal=2)
            ],
            templates=[
                Template(name="Card 1", question_format="{{Front}}", answer_format="{{Back}}", ordinal=0)
            ],
            css="",
            deck_id=1,
            modification_time=mock_collection.modification_time,
            type=0,
            usn=0,
            version=0
        )
        
        # Create test notes
        self.notes = [
            Note(
                id=1,
                guid="guid1",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=[],
                fields={
                    "Front": "Front 1",
                    "Back": "Back 1",
                    "ID": "Monster_25_06180_0.13.40.487"
                },
                sort_field=0,
                checksum=0
            ),
            Note(
                id=2,
                guid="guid2",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=[],
                fields={
                    "Front": "Front 2",
                    "Back": "Back 2",
                    "ID": "Monster_25_06181_0.13.41.593"
                },
                sort_field=0,
                checksum=0
            ),
            Note(
                id=3,
                guid="guid3",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=[],
                fields={
                    "Front": "Front 3",
                    "Back": "Back 3",
                    "ID": "Attack_On_Titan_S03_12_06182_0.13.42.698"
                },
                sort_field=0,
                checksum=0
            )
        ]
        
        # Add model and notes to collection
        self.collection.models[self.model.id] = self.model
        for note in self.notes:
            self.collection.notes[note.id] = note
        
        # Test with Monster pattern
        operation = TagNotesOperation(
            model="Test Model",
            source_field="ID",
            pattern=r"^(Monster_\d+)"
        )
        operation.collection = self.collection
        result = operation.execute()
        
        assert result.success
        
        # Check that Monster notes were tagged
        for note in self.notes[:2]:
            assert "Monster_25" in note.tags
        
        # Check that Attack on Titan note was not tagged
        assert not self.notes[2].tags
        
        # Test with Attack on Titan pattern
        operation = TagNotesOperation(
            model="Test Model",
            source_field="ID",
            pattern=r"^(Attack_On_Titan_S\d+_\d+)"
        )
        operation.collection = self.collection
        result = operation.execute()
        
        assert result.success
        
        # Check that Attack on Titan note was tagged
        assert "Attack_On_Titan_S03_12" in self.notes[2].tags
        
        # Check that Monster notes were not tagged again
        for note in self.notes[:2]:
            assert "Monster_25" in note.tags
            assert "Attack_On_Titan_S03_12" not in note.tags
    
    def test_tag_prefix(self, mock_collection):
        """Test operation with tag prefix."""
        self.collection = mock_collection
        
        # Create a test model
        self.model = Model(
            id=1,
            name="Test Model",
            fields=[
                Field(name="Front", ordinal=0),
                Field(name="Back", ordinal=1),
                Field(name="ID", ordinal=2)
            ],
            templates=[
                Template(name="Card 1", question_format="{{Front}}", answer_format="{{Back}}", ordinal=0)
            ],
            css="",
            deck_id=1,
            modification_time=mock_collection.modification_time,
            type=0,
            usn=0,
            version=0
        )
        
        # Create test notes
        self.notes = [
            Note(
                id=1,
                guid="guid1",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=[],
                fields={
                    "Front": "Front 1",
                    "Back": "Back 1",
                    "ID": "Monster_25_06180_0.13.40.487"
                },
                sort_field=0,
                checksum=0
            ),
            Note(
                id=2,
                guid="guid2",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=[],
                fields={
                    "Front": "Front 2",
                    "Back": "Back 2",
                    "ID": "Monster_25_06181_0.13.41.593"
                },
                sort_field=0,
                checksum=0
            )
        ]
        
        # Add model and notes to collection
        self.collection.models[self.model.id] = self.model
        for note in self.notes:
            self.collection.notes[note.id] = note
        
        operation = TagNotesOperation(
            model="Test Model",
            source_field="ID",
            pattern=r"^(Monster_\d+)",
            tag_prefix="Series_"
        )
        operation.collection = self.collection
        result = operation.execute()
        
        assert result.success
        
        # Check that notes were tagged with prefix
        for note in self.notes:
            assert "Series_Monster_25" in note.tags
            assert "Monster_25" not in note.tags


class TestTagNotesIntegration(BaseWriteTest):
    """Integration tests for the tag notes operation."""
    
    # Use the existing fixture from test_data_fixtures.py
    versions_to_test = ["v21"]
    
    def setup_before_operation(self, context):
        """Set up test data before operation."""
        # No need to create a new note, we'll use the existing ones
        pass
    
    def get_operation(self):
        """Get the operation to test."""
        return TagNotesOperation(
            model="subs2srs",
            source_field="SequenceMarker",
            pattern=r"^(\d+)_",  # Extract episode number (e.g., "01" from "01_0001_0.00.05.631")
            tag_prefix="Episode"
        )
    
    def verify_changes(self, context):
        """Verify that the changes were applied correctly."""
        collection = self.get_collection(context)
        
        # Check that notes were tagged with Episode_01 and original tags are preserved
        for note_id, note in collection.notes.items():
            if "subs2srs" in note.fields.get("SequenceMarker", ""):
                # Check that the new tag was added
                assert "Episode_01" in note.tags, f"Note {note_id} should have Episode_01 tag"
                
                # Check that the original tag was preserved
                assert "golden_kamuy_s3_01" in note.tags, f"Note {note_id} should still have golden_kamuy_s3_01 tag" 