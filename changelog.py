#!/usr/bin/env python3

import logging
import json
from dataclasses import dataclass
from typing import Any, Dict, List
from enum import Enum, auto
from anki_types import Model, Collection

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
    def __init__(self, collection: Collection):
        self.collection = collection
        self.changes: List[Change] = []
        
    def add_change(self, change: Change):
        """Add a change to the log."""
        logger.debug(f"Adding change to log: {change}")
        self.changes.append(change)

    def add_model_change(self):
        """Add a change to update models in the collection.
        
        This creates a change that updates the entire models JSON in the collection table,
        since models are stored as a single JSON column.
        """
        models_dict = {str(model_id): model.to_dict() for model_id, model in self.collection.models.items()}
        self.add_change(Change(
            type=ChangeType.UPDATE_MODEL_FIELD,
            table='col',
            where={'id': 1},  # col table always has id=1
            updates={'models': json.dumps(models_dict)}
        ))
            
    def clear(self):
        """Clear all changes from the log."""
        self.changes = [] 