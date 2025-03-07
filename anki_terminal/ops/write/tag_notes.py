import re
from typing import Any, Dict, List, Optional

from anki_terminal.anki_types import Note
from anki_terminal.changelog import Change, ChangeType
from anki_terminal.ops.op_base import Operation, OperationArgument, OperationResult


class TagNotesOperation(Operation):
    """Operation to tag notes based on field data."""
    
    name = "tag-notes"
    description = "Tag notes based on field data using a regular expression pattern"
    readonly = False
    
    @classmethod
    def setup_subparser(cls, subparser):
        """Set up the subparser for this operation."""
        subparser.add_argument(
            "--model",
            required=True,
            help="Name of the model to tag notes in"
        )
        subparser.add_argument(
            "--source-field",
            required=True,
            help="Field containing the data to extract tags from"
        )
        subparser.add_argument(
            "--pattern",
            required=True,
            help="Regular expression pattern to extract tags. Must contain a capture group."
        )
        subparser.add_argument(
            "--tag-prefix",
            help="Prefix to add to extracted tags (optional)"
        )
    
    def __init__(self, printer=None, **kwargs):
        """Initialize the operation.
        
        Args:
            **kwargs: Operation-specific arguments
        """
        super().__init__(printer, **kwargs)
        self.args = {
            "model_name": kwargs["model"],
            "source_field": kwargs["source_field"],
            "pattern": kwargs["pattern"],
            "tag_prefix": kwargs.get("tag_prefix", "")
        }
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed.
        
        Raises:
            ValueError: If validation fails
        """
        # Check if model exists
        model = self._get_model(self.args["model_name"])
        
        # Validate source field exists
        field_names = [f.name for f in model.fields]
        if self.args["source_field"] not in field_names:
            raise ValueError(f"Source field '{self.args['source_field']}' not found in model")
        
        # Validate pattern has capture groups
        try:
            pattern = re.compile(self.args["pattern"])
            if pattern.groups == 0:
                raise ValueError("Pattern must contain at least one capture group")
        except re.error as e:
            raise ValueError(f"Invalid regular expression pattern: {str(e)}")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult indicating success/failure and containing changes
        """
        model = self._get_model(self.args["model_name"])
        
        # Get all notes for this model
        model_notes = [note for note in self.collection.notes.values() if note.model_id == model.id]
        
        # Compile pattern
        pattern = re.compile(self.args["pattern"])
        
        # Track changes
        changes = []
        updated_count = 0
        skipped_count = 0
        
        # Process each note
        for note in model_notes:
            try:
                # Get source field value
                source_value = note.fields[self.args["source_field"]]
                if not source_value:
                    skipped_count += 1
                    continue
                
                # Extract tag using pattern
                match = pattern.search(source_value)
                if not match:
                    skipped_count += 1
                    continue
                
                # Get the first capture group and create tag
                tag = match.group(1)
                if self.args["tag_prefix"]:
                    tag = f"{self.args['tag_prefix']}_{tag}"
                
                # Add tag if not already present
                if tag not in note.tags:
                    note.tags.append(tag)
                    changes.append(Change(
                        type=ChangeType.NOTE_TAGS_UPDATED,
                        data={
                            'note_id': note.id,
                            'model_id': model.id,
                            'tags': note.tags
                        }
                    ))
                    updated_count += 1
                else:
                    skipped_count += 1
                    
            except (KeyError, ValueError) as e:
                skipped_count += 1
                continue
        
        return OperationResult(
            success=True,
            message=f"Updated {updated_count} notes, skipped {skipped_count} notes",
            changes=changes
        ) 