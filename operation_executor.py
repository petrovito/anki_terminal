import logging
from typing import Optional
from operation_models import OperationType, OperationRecipe
from read_operations import ReadOperations
from write_operations import WriteOperations

logger = logging.getLogger('anki_inspector')

class OperationExecutor:
    """Execute operations based on operation recipes."""
    def __init__(self, read_ops: ReadOperations, write_ops: WriteOperations):
        self._read_ops = read_ops
        self._write_ops = write_ops

    def execute(self, recipe: OperationRecipe) -> None:
        """Execute an operation based on the recipe."""
        logger.info(f"Executing operation: {recipe.operation_type.value}")
        
        # Validate read-only mode
        if not recipe.operation_type.is_read_only and self._write_ops is None:
            raise RuntimeError("Cannot perform write operation in read-only mode")
        
        # Execute based on operation type
        if recipe.operation_type == OperationType.NUM_CARDS:
            print(self._read_ops.num_cards())
        elif recipe.operation_type == OperationType.NUM_NOTES:
            print(self._read_ops.num_notes())
        elif recipe.operation_type == OperationType.LIST_MODELS:
            models = self._read_ops.list_models()
            for model in models:
                print(f"{model['name']} ({model['type']})")
        elif recipe.operation_type == OperationType.LIST_TEMPLATES:
            templates = self._read_ops.list_templates(model_name=recipe.model_name)
            for template in templates:
                print(f"{template['name']} (ordinal: {template['ordinal']})")
        elif recipe.operation_type == OperationType.LIST_FIELDS:
            fields = self._read_ops.list_fields(model_name=recipe.model_name)
            for field in fields:
                print(field['name'])
        elif recipe.operation_type == OperationType.PRINT_QUESTION:
            question = self._read_ops.get_question_format(
                model_name=recipe.model_name,
                template_name=recipe.template_name
            )
            print(question)
        elif recipe.operation_type == OperationType.PRINT_ANSWER:
            answer = self._read_ops.get_answer_format(
                model_name=recipe.model_name,
                template_name=recipe.template_name
            )
            print(answer)
        elif recipe.operation_type == OperationType.PRINT_CSS:
            css = self._read_ops.get_css(model_name=recipe.model_name)
            print(css)
        elif recipe.operation_type == OperationType.NOTE_EXAMPLE:
            example = self._read_ops.get_note_example(model_name=recipe.model_name)
            for field, value in example.items():
                print(f"{field}: {value}")
        elif recipe.operation_type == OperationType.RENAME_FIELD:
            if not recipe.old_field_name or not recipe.new_field_name:
                raise ValueError("Must specify old_field_name and new_field_name for rename-field operation")
            self._write_ops.rename_field(recipe.model_name, recipe.old_field_name, recipe.new_field_name)
        elif recipe.operation_type == OperationType.ADD_MODEL:
            if not recipe.model_name or not recipe.fields or not recipe.template_name:
                raise ValueError("Must specify model_name, fields, and template_name for add-model operation")
            self._write_ops.add_model(
                model_name=recipe.model_name,
                fields=recipe.fields,
                template_name=recipe.template_name,
                question_format=recipe.question_format,
                answer_format=recipe.answer_format,
                css=recipe.css
            )
        elif recipe.operation_type == OperationType.ADD_FIELD:
            if not recipe.model_name or not recipe.field_name:
                raise ValueError("Must specify model_name and field_name for add-field operation")
            self._write_ops.add_field(
                model_name=recipe.model_name,
                field_name=recipe.field_name
            )
        elif recipe.operation_type == OperationType.MIGRATE_NOTES:
            if not recipe.model_name or not recipe.target_model_name or not recipe.field_mapping:
                raise ValueError("Must specify model_name, target_model_name, and field_mapping for migrate-notes operation")
            self._write_ops.migrate_notes(
                source_model_name=recipe.model_name,
                target_model_name=recipe.target_model_name,
                field_mapping_json=recipe.field_mapping
            )
        elif recipe.operation_type == OperationType.POPULATE_FIELDS:
            if not recipe.model_name or not recipe.populator_class or not recipe.populator_config:
                raise ValueError("Must specify model_name, populator_class, and populator_config for populate-fields operation")
            self._write_ops.populate_fields(
                model_name=recipe.model_name,
                populator_class=recipe.populator_class,
                populator_config=recipe.populator_config,
                batch_size=recipe.batch_size
            )
        else:
            raise ValueError(f"Unknown operation type: {recipe.operation_type}") 