import logging
from enum import Enum
from typing import Dict, Optional
from anki_types import Collection, Model, Template

logger = logging.getLogger('anki_inspector')

class OperationType(Enum):
    NUM_CARDS = 'num_cards'
    LIST_FIELDS = 'list_fields'
    LIST_MODELS = 'list_models'
    LIST_TEMPLATES = 'list_templates'
    PRINT_TEMPLATE = 'print_template'
    PRINT_QUESTION = 'print_question'
    PRINT_ANSWER = 'print_answer'
    PRINT_CSS = 'print_css'
    RUN_ALL = 'run_all'

class OperationRecipe:
    def __init__(self, operation_type: OperationType, model_name: str = None, template_name: str = None):
        self.operation_type = operation_type
        self.model_name = model_name
        self.template_name = template_name

class Operations:
    def __init__(self, collection: Collection):
        self.collection = collection

    def _get_model(self, model_name: Optional[str] = None) -> Model:
        """Get a model by name or return the only model if there's just one."""
        if model_name:
            # Find model by name
            for model in self.collection.models.values():
                if model.name == model_name:
                    return model
            raise ValueError(f"Model not found: {model_name}")
        
        # No model specified
        if len(self.collection.models) == 1:
            return next(iter(self.collection.models.values()))
        
        model_names = [model.name for model in self.collection.models.values()]
        raise ValueError(
            f"Multiple models found, please specify one: {', '.join(model_names)}"
        )

    def num_cards(self) -> None:
        """Print the total number of cards in the collection."""
        logger.debug("Counting total number of cards")
        result = len(self.collection.cards)
        print(result)

    def list_fields(self, model_name: Optional[str] = None) -> None:
        """Print fields for a specific model or the only model if there's just one."""
        logger.debug(f"Listing fields for model: {model_name if model_name else 'default'}")
        
        model = self._get_model(model_name)
        fields = [f"{field}:text" for field in model.fields]
        print(', '.join(fields))

    def _get_template(self, model_name: Optional[str] = None, template_name: Optional[str] = None) -> Template:
        """Get a template from a model, handling multiple template cases."""
        model = self._get_model(model_name)
        
        if template_name:
            # Find template by name
            for template in model.templates:
                if template.name == template_name:
                    return template
            raise ValueError(f"Template not found: {template_name}")
        
        # No template specified
        if len(model.templates) > 1:
            template_names = [t.name for t in model.templates]
            raise ValueError(
                f"Multiple templates found in model {model.name}, please specify one: {', '.join(template_names)}"
            )
        
        return model.templates[0]

    def print_question(self, model_name: Optional[str] = None, template_name: Optional[str] = None) -> None:
        """Print the question format for the specified model and template."""
        logger.debug(f"Getting question format for model: {model_name if model_name else 'default'}, "
                    f"template: {template_name if template_name else 'default'}")
        template = self._get_template(model_name, template_name)
        print(template.question_format)

    def print_answer(self, model_name: Optional[str] = None, template_name: Optional[str] = None) -> None:
        """Print the answer format for the specified model and template."""
        logger.debug(f"Getting answer format for model: {model_name if model_name else 'default'}, "
                    f"template: {template_name if template_name else 'default'}")
        template = self._get_template(model_name, template_name)
        print(template.answer_format)

    def print_css(self, model_name: Optional[str] = None) -> None:
        """Print the CSS for the specified model."""
        logger.debug(f"Getting CSS for model: {model_name if model_name else 'default'}")
        model = self._get_model(model_name)
        print(model.css)

    def print_template(self, model_name: Optional[str] = None) -> None:
        """Print all template details (for backwards compatibility)."""
        logger.debug(f"Getting template for model: {model_name if model_name else 'default'}")
        
        template = self._get_template(model_name)
        model = self._get_model(model_name)
        
        output = []
        output.append("Question Format:")
        output.append(template.question_format)
        output.append("\nAnswer Format:")
        output.append(template.answer_format)
        output.append("\nCSS:")
        output.append(model.css)
        print("\n".join(output))

    def list_models(self) -> None:
        """Print all models/note types with their basic information."""
        logger.debug("Listing all models/note types")
        
        for model_id, model in self.collection.models.items():
            model_type = "Standard" if model.type == 0 else "Cloze"
            print(f"{model.name} (ID: {model_id}, Type: {model_type})")

    def list_templates(self, model_name: Optional[str] = None) -> None:
        """List all templates for a specific model."""
        logger.debug(f"Listing templates for model: {model_name if model_name else 'default'}")
        
        model = self._get_model(model_name)
        for template in model.templates:
            print(f"{template.name} (ord: {template.ordinal})")

    def run(self, recipe: OperationRecipe) -> None:
        """Execute operation based on the recipe."""
        logger.info(f"Running operation: {recipe.operation_type.value}")
        
        if recipe.operation_type == OperationType.NUM_CARDS:
            self.num_cards()
        elif recipe.operation_type == OperationType.LIST_FIELDS:
            self.list_fields(recipe.model_name)
        elif recipe.operation_type == OperationType.LIST_MODELS:
            self.list_models()
        elif recipe.operation_type == OperationType.LIST_TEMPLATES:
            self.list_templates(recipe.model_name)
        elif recipe.operation_type == OperationType.PRINT_TEMPLATE:
            self.print_template(recipe.model_name)
        elif recipe.operation_type == OperationType.PRINT_QUESTION:
            self.print_question(recipe.model_name, recipe.template_name)
        elif recipe.operation_type == OperationType.PRINT_ANSWER:
            self.print_answer(recipe.model_name, recipe.template_name)
        elif recipe.operation_type == OperationType.PRINT_CSS:
            self.print_css(recipe.model_name)
        elif recipe.operation_type == OperationType.RUN_ALL:
            self.run(OperationRecipe(OperationType.NUM_CARDS))
            self.run(OperationRecipe(OperationType.LIST_MODELS))
            self.run(OperationRecipe(OperationType.LIST_TEMPLATES, recipe.model_name))
            self.run(OperationRecipe(OperationType.LIST_FIELDS, recipe.model_name))
            self.run(OperationRecipe(OperationType.PRINT_QUESTION, recipe.model_name, recipe.template_name))
            self.run(OperationRecipe(OperationType.PRINT_ANSWER, recipe.model_name, recipe.template_name))
            self.run(OperationRecipe(OperationType.PRINT_CSS, recipe.model_name))
