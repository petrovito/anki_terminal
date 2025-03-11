from typing import Dict, List

from pykakasi import kakasi

from anki_terminal.anki_types import Model, Note

from .populator_base import FieldPopulator, PopulatorConfigArgument


class FuriganaPopulator(FieldPopulator):
    """A field populator that adds furigana readings to Japanese text."""
    
    name = "furigana"
    description = "Add furigana readings to Japanese text"
    config_args = [
        PopulatorConfigArgument(
            name="source_field",
            description="Field containing Japanese text",
            required=True
        ),
        PopulatorConfigArgument(
            name="target_field",
            description="Field to store text with furigana readings",
            required=True
        )
    ]
    
    def __init__(self, config):
        """Initialize the furigana populator.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.kakasi = kakasi()
    
    @property
    def supports_batching(self) -> bool:
        """Whether this populator supports batch operations."""
        return True
    
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
    
    def _add_furigana(self, text: str) -> str:
        """Add furigana readings to Japanese text.
        
        Args:
            text: The Japanese text to add furigana to
            
        Returns:
            Text with furigana readings added in brackets after kanji
        """
        if not text:
            return ""
        
        result = self.kakasi.convert(text)
        
        # Process each token to add furigana only for kanji
        processed_text = ""
        for item in result:
            orig = item['orig']
            hira = item['hira']
            
            # Check if the original text contains kanji
            # If it does and the reading is different, add furigana
            if orig != hira and any(ord(c) >= 0x4E00 and ord(c) <= 0x9FFF for c in orig):
                processed_text += f"{orig}[{hira}]"
            else:
                processed_text += orig
        
        return processed_text
    
    def _populate_fields_impl(self, note: Note) -> Dict[str, str]:
        """Add furigana readings to the Japanese text in the source field.
        
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
        
        source_text = note.fields[source_field]
        furigana_text = self._add_furigana(source_text)
        
        return {target_field: furigana_text}
    
    def _populate_batch_impl(self, notes: List[Note]) -> Dict[int, Dict[str, str]]:
        """Add furigana readings to Japanese text for multiple notes.
        
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