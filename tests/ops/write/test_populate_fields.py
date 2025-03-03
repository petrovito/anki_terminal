import pytest
import os
import json
import tempfile
from typing import Dict, Any

from ops.write.populate_fields import PopulateFieldsOperation
from tests.ops.test_base import OperationTestBase
from tests.ops.base_write_test import BaseWriteTest
from anki_types import Collection, Model, Field, Note
from tests.fixtures.test_data_fixtures import apkg_v2_path, apkg_v21_path
from populators.base import FieldPopulator

# Create a simple test populator for unit tests
class TestFieldPopulator(FieldPopulator):
    """A simple field populator for testing."""
    
    def __init__(self, config_path: str):
        """Initialize the populator from a config file."""
        try:
            with open(config_path) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid populator configuration: {str(e)}")
            
        if "source_field" not in config or "target_field" not in config:
            raise ValueError("Config must specify 'source_field' and 'target_field'")
            
        self.source_field = config["source_field"]
        self.target_field = config["target_field"]
        self.supports_batch = config.get("supports_batch", False)
    
    @property
    def supports_batching(self) -> bool:
        """Whether this populator supports batch operations."""
        return self.supports_batch
    
    @property
    def target_fields(self) -> list[str]:
        """Get list of fields that will be modified by this populator."""
        return [self.target_field]
    
    def populate_fields(self, note: Note) -> Dict[str, str]:
        """Populate fields for a single note."""
        if self.source_field not in note.fields:
            raise ValueError(f"Source field '{self.source_field}' not found in note")
        return {self.target_field: note.fields[self.source_field].upper()}
    
    def populate_batch(self, notes: list[Note]) -> Dict[int, Dict[str, str]]:
        """Populate fields for a batch of notes."""
        if not self.supports_batching:
            raise NotImplementedError("This populator does not support batch operations")
            
        updates = {}
        for note in notes:
            if self.source_field in note.fields:
                updates[note.id] = {self.target_field: note.fields[self.source_field].upper()}
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
            "populator_class": "tests.ops.write.test_populate_fields.TestFieldPopulator",
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
    
    def test_execution(self, mock_collection, config_file):
        """Test operation execution.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
            config_file: Pytest fixture providing a temporary config file
        """
        # Create and validate operation
        valid_args = {
            "model_name": "Basic",
            "populator_class": "tests.ops.write.test_populate_fields.TestFieldPopulator",
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
        if hasattr(self, 'config_file') and os.path.exists(self.config_file):
            os.unlink(self.config_file)

class TestPopulateFieldsIntegration(BaseWriteTest):
    """Integration tests for PopulateFieldsOperation using real Anki packages."""
    
    # Test only v21 for now
    versions_to_test = ["v21"]
    
    # Test parameters
    model_name = "Basic"
    config_file = None
    model_id = None
    
    @pytest.fixture(autouse=True)
    def setup_config(self):
        """Create a temporary config file for the test populator."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({
                "source_field": "Front",
                "target_field": "Back",
                "supports_batch": True
            }, f)
            self.config_file = f.name
    
    def setup_before_operation(self, context):
        """Get model ID for verification."""
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
            populator_class="tests.ops.write.test_populate_fields.TestFieldPopulator",
            populator_config=self.config_file,
            batch_size=10
        )
    
    def verify_changes(self, context):
        """Verify that fields were populated."""
        collection = self.get_collection(context)
        
        # Find the model by name
        model_id = None
        for mid, model in collection.models.items():
            if model.name == self.model_name:
                model_id = mid
                break
        
        assert model_id is not None, f"Model {self.model_name} not found"
        
        # Verify fields were updated
        for note in collection.notes.values():
            if note.model_id == model_id:
                assert "Front" in note.fields, "Front field missing in note"
                assert "Back" in note.fields, "Back field missing in note"
                assert note.fields["Back"] == note.fields["Front"].upper(), "Back field not updated correctly"
    
    def teardown_method(self, method):
        """Clean up temporary files."""
        if self.config_file and os.path.exists(self.config_file):
            os.unlink(self.config_file) 