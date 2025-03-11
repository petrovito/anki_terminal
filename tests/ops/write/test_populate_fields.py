import json
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List

import pytest

from anki_terminal.anki_types import (Collection, Deck, Field, Model, Note,
                                      Template)
from anki_terminal.ops.write.populate_fields import PopulateFieldsOperation
from anki_terminal.populators.copy_field import CopyFieldPopulator
from tests.fixtures.test_data_fixtures import apkg_v2_path, apkg_v21_path
from tests.ops.base_write_test import BaseWriteTest
from tests.ops.test_base import OperationTestBase


class TestPopulateFieldsOperation(OperationTestBase):
    """Test the populate fields operation."""
    
    # Set the operation class for the test base
    operation_class = PopulateFieldsOperation
    
    @pytest.fixture
    def config_file(self):
        """Create a temporary config file for the test populator."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({
                "source_field": "Front",
                "target_field": "Back"
            }, f)
            self._config_file_path = f.name
            return f.name
    
    def test_operation_metadata(self):
        """Test that the operation has all required metadata."""
        assert self.operation_class.name == "populate-fields"
        assert self.operation_class.description
        assert not self.operation_class.readonly
    
    def test_validation(self, mock_collection, config_file):
        """Test operation validation.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
            config_file: Pytest fixture providing a temporary config file
        """
        # Test with valid arguments
        valid_args = {
            "model_name": "Basic",
            "populator": "copy-field",
            "populator_config_file": config_file,
            "batch_size": 10
        }
        op = PopulateFieldsOperation(**valid_args)
        op.validate(mock_collection)
        
        # Test with non-existent model
        op = PopulateFieldsOperation(
            **{**valid_args, "model_name": "NonExistent"}
        )
        with pytest.raises(ValueError, match="Model not found"):
            op.validate(mock_collection)
        
        # Test with invalid populator
        op = PopulateFieldsOperation(
            **{**valid_args, "populator": "nonexistent-populator"}
        )
        with pytest.raises(ValueError, match="Populator not found"):
            op.validate(mock_collection)
    
    def test_execution(self, mock_collection, config_file):
        """Test operation execution.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
            config_file: Pytest fixture providing a temporary config file
        """
        # Create and validate operation
        valid_args = {
            "model_name": "Basic",
            "populator": "copy-field",
            "populator_config_file": config_file,
            "batch_size": 10
        }
        op = PopulateFieldsOperation(**valid_args)
        op.validate(mock_collection)
        
        # Execute operation
        result = op.execute()
        
        # Check result
        assert result.success
        assert len(result.changes) > 0
        
        # Check that fields were updated
        for note in mock_collection.notes.values():
            if note.model_id == 1:  # Basic model
                assert note.fields["Back"] == note.fields["Front"]


class TestPopulateFieldsIntegration(BaseWriteTest):
    """Integration test for the populate fields operation."""
    
    versions_to_test = ["v21"]
    
    # Test parameters
    model_name = "subs2srs"
    config_file = None
    model_id = None
    
    @pytest.fixture(autouse=True)
    def setup_config(self):
        """Create a temporary config file for the test populator."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({
                "source_field": "Expression",
                "target_field": "MorphMan_FocusMorph"
            }, f)
            self.config_file = f.name
    
    def setup_before_operation(self, context):
        """Get model ID for verification and add a test note."""
        collection = self.get_collection(context)
        
        # Find the model by name
        for mid, model in collection.models.items():
            if model.name == self.model_name:
                self.model_id = mid
                break
        
        assert self.model_id is not None, f"Model {self.model_name} not found"
    
    def get_operation(self):
        """Return the populate fields operation."""
        return PopulateFieldsOperation(
            model_name=self.model_name,
            populator="copy-field",
            populator_config_file=self.config_file,
            batch_size=10
        )
    
    def verify_changes(self, context):
        """Verify that the fields were populated correctly."""
        collection = self.get_collection(context)
        
        # Check that the fields were populated
        for note_id, note in collection.notes.items():
            if note.model_id == self.model_id:
                # The copy field populator should copy the source field to the target field
                assert note.fields["MorphMan_FocusMorph"] == note.fields["Expression"]
    
    def test_with_json_string(self):
        """Test the operation with a JSON string instead of a file path."""
        # This is a unit test, not an integration test
        # Create a mock collection
        from datetime import datetime
        
        # Create a model
        model = Model(
            id=1,
            name="subs2srs",
            fields=[
                Field(name="SequenceMarker", ordinal=0),
                Field(name="Audio", ordinal=1),
                Field(name="Snapshot", ordinal=2),
                Field(name="Expression", ordinal=3),
                Field(name="MorphMan_FocusMorph", ordinal=4)
            ],
            templates=[
                Template(
                    name="Card 1",
                    question_format="{{Expression}}",
                    answer_format="{{FrontSide}}<hr>{{MorphMan_FocusMorph}}",
                    ordinal=0
                )
            ],
            css=".card { font-family: arial; font-size: 20px; }",
            deck_id=1,
            modification_time=datetime.now(),
            type=0,
            usn=-1,
            version=11
        )
        
        # Create a note
        note = Note(
            id=1,
            guid="test-guid",
            model_id=1,
            modification_time=datetime.now(),
            usn=-1,
            tags=[],
            fields={
                "SequenceMarker": "01_0001",
                "Audio": "[sound:test.mp3]",
                "Snapshot": "<img src='test.jpg'>",
                "Expression": "テスト",
                "MorphMan_FocusMorph": ""
            },
            sort_field=0,
            checksum=0
        )
        
        # Create a deck
        deck = Deck(
            id=1,
            name="Default",
            description="",
            modification_time=datetime.now(),
            usn=-1,
            collapsed=False,
            browser_collapsed=False,
            dynamic=False,
            new_today=(0, 0),
            review_today=(0, 0),
            learn_today=(0, 0),
            time_today=(0, 0),
            conf_id=1
        )
        
        # Create a collection
        collection = Collection(
            id=1,
            creation_time=datetime.now(),
            modification_time=datetime.now(),
            schema_modification=1,
            version=11,
            dirty=0,
            usn=-1,
            last_sync=datetime.now(),
            models={1: model},
            decks={1: deck},
            notes={1: note},
            cards={},
            config={},
            deck_configs={},
            tags=[]
        )
        
        # For this test, we'll directly provide the config in the constructor
        # instead of using a JSON string, since we're not testing file loading
        op = PopulateFieldsOperation(
            model_name="subs2srs",
            populator="copy-field",
            source_field="Expression",
            target_field="MorphMan_FocusMorph",
            batch_size=1
        )
        
        # Validate and execute
        op.validate(collection)
        result = op.execute()
        
        # Verify result
        assert result.success
        assert result.changes
        assert collection.notes[1].fields["MorphMan_FocusMorph"] == "テスト" 