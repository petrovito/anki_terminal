import logging
from enum import Enum
from typing import Dict, Optional
from anki_types import Collection, Model, Template

logger = logging.getLogger('anki_inspector')

class OperationType(Enum):
    NUM_CARDS = 'num_cards'
    LIST_FIELDS = 'list_fields'
    PRINT_TEMPLATE = 'print_template'
    RUN_ALL = 'run_all'

class OperationRecipe:
    def __init__(self, operation_type: OperationType, model_name: str = None):
        self.operation_type = operation_type
        self.model_name = model_name

class Operations:
    def __init__(self, collection: Collection):
        self.collection = collection

    def num_cards(self) -> int:
        """Get the total number of cards in the collection."""
        logger.debug("Counting total number of cards")
        return len(self.collection.cards)

    def list_fields(self) -> Dict[str, list]:
        """List all fields from all note types."""
        logger.debug("Listing fields for all models")
        fields_by_model = {}
        for model_id, model in self.collection.models.items():
            fields_by_model[model.name] = model.fields
        return fields_by_model

    def print_template(self, model_name: Optional[str] = None) -> Dict[str, dict]:
        """Print the templates (card types) for the specified model or all models."""
        if model_name:
            logger.debug(f"Getting templates for model: {model_name}")
        else:
            logger.debug("Getting templates for all models")

        templates = {}
        for model_id, model in self.collection.models.items():
            if model_name is None or model.name == model_name:
                templates[model.name] = {
                    'templates': [t.name for t in model.templates],
                    'fields': model.fields
                }
        return templates

    def run(self, recipe: OperationRecipe) -> None:
        """Execute operation based on the recipe."""
        logger.info(f"Running operation: {recipe.operation_type.value}")
        
        if recipe.operation_type == OperationType.NUM_CARDS:
            result = self.num_cards()
            logger.info(f"Total number of cards: {result}")
            print(result)

        elif recipe.operation_type == OperationType.LIST_FIELDS:
            fields = self.list_fields()
            output = []
            for model_name, field_list in fields.items():
                output.append(f"{model_name}:")
                for field in field_list:
                    output.append(f"\t{field}")
            logger.info("Fields by model:\n" + "\n".join(output))
            print("\n".join(output))

        elif recipe.operation_type == OperationType.PRINT_TEMPLATE:
            templates = self.print_template(recipe.model_name)
            output = []
            for model_name, data in templates.items():
                output.append(f"{model_name}:")
                output.append("\tFields:")
                for field in data['fields']:
                    output.append(f"\t\t{field}")
                output.append("\tCard Types:")
                for template in data['templates']:
                    output.append(f"\t\t{template}")
            logger.info("Templates:\n" + "\n".join(output))
            print("\n".join(output))

        elif recipe.operation_type == OperationType.RUN_ALL:
            logger.info("Running all operations")
            self.run(OperationRecipe(OperationType.NUM_CARDS))
            self.run(OperationRecipe(OperationType.LIST_FIELDS))
            self.run(OperationRecipe(OperationType.PRINT_TEMPLATE)) 