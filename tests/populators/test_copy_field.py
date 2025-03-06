import pytest

from anki_terminal.populators.copy_field import CopyFieldPopulator
from tests.populators.base_test import PopulatorTestBase


class TestCopyFieldPopulator(PopulatorTestBase):
    """Unit tests for CopyFieldPopulator."""
    
    populator_class = CopyFieldPopulator
    config = {
        "source_field": "Field1",
        "target_field": "Field3",
        "supports_batch": True
    }
    
    def test_validation_missing_field(self, test_model):
        """Test validation with missing field."""
        # Create a populator with a nonexistent source field
        config = {
            "source_field": "NonexistentField",
            "target_field": "Field3",
            "supports_batch": True
        }
        populator = self.create_populator(config_json=config)
        
        # Validation should raise an exception
        with pytest.raises(ValueError):
            populator.validate(test_model)
        
        # Create a populator with a nonexistent target field
        config = {
            "source_field": "Field1",
            "target_field": "NonexistentField",
            "supports_batch": True
        }
        populator = self.create_populator(config_json=config)
        
        # Validation should raise an exception
        with pytest.raises(ValueError):
            populator.validate(test_model)
    
    def test_populate_fields(self, test_model, test_notes):
        """Test that fields are populated correctly."""
        populator = self.create_populator()
        
        # Validate the populator
        populator.validate(test_model)
        
        # Populate fields for a single note
        note = test_notes[0]
        result = populator.populate_fields(note)
        
        # Verify the result
        assert "Field3" in result
        assert result["Field3"] == note.fields["Field1"]
    
    def test_populate_batch(self, test_model, test_notes):
        """Test that batch population works correctly."""
        populator = self.create_populator()
        
        # Validate the populator
        populator.validate(test_model)
        
        # Populate fields for multiple notes
        result = populator.populate_batch(test_notes)
        
        # Verify the result
        assert len(result) == len(test_notes)
        for note_id, fields in result.items():
            note = next(n for n in test_notes if n.id == note_id)
            assert "Field3" in fields
            assert fields["Field3"] == note.fields["Field1"] 