from typing import Dict, Optional

from ops.base import Operation, OperationResult
from anki_types import Model
from changelog import ChangeLog, Change, ChangeType

class RenameFieldOperation(Operation):
    """Operation to rename a field in a model."""
    
    name = "rename_field"
    description = "Rename a field in a model and update all related notes"
    readonly = False
    required_args = {"old_field_name", "new_field_name"}
    optional_args = {
        "model_name": None,  # If None, uses default/only model
    }
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed.
        
        Raises:
            ValueError: If arguments are invalid
        """
        model = self._get_model(self.args["model_name"])
        
        # Check if old field exists
        old_field = next((f for f in model.fields if f.name == self.args["old_field_name"]), None)
        if not old_field:
            raise ValueError(f"Field '{self.args['old_field_name']}' not found in model '{model.name}'")
        
        # Check if new field already exists
        if any(f.name == self.args["new_field_name"] for f in model.fields):
            raise ValueError(f"Field '{self.args['new_field_name']}' already exists in model '{model.name}'")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult indicating success/failure and containing changes
        """
        model = self._get_model(self.args["model_name"])
        old_field_name = self.args["old_field_name"]
        new_field_name = self.args["new_field_name"]
        
        # Update field name in model
        old_field = next(f for f in model.fields if f.name == old_field_name)
        old_field.name = new_field_name
        
        # Update in-memory note field names
        for note in self.collection.notes.values():
            if note.model_id == model.id:
                new_fields = {}
                for field_name, value in note.fields.items():
                    if field_name == old_field_name:
                        new_fields[new_field_name] = value
                    else:
                        new_fields[field_name] = value
                note.fields = new_fields
        
        # Create change record
        change = Change(
            type=ChangeType.MODEL_UPDATED,
            data={
                'models': {
                    str(model_id): model.to_dict()
                    for model_id, model in self.collection.models.items()
                }
            }
        )
        
        return OperationResult(
            success=True,
            message=f"Renamed field '{old_field_name}' to '{new_field_name}' in model '{model.name}'",
            changes=[change]
        ) 