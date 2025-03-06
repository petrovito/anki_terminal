import json
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List

import pytest

from anki_terminal.anki_types import (Collection, Deck, Field, Model, Note,
                                      Template)
from anki_terminal.ops.write.populate_fields import PopulateFieldsOperation
from anki_terminal.populators.populator_base import (FieldPopulator,
                                                     PopulatorConfigArgument)
from tests.fixtures.test_data_fixtures import apkg_v2_path, apkg_v21_path
from tests.ops.base_write_test import BaseWriteTest
from tests.ops.test_base import OperationTestBase


# Create a simple test populator for unit tests
class MockFieldPopulator(FieldPopulator):
    """A simple field populator for testing."""
    
    name = "test-populator"
    description = "A simple field populator for testing"
    config_args = [
        PopulatorConfigArgument(
            name="source_field",
            description="Field to copy values from",
            required=True
        ),
        PopulatorConfigArgument(
            name="target_field",
            description="Field to copy values to",
            required=True
        ),
        PopulatorConfigArgument(
            name="supports_batch",
            description="Whether this populator supports batch operations",
            required=False,
            default=False
        )
    ]
    
    @property
    def supports_batching(self) -> bool:
        """Whether this populator supports batch operations."""
        return self.config["supports_batch"]
    
    @property
    def target_fields(self) -> List[str]:
        """Get list of fields that will be modified by this populator."""
        return [self.config["target_field"]]
    
    def _validate_impl(self, model: Model) -> None:
        """Validate that the source field exists in the model.
        
        Args:
            model: The model to validate against
            
        Raises:
            ValueError: If the source field doesn't exist in the model
        """
        field_names = [f.name for f in model.fields]
        if self.config["source_field"] not in field_names:
            raise ValueError(f"Source field '{self.config['source_field']}' not found in model")
    
    def _populate_fields_impl(self, note: Note) -> Dict[str, str]:
        """Populate fields for a single note."""
        source_field = self.config["source_field"]
        target_field = self.config["target_field"]
        
        if source_field not in note.fields:
            raise ValueError(f"Source field '{source_field}' not found in note")
        return {target_field: note.fields[source_field].upper()}
    
    def _populate_batch_impl(self, notes: List[Note]) -> Dict[int, Dict[str, str]]:
        """Populate fields for a batch of notes."""
        source_field = self.config["source_field"]
        target_field = self.config["target_field"]
        
        updates = {}
        for note in notes:
            if source_field in note.fields:
                updates[note.id] = {target_field: note.fields[source_field].upper()}
        return updates

class TestPopulateFieldsOperation(OperationTestBase):
    """Unit tests for PopulateFieldsOperation."""
    
    operation_class = PopulateFieldsOperation
    
    @pytest.fixture
    def config_file(self):
        """Create a temporary config file for the test populator."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({
                "source_field": "Front",
                "target_field": "Back",
                "supports_batch": True
            }, f)
            self._config_file_path = f.name
            return f.name
    
    def test_validation(self, mock_collection, config_file):
        """Test operation validation.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
            config_file: Pytest fixture providing a temporary config file
        """
        # Test with valid arguments
        valid_args = {
            "model_name": "Basic",
            "populator_class": "tests.ops.write.test_populate_fields.MockFieldPopulator",
            "populator_config": config_file,
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
        
        # Test with invalid populator class
        op = PopulateFieldsOperation(
            **{**valid_args, "populator_class": "nonexistent.module.Class"}
        )
        with pytest.raises(ValueError, match="Could not load populator class"):
            op.validate(mock_collection)
        
        # Test with invalid target field
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({
                "source_field": "Front",
                "target_field": "NonExistent",
                "supports_batch": True
            }, f)
            invalid_config = f.name
        
        op = PopulateFieldsOperation(
            **{**valid_args, "populator_config": invalid_config}
        )
        with pytest.raises(ValueError, match="Target fields not found in model"):
            op.validate(mock_collection)
        os.unlink(invalid_config)
        
        # Test with JSON string instead of file path
        json_config = json.dumps({
            "source_field": "Front",
            "target_field": "Back",
            "supports_batch": True
        })
        op = PopulateFieldsOperation(
            **{**valid_args, "populator_config": json_config}
        )
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
            "populator_class": "tests.ops.write.test_populate_fields.MockFieldPopulator",
            "populator_config": config_file,
            "batch_size": 10
        }
        op = PopulateFieldsOperation(**valid_args)
        op.validate(mock_collection)
        
        # Execute operation
        result = op.execute()
        
        # Verify result
        assert result.success
        assert result.changes  # Should have recorded changes
        
        # Verify fields were updated
        for note in mock_collection.notes.values():
            if note.model_id == 1:  # Basic model
                assert note.fields["Back"] == note.fields["Front"].upper()
    
    def teardown_method(self, method):
        """Clean up temporary files."""
        if hasattr(self, '_config_file_path') and os.path.exists(self._config_file_path):
            os.unlink(self._config_file_path)

class TestPopulateFieldsIntegration(BaseWriteTest):
    """Integration tests for PopulateFieldsOperation using real Anki packages."""
    
    # Test only v21 for now
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
                "target_field": "MorphMan_FocusMorph",
                "supports_batch": True
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
        
        # Add TestFieldPopulator to the module path
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    def get_operation(self):
        """Return the populate fields operation."""
        return PopulateFieldsOperation(
            model_name=self.model_name,
            populator_class="tests.ops.write.test_populate_fields.MockFieldPopulator",
            populator_config=self.config_file,
            batch_size=10
        )
    
    def verify_changes(self, context):
        """Verify that the fields were populated correctly."""
        collection = self.get_collection(context)
        
        # Check that the fields were populated
        for note_id, note in collection.notes.items():
            if note.model_id == self.model_id:
                # The test populator should uppercase the source field
                assert note.fields["MorphMan_FocusMorph"] == note.fields["Expression"].upper()
    
    def teardown_method(self, method):
        """Clean up temporary files."""
        if self.config_file and os.path.exists(self.config_file):
            os.unlink(self.config_file)
            
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
        
        # Create operation with JSON string
        json_config = json.dumps({
            "source_field": "Expression",
            "target_field": "MorphMan_FocusMorph",
            "supports_batch": True
        })
        
        op = PopulateFieldsOperation(
            model_name="subs2srs",
            populator_class="tests.ops.write.test_populate_fields.MockFieldPopulator",
            populator_config=json_config,
            batch_size=1
        )
        
        # Validate and execute
        op.validate(collection)
        result = op.execute()
        
        # Verify result
        assert result.success
        assert result.changes
        assert collection.notes[1].fields["MorphMan_FocusMorph"] == "テスト".upper() 