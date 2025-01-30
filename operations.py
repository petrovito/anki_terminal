import logging
import json
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, List

from anki_types import Collection
from read_operations import ReadOperations
from write_operations import WriteOperations
from changelog import ChangeLog
from operation_executor import OperationExecutor
from operation_models import UserOperationRecipe, OperationPlan, OperationRecipe, UserOperationType, OperationType

logger = logging.getLogger('anki_inspector')

class UserOperationParser:
    """Parse user inputs into an operation plan."""
    def __init__(self):
        pass

    def parse(self, user_recipe: UserOperationRecipe) -> OperationPlan:
        """Parse the user operation recipe into an operation plan."""
        logger.info(f"Parsing operation: {user_recipe.operation_type.value}")
        # Convert UserOperationRecipe to OperationRecipe
        operation_recipe = self._convert_to_operation_recipe(user_recipe)
        # Create a plan with a single operation for now
        return OperationPlan(operations=[operation_recipe])

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
