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
from arg_parser import parse_script_line
from script_manager import ScriptManager
from config_manager import ConfigManager

logger = logging.getLogger('anki_inspector')

class UserOperationParser:
    """Parse user inputs into an operation plan."""
    def __init__(self, builtin_configs_dir: Optional[Path] = None, builtin_templates_dir: Optional[Path] = None):
        self.script_manager = ScriptManager()
        self.config_manager = ConfigManager(
            builtin_configs_dir=builtin_configs_dir,
            builtin_templates_dir=builtin_templates_dir
        )

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
            return OperationPlan(
                operations=operations,
                output_path=None,
                read_only=True
            )

        # For all other operations
        # Validate required fields based on operation type
        self._validate_required_fields(user_recipe)
        
        # Validate output path for write operations
        if not user_recipe.operation_type.is_read_only and not output_path:
            raise ValueError("Output path must be specified for write operations")

        # Convert to operation recipe
        operation = self._convert_to_operation_recipe(user_recipe)
        
        return OperationPlan(
            operations=[operation],
            output_path=output_path,
            read_only=user_recipe.operation_type.is_read_only
        )

    def parse_from_args(self, args) -> OperationPlan:
        """Parse command line arguments into an operation plan."""
        # Handle script file if provided
        if args.command == UserOperationType.RUN_SCRIPT:
            if not args.script_file:
                raise ValueError("Must specify script-file for run-script operation")
                
            # Resolve script path using ScriptManager
            try:
                script_path = self.script_manager.resolve_script_path(str(args.script_file))
            except ValueError as e:
                raise ValueError(f"Script file error: {str(e)}")
            
            if not script_path.exists():
                raise ValueError(f"Script file not found: {script_path}")
            
            # Read and parse script file
            operations = []
            read_only = True
            with open(script_path) as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        line_args = parse_script_line(line)
                        if line_args:
                            # Load config if specified in the line
                            config_args = {}
                            if line_args.config:
                                try:
                                    config_path = self.config_manager.resolve_config_path(str(line_args.config))
                                    config_args = self.config_manager.load_config(str(config_path))
                                except ValueError as e:
                                    raise ValueError(f"Configuration error at line {line_num}: {str(e)}")

                            # Parse into operation recipe
                            line_recipe = UserOperationRecipe(
                                operation_type=line_args.command,
                                model_name=line_args.model or config_args.get('model_name'),
                                template_name=line_args.template or config_args.get('template_name'),
                                old_field_name=line_args.old_field or config_args.get('old_field_name'),
                                new_field_name=line_args.new_field or config_args.get('new_field_name'),
                                fields=json.loads(line_args.fields) if line_args.fields else config_args.get('fields'),
                                question_format=line_args.question_format or config_args.get('question_format'),
                                answer_format=line_args.answer_format or config_args.get('answer_format'),
                                css=line_args.css or config_args.get('css'),
                                batch_size=line_args.batch_size or config_args.get('batch_size'),
                                populator_class=line_args.populator_class or config_args.get('populator_class'),
                                populator_config=line_args.populator_config or config_args.get('populator_config'),
                                target_model_name=line_args.target_model or config_args.get('target_model_name'),
                                field_mapping=line_args.field_mapping or config_args.get('field_mapping')
                            )
                            operation = self._convert_to_operation_recipe(line_recipe)
                            operations.append(operation)
                            # Update read_only status
                            if not line_recipe.operation_type.is_read_only:
                                read_only = False
                    except Exception as e:
                        raise ValueError(f"Error in script file at line {line_num}: {str(e)}")
            
            return OperationPlan(
                operations=operations,
                output_path=Path(args.output) if args.output else None,
                read_only=read_only
            )

        # Load config file if provided
        config_args = {}
        if args.config:
            try:
                # Try to resolve config path using ConfigManager
                config_path = self.config_manager.resolve_config_path(str(args.config))
                config_args = self.config_manager.load_config(str(config_path))
            except ValueError as e:
                raise ValueError(f"Configuration error: {str(e)}")

        # Create operation recipe from command line args, using config values as fallback
        user_recipe = UserOperationRecipe(
            operation_type=args.command,
            model_name=args.model or config_args.get('model_name'),
            template_name=args.template or config_args.get('template_name'),
            old_field_name=args.old_field or config_args.get('old_field_name'),
            new_field_name=args.new_field or config_args.get('new_field_name'),
            fields=json.loads(args.fields) if args.fields else config_args.get('fields'),
            question_format=args.question_format or config_args.get('question_format'),
            answer_format=args.answer_format or config_args.get('answer_format'),
            css=args.css or config_args.get('css'),
            batch_size=args.batch_size or config_args.get('batch_size'),
            populator_class=args.populator_class or config_args.get('populator_class'),
            populator_config=args.populator_config or config_args.get('populator_config'),
            target_model_name=args.target_model or config_args.get('target_model_name'),
            field_mapping=args.field_mapping or config_args.get('field_mapping')
        )

        return self.parse(user_recipe, Path(args.output) if args.output else None)

    def _validate_required_fields(self, recipe: UserOperationRecipe):
        """Validate that all required fields are provided for the operation type."""
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
