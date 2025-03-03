#!/usr/bin/env python3

import logging
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum, auto
from anki_terminal.anki_types import Model, Note

logger = logging.getLogger('anki_inspector')

class ChangeType(Enum):
    """Types of changes that can be made."""
    MODEL_UPDATED = auto()  # Model structure changed (fields, templates, etc)
    NOTE_FIELDS_UPDATED = auto()  # Note field values changed
    NOTE_MIGRATED = auto()  # Note moved to different model

@dataclass
class Change:
    """Represents a single change in the collection."""
    type: ChangeType
    data: Dict[str, Any]

class ChangeLog:
    """Tracks changes made to the collection."""
    
    def __init__(self):
        self.changes: List[Change] = []

    def add_model_change(self, models: Dict[int, Model]) -> None:
        """Record a change to models."""
        self.changes.append(Change(
            type=ChangeType.MODEL_UPDATED,
            data={
                'models': {
                    str(model_id): model.to_dict()
                    for model_id, model in models.items()
                }
            }
        ))

    def add_note_fields_change(self, note: Note, model: Model) -> None:
        """Record a change to note fields."""
        self.changes.append(Change(
            type=ChangeType.NOTE_FIELDS_UPDATED,
            data={
                'note_id': note.id,
                'model_id': model.id,
                'fields': note.fields
            }
        ))

    def add_note_migration_change(self, source_model: Model, target_model: Model, note: Note) -> None:
        """Record a note migration between models."""
        self.changes.append(Change(
            type=ChangeType.NOTE_MIGRATED,
            data={
                'note_id': note.id,
                'source_model_id': source_model.id,
                'target_model_id': target_model.id,
                'fields': note.fields
            }
        ))

    def has_changes(self) -> bool:
        """Check if there are any pending changes."""
        return len(self.changes) > 0 