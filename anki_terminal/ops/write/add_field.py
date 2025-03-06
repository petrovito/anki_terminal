from anki_terminal.anki_types import Field
from anki_terminal.changelog import Change, ChangeType
from anki_terminal.ops.op_base import (Operation, OperationArgument,
                                       OperationResult)


class AddFieldOperation(Operation):
    """Operation to add a new field to an existing model."""
    
    name = "add-field"
    description = "Add a new field to an existing model"
    readonly = False
    arguments = [
        OperationArgument(
            name="model_name",
            description="Name of the model to add the field to",
            required=True
        ),
        OperationArgument(
            name="field_name",
            description="Name of the new field to add",
            required=True
        )
    ]
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed.
        
        Raises:
            ValueError: If arguments are invalid
        """
        model = self._get_model(self.args["model_name"])
        
        # Check if field already exists
        if any(f.name == self.args["field_name"] for f in model.fields):
            raise ValueError(f"Field '{self.args['field_name']}' already exists in model '{model.name}'")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult indicating success/failure and containing changes
        """
        model = self._get_model(self.args["model_name"])
        field_name = self.args["field_name"]
        
        # Create and add new field to model
        new_field = Field(
            name=field_name,
            ordinal=len(model.fields),
            sticky=False,
            rtl=False,
            font="Arial",
            font_size=20,
            description="",
            plain_text=True
        )
        model.fields.append(new_field)
        
        # Initialize field in existing notes
        for note in self.collection.notes.values():
            if note.model_id == model.id:
                note.fields[field_name] = ""
        
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
        
        # Create individual note changes for each affected note
        note_changes = []
        for note in self.collection.notes.values():
            if note.model_id == model.id:
                note_changes.append(Change(
                    type=ChangeType.NOTE_FIELDS_UPDATED,
                    data={
                        'note_id': note.id,
                        'model_id': model.id,
                        'fields': note.fields
                    }
                ))
        
        return OperationResult(
            success=True,
            message=f"Added field '{field_name}' to model '{model.name}' successfully",
            changes=[change] + note_changes
        ) 