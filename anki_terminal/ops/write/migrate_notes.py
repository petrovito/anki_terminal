from datetime import datetime
from typing import Dict, List

from anki_terminal.commons.anki_types import Note
from anki_terminal.commons.changelog import Change, ChangeType
from anki_terminal.ops.op_base import (Operation, OperationArgument,
                                       OperationResult)


class MigrateNotesOperation(Operation):
    """Operation to migrate notes from one model to another."""
    
    name = "migrate-notes"
    description = "Migrate notes from one model to another with field mapping"
    readonly = False
    arguments = [
        OperationArgument(
            name="model",
            description="Name of the source model",
            required=True
        ),
        OperationArgument(
            name="target_model",
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
            if model.name == self.args["model"]:
                source_model = model
                break
        if not source_model:
            raise ValueError(f"Source model not found: {self.args['model']}")
        
        # Check if target model exists
        target_model = None
        for model in self.collection.models.values():
            if model.name == self.args["target_model"]:
                target_model = model
                break
        if not target_model:
            raise ValueError(f"Target model not found: {self.args['target_model']}")
        
        # Check if field mapping is a dictionary
        if not isinstance(self.args["field_mapping"], dict):
            raise ValueError("Field mapping must be a dictionary")
        
        # Check if source fields exist in source model
        source_field_names = [f.name for f in source_model.fields]
        for source_field in self.args["field_mapping"].keys():
            if source_field not in source_field_names:
                raise ValueError(f"Source field not found in source model: {source_field}")
        
        # Check if target fields exist in target model
        target_field_names = [f.name for f in target_model.fields]
        for target_field in self.args["field_mapping"].values():
            if target_field not in target_field_names:
                raise ValueError(f"Target field not found in target model: {target_field}")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult indicating success/failure and containing changes
        """
        # Get source and target models
        source_model = None
        target_model = None
        for model in self.collection.models.values():
            if model.name == self.args["model"]:
                source_model = model
            elif model.name == self.args["target_model"]:
                target_model = model
        
        # Get notes for source model
        source_notes = []
        for note in self.collection.notes.values():
            if note.model_id == source_model.id:
                source_notes.append(note)
        
        # Create new notes for target model
        new_notes = []
        note_changes = []
        for source_note in source_notes:
            # Create new note
            new_note_id = source_note.id
            new_note = Note(
                id=new_note_id,
                guid=source_note.guid,
                model_id=target_model.id,
                modification_time=datetime.now(),
                usn=-1,  # Needs sync
                tags=source_note.tags.copy(),
                fields={},
                sort_field=0,  # Will be updated when fields are populated
                checksum=0,  # Will be updated when fields are populated
                flags=0,
                data={}
            )
            
            # Copy fields according to mapping
            field_mapping = self.args["field_mapping"]
            for source_field, target_field in field_mapping.items():
                if source_field in source_note.fields:
                    new_note.fields[target_field] = source_note.fields[source_field]
            for target_field in target_model.fields:
                if target_field.name not in field_mapping.values():
                    new_note.fields[target_field.name] = ""
            

            # Remove source note from collection
            del self.collection.notes[source_note.id]

            # Add new note to collection
            self.collection.notes[new_note_id] = new_note
            new_notes.append(new_note)

            
            # Create change record for new note
            note_changes.append(Change.note_migrated(new_note, source_model.id, target_model.id))
            
            
            # Create change record for deleted note
            note_changes.append(Change.note_migrated(source_note, source_model.id, target_model.id))
        
        return OperationResult(
            success=True,
            message=f"Migrated {len(source_notes)} notes from '{source_model.name}' to '{target_model.name}'",
            changes=note_changes
        ) 