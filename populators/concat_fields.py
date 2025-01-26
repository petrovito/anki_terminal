from typing import Dict, List
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
    
    @property
    def supports_batching(self) -> bool:
        """Whether this populator supports batch operations."""
        return True
    
    @property
    def target_fields(self) -> List[str]:
        """Get list of fields that will be modified by this populator."""
        return [self.target_field]
    
    def populate_fields(self, note: Note) -> Dict[str, str]:
        """Populate fields for a single note."""
        # Verify all source fields exist
        missing_fields = [f for f in self.source_fields if f not in note.fields]
        if missing_fields:
            raise ValueError(f"Source fields not found in note: {missing_fields}")
            
        # Get values from source fields
        values = [note.fields[field] for field in self.source_fields]
        
        # Concatenate with separator
        return {self.target_field: self.separator.join(values)}

    def populate_batch(self, notes: List[Note]) -> Dict[int, Dict[str, str]]:
        """Populate fields for a batch of notes.
        
        This is more efficient than processing one note at a time because we:
        1. Check field existence once for all notes
        2. Process valid notes in bulk
        3. Skip invalid notes without stopping the batch
        """
        updates = {}
        
        # First verify all source fields exist in at least one note
        # This helps catch configuration errors early
        all_fields = set()
        for note in notes:
            all_fields.update(note.fields.keys())
        missing_fields = [f for f in self.source_fields if f not in all_fields]
        if missing_fields:
            raise ValueError(f"Source fields not found in any note: {missing_fields}")
        
        # Process each note, skipping those with missing fields
        for note in notes:
            # Check if this note has all required fields
            if all(field in note.fields for field in self.source_fields):
                # Get values and concatenate
                values = [note.fields[field] for field in self.source_fields]
                updates[note.id] = {self.target_field: self.separator.join(values)}
        
        return updates 