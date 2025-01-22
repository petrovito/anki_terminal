import logging
from typing import Dict, List, Optional
from anki_types import Collection, Model, Template

logger = logging.getLogger('anki_inspector')

class ReadOperations:
    """Low-level read operations on the collection."""
    def __init__(self, collection: Collection):
        self.collection = collection

    def num_cards(self) -> int:
        """Get the total number of cards in the collection."""
        logger.debug("Counting total number of cards")
        return len(self.collection.cards)

    def list_fields(self, model_name: Optional[str] = None) -> List[dict]:
        """Get fields for a specific model."""
        logger.debug(f"Listing fields for model: {model_name if model_name else 'default'}")
        model = self._get_model(model_name)
        return [
            {
                "name": field,
                "type": "text"
            }
            for field in model.fields
        ]

    def list_models(self) -> List[dict]:
        """Get all models/note types with their basic information."""
        logger.debug("Listing all models/note types")
        return [
            {
                "name": model.name,
                "id": model_id,
                "type": "Standard" if model.type == 0 else "Cloze"
            }
            for model_id, model in self.collection.models.items()
        ]

    def list_templates(self, model_name: Optional[str] = None) -> List[dict]:
        """Get all templates for a specific model."""
        logger.debug(f"Listing templates for model: {model_name if model_name else 'default'}")
        model = self._get_model(model_name)
        return [
            {
                "name": template.name,
                "ordinal": template.ordinal
            }
            for template in model.templates
        ]

    def get_question_format(self, model_name: Optional[str] = None, template_name: Optional[str] = None) -> str:
        """Get the question format for the specified model and template."""
        logger.debug(f"Getting question format for model: {model_name if model_name else 'default'}, "
                    f"template: {template_name if template_name else 'default'}")
        template = self._get_template(model_name, template_name)
        return template.question_format

    def get_answer_format(self, model_name: Optional[str] = None, template_name: Optional[str] = None) -> str:
        """Get the answer format for the specified model and template."""
        logger.debug(f"Getting answer format for model: {model_name if model_name else 'default'}, "
                    f"template: {template_name if template_name else 'default'}")
        template = self._get_template(model_name, template_name)
        return template.answer_format

    def get_css(self, model_name: Optional[str] = None) -> str:
        """Get the CSS for the specified model."""
        logger.debug(f"Getting CSS for model: {model_name if model_name else 'default'}")
        model = self._get_model(model_name)
        return model.css

    # Helper methods
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