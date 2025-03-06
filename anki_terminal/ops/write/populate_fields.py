import importlib
import json
from typing import Any, Dict, List, Type

from anki_terminal.anki_types import Note
from anki_terminal.changelog import Change, ChangeType
from anki_terminal.ops.op_base import (Operation, OperationArgument,
                                       OperationResult)
from anki_terminal.populators.populator_base import FieldPopulator
from anki_terminal.populators.populator_registry import PopulatorRegistry


class PopulateFieldsOperation(Operation):
    """Operation to populate fields in notes using a field populator."""
    
    name = "populate-fields"
    description = "Populate fields in notes using a field populator"
    readonly = False
    
    @classmethod
    def setup_subparser(cls, subparser):
        """Set up the subparser for this operation with sub-subparsers for populators."""
        # Add common arguments
        subparser.add_argument(
            "--model",
            required=True,
            help="Name of the model to populate fields in"
        )
        subparser.add_argument(
            "--batch-size",
            type=int,
            default=1,
            help="Size of batches to process notes in. Default is 1 (no batching)."
        )
        
        # Create sub-subparsers for each populator
        populator_subparsers = subparser.add_subparsers(
            dest="populator",
            help="Field populator to use"
        )
        
        # Add a subparser for each registered populator
        registry = PopulatorRegistry()
        for populator_name, populator_class in registry.get_all_populators().items():
            populator_parser = populator_subparsers.add_parser(
                populator_name,
                help=populator_class.description
            )
            
            # Add populator-specific arguments
            for arg in populator_class.get_config_arguments():
                populator_parser.add_argument(
                    f"--{arg.name.replace('_', '-')}",
                    required=arg.required,
                    default=arg.default,
                    help=arg.description + (" (required)" if arg.required else f" (default: {arg.default})")
                )

    
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