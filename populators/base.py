from abc import ABC, abstractmethod
from typing import Dict, List
from anki_types import Note

class FieldPopulator(ABC):
    """Abstract base class for field population strategies.
    
    This class defines the interface for field population strategies.
    Subclasses must implement the populate_fields method to define
    how fields should be populated based on the current note content.
    """
    
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