import pytest
import tempfile
from pathlib import Path
from anki_terminal.anki_context import AnkiContext
from anki_terminal.ops.write.rename_field import RenameFieldOperation
from anki_terminal.ops.read.list_operation import ListOperation
from tests.fixtures.test_data_fixtures import apkg_v2_path

def test_write_operation_persists(apkg_v2_path):
    """Test that write operations are correctly persisted to disk.
    
    This test:
    1. Opens the test v2 apkg file
    2. Performs a rename field operation
    3. Saves to a new apkg file
    4. Opens the new file and verifies the changes
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Setup output path
        tmp_dir = Path(tmp_dir)
        output_path = tmp_dir / "modified.apkg"
        
        # First context: Perform the write operation
        with AnkiContext(apkg_v2_path, output_path=output_path, read_only=False) as context:
            # Get original fields for verification
            list_op = ListOperation(path="/models/Basic Card/fields")
            results = context.run(list_op)
            assert results[0].success
            original_fields = {f["name"] for f in results[0].data["fields"]}
            assert "Front" in original_fields
            
            # Perform rename operation
            rename_op = RenameFieldOperation(
                old_field_name="Front",
                new_field_name="Question",
                model_name="Basic Card"
            )
            results = context.run(rename_op)
            assert results[0].success
        
        # Verify the output file exists
        assert output_path.exists(), "Output file was not created"
        
        # Second context: Verify the changes persisted
        with AnkiContext(output_path, read_only=True) as verify_context:
            list_op = ListOperation(path="/models/Basic Card/fields")
            results = verify_context.run(list_op)
            assert results[0].success
            
            # Verify field was renamed
            new_fields = {f["name"] for f in results[0].data["fields"]}
            assert "Front" not in new_fields, "Old field name should not exist"
            assert "Question" in new_fields, "New field name should exist" 