from anki_terminal.commons.changelog import Change, ChangeType
from anki_terminal.ops.op_base import (Operation, OperationArgument,
                                       OperationResult)


class RenameModelOperation(Operation):
    """Operation to rename a model."""
    
    name = "rename-model"
    description = "Rename a model and update all related notes"
    readonly = False
    arguments = [
        OperationArgument(
            name="old_model_name",
            description="Current name of the model to rename",
            required=True
        ),
        OperationArgument(
            name="new_model_name",
            description="New name for the model",
            required=True
        )
    ]
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed.
        
        Raises:
            ValueError: If arguments are invalid
        """
        # Check if old model exists
        old_model = next((m for m in self.collection.models.values() 
                         if m.name == self.args["old_model_name"]), None)
        if not old_model:
            raise ValueError(f"Model '{self.args['old_model_name']}' not found")
        
        # Check if new model name already exists
        if any(m.name == self.args["new_model_name"] for m in self.collection.models.values()):
            raise ValueError(f"Model '{self.args['new_model_name']}' already exists")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult indicating success/failure and containing changes
        """
        old_model_name = self.args["old_model_name"]
        new_model_name = self.args["new_model_name"]
        
        # Find and rename the model
        model = next(m for m in self.collection.models.values() 
                    if m.name == old_model_name)
        model.name = new_model_name
        
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
            message=f"Renamed model '{old_model_name}' to '{new_model_name}'",
            changes=[change] + note_changes
        ) 