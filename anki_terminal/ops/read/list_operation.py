from typing import Any, Dict, List, Optional

from anki_terminal.ops.anki_path import AnkiPath
from anki_terminal.ops.op_base import OperationArgument, OperationResult
from anki_terminal.ops.read.path_operation import PathOperation


class ListOperation(PathOperation):
    """Operation to list Anki objects at the specified path."""
    
    name = "list"
    description = "List Anki objects at the specified path"
    arguments = [
        OperationArgument(
            name="path",
            description="Path to the Anki object(s)",
            required=True
        ),
        OperationArgument(
            name="limit",
            description="Maximum number of items to return (0 for all)",
            required=False,
            default=0
        )
    ]
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed."""
        super()._validate_impl()
        
        # List operation only works on collections
        if not self.path.is_collection:
            raise ValueError(f"Path must refer to a collection of objects: {self.path}")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation."""
        if self.path.object_type == 'models':
            return self._list_models()
        elif self.path.object_type == 'fields':
            return self._list_fields()
        elif self.path.object_type == 'templates':
            return self._list_templates()
        elif self.path.object_type == 'cards':
            return self._list_cards()
        elif self.path.object_type == 'notes':
            return self._list_notes()
    
    def _list_models(self) -> OperationResult:
        """List all models/note types."""
        models = [
            {
                "name": model.name,
                "id": model_id,
                "type": "Standard" if model.type == 0 else "Cloze"
            }
            for model_id, model in self.collection.models.items()
        ]
        
        self.printer.print_result({"models": models})
        
        return OperationResult(
            success=True,
            message=f"Listed {len(models)} models",
            data={"models": models}
        )
    
    def _list_fields(self) -> OperationResult:
        """List all fields in the specified model."""
        model = self._get_model(self.path.model_name)
        
        fields = [
            {"name": field.name, "type": "text"}
            for field in model.fields
        ]
        
        self.printer.print_result({"fields": fields})
        
        return OperationResult(
            success=True,
            message=f"Listed {len(fields)} fields from model '{model.name}'",
            data={"fields": fields}
        )
    
    def _list_templates(self) -> OperationResult:
        """List all templates in the specified model."""
        model = self._get_model(self.path.model_name)
        
        templates = [
            {
                "name": template.name,
                "ordinal": template.ordinal
            }
            for template in model.templates
        ]
        
        self.printer.print_result({"templates": templates})
        
        return OperationResult(
            success=True,
            message=f"Listed {len(templates)} templates from model '{model.name}'",
            data={"templates": templates}
        )
    
    def _list_cards(self) -> OperationResult:
        """List cards, optionally filtered by model."""
        if self.path.model_name:
            model = self._get_model(self.path.model_name)
            cards = [
                {
                    "id": card_id,
                    "note_id": card.note_id
                }
                for card_id, card in self.collection.cards.items()
                if self.collection.notes[card.note_id].model_id == model.id
            ]
        else:
            cards = [
                {
                    "id": card_id,
                    "note_id": card.note_id
                }
                for card_id, card in self.collection.cards.items()
            ]
        
        self.printer.print_result({"cards": cards})
        
        return OperationResult(
            success=True,
            message=f"Listed {len(cards)} cards",
            data={"cards": cards}
        )
    
    def _list_notes(self) -> OperationResult:
        """List notes, optionally filtered by model."""
        limit = int(self.args["limit"])
        
        if self.path.model_name:
            model = self._get_model(self.path.model_name)
            raw_notes = [
                (note_id, note, model)
                for note_id, note in self.collection.notes.items()
                if note.model_id == model.id
            ]
        else:
            # When listing all notes, we need to get the model for each note
            raw_notes = []
            for note_id, note in self.collection.notes.items():
                model = None
                for m in self.collection.models.values():
                    if m.id == note.model_id:
                        model = m
                        break
                if model:
                    raw_notes.append((note_id, note, model))
        
        # Apply limit if specified
        if limit > 0:
            raw_notes = raw_notes[:limit]
        
        # Format notes for better readability
        notes = []
        for note_id, note, model in raw_notes:
            formatted_fields = {}
            
            # Parse the fields based on the model's field definitions
            if isinstance(note.fields, dict):
                # Fields are already a dictionary
                raw_fields = note.fields
            elif isinstance(note.fields, str):
                # Fields are a string with separators
                field_values = note.fields.split('\x1f')
                raw_fields = {}
                for i, field in enumerate(model.fields):
                    if i < len(field_values):
                        raw_fields[field.name] = field_values[i]
                    else:
                        raw_fields[field.name] = ""
            else:
                # Unknown format, try to convert to string
                raw_fields = {}
                for field in model.fields:
                    raw_fields[field.name] = ""
            
            # Format the fields for display
            for field in model.fields:
                field_name = field.name
                field_content = raw_fields.get(field_name, "")
                
                # Truncate very long field content
                if len(field_content) > 100:
                    field_content = field_content[:97] + "..."
                
                # Replace special characters for better display
                field_content = field_content.replace("\u001f", " | ")
                
                formatted_fields[field_name] = field_content
            
            notes.append({
                "id": note_id,
                "model": model.name,
                "fields": formatted_fields
            })
        
        self.printer.print_result({"notes": notes})
        
        return OperationResult(
            success=True,
            message=f"Listed {len(notes)} notes" + (f" (limited to {limit})" if limit > 0 else ""),
            data={"notes": notes}
        ) 