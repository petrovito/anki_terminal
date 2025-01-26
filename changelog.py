#!/usr/bin/env python3

import logging
import json
from dataclasses import dataclass
from typing import Any, Dict, List
from enum import Enum, auto
from anki_types import Model, Collection, Note

logger = logging.getLogger('anki_inspector')

class ChangeType(Enum):
    """Types of changes that can be made."""
    UPDATE_NOTE_FIELD = auto()
    UPDATE_MODEL_FIELD = auto()
    ADD_MODEL = auto()
    MIGRATE_NOTES = auto()

@dataclass
class Change:
    """Represents a single change in the database."""
    type: ChangeType
    table: str
    where: Dict[str, Any]  # Conditions to identify the record
    updates: Dict[str, Any]  # New values to set
    
class ChangeLog:
    """Tracks changes to be applied to the database."""
    def __init__(self):
        self.changes: List[Change] = []
        
    def add_change(self, change: Change):
        """Add a change to the log."""
        logger.debug(f"Adding change to log: {change}")
        self.changes.append(change)

    def add_model_change(self, models: Dict[int, Model]):
        """Add a change to update models in the collection.
        
        Args:
            models: Dictionary mapping model IDs to Model objects
        
        This creates a change that updates the entire models JSON in the collection table,
        since models are stored as a single JSON column.
        """
        models_dict = {str(model_id): model.to_dict() for model_id, model in models.items()}
        self.add_change(Change(
            type=ChangeType.UPDATE_MODEL_FIELD,
            table='col',
            where={'id': 1},  # col table always has id=1
            updates={'models': json.dumps(models_dict)}
        ))

    def add_note_fields_change(self, note: Note, model: Model):
        """Add a change to update a note's fields.
        
        Args:
            note: The note to update
            model: The model this note belongs to, used for field ordering
        """
        # Create ordered list of field values
        field_values = [note.fields[field] for field in model.fields]
        
        # Add change to update note fields
        self.add_change(Change(
            type=ChangeType.UPDATE_NOTE_FIELD,
            table='notes',
            where={'id': note.id},
            updates={'flds': '\x1f'.join(str(v) for v in field_values)}
        ))
            
    def add_note_migration_change(self, source_model: Model, target_model: Model, note: Note):
        """Add a change to migrate a note from one model to another.
        
        Args:
            source_model: The model to migrate from
            target_model: The model to migrate to
            note: The note being migrated
        """
        # Create ordered list of field values for target model
        field_values = [note.fields[field] for field in target_model.fields]
        
        # Add change to migrate note
        self.add_change(Change(
            type=ChangeType.MIGRATE_NOTES,
            table='notes',
            where={'mid': source_model.id},
            updates={
                'mid': target_model.id,
                'flds': '\x1f'.join(str(v) for v in field_values)
            }
        ))
            
    def clear(self):
        """Clear all changes from the log."""
        self.changes = [] 