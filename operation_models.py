from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
from enum import Enum
from ops.base import Operation

class UserOperationType(str, Enum):
    """User-facing operation types."""
    # Read operations
    NUM_CARDS = 'num-cards'
    NUM_NOTES = 'num-notes'
    LIST_MODELS = 'list-models'
    LIST_TEMPLATES = 'list-templates'
    LIST_FIELDS = 'list-fields'
    PRINT_QUESTION = 'print-question'
    PRINT_ANSWER = 'print-answer'
    PRINT_CSS = 'print-css'
    NOTE_EXAMPLE = 'note-example'
    
    # Write operations
    RENAME_FIELD = 'rename-field'
    ADD_MODEL = 'add-model'
    ADD_FIELD = 'add-field'
    MIGRATE_NOTES = 'migrate-notes'
    POPULATE_FIELDS = 'populate-fields'
    
    # Special operations
    RUN_ALL = 'run-all'
    RUN_SCRIPT = 'run-script'

    @property
    def is_read_only(self) -> bool:
        """Return True if this operation type is read-only."""
        return self in [
            UserOperationType.NUM_CARDS,
            UserOperationType.NUM_NOTES,
            UserOperationType.LIST_MODELS,
            UserOperationType.LIST_TEMPLATES,
            UserOperationType.LIST_FIELDS,
            UserOperationType.PRINT_QUESTION,
            UserOperationType.PRINT_ANSWER,
            UserOperationType.PRINT_CSS,
            UserOperationType.NOTE_EXAMPLE,
            UserOperationType.RUN_ALL,
            UserOperationType.RUN_SCRIPT  # Script is read-only if all its operations are
        ]

@dataclass
class UserOperationRecipe:
    """Recipe for executing a user operation."""
    operation_type: UserOperationType
    model_name: Optional[str] = None
    template_name: Optional[str] = None
    old_field_name: Optional[str] = None
    new_field_name: Optional[str] = None
    field_name: Optional[str] = None
    target_model_name: Optional[str] = None
    field_mapping: Optional[str] = None
    fields: Optional[List[str]] = None
    question_format: Optional[str] = None
    answer_format: Optional[str] = None
    css: Optional[str] = None
    populator_class: Optional[str] = None
    populator_config: Optional[str] = None
    batch_size: Optional[int] = None

@dataclass
class OperationPlan:
    """A plan of operations to execute."""
    operations: List[Operation]  # List of Operation objects to execute
    output_path: Optional[Path] = None
    read_only: bool = True  # True if all operations are read-only

    @property
    def has_write_operations(self) -> bool:
        """Return True if any operation in the plan is not read-only."""
        return any(not op.readonly for op in self.operations)
