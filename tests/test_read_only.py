import pytest
import tempfile
import zipfile
from pathlib import Path
from anki_context import AnkiContext
from operation_models import UserOperationType, UserOperationRecipe
from operations import UserOperationParser
from operation_executor import OperationExecutor

def test_read_only_extracts_only_db():
    """Test that read-only mode only extracts the database file."""
    with AnkiContext("test_data/jap.apkg", read_only=True) as inspector:
        # Get the temp directory from the extractor
        temp_dir = Path(inspector._extractor.temp_dir)
        
        # Check that only collection.anki2 exists
        files = list(temp_dir.glob('*'))
        assert len(files) == 1, f"Expected only one file, found: {files}"
        assert files[0].name == 'collection.anki2'
        
        # Verify that the original apkg has more files
        with zipfile.ZipFile("test_data/jap.apkg", 'r') as zf:
            apkg_files = zf.namelist()
            assert len(apkg_files) > 1, "Test file should contain more than just the database"
            assert 'collection.anki2' in apkg_files
            assert any(f.startswith('media') for f in apkg_files), "Test file should contain media files"

def test_read_only_operations_work():
    """Test that read operations work correctly in read-only mode."""
    with AnkiContext("test_data/jap.apkg", read_only=True) as inspector:
        # Test a few read operations
        recipes = [
            UserOperationRecipe(operation_type=UserOperationType.NUM_CARDS),
            UserOperationRecipe(operation_type=UserOperationType.LIST_MODELS),
            UserOperationRecipe(operation_type=UserOperationType.LIST_FIELDS)
        ]
        
        parser = UserOperationParser()
        executor = OperationExecutor(inspector._read_ops, inspector._write_ops)
        
        for recipe in recipes:
            operation_plan = parser.parse(recipe)
            executor.execute(operation_plan.operations[0])  # Should not raise any errors

def test_write_operation_fails_in_read_only():
    """Test that write operations fail in read-only mode."""
    with AnkiContext("test_data/jap.apkg", read_only=True) as inspector:
        user_recipe = UserOperationRecipe(
            operation_type=UserOperationType.RENAME_FIELD,
            old_field_name="Front",
            new_field_name="Question"
        )
        
        parser = UserOperationParser()
        operation_plan = parser.parse(user_recipe)
        executor = OperationExecutor(inspector._read_ops, inspector._write_ops)
        
        with pytest.raises(RuntimeError, match="Cannot perform write operation in read-only mode"):
            executor.execute(operation_plan.operations[0])

def test_write_mode_without_output_path_fails():
    """Test that write mode without output path fails."""
    with pytest.raises(ValueError, match="Output path must be specified for write operations"):
        with AnkiContext("test_data/jap.apkg", read_only=False) as inspector:
            pass  # Should fail before reaching here 