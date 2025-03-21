import re
from typing import Any, Dict, List

from anki_terminal.commons.anki_types import Note
from anki_terminal.populators.populator_base import FieldPopulator, PopulatorConfigArgument


class RemoveBracketsPopulator(FieldPopulator):
    """A field populator that removes text in round brackets (parentheses) from fields."""
    
    name = "remove-brackets"
    description = "Remove text in round brackets (parentheses) from fields"
    config_args = [
        PopulatorConfigArgument(
            name="source_field",
            description="Field containing text to process",
            required=True
        ),
        PopulatorConfigArgument(
            name="target_field",
            description="Field to store the processed text (if not specified, updates source field)",
            required=False,
            default=None
        )
    ]
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the populator with a configuration."""
        super().__init__(config)
        
        # Set target field to source field if not specified
        if not self.config.get("target_field"):
            self.config["target_field"] = self.config["source_field"]
    
    @property
    def target_fields(self) -> List[str]:
        """Get list of fields that will be modified by this populator.
        
        Returns:
            List of field names that will be modified
        """
        return [self.config["target_field"]]
    
    def _populate_fields_impl(self, note: Note) -> Dict[str, str]:
        """Implementation-specific field population logic.
        
        Args:
            note: The note to populate fields for
            
        Returns:
            A dictionary mapping field names to their new values.
            
        Raises:
            ValueError: If the note cannot be processed
        """
        source_field = self.config["source_field"]
        target_field = self.config["target_field"]
        
        # Check if source field exists in note
        if source_field not in note.fields:
            return {}  # Skip notes without the source field
        
        original_text = note.fields[source_field]
        
        # Skip empty fields
        if not original_text:
            return {}
        
        # Remove text in round brackets using regex
        # This handles both full-width (Japanese) and half-width (English) parentheses
        # The pattern matches the innermost brackets first, then works outward
        processed_text = original_text
        while True:
            # Find the innermost brackets
            match = re.search(r'[（(][^（）()]*[）)]', processed_text)
            if not match:
                break
            # Remove the matched brackets and their content
            processed_text = processed_text[:match.start()] + processed_text[match.end():]
        
        # Skip if no changes were made
        if processed_text == original_text:
            return {}
        
        # Return the updated field
        return {target_field: processed_text} 