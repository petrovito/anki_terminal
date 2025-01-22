import logging
import json
from typing import Optional
from anki_types import Collection
from changelog import ChangeLog, Change, ChangeType

logger = logging.getLogger('anki_inspector')

class WriteOperations:
    """Low-level write operations on the collection."""
    def __init__(self, collection: Collection):
        self.collection = collection
        self.changelog = ChangeLog()
    # To be implemented later 

    def rename_field(self, model_name: Optional[str], old_field_name: str, new_field_name: str) -> None:
        """Rename a field in a model and update all related notes. Does not update templates."""
        logger.debug(f"Renaming field '{old_field_name}' to '{new_field_name}' in model: {model_name if model_name else 'default'}")
        
        # Get the model using the same helper as read operations
        model = None
        if model_name:
            # Find model by name
            for m in self.collection.models.values():
                if m.name == model_name:
                    model = m
                    break
            if not model:
                raise ValueError(f"Model not found: {model_name}")
        else:
            # No model specified, use default if only one exists
            if len(self.collection.models) == 1:
                model = next(iter(self.collection.models.values()))
            else:
                model_names = [m.name for m in self.collection.models.values()]
                raise ValueError(f"Multiple models found, please specify one: {', '.join(model_names)}")

        # Check if old field exists and new field doesn't
        if old_field_name not in model.fields:
            raise ValueError(f"Field '{old_field_name}' not found in model '{model.name}'")
        if new_field_name in model.fields:
            raise ValueError(f"Field '{new_field_name}' already exists in model '{model.name}'")

        # Update field name in model and create changelog entry
        old_field_idx = model.fields.index(old_field_name)
        model.fields[old_field_idx] = new_field_name
        
        # Add model change to changelog
        # Models are stored as JSON in the 'models' column of the 'col' table
        models_dict = {str(model_id): model.to_dict() for model_id, model in self.collection.models.items()}
        self.changelog.add_change(Change(
            type=ChangeType.UPDATE_MODEL_FIELD,
            table='col',
            where={'id': 1},  # col table always has id=1
            updates={'models': json.dumps(models_dict)}
        ))

        # Update notes to use new field name
        for note in self.collection.notes:
            if note.model_id == model.id:
                # Create new fields dict with updated field name
                new_fields = {}
                for field_name, value in note.fields.items():
                    if field_name == old_field_name:
                        new_fields[new_field_name] = value
                    else:
                        new_fields[field_name] = value
                note.fields = new_fields
                
                # Add note change to changelog
                self.changelog.add_change(Change(
                    type=ChangeType.UPDATE_NOTE_FIELD,
                    table='notes',
                    where={'id': note.id},
                    updates={'flds': '\x1f'.join(str(v) for v in new_fields.values())}
                )) 