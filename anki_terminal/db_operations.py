import json
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from anki_terminal.changelog import Change, ChangeType


class DBOperationType(Enum):
    """Types of database operations."""
    UPDATE_MODEL = auto()
    UPDATE_NOTE = auto()
    UPDATE_NOTE_MODEL = auto()

@dataclass
class DBOperation:
    """Represents a single database operation."""
    type: DBOperationType
    table: str
    where: Dict[str, Any]  # Conditions
    values: Dict[str, Any]  # New values
    metadata: Optional[Dict[str, Any]] = None  # Version-specific metadata

class DBOperationGenerator:
    """Base class for generating database operations from changes."""
    
    # The field separator is the same for both Anki v2 and v21
    FIELD_SEPARATOR = '\x1f'
    
    def generate_operations(self, change: Change) -> List[DBOperation]:
        """Generate database operations from a change.
        
        Args:
            change: The change to generate operations for
            
        Returns:
            List of database operations
            
        Raises:
            ValueError: If the change type is not supported
        """
        if change.type == ChangeType.MODEL_UPDATED:
            return self._generate_model_update(change)
        elif change.type == ChangeType.NOTE_FIELDS_UPDATED:
            return self._generate_note_update(change)
        elif change.type == ChangeType.NOTE_MIGRATED:
            return self._generate_note_migration(change)
        elif change.type == ChangeType.NOTE_TAGS_UPDATED:
            return self._generate_note_tags_update(change)
        else:
            raise ValueError(f"Unsupported change type: {change.type}")

    def _generate_model_update(self, change: Change) -> List[DBOperation]:
        """Generate operations for model updates."""
        return [DBOperation(
            type=DBOperationType.UPDATE_MODEL,
            table='col',
            where={'id': 1},  # col table always has id=1
            values={'models': json.dumps(change.data['models'])},
            metadata={'field_separator': self.FIELD_SEPARATOR}
        )]

    def _generate_note_update(self, change: Change) -> List[DBOperation]:
        """Generate operations for note field updates."""
        fields_str = self.FIELD_SEPARATOR.join(str(v) for v in change.data['fields'].values())
        return [DBOperation(
            type=DBOperationType.UPDATE_NOTE,
            table='notes',
            where={'id': change.data['note_id']},
            values={'flds': fields_str},
            metadata={'field_separator': self.FIELD_SEPARATOR}
        )]

    def _generate_note_migration(self, change: Change) -> List[DBOperation]:
        """Generate operations for note migration."""
        fields_str = self.FIELD_SEPARATOR.join(str(v) for v in change.data['fields'].values())
        return [DBOperation(
            type=DBOperationType.UPDATE_NOTE_MODEL,
            table='notes',
            where={'id': change.data['note_id']},
            values={
                'mid': change.data['target_model_id'],
                'flds': fields_str
            },
            metadata={'field_separator': self.FIELD_SEPARATOR}
        )]

    def _generate_note_tags_update(self, change: Change) -> List[DBOperation]:
        """Generate operations for note tags update."""
        note_id = change.data['note_id']
        tags = change.data['tags']
        tags_str = ' '.join(tags)
        return [DBOperation(
            type=DBOperationType.UPDATE_NOTE,
            table='notes',
            where={'id': note_id},
            values={'tags': tags_str},
            metadata={'field_separator': self.FIELD_SEPARATOR}
        )] 