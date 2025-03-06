import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Type, Union

import pytest

from anki_terminal.anki_context import AnkiContext
from anki_terminal.anki_types import Collection
from anki_terminal.ops.op_base import Operation, OperationResult


class BaseWriteTest:
    """Base class for testing write operations.
    
    This class provides a framework for testing write operations by:
    1. Opening an Anki package
    2. Executing a write operation
    3. Saving to a temporary file
    4. Opening the temporary file to verify the changes
    
    Subclasses should implement:
    - get_operation(): Returns the operation to test
    - verify_changes(): Verifies the changes were applied correctly
    """
    
    # Default to testing only v21 if not specified
    versions_to_test = ["v21"]
    
    def get_collection(self, context: AnkiContext) -> Collection:
        """Get the collection from the context.
        
        This is a helper method to access the private _collection member directly.
        
        Args:
            context: AnkiContext to get the collection from
            
        Returns:
            Collection: The collection from the context
        """
        return context._collection
    
    def get_operation(self) -> Operation:
        """Return the operation to test.
        
        This method must be implemented by subclasses.
        
        Returns:
            Operation: The operation to test
        """
        raise NotImplementedError("Subclasses must implement get_operation()")
    
    def verify_changes(self, context: AnkiContext) -> None:
        """Verify that changes were applied correctly.
        
        This method must be implemented by subclasses.
        
        Args:
            context: AnkiContext opened with the modified package
        """
        raise NotImplementedError("Subclasses must implement verify_changes()")
    
    def setup_before_operation(self, context: AnkiContext) -> None:
        """Optional setup before running the operation.
        
        Subclasses can override this method to perform setup before the operation.
        
        Args:
            context: AnkiContext opened with the original package
        """
        pass
    
    def run_operation(self, context: AnkiContext) -> List[OperationResult]:
        """Run the operation and return the results.
        
        Args:
            context: AnkiContext to run the operation in
            
        Returns:
            List[OperationResult]: Results of the operation
        """
        operation = self.get_operation()
        results = context.run(operation)
        return results
    
    @pytest.mark.parametrize("version", versions_to_test)
    def test_write_operation(self, request, version, tmp_path):
        """Test that a write operation is correctly persisted to disk.
        
        This test:
        1. Opens the test apkg file
        2. Performs the write operation
        3. Saves to a new apkg file
        4. Opens the new file and verifies the changes
        
        Args:
            request: pytest request object
            version: Version of Anki to test (v2 or v21)
            tmp_path: Temporary directory for the test
        """
        # Get the appropriate fixture based on the version
        fixture_name = f"apkg_{version}_path"
        apkg_path = request.getfixturevalue(fixture_name)
        
        # Setup output path
        output_path = tmp_path / f"modified_{version}.apkg"
        
        # First context: Perform the write operation
        with AnkiContext(apkg_path, output_path=output_path, read_only=False) as context:
            # Optional setup before operation
            self.setup_before_operation(context)
            
            # Run the operation
            results = self.run_operation(context)
            
            # Assert operation was successful
            assert results[0].success, f"Operation failed: {results[0].error}"
        
        # Verify the output file exists
        assert output_path.exists(), "Output file was not created"
        
        # Second context: Verify the changes persisted
        with AnkiContext(output_path, read_only=True) as verify_context:
            self.verify_changes(verify_context) 