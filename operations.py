import logging
from typing import Dict, Optional
from anki_types import Collection, Model, Template

logger = logging.getLogger('anki_inspector')

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