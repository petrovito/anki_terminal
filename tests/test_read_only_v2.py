import pytest
import tempfile
import zipfile
from pathlib import Path
from anki_terminal.anki_context import AnkiContext
from anki_terminal.ops.read.list_operation import ListOperation
from anki_terminal.ops.write.rename_field import RenameFieldOperation
from tests.fixtures.test_data_fixtures import apkg_v2_path

def test_read_only_extracts_only_db(apkg_v2_path):
    """Test that read-only mode only extracts the database file."""
    with AnkiContext(apkg_v2_path, read_only=True) as context:
        # Get the temp directory from the extractor
        temp_dir = Path(context._extractor.temp_dir)
        
        # Check that only collection.anki2 exists
        files = list(temp_dir.glob('*'))
        assert len(files) == 1, f"Expected only one file, found: {files}"
        assert files[0].name == 'collection.anki2'
        
        # Verify that the original apkg has more files
        with zipfile.ZipFile(apkg_v2_path, 'r') as zf:
            apkg_files = zf.namelist()
            assert len(apkg_files) > 1, "Test file should contain more than just the database"
            assert 'collection.anki2' in apkg_files
            assert any(f.startswith('media') for f in apkg_files), "Test file should contain media files"

def test_read_only_operations_work(apkg_v2_path):
    """Test that read operations work correctly in read-only mode."""
    with AnkiContext(apkg_v2_path, read_only=True) as context:
        # Test list fields operation
        op = ListOperation(path="/models/Basic Card/fields")
        results = context.run(op)
        assert results[0].success

def test_write_operation_fails_in_read_only(apkg_v2_path):
    """Test that write operations fail in read-only mode."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "output.apkg"
        with AnkiContext(apkg_v2_path, read_only=True) as context:
            op = RenameFieldOperation(
                old_field_name="Front",
                new_field_name="Question"
            )
            
            with pytest.raises(RuntimeError, match="Cannot perform write operation in read-only mode"):
                context.run(op)

