from typing import Dict, Type

from ops.base import Operation
from ops.read.list_fields import ListFieldsOperation
from ops.write.rename_field import RenameFieldOperation

class OperationRegistry:
    """Registry of all available operations."""
    
    def __init__(self):
        self._operations: Dict[str, Type[Operation]] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default operations."""
        # Read operations
        self.register(ListFieldsOperation)
        
        # Write operations
        self.register(RenameFieldOperation)
    
    def register(self, operation_class: Type[Operation]):
        """Register a new operation.
        
        Args:
            operation_class: The operation class to register
            
        Raises:
            ValueError: If operation name is already registered
        """
        if operation_class.name in self._operations:
            raise ValueError(f"Operation already registered: {operation_class.name}")
        
        self._operations[operation_class.name] = operation_class
    
    def get(self, name: str) -> Type[Operation]:
        """Get an operation class by name.
        
        Args:
            name: Name of the operation
            
        Returns:
            The operation class
            
        Raises:
            KeyError: If operation not found
        """
        if name not in self._operations:
            raise KeyError(f"Operation not found: {name}")
        
        return self._operations[name]
    
    def list_operations(self) -> Dict[str, Dict[str, any]]:
        """List all registered operations.
        
        Returns:
            Dictionary mapping operation names to their metadata
        """
        return {
            name: {
                "description": op.description,
                "readonly": op.readonly,
                "required_args": list(op.required_args),
                "optional_args": op.optional_args
            }
            for name, op in self._operations.items()
        } 