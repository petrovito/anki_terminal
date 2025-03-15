from anki_terminal.commons.changelog import Change, ChangeType
from anki_terminal.ops.op_base import (Operation, OperationArgument,
                                       OperationResult)


class RenameFieldOperation(Operation):
    """Operation to rename a field in a model."""
    
    name = "rename-field"
    description = "Rename a field in a model and update all related notes"
    readonly = False
    arguments = [
        OperationArgument(
            name="old_field_name",
            description="Current name of the field to rename",
            required=True
        ),
        OperationArgument(
            name="new_field_name",
            description="New name for the field",
            required=True
        ),
        OperationArgument(
            name="model",
            description="Name of the model containing the field",
            required=False,
            default=None
        )
    ]
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed.
        
        Raises:
            ValueError: If arguments are invalid
        """
        model = self._get_model(self.args["model"])
        
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
        model = self._get_model(self.args["model"])
        old_field_name = self.args["old_field_name"]
        new_field_name = self.args["new_field_name"]
        
        # Find and rename the field
        for field in model.fields:
            if field.name == old_field_name:
                field.name = new_field_name
                break
        
        # Update field name in all notes using this model
        for note in self.collection.notes.values():
            if note.model_id == model.id and old_field_name in note.fields:
                # Copy the field value to the new field name
                note.fields[new_field_name] = note.fields[old_field_name]
                # Remove the old field
                del note.fields[old_field_name]
        
        # Create change record
        change = Change.model_updated({
            model_id: model for model_id, model in self.collection.models.items()
        })
        
        # Create individual note changes for each affected note
        note_changes = []
        for note in self.collection.notes.values():
            if note.model_id == model.id:
                note_changes.append(Change.note_fields_updated(note, model.id))
        
        return OperationResult(
            success=True,
            message=f"Renamed field '{old_field_name}' to '{new_field_name}' in model '{model.name}'",
            changes=[change] + note_changes
        ) 