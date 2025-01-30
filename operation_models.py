from dataclasses import dataclass
from typing import Optional, List
from enum import Enum, auto

class UserOperationType(Enum):
    """Types of operations that can be performed by users."""
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
    ADD_FIELD = ("add-field", False)  # Added missing operation
    MIGRATE_NOTES = ("migrate-notes", False)
    POPULATE_FIELDS = ("populate-fields", False)  # New operation
    
    # Special operations
    RUN_ALL = ("run-all", True)  # This is a read-only operation that runs multiple read operations

    def __init__(self, value: str, is_read_only: bool):
        self._value_ = value
        self.is_read_only = is_read_only

class OperationType(Enum):
    """Types of operations that can be executed internally."""
    # Read operations
    NUM_CARDS = (auto(), True)
    NUM_NOTES = (auto(), True)
    LIST_MODELS = (auto(), True)
    LIST_TEMPLATES = (auto(), True)
    LIST_FIELDS = (auto(), True)
    PRINT_QUESTION = (auto(), True)
    PRINT_ANSWER = (auto(), True)
    PRINT_CSS = (auto(), True)
    NOTE_EXAMPLE = (auto(), True)
    
    # Write operations
    RENAME_FIELD = (auto(), False)
    ADD_MODEL = (auto(), False)
    ADD_FIELD = (auto(), False)  # Added missing operation
    MIGRATE_NOTES = (auto(), False)
    POPULATE_FIELDS = (auto(), False)
    
    # Special operations
    RUN_ALL = (auto(), True)

    def __init__(self, value: int, is_read_only: bool):
        self._value_ = value
        self.is_read_only = is_read_only

@dataclass
class UserOperationRecipe:
    """Recipe for an operation to perform."""
    operation_type: UserOperationType
    model_name: Optional[str] = None  # Required for add-model and migrate-notes (source)
    template_name: Optional[str] = None  # Required for add-model and template operations
    old_field_name: Optional[str] = None  # Required for rename-field
    new_field_name: Optional[str] = None  # Required for rename-field
    field_name: Optional[str] = None  # Required for add-field
    target_model_name: Optional[str] = None  # Required for migrate-notes
    field_mapping: Optional[str] = None  # Required for migrate-notes
    fields: Optional[List[str]] = None  # Required for add-model
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

@dataclass
class OperationPlan:
    """Plan for executing a series of operations."""
    operations: List[UserOperationRecipe]

@dataclass
class OperationRecipe:
    """Represents an operation ready for execution."""
    operation_type: OperationType
    model_name: Optional[str] = None
    template_name: Optional[str] = None
    old_field_name: Optional[str] = None
    new_field_name: Optional[str] = None
    field_name: Optional[str] = None  # Required for add-field
    target_model_name: Optional[str] = None
    field_mapping: Optional[str] = None
    fields: Optional[List[str]] = None
    question_format: Optional[str] = None
    answer_format: Optional[str] = None
    css: Optional[str] = None
    populator_class: Optional[str] = None
    populator_config: Optional[str] = None
    batch_size: Optional[int] = None 