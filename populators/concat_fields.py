from typing import Dict
import json
from anki_types import Note
from .base import FieldPopulator

class ConcatFieldsPopulator(FieldPopulator):
    """A field populator that concatenates multiple fields."""
    
    def __init__(self, config_path: str):
        """Initialize the populator from a config file.
        
        The config file should be a JSON file with the following structure:
        {
            "source_fields": ["field1", "field2"],
            "target_field": "field3",
            "separator": " "  # optional, defaults to space
        }
        """
        try:
            with open(config_path) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid populator configuration: {str(e)}")
            
        if "source_fields" not in config or "target_field" not in config:
            raise ValueError("Config must specify 'source_fields' and 'target_field'")
            
        self.source_fields = config["source_fields"]
        self.target_field = config["target_field"]
        self.separator = config.get("separator", " ")
    
    def populate_fields(self, note: Note) -> Dict[str, str]:
        # Verify all source fields exist
        missing_fields = [f for f in self.source_fields if f not in note.fields]
        if missing_fields:
            raise ValueError(f"Source fields not found in note: {missing_fields}")
            
        # Get values from source fields
        values = [note.fields[field] for field in self.source_fields]
        
        # Concatenate with separator
        return {self.target_field: self.separator.join(values)} 