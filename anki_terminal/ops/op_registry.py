from typing import Dict, Type

from anki_terminal.ops.op_base import Operation
from anki_terminal.ops.read.birds_eye_view_operation import BirdsEyeViewOperation
from anki_terminal.ops.read.count_operation import CountOperation
from anki_terminal.ops.read.get_operation import GetOperation
from anki_terminal.ops.read.list_operation import ListOperation
from anki_terminal.ops.write.add_field import AddFieldOperation
from anki_terminal.ops.write.add_model import AddModelOperation
from anki_terminal.ops.write.divide_decks import DivideIntoDecksByTagsOperation
from anki_terminal.ops.write.migrate_notes import MigrateNotesOperation
from anki_terminal.ops.write.populate_fields import PopulateFieldsOperation
from anki_terminal.ops.write.remove_empty_notes import RemoveEmptyNotesOperation
from anki_terminal.ops.write.rename_field import RenameFieldOperation
from anki_terminal.ops.write.rename_model import RenameModelOperation
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
        self.register(BirdsEyeViewOperation)
        
        # Write operations
        self.register(RenameFieldOperation)
        self.register(RenameModelOperation)
        self.register(PopulateFieldsOperation)
        self.register(MigrateNotesOperation)
        self.register(AddModelOperation)
        self.register(AddFieldOperation)
        self.register(TagNotesOperation)
        self.register(DivideIntoDecksByTagsOperation)
        self.register(RemoveEmptyNotesOperation)
    
    def register(self, operation_class: Type[Operation]) -> None:
        """Register an operation.
        
        Args:
            operation_class: Operation class to register
            
        Raises:
            ValueError: If operation name is already registered
        """
        if not operation_class.name:
            raise ValueError("Operation must have a name")
            
        if operation_class.name in self._operations:
            raise ValueError(f"Operation '{operation_class.name}' already registered")
            
        self._operations[operation_class.name] = operation_class
    
    def get(self, name: str) -> Type[Operation]:
        """Get an operation by name.
        
        Args:
            name: Name of the operation
            
        Returns:
            Operation class
            
        Raises:
            KeyError: If operation is not registered
        """
        if name not in self._operations:
            raise KeyError(f"Operation '{name}' not registered")
            
        return self._operations[name]
    
    def get_all(self) -> Dict[str, Type[Operation]]:
        """Get all registered operations.
        
        Returns:
            Dictionary of operation names to operation classes
        """
        return self._operations.copy()
    
    def list_operations(self) -> Dict[str, Type[Operation]]:
        """List all registered operations.
        
        Returns:
            Dictionary mapping operation names to their operation classes
        """
        return self._operations
