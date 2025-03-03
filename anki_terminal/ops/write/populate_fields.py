from anki_terminal.ops.base import Operation, OperationResult, OperationArgument
from anki_terminal.changelog import Change, ChangeType
import importlib
from typing import List
from anki_terminal.anki_types import Note
from anki_terminal.populators.base import FieldPopulator

class PopulateFieldsOperation(Operation):
    """Operation to populate fields in notes using a field populator."""
    
    name = "populate-fields"
    description = "Populate fields in notes using a field populator"
    readonly = False
    arguments = [
        OperationArgument(
            name="model_name",
            description="Name of the model to populate fields in",
            required=True
        ),
        OperationArgument(
            name="populator_class",
            description="Full path to the populator class (e.g. 'populators.copy_field.CopyFieldPopulator')",
            required=True
        ),
        OperationArgument(
            name="populator_config",
            description="Path to the JSON configuration file for the populator",
            required=True
        ),
        OperationArgument(
            name="batch_size",
            description="Size of batches to process notes in. Default is 1 (no batching).",
            required=False,
            default=1
        )
    ]
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed.
        
        Raises:
            ValueError: If arguments are invalid
        """
        # Check if model exists
        model = self._get_model(self.args["model_name"])
        
        # Import and instantiate the populator class
        try:
            module_path, class_name = self.args["populator_class"].rsplit('.', 1)
            module = importlib.import_module(module_path)
            populator_cls = getattr(module, class_name)
            
            if not issubclass(populator_cls, FieldPopulator):
                raise ValueError(f"Class {self.args['populator_class']} is not a subclass of FieldPopulator")
                
            populator = populator_cls(self.args["populator_config"])
            
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Could not load populator class {self.args['populator_class']}: {str(e)}")

        # Get field names from model
        field_names = [f.name for f in model.fields]

        # Verify target fields exist in model
        invalid_fields = [f for f in populator.target_fields if f not in field_names]
        if invalid_fields:
            raise ValueError(f"Target fields not found in model: {invalid_fields}")

        # Get all notes for this model
        model_notes = [note for note in self.collection.notes.values() if note.model_id == model.id]
        if not model_notes:
            raise ValueError(f"No notes found for model: {self.args['model_name']}")

        # Check if batching is requested and supported
        batch_size = self.args["batch_size"]
        if batch_size is not None and batch_size > 1:
            if not populator.supports_batching:
                raise ValueError(f"Populator {self.args['populator_class']} does not support batch operations")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult indicating success/failure and containing changes
        """
        model = self._get_model(self.args["model_name"])
        
        # Import and instantiate the populator class
        module_path, class_name = self.args["populator_class"].rsplit('.', 1)
        module = importlib.import_module(module_path)
        populator_cls = getattr(module, class_name)
        populator = populator_cls(self.args["populator_config"])
        
        # Get all notes for this model
        model_notes = [note for note in self.collection.notes.values() if note.model_id == model.id]
        
        # Track changes
        changes = []
        updated_count = 0
        skipped_count = 0
        
        # Check if batching is requested and supported
        batch_size = self.args["batch_size"]
        if batch_size is not None and batch_size > 1 and populator.supports_batching:
            # Process notes in batches
            for i in range(0, len(model_notes), batch_size):
                batch = model_notes[i:i + batch_size]
                try:
                    updates = populator.populate_batch(batch)
                    
                    # Apply updates and add to changelog
                    for note_id, field_updates in updates.items():
                        note = next(n for n in batch if n.id == note_id)
                        note.fields.update(field_updates)
                        changes.append(Change(
                            type=ChangeType.NOTE_FIELDS_UPDATED,
                            data={
                                'note_id': note.id,
                                'model_id': model.id,
                                'fields': note.fields
                            }
                        ))
                    
                    updated_count += len(updates)
                    skipped_count += len(batch) - len(updates)
                except ValueError as e:
                    skipped_count += len(batch)
        else:
            # Process notes one at a time
            for note in model_notes:
                try:
                    updates = populator.populate_fields(note)
                    note.fields.update(updates)
                    changes.append(Change(
                        type=ChangeType.NOTE_FIELDS_UPDATED,
                        data={
                            'note_id': note.id,
                            'model_id': model.id,
                            'fields': note.fields
                        }
                    ))
                    updated_count += 1
                except ValueError as e:
                    skipped_count += 1
        
        return OperationResult(
            success=True,
            message=f"Updated {updated_count} notes, skipped {skipped_count} notes",
            changes=changes
        ) 