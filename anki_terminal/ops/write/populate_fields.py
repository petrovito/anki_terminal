import logging
from typing import Any, Dict, List, Type

from anki_terminal.anki_types import Note
from anki_terminal.changelog import Change
from anki_terminal.ops.op_base import (Operation, OperationArgument,
                                       OperationResult)
from anki_terminal.populators.populator_base import FieldPopulator
from anki_terminal.populators.populator_factory import PopulatorFactory
from anki_terminal.populators.populator_registry import PopulatorRegistry

logger = logging.getLogger('anki_inspector')

class PopulateFieldsOperation(Operation):
    """Operation to populate fields in notes using a field populator."""
    
    name = "populate-fields"
    description = "Populate fields in notes using a field populator"
    readonly = False
    
    # Class-level factory instance
    factory = PopulatorFactory()
    
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
        subparser.add_argument(
            "--populator-config-file",
            help="Path to a configuration file for the populator",
            dest="populator_config_file"
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
    
    def __init__(self, **kwargs):
        """Initialize the operation.
        
        Args:
            **kwargs: Operation arguments
        """
        super().__init__(**kwargs)
        self._populator = None
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed.
        
        Raises:
            ValueError: If arguments are invalid
        """
        # Check if model exists
        model = self._get_model(self.args["model_name"])
        
        # Create the populator and store it for later use
        self._populator = self.factory.create_populator_from_args(self.args)
        
        # Validate the populator
        self._populator.validate(model)

        # Get all notes for this model
        model_notes = [note for note in self.collection.notes.values() if note.model_id == model.id]
        if not model_notes:
            raise ValueError(f"No notes found for model: {self.args['model_name']}")

        # Check if batching is requested and supported
        batch_size = self.args["batch_size"]
        if batch_size is not None and batch_size > 1:
            if not self._populator.supports_batching:
                raise ValueError(f"Populator {self._populator.__class__.__name__} does not support batch operations")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult indicating success/failure and containing changes
        """
        model = self._get_model(self.args["model_name"])
        
        # Use the populator created during validation
        if not self._populator:
            raise ValueError("Populator not initialized. Call validate() first.")
        
        # Get all notes for this model
        model_notes = [note for note in self.collection.notes.values() if note.model_id == model.id]
        
        # Track changes
        changes = []
        updated_count = 0
        skipped_count = 0
        
        # Check if batching is requested and supported
        batch_size = self.args["batch_size"]
        if batch_size is not None and batch_size > 1 and self._populator.supports_batching:
            # Process notes in batches
            for i in range(0, len(model_notes), batch_size):
                batch = model_notes[i:i+batch_size]
                try:
                    # Populate fields for this batch
                    batch_results = self._populator.populate_batch(batch)
                    
                    # Update notes and record changes
                    for note_id, field_updates in batch_results.items():
                        note = next(n for n in batch if n.id == note_id)
                        
                        # Update note fields
                        for field_name, field_value in field_updates.items():
                            note.fields[field_name] = field_value
                        
                        # Record change
                        changes.append(Change.note_fields_updated(note, model.id))
                        updated_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing batch: {str(e)}")
                    skipped_count += len(batch)
        else:
            # Process notes individually
            for note in model_notes:
                try:
                    # Populate fields for this note
                    field_updates = self._populator.populate_fields(note)
                    
                    # Update note fields
                    for field_name, field_value in field_updates.items():
                        note.fields[field_name] = field_value
                    
                    # Record change
                    changes.append(Change.note_fields_updated(note, model.id))
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing note {note.id}: {str(e)}")
                    skipped_count += 1
        
        return OperationResult(
            success=True,
            message=f"Updated {updated_count} notes, skipped {skipped_count} notes",
            changes=changes
        ) 