import pytest
import json
import tempfile
from pathlib import Path
from anki_context import AnkiContext
from operations import OperationType, OperationRecipe
from populators.copy_field import CopyFieldPopulator
from populators.concat_fields import ConcatFieldsPopulator
from anki_types import Note

def create_test_config(tmp_path: Path, config: dict) -> Path:
    """Helper to create a temporary config file."""
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
    return config_path

def test_copy_field_populator(tmp_path):
    """Test that copy field populator works correctly."""
    # Create test config
    config = {
        "source_field": "Front",
        "target_field": "Back"
    }
    config_path = create_test_config(tmp_path, config)
    
    # Create output file
    output_path = tmp_path / "output.apkg"
    
    # Run populate fields operation
    with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as context:
        recipe = OperationRecipe(
            operation_type=OperationType.POPULATE_FIELDS,
            model_name="Basic Card",
            populator_class="populators.copy_field.CopyFieldPopulator",
            populator_config=str(config_path)
        )
        context.run(recipe)
    
    # Verify changes
    with AnkiContext(output_path, read_only=True) as context:
        example = context._operations._read_ops.get_note_example("Basic Card")
        assert example["Back"] == example["Front"]

def test_concat_fields_populator(tmp_path):
    """Test that concat fields populator works correctly."""
    # First add a new field to copy into
    output1 = tmp_path / "with_new_field.apkg"
    with AnkiContext("test_data/jap.apkg", output1, read_only=False) as context:
        # Add new model with extra field
        context.run(OperationRecipe(
            operation_type=OperationType.ADD_MODEL,
            model_name="Test Model",
            fields=["Front", "Back", "Combined"],
            template_name="Card 1",
            question_format="{{Front}}",
            answer_format="{{Back}}",
            css=".card { font-family: arial; }"
        ))
        
        # Migrate notes to new model
        context.run(OperationRecipe(
            operation_type=OperationType.MIGRATE_NOTES,
            model_name="Basic Card",
            target_model_name="Test Model",
            field_mapping='{"Front": "Front", "Back": "Back"}'
        ))
    
    # Now test concatenation
    config = {
        "source_fields": ["Front", "Back"],
        "target_field": "Combined",
        "separator": " - "
    }
    config_path = create_test_config(tmp_path, config)
    output2 = tmp_path / "populated.apkg"
    
    with AnkiContext(output1, output2, read_only=False) as context:
        recipe = OperationRecipe(
            operation_type=OperationType.POPULATE_FIELDS,
            model_name="Test Model",
            populator_class="populators.concat_fields.ConcatFieldsPopulator",
            populator_config=str(config_path)
        )
        context.run(recipe)
    
    # Verify changes
    with AnkiContext(output2, read_only=True) as context:
        example = context._operations._read_ops.get_note_example("Test Model")
        assert example["Combined"] == f"{example['Front']} - {example['Back']}"

def test_copy_field_populator_missing_source(tmp_path):
    """Test that copy field populator handles missing source field."""
    config = {
        "source_field": "NonExistent",
        "target_field": "Back"
    }
    config_path = create_test_config(tmp_path, config)
    
    # Create output file
    output_path = tmp_path / "output.apkg"
    
    # Run populate fields operation
    with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as context:
        recipe = OperationRecipe(
            operation_type=OperationType.POPULATE_FIELDS,
            model_name="Basic Card",
            populator_class="populators.copy_field.CopyFieldPopulator",
            populator_config=str(config_path)
        )
        # Should log warning and skip notes, but not fail
        context.run(recipe)

def test_concat_fields_populator_missing_source(tmp_path):
    """Test that concat fields populator handles missing source field."""
    config = {
        "source_fields": ["Front", "NonExistent"],
        "target_field": "Back"
    }
    config_path = create_test_config(tmp_path, config)
    
    # Create output file
    output_path = tmp_path / "output.apkg"
    
    # Run populate fields operation
    with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as context:
        recipe = OperationRecipe(
            operation_type=OperationType.POPULATE_FIELDS,
            model_name="Basic Card",
            populator_class="populators.concat_fields.ConcatFieldsPopulator",
            populator_config=str(config_path)
        )
        # Should log warning and skip notes, but not fail
        context.run(recipe)

def test_invalid_populator_class(tmp_path):
    """Test that invalid populator class is handled gracefully."""
    config_path = create_test_config(tmp_path, {})
    output_path = tmp_path / "output.apkg"
    
    with pytest.raises(ValueError, match="Could not load populator class"):
        with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as context:
            recipe = OperationRecipe(
                operation_type=OperationType.POPULATE_FIELDS,
                model_name="Basic Card",
                populator_class="nonexistent.populator.Class",
                populator_config=str(config_path)
            )
            context.run(recipe)

def test_invalid_config_file(tmp_path):
    """Test that invalid config file is handled gracefully."""
    # Create invalid JSON file
    config_path = tmp_path / "invalid.json"
    with open(config_path, "w") as f:
        f.write("invalid json")
    
    output_path = tmp_path / "output.apkg"
    
    with pytest.raises(ValueError, match="Invalid populator configuration"):
        with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as context:
            recipe = OperationRecipe(
                operation_type=OperationType.POPULATE_FIELDS,
                model_name="Basic Card",
                populator_class="populators.copy_field.CopyFieldPopulator",
                populator_config=str(config_path)
            )
            context.run(recipe)

def test_missing_config_fields(tmp_path):
    """Test that missing required config fields are handled gracefully."""
    config = {}  # Missing required fields
    config_path = create_test_config(tmp_path, config)
    output_path = tmp_path / "output.apkg"
    
    with pytest.raises(ValueError, match="Config must specify"):
        with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as context:
            recipe = OperationRecipe(
                operation_type=OperationType.POPULATE_FIELDS,
                model_name="Basic Card",
                populator_class="populators.copy_field.CopyFieldPopulator",
                populator_config=str(config_path)
            )
            context.run(recipe) 