import logging
import json
from typing import Optional
from anki_types import Collection, Model, Template
from changelog import ChangeLog, Change, ChangeType
import time
from datetime import datetime

logger = logging.getLogger('anki_inspector')

class WriteOperations:
    """Low-level write operations on the collection."""
    def __init__(self, collection: Collection, changelog: ChangeLog):
        self.collection = collection
        self.changelog = changelog

    def _get_model(self, model_name: Optional[str]) -> Model:
        """Get a model by name or return the only model if there's just one."""
        if model_name:
            # Find model by name
            for model in self.collection.models.values():
                if model.name == model_name:
                    return model
            raise ValueError(f"Model not found: {model_name}")
        
        # No model specified, use default if only one exists
        if len(self.collection.models) == 1:
            return next(iter(self.collection.models.values()))
        
        model_names = [model.name for model in self.collection.models.values()]
        raise ValueError(f"Multiple models found, please specify one: {', '.join(model_names)}")

    def rename_field(self, model_name: Optional[str], old_field_name: str, new_field_name: str) -> None:
        """Rename a field in a model and update all related notes. Does not update templates."""
        logger.debug(f"Renaming field '{old_field_name}' to '{new_field_name}' in model: {model_name if model_name else 'default'}")
        model = self._get_model(model_name)        
        # Check if old field exists and new field doesn't
        if old_field_name not in model.fields:
            raise ValueError(f"Field '{old_field_name}' not found in model '{model.name}'")
        if new_field_name in model.fields:
            raise ValueError(f"Field '{new_field_name}' already exists in model '{model.name}'")

        # Update field name in model and create changelog entry
        old_field_idx = model.fields.index(old_field_name)
        model.fields[old_field_idx] = new_field_name

        # Update in-memory note field names
        for note in self.collection.notes:
            if note.model_id == model.id:
                new_fields = {}
                for field_name, value in note.fields.items():
                    if field_name == old_field_name:
                        new_fields[new_field_name] = value
                    else:
                        new_fields[field_name] = value
                note.fields = new_fields 

        # Add model change to changelog
        # Note: We don't need to update the database since note fields are stored as ordered values
        self.changelog.add_model_change()

    def add_model(self, model_name: str, model_id: Optional[int] = None) -> None:
        """Add a new model with the given name and optional ID.
        
        Args:
            model_name: Name of the model to create
            model_id: Optional ID for the model. If not provided, a new unique ID will be generated.
        """
        # Check if model name already exists
        for model in self.collection.models.values():
            if model.name == model_name:
                raise ValueError(f"Model already exists: {model_name}")

        # Generate model ID if not provided
        if model_id is None:
            # Find max ID and add 1, or use a random base number if no models exist
            model_id = max(self.collection.models.keys(), default=1000000000) + 1

        # Get first available deck ID from collection
        deck_id = next(iter(self.collection.decks.keys()))

        # Create new model with default values
        model = Model(
            id=model_id,
            name=model_name,
            fields=["Front", "Back"],  # Default fields
            templates=[
                Template(
                    name="Card 1",
                    question_format="{{Front}}",
                    answer_format="{{FrontSide}}\n<hr id=\"answer\">\n{{Back}}",
                    ordinal=0
                )
            ],
            css=".card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}",
            deck_id=deck_id,
            modification_time=datetime.now(),
            type=0,  # Standard (not cloze)
            usn=-1,  # -1 indicates needs sync
            version=1  # Start with version 1
        )

        # Add model to collection
        self.collection.models[model_id] = model

        # Add change to changelog
        # Create a dictionary of all models including the new one
        models_dict = {
            str(mid): m.to_dict() 
            for mid, m in self.collection.models.items()
        }
        
        # Add change to changelog
        self.changelog.add_change(Change(
            type=ChangeType.ADD_MODEL,
            table='col',
            where={'id': 1},  # Collection row ID is always 1
            updates={'models': json.dumps(models_dict)}
        ))