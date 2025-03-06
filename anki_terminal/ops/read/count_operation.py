from typing import Dict, Optional

from anki_terminal.ops.op_base import OperationResult
from anki_terminal.ops.read.path_operation import PathOperation


class CountOperation(PathOperation):
    """Operation to count Anki objects at the specified path."""
    
    name = "count"
    description = "Count Anki objects at the specified path"
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed."""
        super()._validate_impl()
        
        # Count operation only works on collections
        if not self.path.is_collection:
            raise ValueError(f"Path must refer to a collection of objects: {self.path}")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation."""
        if self.path.object_type == 'models':
            return self._count_models()
        elif self.path.object_type == 'fields':
            return self._count_fields()
        elif self.path.object_type == 'templates':
            return self._count_templates()
        elif self.path.object_type == 'cards':
            return self._count_cards()
        elif self.path.object_type == 'notes':
            return self._count_notes()
    
    def _count_models(self) -> OperationResult:
        """Count all models."""
        count = len(self.collection.models)
        
        self.printer.print_result({"count": count})
        
        return OperationResult(
            success=True,
            message=f"Counted {count} models",
            data={"count": count}
        )
    
    def _count_fields(self) -> OperationResult:
        """Count fields in the specified model."""
        model = self._get_model(self.path.model_name)
        count = len(model.fields)
        
        self.printer.print_result({"count": count})
        
        return OperationResult(
            success=True,
            message=f"Counted {count} fields in model '{model.name}'",
            data={"count": count}
        )
    
    def _count_templates(self) -> OperationResult:
        """Count templates in the specified model."""
        model = self._get_model(self.path.model_name)
        count = len(model.templates)
        
        self.printer.print_result({"count": count})
        
        return OperationResult(
            success=True,
            message=f"Counted {count} templates in model '{model.name}'",
            data={"count": count}
        )
    
    def _count_cards(self) -> OperationResult:
        """Count cards, optionally filtered by model."""
        if self.path.model_name:
            model = self._get_model(self.path.model_name)
            count = sum(
                1 for card in self.collection.cards.values()
                if self.collection.notes[card.note_id].model_id == model.id
            )
        else:
            count = len(self.collection.cards)
        
        self.printer.print_result({"count": count})
        
        return OperationResult(
            success=True,
            message=f"Counted {count} cards",
            data={"count": count}
        )
    
    def _count_notes(self) -> OperationResult:
        """Count notes, optionally filtered by model."""
        if self.path.model_name:
            model = self._get_model(self.path.model_name)
            count = sum(
                1 for note in self.collection.notes.values()
                if note.model_id == model.id
            )
            
            self.printer.print_result({"count": count})
            
            return OperationResult(
                success=True,
                message=f"Counted {count} notes for model '{model.name}'",
                data={"count": count}
            )
        else:
            # Count notes per model
            counts = {}
            for model_id, model in self.collection.models.items():
                counts[model.name] = sum(
                    1 for note in self.collection.notes.values()
                    if note.model_id == model_id
                )
            
            total = sum(counts.values())
            
            self.printer.print_result({"total": total, "by_model": counts})
            
            return OperationResult(
                success=True,
                message=f"Counted {total} notes across {len(counts)} models",
                data={"total": total, "by_model": counts}
            ) 