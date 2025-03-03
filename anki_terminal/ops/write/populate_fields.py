from anki_terminal.ops.base import Operation, OperationResult, OperationArgument
from anki_terminal.changelog import Change, ChangeType
import importlib
import json
from typing import List, Dict, Any
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
            description="Path to the JSON configuration file for the populator or a JSON string",
            required=True
        ),
        OperationArgument(
            name="batch_size",
            description="Size of batches to process notes in. Default is 1 (no batching).",
            required=False,
            default=1
        )
    ]
    
    def _load_populator_config(self) -> Dict[str, Any]:
        """Load the populator configuration from a file or JSON string.
        
        Returns:
            Dictionary containing the populator configuration
            
        Raises:
            ValueError: If the configuration cannot be loaded
        """
        config_path_or_json = self.args["populator_config"]
        
        # Try to parse as JSON string first
        try:
            return json.loads(config_path_or_json)
        except json.JSONDecodeError:
            # Not a valid JSON string, try as file path
            try:
                with open(config_path_or_json) as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                raise ValueError(f"Invalid populator configuration: {str(e)}")
    
    def _get_populator(self) -> FieldPopulator:
        """Get an instance of the populator class.
        
        Returns:
            Initialized populator instance
            
        Raises:
            ValueError: If the populator class cannot be loaded
        """
        try:
            module_path, class_name = self.args["populator_class"].rsplit('.', 1)
            module = importlib.import_module(module_path)
            populator_cls = getattr(module, class_name)
            
            if not issubclass(populator_cls, FieldPopulator):
                raise ValueError(f"Class {self.args['populator_class']} is not a subclass of FieldPopulator")
            
            config = self._load_populator_config()
            return populator_cls(config)
            
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Could not load populator class {self.args['populator_class']}: {str(e)}")
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed.
        
        Raises:
            ValueError: If arguments are invalid
        """
        # Check if model exists
        model = self._get_model(self.args["model_name"])
        
        # Get populator and validate it
        populator = self._get_populator()
        populator.validate(model)

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
        populator = self._get_populator()
        
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