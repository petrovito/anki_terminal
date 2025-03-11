#!/usr/bin/env python3

import json
import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from anki_terminal.commons.anki_types import Model, Note

logger = logging.getLogger('anki_inspector')

class ChangeType(Enum):
    """Types of changes that can be made."""
    MODEL_UPDATED = auto()  # Model structure changed (fields, templates, etc)
    NOTE_FIELDS_UPDATED = auto()  # Note field values changed
    NOTE_MIGRATED = auto()  # Note moved to different model
    NOTE_TAGS_UPDATED = auto()  # Note tags changed
    CARD_MOVED = auto()  # Card moved to different deck
    DECK_CREATED = auto()  # New deck created

@dataclass
class Change:
    """Represents a single change in the collection."""
    type: ChangeType
    data: Dict[str, Any]
    
    @staticmethod
    def model_updated(models: Dict[int, Model]) -> 'Change':
        """Create a change record for model updates.
        
        Args:
            models: Dictionary mapping model IDs to Model objects
            
        Returns:
            Change object representing the model update
        """
        return Change(
            type=ChangeType.MODEL_UPDATED,
            data={
                'models': {
                    str(model_id): model.to_dict()
                    for model_id, model in models.items()
                }
            }
        )
    
    @staticmethod
    def note_fields_updated(note: Note, model_id: int) -> 'Change':
        """Create a change record for note field updates.
        
        Args:
            note: The note with updated fields
            model_id: ID of the note's model
            
        Returns:
            Change object representing the note fields update
        """
        return Change(
            type=ChangeType.NOTE_FIELDS_UPDATED,
            data={
                'note_id': note.id,
                'model_id': model_id,
                'fields': note.fields
            }
        )
    
    @staticmethod
    def note_migrated(note: Note, source_model_id: int, target_model_id: int) -> 'Change':
        """Create a change record for note migration between models.
        
        Args:
            note: The migrated note
            source_model_id: ID of the source model
            target_model_id: ID of the target model
            
        Returns:
            Change object representing the note migration
        """
        return Change(
            type=ChangeType.NOTE_MIGRATED,
            data={
                'note_id': note.id,
                'source_model_id': source_model_id,
                'target_model_id': target_model_id,
                'fields': note.fields
            }
        )
    
    @staticmethod
    def note_tags_updated(note: Note, model_id: int) -> 'Change':
        """Create a change record for note tags updates.
        
        Args:
            note: The note with updated tags
            model_id: ID of the note's model
            
        Returns:
            Change object representing the note tags update
        """
        return Change(
            type=ChangeType.NOTE_TAGS_UPDATED,
            data={
                'note_id': note.id,
                'model_id': model_id,
                'tags': note.tags
            }
        )
    
    @staticmethod
    def card_moved(card_id: int, source_deck_id: int, target_deck_id: int) -> 'Change':
        """Create a change record for card movement between decks.
        
        Args:
            card_id: ID of the card being moved
            source_deck_id: ID of the source deck
            target_deck_id: ID of the target deck
            
        Returns:
            Change object representing the card movement
        """
        return Change(
            type=ChangeType.CARD_MOVED,
            data={
                'card_id': card_id,
                'source_deck_id': source_deck_id,
                'target_deck_id': target_deck_id
            }
        )
    
    @staticmethod
    def deck_created(decks: Dict[int, Any]) -> 'Change':
        """Create a change record for deck creation.
        
        Args:
            decks: Dictionary mapping deck IDs to deck objects
            
        Returns:
            Change object representing the deck creation
        """
        return Change(
            type=ChangeType.DECK_CREATED,
            data={
                'decks': decks
            }
        )

class ChangeLog:
    """Tracks changes made to the collection."""
    
    def __init__(self):
        self.changes: List[Change] = []
    
    def add_change(self, change: Change) -> None:
        """Add a change to the log.
        
        Args:
            change: The change to add
        """
        self.changes.append(change)
    
    def has_changes(self) -> bool:
        """Check if there are any pending changes."""
        return len(self.changes) > 0 