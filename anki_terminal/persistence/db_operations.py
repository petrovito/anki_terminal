import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from anki_terminal.commons.changelog import Change, ChangeType


@dataclass
class DBOperation:
    """Represents a single database operation."""
    table: str
    where: Dict[str, Any]  # Conditions
    values: Dict[str, Any]  # New values

class DBOperationGenerator:
    """Class for generating database operations from changes."""
    
    # Anki uses the unit separator character (ASCII 31) to separate fields
    FIELD_SEPARATOR = '\u001f'
    
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
        elif change.type == ChangeType.CARD_MOVED:
            return self._generate_card_move(change)
        elif change.type == ChangeType.DECK_CREATED:
            return self._generate_deck_created(change)
        else:
            raise ValueError(f"Unsupported change type: {change.type}")

    def _generate_model_update(self, change: Change) -> List[DBOperation]:
        """Generate operations for model updates."""
        return [DBOperation(
            table='col',
            where={'id': 1},  # col table always has id=1
            values={'models': json.dumps(change.data['models'])}
        )]

    def _generate_note_update(self, change: Change) -> List[DBOperation]:
        """Generate operations for note field updates."""
        fields_str = self.FIELD_SEPARATOR.join(str(v) for v in change.data['fields'].values())
        return [DBOperation(
            table='notes',
            where={'id': change.data['note_id']},
            values={'flds': fields_str}
        )]

    def _generate_note_migration(self, change: Change) -> List[DBOperation]:
        """Generate operations for note migration."""
        fields_str = self.FIELD_SEPARATOR.join(str(v) for v in change.data['fields'].values())
        return [DBOperation(
            table='notes',
            where={'guid': change.data['note_guid']},
            values={
                'mid': change.data['target_model_id'],
                'flds': fields_str
            }
        )]

    def _generate_note_tags_update(self, change: Change) -> List[DBOperation]:
        """Generate operations for note tags update."""
        note_id = change.data['note_id']
        tags = change.data['tags']
        tags_str = ' '.join(tags)
        return [DBOperation(
            table='notes',
            where={'id': note_id},
            values={'tags': tags_str}
        )]
    
    def _generate_card_move(self, change: Change) -> List[DBOperation]:
        """Generate operations for card move."""
        card_id = change.data['card_id']
        target_deck_id = change.data['target_deck_id']
        return [DBOperation(
            table='cards',
            where={'id': card_id},
            values={'did': target_deck_id}
        )]
    
    def _generate_deck_created(self, change: Change) -> List[DBOperation]:
        """Generate operations for deck creation."""
        return [DBOperation(
            table='col',
            where={'id': 1},  # col table always has id=1
            values={'decks': json.dumps(change.data['decks'])}
        )] 