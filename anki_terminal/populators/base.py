from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, TypedDict, ClassVar
from anki_terminal.anki_types import Note, Model

class PopulatorConfigArgument:
    """Definition of a configuration argument for a field populator."""
    
    def __init__(
        self,
        name: str,
        description: str,
        required: bool = True,
        default: Any = None
    ):
        """Initialize a populator config argument.
        
        Args:
            name: Name of the argument
            description: Description of the argument
            required: Whether the argument is required
            default: Default value for the argument if not provided
        """
        self.name = name
        self.description = description
        self.required = required
        self.default = default

class FieldPopulator(ABC):
    """Abstract base class for field population strategies.
    
    This class defines the interface for field population strategies.
    Subclasses must implement the _populate_fields_impl method to define
    how fields should be populated based on the current note content.
    """
    
    # Class variables to be defined by subclasses
    name: ClassVar[str] = ""
    description: ClassVar[str] = ""
    config_args: ClassVar[List[PopulatorConfigArgument]] = []
    
    def __init__(self, config):
        """Initialize the populator with a configuration.
        
        Args:
            config: Dictionary containing configuration values or a JSON string or a file path
            
        Raises:
            ValueError: If required configuration values are missing
        """
        # Handle different types of config input
        if isinstance(config, str):
            # Check if it's a file path
            if config.endswith('.json'):
                import os
                if os.path.exists(config):
                    import json
                    with open(config, 'r') as f:
                        self.config = json.load(f)
                else:
                    # Assume it's a JSON string
                    import json
                    self.config = json.loads(config)
            else:
                # Assume it's a JSON string
                import json
                self.config = json.loads(config)
        else:
            # Assume it's a dictionary
            self.config = config
        
        # Apply defaults for missing optional arguments
        for arg in self.config_args:
            if arg.name not in self.config and not arg.required:
                self.config[arg.name] = arg.default
    
    @property
    def supports_batching(self) -> bool:
        """Whether this populator supports batch operations."""
        return False
    
    @property
    @abstractmethod
    def target_fields(self) -> List[str]:
        """Get list of fields that will be modified by this populator."""
        pass
    
    def validate(self, model: Model) -> None:
        """Validate that the populator can be used with the given model.
        
        Args:
            model: The model to validate against
            
        Raises:
            ValueError: If the populator cannot be used with the model
        """
        # Check required config arguments
        missing_args = [arg.name for arg in self.config_args 
                       if arg.required and arg.name not in self.config]
        if missing_args:
            raise ValueError(f"Missing required configuration arguments: {', '.join(missing_args)}")
        
        # Check that target fields exist in the model
        field_names = [f.name for f in model.fields]
        invalid_fields = [f for f in self.target_fields if f not in field_names]
        if invalid_fields:
            raise ValueError(f"Target fields not found in model: {', '.join(invalid_fields)}")
        
        # Call implementation-specific validation
        self._validate_impl(model)
    
    def _validate_impl(self, model: Model) -> None:
        """Implementation-specific validation.
        
        Args:
            model: The model to validate against
            
        Raises:
            ValueError: If the populator cannot be used with the model
        """
        # Default implementation does nothing
        pass
    
    def populate_fields(self, note: Note) -> Dict[str, str]:
        """Determine how to populate fields for a given note.
        
        Args:
            note: The note to populate fields for
            
        Returns:
            A dictionary mapping field names to their new values.
            Only fields that should be modified need to be included.
            
        Raises:
            ValueError: If the note cannot be processed
        """
        return self._populate_fields_impl(note)
    
    @abstractmethod
    def _populate_fields_impl(self, note: Note) -> Dict[str, str]:
        """Implementation-specific field population logic.
        
        Args:
            note: The note to populate fields for
            
        Returns:
            A dictionary mapping field names to their new values.
            
        Raises:
            ValueError: If the note cannot be processed
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
        return self._populate_batch_impl(notes)
    
    def _populate_batch_impl(self, notes: List[Note]) -> Dict[int, Dict[str, str]]:
        """Implementation-specific batch population logic.
        
        Args:
            notes: List of notes to populate fields for
            
        Returns:
            Dictionary mapping note IDs to their field updates
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclass must implement _populate_batch_impl if supports_batching is True")

    @classmethod
    def from_json_config(cls, config_dict: Dict[str, Any]) -> 'FieldPopulator':
        """Create a populator instance from a JSON configuration dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            Initialized populator instance
            
        Raises:
            ValueError: If required configuration values are missing
        """
        return cls(config_dict) 