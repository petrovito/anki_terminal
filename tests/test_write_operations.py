import pytest
import tempfile
import logging
from pathlib import Path
from anki_context import AnkiContext
from operations import OperationType, OperationRecipe

logger = logging.getLogger('anki_inspector')

def test_rename_field_persists():
    """Test that field renaming persists when saving and reopening the apkg file."""
    # Create a temporary directory for the output file
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_path = Path(tmp_dir)
        output_path = tmp_dir_path / "output.apkg"
        
        # First context: Rename the field and save
        with AnkiContext("test_data/jap.apkg", output_path) as inspector:
            recipe = OperationRecipe(
                OperationType.RENAME_FIELD,
                old_field_name="Front",
                new_field_name="Question"
            )
            inspector._operations.run(recipe)
        
        # Second context: Verify changes persisted
        with AnkiContext(output_path) as inspector:
            # Check model fields
            fields = inspector._operations.read_ops.list_fields()
            field_names = {field["name"] for field in fields}
            logger.debug(f"Field names in saved file: {field_names}")
            assert "Question" in field_names, f"Field 'Question' not found in {field_names}"
            assert "Front" not in field_names, f"Field 'Front' still exists in {field_names}"
            
            # Check note content
            example = inspector._operations.read_ops.get_note_example()
            logger.debug(f"Example note in saved file: {example}")
            assert "Question" in example
            assert "Front" not in example
            
            # Template content should still use the old field name
            question_format = inspector._operations.read_ops.get_question_format()
            logger.debug(f"Question format in saved file: {question_format}")
            assert "{{Front}}" in question_format
            assert "{{Question}}" not in question_format 