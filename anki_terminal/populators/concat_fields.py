from typing import Dict, List

from anki_terminal.commons.anki_types import Model, Note

from .populator_base import FieldPopulator, PopulatorConfigArgument


class ConcatFieldsPopulator(FieldPopulator):
    """A field populator that concatenates multiple fields."""
    
    name = "concat-fields"
    description = "Concatenate multiple fields into a target field"
    config_args = [
        PopulatorConfigArgument(
            name="source_fields",
            description="List of fields to concatenate",
            required=True
        ),
        PopulatorConfigArgument(
            name="target_field",
            description="Field to store the concatenated result",
            required=True
        ),
        PopulatorConfigArgument(
            name="separator",
            description="Separator to use between fields",
            required=False,
            default=" "
        )
    ]
    
    @property
    def supports_batching(self) -> bool:
        """Whether this populator supports batch operations."""
        return True
    
    @property
    def target_fields(self) -> List[str]:
        """Get list of fields that will be modified by this populator."""
        return [self.config["target_field"]]
    
    def _validate_impl(self, model: Model) -> None:
        """Validate that the source fields exist in the model.
        
        Args:
            model: The model to validate against
            
        Raises:
            ValueError: If any source field doesn't exist in the model
        """
        field_names = [f.name for f in model.fields]
        missing_fields = [f for f in self.config["source_fields"] if f not in field_names]
        if missing_fields:
            raise ValueError(f"Source fields not found in model: {', '.join(missing_fields)}")
    
    def _populate_fields_impl(self, note: Note) -> Dict[str, str]:
        """Concatenate source fields into the target field.
        
        Args:
            note: The note to populate fields for
            
        Returns:
            A dictionary mapping the target field to its new value
            
        Raises:
            ValueError: If any source field is not found in the note
        """
        source_fields = self.config["source_fields"]
        target_field = self.config["target_field"]
        separator = self.config["separator"]
        
        # Verify all source fields exist
        missing_fields = [f for f in source_fields if f not in note.fields]
        if missing_fields:
            raise ValueError(f"Source fields not found in note: {', '.join(missing_fields)}")
            
        # Get values from source fields
        values = [note.fields[field] for field in source_fields]
        
        # Concatenate with separator
        return {target_field: separator.join(values)}

    def _populate_batch_impl(self, notes: List[Note]) -> Dict[int, Dict[str, str]]:
        """Populate fields for a batch of notes.
        
        Args:
            notes: List of notes to populate fields for
            
        Returns:
            Dictionary mapping note IDs to their field updates
            
        Raises:
            ValueError: If source fields are not found in any note
        """
        updates = {}
        source_fields = self.config["source_fields"]
        target_field = self.config["target_field"]
        separator = self.config["separator"]
        
        # First verify all source fields exist in at least one note
        # This helps catch configuration errors early
        all_fields = set()
        for note in notes:
            all_fields.update(note.fields.keys())
        missing_fields = [f for f in source_fields if f not in all_fields]
        if missing_fields:
            raise ValueError(f"Source fields not found in any note: {', '.join(missing_fields)}")
        
        # Process each note, skipping those with missing fields
        for note in notes:
            # Check if this note has all required fields
            if all(field in note.fields for field in source_fields):
                # Get values and concatenate
                values = [note.fields[field] for field in source_fields]
                updates[note.id] = {target_field: separator.join(values)}
        
        return updates 