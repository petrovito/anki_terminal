from typing import Dict, Type

from anki_terminal.ops.op_base import Operation
from anki_terminal.ops.read.count_operation import CountOperation
from anki_terminal.ops.read.get_operation import GetOperation
from anki_terminal.ops.read.list_operation import ListOperation
from anki_terminal.ops.write.add_field import AddFieldOperation
from anki_terminal.ops.write.add_model import AddModelOperation
from anki_terminal.ops.write.migrate_notes import MigrateNotesOperation
from anki_terminal.ops.write.populate_fields import PopulateFieldsOperation
from anki_terminal.ops.write.rename_field import RenameFieldOperation
from anki_terminal.ops.write.tag_notes import TagNotesOperation


class OperationRegistry:
    """Registry of all available operations."""
    
    def __init__(self):
        self._operations: Dict[str, Type[Operation]] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default operations."""
        # Read operations
        self.register(ListOperation)
        self.register(CountOperation)
        self.register(GetOperation)
        
        # Write operations
        self.register(RenameFieldOperation)
        self.register(PopulateFieldsOperation)
        self.register(MigrateNotesOperation)
        self.register(AddModelOperation)
        self.register(AddFieldOperation)
        self.register(TagNotesOperation)
    
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
                "arguments": op.arguments
            }
            for name, op in self._operations.items()
        } 