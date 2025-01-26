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
    ADD_MODEL = ("add-model", False)
    MIGRATE_NOTES = ("migrate-notes", False)
    POPULATE_FIELDS = ("populate-fields", False)  # New operation
    
    # Special operations
    RUN_ALL = ("run-all", True)  # This is a read-only operation that runs multiple read operations

    def __init__(self, value: str, is_read_only: bool):
        self._value_ = value
        self.is_read_only = is_read_only

@dataclass
class OperationRecipe:
    """Recipe for an operation to perform."""
    operation_type: OperationType
    model_name: Optional[str] = None  # Required for add-model and migrate-notes (source)
    template_name: Optional[str] = None  # Required for add-model and template operations
    old_field_name: Optional[str] = None  # Required for rename-field
    new_field_name: Optional[str] = None  # Required for rename-field
    target_model_name: Optional[str] = None  # Required for migrate-notes (target)
    field_mapping: Optional[str] = None  # Required for migrate-notes
    fields: Optional[list[str]] = None  # Required for add-model
    question_format: Optional[str] = None  # Required for add-model
    answer_format: Optional[str] = None  # Required for add-model
    css: Optional[str] = None  # Required for add-model
    populator_class: Optional[str] = None  # Required for populate-fields (e.g. "populators.copy_field.CopyFieldPopulator")
    populator_config: Optional[str] = None  # Required for populate-fields (path to JSON config file)
    batch_size: Optional[int] = None  # Optional for populate-fields, controls batch processing

    @property
    def is_read_only(self) -> bool:
        """Whether this operation is read-only."""
        return self.operation_type.is_read_only

class UserOperations:
    """High-level operations available to users."""
    def __init__(self, collection: Collection, changelog: ChangeLog):
        self._read_ops = ReadOperations(collection)
        self._write_ops = WriteOperations(collection)
        self._write_ops.changelog = changelog  # Use the same changelog instance

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

        elif recipe.operation_type == OperationType.ADD_MODEL:
            if not recipe.model_name:
                raise ValueError("Model name must be provided")
            if not recipe.fields:
                raise ValueError("Field list must be provided")
            if not recipe.template_name:
                raise ValueError("Template name must be provided")
            if not recipe.question_format:
                raise ValueError("Question format must be provided")
            if not recipe.answer_format:
                raise ValueError("Answer format must be provided")
            if not recipe.css:
                raise ValueError("CSS must be provided")
            
            self._write_ops.add_model(
                model_name=recipe.model_name,
                fields=recipe.fields,
                template_name=recipe.template_name,
                question_format=recipe.question_format,
                answer_format=recipe.answer_format,
                css=recipe.css
            )
            print(f"Added model '{recipe.model_name}' successfully")

        elif recipe.operation_type == OperationType.MIGRATE_NOTES:
            if not recipe.model_name:
                raise ValueError("Source model name must be provided")
            if not recipe.target_model_name:
                raise ValueError("Target model name must be provided")
            if not recipe.field_mapping:
                raise ValueError("Field mapping must be provided")
            self._write_ops.migrate_notes(recipe.model_name, recipe.target_model_name, recipe.field_mapping)
            print(f"Successfully migrated notes from '{recipe.model_name}' to '{recipe.target_model_name}'")

        elif recipe.operation_type == OperationType.POPULATE_FIELDS:
            if not recipe.model_name:
                raise ValueError("Model name must be provided")
            if not recipe.populator_class:
                raise ValueError("Populator class must be provided")
            if not recipe.populator_config:
                raise ValueError("Populator configuration must be provided")
            self._write_ops.populate_fields(
                model_name=recipe.model_name,
                populator_class=recipe.populator_class,
                config_path=recipe.populator_config,
                batch_size=recipe.batch_size
            )
            print(f"Successfully populated fields in model '{recipe.model_name}' using {recipe.populator_class} populator")

        elif recipe.operation_type == OperationType.RUN_ALL:
            self.run(OperationRecipe(OperationType.NUM_CARDS))
            self.run(OperationRecipe(OperationType.LIST_MODELS))
            self.run(OperationRecipe(OperationType.LIST_TEMPLATES, recipe.model_name))
            self.run(OperationRecipe(OperationType.LIST_FIELDS, recipe.model_name))
            self.run(OperationRecipe(OperationType.PRINT_QUESTION, recipe.model_name, recipe.template_name))
            self.run(OperationRecipe(OperationType.PRINT_ANSWER, recipe.model_name, recipe.template_name))
            self.run(OperationRecipe(OperationType.PRINT_CSS, recipe.model_name))
            self.run(OperationRecipe(OperationType.NOTE_EXAMPLE, recipe.model_name))
