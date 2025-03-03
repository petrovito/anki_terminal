from anki_terminal.ops.base import Operation, OperationResult, OperationArgument
from anki_terminal.anki_types import Note
from anki_terminal.changelog import Change, ChangeType
from datetime import datetime
from typing import Dict, List

class MigrateNotesOperation(Operation):
    """Operation to migrate notes from one model to another."""
    
    name = "migrate-notes"
    description = "Migrate notes from one model to another with field mapping"
    readonly = False
    arguments = [
        OperationArgument(
            name="model_name",
            description="Name of the source model",
            required=True
        ),
        OperationArgument(
            name="target_model_name",
            description="Name of the target model",
            required=True
        ),
        OperationArgument(
            name="field_mapping",
            description="Dictionary mapping source fields to target fields",
            required=True
        )
    ]
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed.
        
        Raises:
            ValueError: If arguments are invalid
        """
        # Check if source model exists
        source_model = None
        for model in self.collection.models.values():
            if model.name == self.args["model_name"]:
                source_model = model
                break
        if not source_model:
            raise ValueError(f"Source model not found: {self.args['model_name']}")
        
        # Check if target model exists
        target_model = None
        for model in self.collection.models.values():
            if model.name == self.args["target_model_name"]:
                target_model = model
                break
        if not target_model:
            raise ValueError(f"Target model not found: {self.args['target_model_name']}")
        
        # Validate field mapping
        if not isinstance(self.args["field_mapping"], dict):
            raise ValueError("Field mapping must be a dictionary")
        
        # Check source fields exist in source model
        source_field_names = {field.name for field in source_model.fields}
        for source_field in self.args["field_mapping"].keys():
            if source_field not in source_field_names:
                raise ValueError(f"Source field not found in source model: {source_field}")
        
        # Check target fields exist in target model
        target_field_names = {field.name for field in target_model.fields}
        for target_field in self.args["field_mapping"].values():
            if target_field not in target_field_names:
                raise ValueError(f"Target field not found in target model: {target_field}")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult indicating success/failure and containing changes
        """
        # Get source and target models
        source_model = next(m for m in self.collection.models.values() if m.name == self.args["model_name"])
        target_model = next(m for m in self.collection.models.values() if m.name == self.args["target_model_name"])
        
        # Get notes to migrate
        notes_to_migrate = [
            note for note in self.collection.notes.values()
            if note.model_id == source_model.id
        ]
        
        if not notes_to_migrate:
            return OperationResult(
                success=True,
                message=f"No notes found for model '{self.args['model_name']}'",
                changes=[]
            )
        
        # Update each note
        for note in notes_to_migrate:
            # Map fields according to field_mapping
            new_fields = {field.name: "" for field in target_model.fields}  # Initialize all fields empty
            for source_field, target_field in self.args["field_mapping"].items():
                new_fields[target_field] = note.fields[source_field]
            
            # Update note
            note.model_id = target_model.id
            note.fields = new_fields
            note.modification_time = datetime.now()
            note.usn = -1  # -1 indicates needs sync
        
        # Create change records - one for each migrated note
        changes = []
        for note in notes_to_migrate:
            changes.append(Change(
                type=ChangeType.NOTE_MIGRATED,  # Use NOTE_MIGRATED instead of NOTE_FIELDS_UPDATED
                data={
                    'note_id': note.id,
                    'source_model_id': source_model.id,
                    'target_model_id': target_model.id,
                    'fields': note.fields
                }
            ))
        
        return OperationResult(
            success=True,
            message=f"Migrated {len(notes_to_migrate)} notes from '{self.args['model_name']}' to '{self.args['target_model_name']}'",
            changes=changes
        ) 