from typing import Dict, List

from anki_terminal.anki_types import Model, Note

from .populator_base import FieldPopulator, PopulatorConfigArgument


class CopyFieldPopulator(FieldPopulator):
    """A field populator that copies values from one field to another."""
    
    name = "copy-field"
    description = "Copy values from one field to another"
    config_args = [
        PopulatorConfigArgument(
            name="source_field",
            description="Field to copy values from",
            required=True
        ),
        PopulatorConfigArgument(
            name="target_field",
            description="Field to copy values to",
            required=True
        )
    ]
    
    @property
    def supports_batching(self) -> bool:
        """Whether this populator supports batch operations."""
        return self.config.get("supports_batch", False)
    
    @property
    def target_fields(self) -> List[str]:
        """Get list of fields that will be modified by this populator."""
        return [self.config["target_field"]]
    
    def _validate_impl(self, model: Model) -> None:
        """Validate that the source field exists in the model.
        
        Args:
            model: The model to validate against
            
        Raises:
            ValueError: If the source field doesn't exist in the model
        """
        field_names = [f.name for f in model.fields]
        if self.config["source_field"] not in field_names:
            raise ValueError(f"Source field '{self.config['source_field']}' not found in model")
    
    def _populate_fields_impl(self, note: Note) -> Dict[str, str]:
        """Copy the source field value to the target field.
        
        Args:
            note: The note to populate fields for
            
        Returns:
            A dictionary mapping the target field to its new value
            
        Raises:
            ValueError: If the source field is not found in the note
        """
        source_field = self.config["source_field"]
        target_field = self.config["target_field"]
        
        if source_field not in note.fields:
            raise ValueError(f"Source field '{source_field}' not found in note")
        
        return {target_field: note.fields[source_field]}
    
    def _populate_batch_impl(self, notes: List[Note]) -> Dict[int, Dict[str, str]]:
        """Copy the source field value to the target field for multiple notes.
        
        Args:
            notes: The notes to populate fields for
            
        Returns:
            A dictionary mapping note IDs to their field updates
        """
        result = {}
        for note in notes:
            try:
                result[note.id] = self._populate_fields_impl(note)
            except ValueError:
                # Skip notes with missing source fields
                pass
        return result 