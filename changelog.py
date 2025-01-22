#!/usr/bin/env python3

import logging
from dataclasses import dataclass
from typing import Any, Dict, List
from enum import Enum, auto

logger = logging.getLogger('anki_inspector')

class ChangeType(Enum):
    """Types of changes that can be made to the database."""
    UPDATE_MODEL_FIELD = auto()  # Rename a field in a model
    UPDATE_TEMPLATE = auto()     # Update template content
    UPDATE_NOTE_FIELD = auto()   # Update a field in a note

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
            
    def clear(self):
        """Clear all changes from the log."""
        self.changes = [] 