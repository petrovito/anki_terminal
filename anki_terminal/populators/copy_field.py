from typing import Dict, List
import json
from anki_terminal.anki_types import Note
from .base import FieldPopulator

class CopyFieldPopulator(FieldPopulator):
    """A field populator that copies values from one field to another."""
    
    def __init__(self, config_path: str):
        """Initialize the populator from a config file.
        
        The config file should be a JSON file with the following structure:
        {
            "source_field": "field1",
            "target_field": "field2"
        }
        """
        try:
            with open(config_path) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid populator configuration: {str(e)}")
            
        if "source_field" not in config or "target_field" not in config:
            raise ValueError("Config must specify 'source_field' and 'target_field'")
            
        self.source_field = config["source_field"]
        self.target_field = config["target_field"]
    
    @property
    def target_fields(self) -> List[str]:
        """Get list of fields that will be modified by this populator."""
        return [self.target_field]
    
    def populate_fields(self, note: Note) -> Dict[str, str]:
        if self.source_field not in note.fields:
            raise ValueError(f"Source field '{self.source_field}' not found in note")
        return {self.target_field: note.fields[self.source_field]} 