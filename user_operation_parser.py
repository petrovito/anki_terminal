import logging
import json
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path

from anki_types import Collection
from read_operations import ReadOperations
from write_operations import WriteOperations
from changelog import ChangeLog
from operation_executor import OperationExecutor
from operation_models import UserOperationRecipe, OperationPlan, OperationRecipe, UserOperationType, OperationType

logger = logging.getLogger('anki_inspector')

class UserOperationParser:
    """Parse user inputs into an operation plan."""
    def parse(self, user_recipe: UserOperationRecipe, output_path: Optional[Path] = None) -> OperationPlan:
        """Parse the user operation recipe into an operation plan.
        
        Args:
            user_recipe: The user operation recipe to parse
            output_path: Optional output path for write operations
            
        Returns:
            An operation plan ready for execution
            
        Raises:
            ValueError: If the recipe is invalid or missing required fields
        """
        logger.info(f"Parsing operation: {user_recipe.operation_type.value}")

        # Validate fields JSON if provided
        fields = None
        if user_recipe.fields is not None:
            if not isinstance(user_recipe.fields, list):
                raise ValueError("Fields must be a JSON array")
            fields = user_recipe.fields

        # Validate output path against operation type
        if not user_recipe.operation_type.is_read_only and not output_path:
            raise ValueError("Output path must be specified for write operations")

        # Validate required fields based on operation type
        self._validate_operation_fields(user_recipe)

        # Handle RUN_ALL operation type
        if user_recipe.operation_type == UserOperationType.RUN_ALL:
            operations = [
                # Basic read operations
                OperationRecipe(operation_type=OperationType.NUM_CARDS),
                OperationRecipe(operation_type=OperationType.NUM_NOTES),
                OperationRecipe(operation_type=OperationType.LIST_MODELS),
                # Model-specific operations (model names will be handled by executor)
                OperationRecipe(operation_type=OperationType.LIST_TEMPLATES),
                OperationRecipe(operation_type=OperationType.LIST_FIELDS),
                OperationRecipe(operation_type=OperationType.PRINT_CSS),
                OperationRecipe(operation_type=OperationType.NOTE_EXAMPLE),
                # Template-specific operations will be handled by executor
                OperationRecipe(operation_type=OperationType.PRINT_QUESTION),
                OperationRecipe(operation_type=OperationType.PRINT_ANSWER)
            ]
            return OperationPlan(operations=operations)
        
        # For all other operations, convert and return a single operation
        operation_recipe = self._convert_to_operation_recipe(user_recipe)
        return OperationPlan(operations=[operation_recipe])

    def _validate_operation_fields(self, recipe: UserOperationRecipe) -> None:
        """Validate that all required fields are present for the given operation type."""
        op_type = recipe.operation_type

        if op_type == UserOperationType.ADD_MODEL:
            if not recipe.model_name or not recipe.fields or not recipe.template_name:
                raise ValueError("Must specify model_name, fields, and template_name for add-model operation")

        elif op_type == UserOperationType.RENAME_FIELD:
            if not recipe.old_field_name or not recipe.new_field_name:
                raise ValueError("Must specify old_field_name and new_field_name for rename-field operation")

        elif op_type == UserOperationType.ADD_FIELD:
            if not recipe.model_name or not recipe.field_name:
                raise ValueError("Must specify model_name and field_name for add-field operation")

        elif op_type == UserOperationType.MIGRATE_NOTES:
            if not recipe.model_name or not recipe.target_model_name or not recipe.field_mapping:
                raise ValueError("Must specify model_name, target_model_name, and field_mapping for migrate-notes operation")
            try:
                json.loads(recipe.field_mapping)
            except json.JSONDecodeError:
                raise ValueError("field_mapping must be a valid JSON string")

        elif op_type == UserOperationType.POPULATE_FIELDS:
            if not recipe.model_name or not recipe.populator_class or not recipe.populator_config:
                raise ValueError("Must specify model_name, populator_class, and populator_config for populate-fields operation")

    def _convert_to_operation_recipe(self, user_recipe: UserOperationRecipe) -> OperationRecipe:
        """Convert a UserOperationRecipe to an OperationRecipe."""
        # Convert UserOperationType to OperationType
        operation_type = OperationType[user_recipe.operation_type.name]
        
        return OperationRecipe(
            operation_type=operation_type,
            model_name=user_recipe.model_name,
            template_name=user_recipe.template_name,
            old_field_name=user_recipe.old_field_name,
            new_field_name=user_recipe.new_field_name,
            field_name=user_recipe.field_name,
            target_model_name=user_recipe.target_model_name,
            field_mapping=user_recipe.field_mapping,
            fields=user_recipe.fields,
            question_format=user_recipe.question_format,
            answer_format=user_recipe.answer_format,
            css=user_recipe.css,
            populator_class=user_recipe.populator_class,
            populator_config=user_recipe.populator_config,
            batch_size=user_recipe.batch_size
        )
