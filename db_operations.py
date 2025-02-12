import json
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from changelog import Change, ChangeType

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
    """Abstract base class for operation generators."""
    def generate_operations(self, change: Change) -> List[DBOperation]:
        raise NotImplementedError

class AnkiV2OperationGenerator(DBOperationGenerator):
    """Generates database operations for Anki v2 format."""
    
    def generate_operations(self, change: Change) -> List[DBOperation]:
        if change.type == ChangeType.MODEL_UPDATED:
            return self._generate_model_update(change)
        elif change.type == ChangeType.NOTE_FIELDS_UPDATED:
            return self._generate_note_update(change)
        elif change.type == ChangeType.NOTE_MIGRATED:
            return self._generate_note_migration(change)
        else:
            raise ValueError(f"Unsupported change type: {change.type}")

    def _generate_model_update(self, change: Change) -> List[DBOperation]:
        """Generate operations for model updates."""
        return [DBOperation(
            type=DBOperationType.UPDATE_MODEL,
            table='col',
            where={'id': 1},  # col table always has id=1
            values={'models': json.dumps(change.data['models'])},
            metadata={'field_separator': '\x1f'}
        )]

    def _generate_note_update(self, change: Change) -> List[DBOperation]:
        """Generate operations for note field updates."""
        fields_str = '\x1f'.join(str(v) for v in change.data['fields'].values())
        return [DBOperation(
            type=DBOperationType.UPDATE_NOTE,
            table='notes',
            where={'id': change.data['note_id']},
            values={'flds': fields_str},
            metadata={'field_separator': '\x1f'}
        )]

    def _generate_note_migration(self, change: Change) -> List[DBOperation]:
        """Generate operations for note migration."""
        fields_str = '\x1f'.join(str(v) for v in change.data['fields'].values())
        return [DBOperation(
            type=DBOperationType.UPDATE_NOTE_MODEL,
            table='notes',
            where={'id': change.data['note_id']},
            values={
                'mid': change.data['target_model_id'],
                'flds': fields_str
            },
            metadata={'field_separator': '\x1f'}
        )]

class AnkiV21OperationGenerator(DBOperationGenerator):
    """Generates database operations for Anki v21 format."""
    
    def generate_operations(self, change: Change) -> List[DBOperation]:
        if change.type == ChangeType.MODEL_UPDATED:
            return self._generate_model_update(change)
        elif change.type == ChangeType.NOTE_FIELDS_UPDATED:
            return self._generate_note_update(change)
        elif change.type == ChangeType.NOTE_MIGRATED:
            return self._generate_note_migration(change)
        else:
            raise ValueError(f"Unsupported change type: {change.type}")

    def _generate_model_update(self, change: Change) -> List[DBOperation]:
        """Generate operations for model updates."""
        return [DBOperation(
            type=DBOperationType.UPDATE_MODEL,
            table='col',
            where={'id': 1},  # col table always has id=1
            values={'models': json.dumps(change.data['models'])},
            metadata={'field_separator': '\t'}
        )]

    def _generate_note_update(self, change: Change) -> List[DBOperation]:
        """Generate operations for note field updates."""
        fields_str = '\t'.join(str(v) for v in change.data['fields'].values())
        return [DBOperation(
            type=DBOperationType.UPDATE_NOTE,
            table='notes',
            where={'id': change.data['note_id']},
            values={'flds': fields_str},
            metadata={'field_separator': '\t'}
        )]

    def _generate_note_migration(self, change: Change) -> List[DBOperation]:
        """Generate operations for note migration."""
        fields_str = '\t'.join(str(v) for v in change.data['fields'].values())
        return [DBOperation(
            type=DBOperationType.UPDATE_NOTE_MODEL,
            table='notes',
            where={'id': change.data['note_id']},
            values={
                'mid': change.data['target_model_id'],
                'flds': fields_str
            },
            metadata={'field_separator': '\t'}
        )] 