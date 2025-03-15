from typing import Dict, List, Set

from anki_terminal.commons.anki_types import Note
from anki_terminal.commons.changelog import Change
from anki_terminal.ops.op_base import (Operation, OperationArgument,
                                       OperationResult)


class RemoveEmptyNotesOperation(Operation):
    """Operation to remove notes where a specific field is empty or contains only whitespace."""
    
    name = "remove-empty-notes"
    description = "Remove notes where a specific field is empty or contains only whitespace"
    readonly = False
    arguments = [
        OperationArgument(
            name="model",
            description="Name of the model to check notes in (optional if there's only one model with notes)",
            required=False,
            default=None
        ),
        OperationArgument(
            name="field",
            description="Name of the field to check for emptiness",
            required=True
        )
    ]
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed.
        
        Raises:
            ValueError: If arguments are invalid
        """
        # Get the model (will automatically find one if not specified)
        model_name = self.args.get("model")
        model = self._get_model(model_name)
        
        # Store the model name for later use
        self.args["model"] = model.name
        
        # Check if field exists in model
        field_names = [f.name for f in model.fields]
        if self.args["field"] not in field_names:
            raise ValueError(f"Field '{self.args['field']}' not found in model '{model.name}'")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult indicating success/failure and containing changes
        """
        model = self._get_model(self.args["model"])
        field_name = self.args["field"]
        
        # Find notes with empty fields
        notes_to_remove: List[Note] = []
        for note in self.collection.notes.values():
            if note.model_id == model.id:
                field_value = note.fields.get(field_name, "")
                # Check if field is empty or contains only whitespace
                if not field_value or field_value.strip() == "":
                    notes_to_remove.append(note)
        
        if not notes_to_remove:
            return OperationResult(
                success=True,
                message=f"No notes found with empty '{field_name}' field in model '{model.name}'",
                changes=[]
            )
        
        # Find cards associated with these notes
        cards_to_remove: Set[int] = set()
        for card in self.collection.cards.values():
            if card.note_id in [note.id for note in notes_to_remove]:
                cards_to_remove.add(card.id)
        
        # Create change records
        changes = []
        
        # Remove cards first
        for card_id in cards_to_remove:
            changes.append(Change.card_deleted(card_id))
            del self.collection.cards[card_id]
        
        # Then remove notes
        for note in notes_to_remove:
            changes.append(Change.note_deleted(note.id))
            del self.collection.notes[note.id]
        
        return OperationResult(
            success=True,
            message=f"Removed {len(notes_to_remove)} notes and {len(cards_to_remove)} cards with empty '{field_name}' field",
            changes=changes
        ) 