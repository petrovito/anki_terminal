import pytest
import tempfile
import logging
from pathlib import Path
from anki_context import AnkiContext
from operation_models import UserOperationType, UserOperationRecipe, OperationType, OperationRecipe, OperationPlan
from user_operation_parser import UserOperationParser
from operation_executor import OperationExecutor

logger = logging.getLogger('anki_inspector')

def test_rename_field_persists():
    """Test that field renaming persists when saving and reopening the apkg file."""
    # Create a temporary directory for the output file
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_path = Path(tmp_dir)
        output_path = tmp_dir_path / "output.apkg"
        
        # First context: Rename the field and save
        with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as inspector:
            user_recipe = UserOperationRecipe(
                operation_type=UserOperationType.RENAME_FIELD,
                old_field_name="Front",
                new_field_name="Question"
            )
            parser = UserOperationParser()
            operation_plan = parser.parse(user_recipe, output_path)
            executor = OperationExecutor(inspector._read_ops, inspector._write_ops)
            executor.execute(operation_plan.operations[0])
        
        # Second context: Verify changes persisted
        with AnkiContext(output_path, read_only=True) as inspector:
            # Check model fields
            fields = inspector._read_ops.list_fields()
            field_names = {field["name"] for field in fields}
            logger.debug(f"Field names in saved file: {field_names}")
            assert "Question" in field_names, f"Field 'Question' not found in {field_names}"
            assert "Front" not in field_names, f"Field 'Front' still exists in {field_names}"
            
            # Check note content
            example = inspector._read_ops.get_note_example()
            logger.debug(f"Example note in saved file: {example}")
            assert "Question" in example
            assert "Front" not in example
            
            # Template content should still use the old field name
            question_format = inspector._read_ops.get_question_format()
            logger.debug(f"Question format in saved file: {question_format}")
            assert "{{Front}}" in question_format
            assert "{{Question}}" not in question_format 

def create_test_model(context: AnkiContext, output_path: Path, model_name: str = "Test Model") -> None:
    """Create a test model with predefined fields and template.

    Args:
        context: The AnkiContext to use
        output_path: Path where the output file will be written
        model_name: Optional name for the model (default: "Test Model")
    """
    user_recipe = UserOperationRecipe(
        operation_type=UserOperationType.ADD_MODEL,
        model_name=model_name,
        fields=["Question", "Answer", "Extra"],
        template_name="Forward Card",
        question_format="{{Question}}\n\n{{Extra}}",
        answer_format="{{FrontSide}}\n\n<hr id='answer'>\n\n{{Answer}}",
        css=".card { font-family: times; font-size: 18px; text-align: left; color: navy; }"
    )
    parser = UserOperationParser()
    operation_plan = parser.parse(user_recipe, output_path)
    executor = OperationExecutor(context._read_ops, context._write_ops)
    executor.execute(operation_plan.operations[0])

def test_add_model_creates_new_model(tmp_path):
    """Test that add_model creates a new model with all required fields."""
    # Create output file
    output_path = tmp_path / "output.apkg"
    
    # Add new model with all required fields
    with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as context:
        create_test_model(context, output_path)
    
    # Verify model was added by opening the file again
    with AnkiContext(output_path, read_only=True) as context:
        # Check model exists with correct type
        models = context._read_ops.list_models()
        assert len(models) == 2  # Original model + new model
        new_model = next(m for m in models if m["name"] == "Test Model")
        assert new_model["type"] == "Standard"
        
        # Check fields - should match exactly what we provided
        fields = context._read_ops.list_fields(model_name="Test Model")
        field_names = [f["name"] for f in fields]
        assert field_names == ["Question", "Answer", "Extra"]
        
        # Check templates - should match our provided name
        templates = context._read_ops.list_templates(model_name="Test Model")
        assert len(templates) == 1
        template = templates[0]
        assert template["name"] == "Forward Card"
        assert template["ordinal"] == 0
        
        # Check template formats - should match exactly what we provided
        question_format = context._read_ops.get_question_format(
            model_name="Test Model",
            template_name="Forward Card"
        )
        assert question_format == "{{Question}}\n\n{{Extra}}"
        
        answer_format = context._read_ops.get_answer_format(
            model_name="Test Model",
            template_name="Forward Card"
        )
        assert answer_format == "{{FrontSide}}\n\n<hr id='answer'>\n\n{{Answer}}"
        
        # Check CSS - should match exactly what we provided
        css = context._read_ops.get_css(model_name="Test Model")
        assert css == ".card { font-family: times; font-size: 18px; text-align: left; color: navy; }"

def test_migrate_notes_moves_notes_correctly(tmp_path):
    """Test that migrate_notes correctly moves notes between models."""
    # Create output files with different names
    model_output = tmp_path / "model_added.apkg"
    final_output = tmp_path / "notes_migrated.apkg"
    
    # First add a new model
    with AnkiContext("test_data/jap.apkg", model_output, read_only=False) as context:
        create_test_model(context, model_output, "Target Model")
    
    # Then migrate notes
    with AnkiContext(model_output, final_output, read_only=False) as context:
        # Get initial note counts
        initial_counts = context._read_ops.num_notes()
        assert initial_counts["Basic Card"] > 0
        assert initial_counts["Target Model"] == 0
        
        # Migrate notes
        context.run(OperationPlan(operations=[OperationRecipe(
            operation_type=OperationType.MIGRATE_NOTES,
            model_name="Basic Card",
            target_model_name="Target Model",
            field_mapping='{"Front": "Question", "Back": "Answer"}'
        )]))
        
        # Verify notes were migrated
        final_counts = context._read_ops.num_notes()
        assert final_counts["Basic Card"] == 0
        assert final_counts["Target Model"] == initial_counts["Basic Card"]
        
        # Check field values were preserved
        example = context._read_ops.get_note_example("Target Model")
        assert "Question" in example
        assert "Answer" in example
        assert example["Question"] != ""  # Should have content
        assert example["Answer"] != ""   # Should have content 