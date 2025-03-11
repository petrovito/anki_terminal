import json
import tempfile
from typing import Dict, List, Type

import pytest

from anki_terminal.commons.anki_types import Field, Model, Note, Template
from anki_terminal.populators.populator_base import FieldPopulator


class PopulatorTestBase:
    """Base class for testing field populators.
    
    This class provides a framework for testing field populators by:
    1. Creating a test model with fields
    2. Creating test notes
    3. Testing validation
    4. Testing field population
    
    Subclasses should set:
    - populator_class: The field populator class to test
    - config: The configuration for the populator
    """
    
    populator_class: Type[FieldPopulator] = None
    config: Dict = None
    
    @pytest.fixture
    def config_file(self):
        """Create a temporary config file for the populator."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(self.config, f)
            self._config_file_path = f.name
            return f.name
    
    @pytest.fixture
    def test_model(self):
        """Create a test model with fields."""
        return Model(
            id=1,
            name="Test Model",
            fields=[
                Field(name="Field1", ordinal=0),
                Field(name="Field2", ordinal=1),
                Field(name="Field3", ordinal=2)
            ],
            templates=[
                Template(
                    name="Card 1",
                    question_format="{{Field1}}",
                    answer_format="{{FrontSide}}<hr>{{Field2}}",
                    ordinal=0
                )
            ],
            css=".card { font-family: arial; font-size: 20px; }",
            deck_id=1,
            modification_time=1234567890,
            type=0,
            usn=-1,
            version=11
        )
    
    @pytest.fixture
    def test_notes(self):
        """Create test notes."""
        return [
            Note(
                id=1,
                guid="test-guid-1",
                model_id=1,
                modification_time=1234567890,
                usn=-1,
                tags=[],
                fields={
                    "Field1": "Value 1-1",
                    "Field2": "Value 1-2",
                    "Field3": ""
                },
                sort_field=0,
                checksum=0
            ),
            Note(
                id=2,
                guid="test-guid-2",
                model_id=1,
                modification_time=1234567890,
                usn=-1,
                tags=[],
                fields={
                    "Field1": "Value 2-1",
                    "Field2": "Value 2-2",
                    "Field3": ""
                },
                sort_field=0,
                checksum=0
            )
        ]
    
    def create_populator(self, config_file=None, config_json=None):
        """Create a populator instance.
        
        Args:
            config_file: Path to config file
            config_json: JSON string configuration or dictionary
            
        Returns:
            Populator instance
        """
        if config_file:
            return self.populator_class(config_file)
        elif config_json:
            if isinstance(config_json, dict):
                return self.populator_class(json.dumps(config_json))
            else:
                return self.populator_class(config_json)
        else:
            return self.populator_class(json.dumps(self.config))
    
    def test_validation(self, test_model):
        """Test that validation works correctly."""
        populator = self.create_populator()
        
        # This should not raise an exception
        populator.validate(test_model)
    
    def test_populate_fields(self, test_model, test_notes):
        """Test that fields are populated correctly."""
        populator = self.create_populator()
        
        # Validate the populator
        populator.validate(test_model)
        
        # Populate fields for a single note
        result = populator.populate_fields(test_notes[0])
        
        # Verify the result
        assert isinstance(result, dict)
        
        # Subclasses should add more specific assertions
    
    def test_populate_batch(self, test_model, test_notes):
        """Test that batch population works correctly if supported."""
        populator = self.create_populator()
        
        # Validate the populator
        populator.validate(test_model)
        
        # Skip if batching is not supported
        if not populator.supports_batching:
            pytest.skip("Populator does not support batching")
        
        # Populate fields for multiple notes
        result = populator.populate_batch(test_notes)
        
        # Verify the result
        assert isinstance(result, dict)
        assert len(result) == len(test_notes)
        
        # Subclasses should add more specific assertions
    
    def teardown_method(self, method):
        """Clean up temporary files."""
        if hasattr(self, '_config_file_path') and self._config_file_path:
            import os
            if os.path.exists(self._config_file_path):
                os.unlink(self._config_file_path) 