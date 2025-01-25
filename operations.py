import logging
import json
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

from anki_types import Collection
from read_operations import ReadOperations
from write_operations import WriteOperations
from changelog import ChangeLog

logger = logging.getLogger('anki_inspector')

class OperationType(Enum):
    """Types of operations that can be performed."""
    # Read operations
    NUM_CARDS = ("num-cards", True)
    NUM_NOTES = ("num-notes", True)
    LIST_MODELS = ("list-models", True)
    LIST_TEMPLATES = ("list-templates", True)
    LIST_FIELDS = ("list-fields", True)
    PRINT_QUESTION = ("print-question", True)
    PRINT_ANSWER = ("print-answer", True)
    PRINT_CSS = ("print-css", True)
    NOTE_EXAMPLE = ("note-example", True)
    
    # Write operations
    RENAME_FIELD = ("rename-field", False)
    
    # Special operations
    RUN_ALL = ("run-all", True)  # This is a read-only operation that runs multiple read operations

    def __init__(self, value: str, is_read_only: bool):
        self._value_ = value
        self.is_read_only = is_read_only

@dataclass
class OperationRecipe:
    """Recipe for an operation to perform."""
    operation_type: OperationType
    model_name: Optional[str] = None
    template_name: Optional[str] = None
    old_field_name: Optional[str] = None
    new_field_name: Optional[str] = None

    @property
    def is_read_only(self) -> bool:
        """Whether this operation is read-only."""
        return self.operation_type.is_read_only

class UserOperations:
    """High-level operations available to users."""
    def __init__(self, collection: Collection, changelog: ChangeLog):
        self._read_ops = ReadOperations(collection)
        self._write_ops = WriteOperations(collection, changelog)

    @property
    def read_ops(self) -> ReadOperations:
        """Get read operations instance."""
        return self._read_ops

    @property
    def write_ops(self) -> WriteOperations:
        """Get write operations instance."""
        return self._write_ops

    def run(self, recipe: OperationRecipe) -> None:
        """Execute operation based on the recipe and format output."""
        logger.info(f"Running operation: {recipe.operation_type.value}")
        
        if recipe.operation_type == OperationType.NUM_CARDS:
            result = self._read_ops.num_cards()
            print(result)

        elif recipe.operation_type == OperationType.NUM_NOTES:
            result = self._read_ops.num_notes(recipe.model_name)
            if recipe.model_name:
                print(result)
            else:
                print(json.dumps(result, indent=2))

        elif recipe.operation_type == OperationType.LIST_FIELDS:
            fields = self._read_ops.list_fields(recipe.model_name)
            print(json.dumps(fields, indent=2))

        elif recipe.operation_type == OperationType.LIST_MODELS:
            models = self._read_ops.list_models()
            print(json.dumps(models, indent=2))

        elif recipe.operation_type == OperationType.LIST_TEMPLATES:
            templates = self._read_ops.list_templates(recipe.model_name)
            print(json.dumps(templates, indent=2))

        elif recipe.operation_type == OperationType.PRINT_QUESTION:
            question = self._read_ops.get_question_format(recipe.model_name, recipe.template_name)
            print(question)

        elif recipe.operation_type == OperationType.PRINT_ANSWER:
            answer = self._read_ops.get_answer_format(recipe.model_name, recipe.template_name)
            print(answer)

        elif recipe.operation_type == OperationType.PRINT_CSS:
            css = self._read_ops.get_css(recipe.model_name)
            print(css)

        elif recipe.operation_type == OperationType.NOTE_EXAMPLE:
            example = self._read_ops.get_note_example(recipe.model_name)
            print(json.dumps(example, indent=2))

        elif recipe.operation_type == OperationType.RENAME_FIELD:
            if not recipe.old_field_name or not recipe.new_field_name:
                raise ValueError("Both old_field_name and new_field_name must be specified for rename_field operation")
            self._write_ops.rename_field(recipe.model_name, recipe.old_field_name, recipe.new_field_name)
            print(f"Renamed field '{recipe.old_field_name}' to '{recipe.new_field_name}'")

        elif recipe.operation_type == OperationType.RUN_ALL:
            self.run(OperationRecipe(OperationType.NUM_CARDS))
            self.run(OperationRecipe(OperationType.LIST_MODELS))
            self.run(OperationRecipe(OperationType.LIST_TEMPLATES, recipe.model_name))
            self.run(OperationRecipe(OperationType.LIST_FIELDS, recipe.model_name))
            self.run(OperationRecipe(OperationType.PRINT_QUESTION, recipe.model_name, recipe.template_name))
            self.run(OperationRecipe(OperationType.PRINT_ANSWER, recipe.model_name, recipe.template_name))
            self.run(OperationRecipe(OperationType.PRINT_CSS, recipe.model_name))
            self.run(OperationRecipe(OperationType.NOTE_EXAMPLE, recipe.model_name))
