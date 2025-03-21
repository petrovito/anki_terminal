import re
from typing import Any, Dict, List, Optional

from anki_terminal.commons.anki_types import Note
from anki_terminal.commons.changelog import Change, ChangeType
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
            "model": kwargs["model"],
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
        model = self._get_model(self.args["model"])
        
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
            raise ValueError(f"Invalid regular expression pattern: {e}")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult indicating success/failure and containing changes
        """
        model = self._get_model(self.args["model"])
        source_field = self.args["source_field"]
        pattern = re.compile(self.args["pattern"])
        tag_prefix = self.args["tag_prefix"]
        
        # Find notes to tag
        notes_to_tag = []
        for note in self.collection.notes.values():
            if note.model_id == model.id and source_field in note.fields:
                notes_to_tag.append(note)
        
        if not notes_to_tag:
            return OperationResult(
                success=True,
                message=f"No notes found for model '{model.name}' with field '{source_field}'",
                changes=[]
            )
        
        # Tag notes
        changes = []
        tags_added = 0
        notes_tagged = 0
        
        for note in notes_to_tag:
            field_content = note.fields[source_field]
            matches = pattern.findall(field_content)
            
            if not matches:
                continue
            
            # Extract tags from matches
            extracted_tags = []
            for match in matches:
                # Handle both tuple (multiple groups) and string (single group) matches
                if isinstance(match, tuple):
                    for group in match:
                        if group:  # Skip empty groups
                            extracted_tags.append(f"{tag_prefix}{group}")
                else:
                    extracted_tags.append(f"{tag_prefix}{match}")
            
            # Add tags to note
            original_tags = set(note.tags)
            note.tags = list(set(note.tags) | set(extracted_tags))
            
            # Only record a change if tags were actually added
            if len(note.tags) > len(original_tags):
                tags_added += len(note.tags) - len(original_tags)
                notes_tagged += 1
                changes.append(Change.note_tags_updated(note, model.id))
        
        return OperationResult(
            success=True,
            message=f"Added {tags_added} tags to {notes_tagged} notes",
            changes=changes
        ) 