from typing import Dict, Type

from anki_terminal.populators.base import FieldPopulator
from anki_terminal.populators.copy_field import CopyFieldPopulator
from anki_terminal.populators.concat_fields import ConcatFieldsPopulator
from anki_terminal.populators.jap_llm import JapLlmPopulator

class PopulatorRegistry:
    """Registry of all available field populators."""
    
    def __init__(self):
        self._populators: Dict[str, Type[FieldPopulator]] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default field populators."""
        self.register(CopyFieldPopulator)
        self.register(ConcatFieldsPopulator)
        self.register(JapLlmPopulator)
    
    def register(self, populator_class: Type[FieldPopulator]):
        """Register a new field populator.
        
        Args:
            populator_class: The field populator class to register
            
        Raises:
            ValueError: If populator name is already registered
        """
        if populator_class.name in self._populators:
            raise ValueError(f"Field populator already registered: {populator_class.name}")
        
        self._populators[populator_class.name] = populator_class
    
    def get(self, name: str) -> Type[FieldPopulator]:
        """Get a field populator class by name.
        
        Args:
            name: Name of the field populator
            
        Returns:
            The field populator class
            
        Raises:
            KeyError: If field populator not found
        """
        if name not in self._populators:
            raise KeyError(f"Field populator not found: {name}")
        
        return self._populators[name]
    
    def list_populators(self) -> Dict[str, Dict[str, any]]:
        """List all registered field populators.
        
        Returns:
            Dictionary mapping populator names to their metadata
        """
        return {
            name: {
                "description": populator.description,
                "config_args": [arg.to_dict() for arg in populator.config_args]
            }
            for name, populator in self._populators.items()
        } 