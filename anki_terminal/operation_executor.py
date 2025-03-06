import logging
from typing import List, Optional

from anki_terminal.anki_types import Collection
from anki_terminal.changelog import ChangeLog
from anki_terminal.ops.op_base import Operation, OperationResult

logger = logging.getLogger('anki_inspector')

class OperationExecutor:
    """Execute operations using the new operation framework."""
    
    def __init__(self, collection: Collection, changelog: Optional[ChangeLog] = None):
        """Initialize the operation executor.
        
        Args:
            collection: The Anki collection to operate on
            changelog: Optional changelog for write operations
        """
        self.collection = collection
        self.changelog = changelog
    
    def validate(self, operation: Operation) -> List[str]:
        """Validate all operations in the plan.
        
        Args:
            operation: The operation to validate
            
        Returns:
            List of validation error messages, empty if all valid
            
        Raises:
            RuntimeError: If changelog is required but not provided
        """
        if not operation.readonly and not self.changelog:
            raise RuntimeError("Cannot execute write operations without changelog")
        
        errors = []
        try:
            operation.validate(self.collection)
        except Exception as e:
            errors.append(f"Validation failed for {operation.name}: {str(e)}")
        
        return errors
    
    def execute(self, operation: Operation) -> List[OperationResult]:
        """Execute all operations in the plan.
        
        Args:
            operation: The operation to execute
            
        Returns:
            List of operation results
            
        Raises:
            RuntimeError: If validation fails or changelog is required but not provided
        """
        # Validate first
        errors = self.validate(operation)
        if errors:
            raise RuntimeError(f"Validation failed:\n" + "\n".join(errors))
        
        # Execute operation
        results = []
        try:
            result = operation.execute()
            
            # Log result
            if result.success:
                logger.info(result.message)
                # Record changes in changelog
                if result.changes:
                    self.changelog.changes.extend(result.changes)
            else:
                logger.error(result.message)
            
            results.append(result)
            
        except Exception as e:
            logger.error(f"Operation failed: {str(e)}")
            results.append(OperationResult(
                success=False,
                message=f"Operation failed: {str(e)}"
            ))
    
        return results