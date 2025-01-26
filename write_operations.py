import logging
import json
import importlib
from typing import Optional, Dict
from anki_types import Collection, Model, Template
from changelog import ChangeLog, Change, ChangeType
import time
from datetime import datetime
from populators.base import FieldPopulator

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

    def populate_fields(self, model_name: str, populator_class: str, config_path: str) -> None:
        """Populate fields in notes using a field populator.
        
        Args:
            model_name: Name of the model to populate fields in
            populator_class: Full path to the populator class (e.g. "populators.copy_field.CopyFieldPopulator")
            config_path: Path to the JSON configuration file for the populator
        """
        # Find model by name
        model = None
        model_id = None
        for mid, m in self.collection.models.items():
            if m.name == model_name:
                model = m
                model_id = mid
                break
        if not model:
            raise ValueError(f"Model not found: {model_name}")
            
        # Import and instantiate the populator class
        try:
            module_path, class_name = populator_class.rsplit('.', 1)
            module = importlib.import_module(module_path)
            populator_cls = getattr(module, class_name)
            
            if not issubclass(populator_cls, FieldPopulator):
                raise ValueError(f"Class {populator_class} is not a subclass of FieldPopulator")
                
            populator = populator_cls(config_path)
            
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Could not load populator class {populator_class}: {str(e)}")
            
        # Process each note
        for note in self.collection.notes:
            if note.model_id == model_id:
                try:
                    # Get field updates from populator
                    updates = populator.populate_fields(note)
                    
                    # Verify target fields exist in model
                    invalid_fields = [f for f in updates.keys() if f not in model.fields]
                    if invalid_fields:
                        raise ValueError(f"Target fields not found in model: {invalid_fields}")
                    
                    # Update note fields
                    note.fields.update(updates)
                    
                    # Create ordered list of field values
                    field_values = [note.fields[field] for field in model.fields]
                    
                    # Add change to changelog
                    self.changelog.add_change(Change(
                        type=ChangeType.UPDATE_NOTE_FIELD,
                        table='notes',
                        where={'id': note.id},
                        updates={'flds': '\x1f'.join(str(v) for v in field_values)}
                    ))
                    
                except ValueError as e:
                    logger.warning(f"Skipping note {note.id}: {str(e)}")
                    continue
                    
        logger.info(f"Populated fields in notes for model '{model_name}' using {populator_class}")

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

    def add_model(self, model_name: str, fields: list[str], template_name: str,
                question_format: str, answer_format: str, css: str) -> None:
        """Add a new model with the given properties.
        
        Args:
            model_name: Name of the model to create
            fields: List of field names for the model
            template_name: Name of the template
            question_format: Format string for the question side
            answer_format: Format string for the answer side
            css: CSS styling for the cards
        """
        # Check if model name already exists
        for model in self.collection.models.values():
            if model.name == model_name:
                raise ValueError(f"Model already exists: {model_name}")

        # Generate model ID
        model_id = max(self.collection.models.keys(), default=1000000000) + 1

        # Get first available deck ID from collection
        deck_id = next(iter(self.collection.decks.keys()))

        # Create new model with provided values
        model = Model(
            id=model_id,
            name=model_name,
            fields=fields,
            templates=[
                Template(
                    name=template_name,
                    question_format=question_format,
                    answer_format=answer_format,
                    ordinal=0
                )
            ],
            css=css,
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

    def migrate_notes(self, source_model_name: str, target_model_name: str, field_mapping_json: str) -> None:
        """Migrate notes from one model to another using a field mapping.
        
        Args:
            source_model_name: Name of the model to migrate notes from
            target_model_name: Name of the model to migrate notes to
            field_mapping_json: JSON string mapping source fields to target fields.
                              Format: {"source_field1": "target_field1", ...}
        """
        # Parse field mapping
        try:
            field_mapping = json.loads(field_mapping_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid field mapping JSON: {e}")

        # Get source and target models
        source_model = None
        target_model = None
        for model in self.collection.models.values():
            if model.name == source_model_name:
                source_model = model
            elif model.name == target_model_name:
                target_model = model
        
        if not source_model:
            raise ValueError(f"Source model not found: {source_model_name}")
        if not target_model:
            raise ValueError(f"Target model not found: {target_model_name}")

        # Validate field mapping
        for source_field in field_mapping:
            if source_field not in source_model.fields:
                raise ValueError(f"Source field not found in {source_model_name}: {source_field}")
            if field_mapping[source_field] not in target_model.fields:
                raise ValueError(f"Target field not found in {target_model_name}: {field_mapping[source_field]}")

        # Check that mapping is injective (no duplicate target fields)
        target_fields = list(field_mapping.values())
        if len(target_fields) != len(set(target_fields)):
            raise ValueError("Field mapping must be injective (no duplicate target fields)")

        # Find notes using source model
        migrated_count = 0
        for note in self.collection.notes:
            if note.model_id == source_model.id:
                # Create new field values using mapping
                new_fields = {field: "" for field in target_model.fields}  # Initialize all fields empty
                for source_field, target_field in field_mapping.items():
                    new_fields[target_field] = note.fields[source_field]
                
                # Update note
                note.model_id = target_model.id
                note.fields = new_fields
                migrated_count += 1

        if migrated_count == 0:
            raise ValueError(f"No notes found for model: {source_model_name}")

        # Add change to changelog
        self.changelog.add_change(Change(
            type=ChangeType.MIGRATE_NOTES,
            table='notes',
            where={'mid': source_model.id},
            updates={
                'mid': target_model.id,
                'flds': '\x1f'.join(str(v) for v in new_fields.values())
            }
        ))