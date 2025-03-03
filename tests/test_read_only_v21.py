import pytest
import tempfile
import zipfile
from pathlib import Path
from anki_context import AnkiContext
from ops.read.list_operation import ListOperation
from ops.write.rename_field import RenameFieldOperation
from tests.fixtures.test_data_fixtures import apkg_v21_path

def test_read_only_extracts_only_db(apkg_v21_path):
    """Test that read-only mode only extracts the database file."""
    with AnkiContext(apkg_v21_path, read_only=True) as context:
        # Get the temp directory from the extractor
        temp_dir = Path(context._extractor.temp_dir)
        
        # Check that only collection.anki21 exists (v21 uses this file)
        files = list(temp_dir.glob('*'))
        assert len(files) == 1, f"Expected only one file, found: {files}"
        assert files[0].name == 'collection.anki21'
        
        # Verify that the original apkg has more files
        with zipfile.ZipFile(apkg_v21_path, 'r') as zf:
            apkg_files = zf.namelist()
            assert len(apkg_files) > 1, "Test file should contain more than just the database"
            assert 'collection.anki21' in apkg_files
            assert 'collection.anki2' in apkg_files  # Should have empty v2 file
            assert 'media' in apkg_files  # Should have media file

def test_read_only_operations_work(apkg_v21_path):
    """Test that read operations work correctly in read-only mode."""
    with AnkiContext(apkg_v21_path, read_only=True) as context:
        # Test list fields operation
        op = ListOperation(path="/models/subs2srs/fields")
        results = context.run(op)
        assert results[0].success

def test_write_operation_fails_in_read_only(apkg_v21_path):
    """Test that write operations fail in read-only mode."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "output.apkg"
        with AnkiContext(apkg_v21_path, read_only=True) as context:
            op = RenameFieldOperation(
                old_field_name="Front",
                new_field_name="Question"
            )
            
            with pytest.raises(RuntimeError, match="Cannot perform write operation in read-only mode"):
                context.run(op)

def test_write_mode_without_output_path_fails(apkg_v21_path):
    """Test that write mode without output path fails."""
    with pytest.raises(ValueError, match="Output path must be specified for write operations"):
        with AnkiContext(apkg_v21_path, read_only=False) as context:
            pass  # Should fail before reaching here
