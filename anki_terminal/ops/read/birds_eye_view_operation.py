from typing import Dict, List, Optional

from anki_terminal.commons.anki_types import Collection, Model, Note
from anki_terminal.ops.op_base import Operation, OperationArgument, OperationResult
from anki_terminal.ops.read.base_read import ReadOperation


class BirdsEyeViewOperation(ReadOperation):
    """Operation to provide a birds-eye view of the Anki collection.
    
    This operation shows:
    1. Models with note counts (filtering out empty models by default)
    2. Decks with card counts
    3. Examples of notes with their fields (3 by default)
    """
    
    name = "birds-eye-view"
    description = "Provide a birds-eye view of the Anki collection"
    arguments = [
        OperationArgument(
            name="show_empty_models",
            description="Whether to show models with no notes",
            required=False,
            default=False
        ),
        OperationArgument(
            name="show_empty_decks",
            description="Whether to show decks with no cards",
            required=False,
            default=False
        ),
        OperationArgument(
            name="example_count",
            description="Number of example notes to show per model",
            required=False,
            default=3
        )
    ]
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed."""
        # No specific validation needed
        pass
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation."""
        # Get models with note counts
        models_data = self._get_models_with_counts()
        
        # Get decks with card counts
        decks_data = self._get_decks_with_counts()
        
        # Get example notes
        examples_data = self._get_example_notes()
        
        # Prepare result data
        result_data = {
            "models": models_data,
            "decks": decks_data,
            "examples": examples_data
        }
        
        # Print the results
        self.printer.print_result(result_data)
        
        return OperationResult(
            success=True,
            message="Birds-eye view of the collection",
            data=result_data
        )
    
    def _get_models_with_counts(self) -> Dict:
        """Get models with their note counts.
        
        Returns:
            Dictionary with model information and note counts
        """
        models_data = {}
        
        for model_id, model in self.collection.models.items():
            # Count notes for this model
            note_count = sum(
                1 for note in self.collection.notes.values()
                if note.model_id == model_id
            )
            
            # Skip empty models if not showing them
            if note_count == 0 and not self.args["show_empty_models"]:
                continue
            
            # Add model data
            models_data[model.name] = {
                "id": model_id,
                "note_count": note_count,
                "fields": [field.name for field in model.fields],
                "templates": [template.name for template in model.templates]
            }
        
        return models_data
    
    def _get_decks_with_counts(self) -> Dict:
        """Get decks with their card counts.
        
        Returns:
            Dictionary with deck information and card counts
        """
        decks_data = {}
        
        for deck_id, deck in self.collection.decks.items():
            # Count cards for this deck
            card_count = sum(
                1 for card in self.collection.cards.values()
                if card.deck_id == deck_id
            )
            
            # Skip empty decks if not showing them
            if card_count == 0 and not self.args["show_empty_decks"]:
                continue
            
            # Add deck data
            decks_data[deck.name] = {
                "id": deck_id,
                "card_count": card_count
            }
        
        return decks_data
    
    def _get_example_notes(self) -> Dict:
        """Get example notes for each model.
        
        Returns:
            Dictionary with example notes for each model
        """
        examples_data = {}
        example_count = self.args["example_count"]
        
        for model_id, model in self.collection.models.items():
            # Get notes for this model
            model_notes = [
                note for note in self.collection.notes.values()
                if note.model_id == model_id
            ]
            
            # Skip if no notes
            if not model_notes:
                continue
            
            # Get up to example_count notes
            example_notes = model_notes[:example_count]
            
            # Format the examples
            model_examples = []
            for note in example_notes:
                # Format fields for display
                formatted_fields = {}
                for field_name, field_content in note.fields.items():
                    # Truncate very long field content
                    if len(field_content) > 100:
                        field_content = field_content[:97] + "..."
                    
                    formatted_fields[field_name] = field_content
                
                model_examples.append({
                    "id": note.id,
                    "fields": formatted_fields,
                    "tags": note.tags
                })
            
            examples_data[model.name] = model_examples
        
        return examples_data 