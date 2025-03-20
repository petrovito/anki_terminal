import logging
from typing import List, Optional

from anki_terminal.commons.anki_types import Collection
from anki_terminal.commons.changelog import ChangeLog
from anki_terminal.metaops.metaop import MetaOp
from anki_terminal.ops.op_base import Operation, OperationResult
from anki_terminal.ops.operation_factory import OperationFactory

logger = logging.getLogger('anki_inspector')

class MetaOpExecutor:
    """Execute operations using the new operation framework."""
    
    def __init__(self, collection: Collection, changelog: Optional[ChangeLog] = None):
        """Initialize the operation executor.
        
        Args:
            collection: The Anki collection to operate on
            changelog: Optional changelog for write operations
        """
        self.collection = collection
        self.changelog = changelog
    

    def execute(self, metaop: MetaOp) -> List[OperationResult]:
        ops = self.resolve_ops(metaop)
        results = []
        for op in ops:
            results.append(self.execute_op(op))
        return results

    def resolve_ops(self, metaop: MetaOp) -> List[Operation]:
        ops = []
        op_factory = OperationFactory()
        self._resolve_ops_recursive(metaop, ops, op_factory, 0, 10, 100)
        return ops

    def _resolve_ops_recursive(self, metaop: MetaOp, ops: List[Operation],
                               op_factory: OperationFactory,
                               depth: int, max_depth: int, max_ops: int) -> None:
        """Resolve operations recursively."""
        if depth > max_depth:
            raise RuntimeError(f"Max depth of {max_depth} reached for meta operation {metaop.name}")
        if len(ops) >= max_ops:
            raise RuntimeError(f"Max number of operations of {max_ops} reached for meta operation {metaop.name}")
        
        if metaop.is_fundamental():
            ops.append(metaop.resolve_op(op_factory))
        else:
            for target_metaop in metaop.resolve():
                self._resolve_ops_recursive(target_metaop, ops, op_factory, depth + 1, max_depth, max_ops)
        
    
    def execute_op(self, op: Operation) -> OperationResult:
        """Execute an operation.
        
        Args:
            operation: The operation to execute
            
        Returns:
            List of operation results
            
        Raises:
            RuntimeError: If validation fails or changelog is required but not provided
        """
        # Validate first
        errors = op.validate(self.collection)
        if errors:
            raise RuntimeError(f"Validation failed:\n" + "\n".join(errors))
        
        # Execute operation
        result = None
        try:
            result = op.execute()
            
            # Log result
            if result.success:
                logger.info(result.message)
                # Record changes in changelog
                if result.changes:
                    self.changelog.changes.extend(result.changes)
            else:
                logger.error(result.message)
            
        except Exception as e:
            logger.error(f"Operation failed: {str(e)}")
            result = OperationResult(
                success=False,
                message=f"Operation failed: {str(e)}"
            )
    
        return result