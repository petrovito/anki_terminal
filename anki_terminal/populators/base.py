from abc import ABC, abstractmethod
from typing import Dict, List
from anki_terminal.anki_types import Note

class FieldPopulator(ABC):
    """Abstract base class for field population strategies.
    
    This class defines the interface for field population strategies.
    Subclasses must implement the populate_fields method to define
    how fields should be populated based on the current note content.
    """
    
    @property
    def supports_batching(self) -> bool:
        """Whether this populator supports batch operations."""
        return False
    
    @property
    @abstractmethod
    def target_fields(self) -> List[str]:
        """Get list of fields that will be modified by this populator."""
        pass
    
    @abstractmethod
    def populate_fields(self, note: Note) -> Dict[str, str]:
        """Determine how to populate fields for a given note.
        
        Args:
            note: The note to populate fields for
            
        Returns:
            A dictionary mapping field names to their new values.
            Only fields that should be modified need to be included.
        """
        pass

    def populate_batch(self, notes: List[Note]) -> Dict[int, Dict[str, str]]:
        """Populate fields for a batch of notes.
        
        Args:
            notes: List of notes to populate fields for
            
        Returns:
            Dictionary mapping note IDs to their field updates
            
        Raises:
            NotImplementedError: If this populator doesn't support batching
        """
        if not self.supports_batching:
            raise NotImplementedError("This populator does not support batch operations")
        raise NotImplementedError("Subclass must implement populate_batch if supports_batching is True") 