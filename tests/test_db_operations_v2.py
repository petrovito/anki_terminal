import pytest
from datetime import datetime

from db_operations import (
    DBOperation, DBOperationType,
    AnkiV2OperationGenerator
)
from changelog import Change, ChangeType
from anki_types import Model, Field

@pytest.fixture
def sample_model() -> Model:
    """Fixture providing a sample model for testing."""
    return Model(
        id=1,
        name="Basic",
        fields=[
            Field(name="Front", ordinal=0),
            Field(name="Back", ordinal=1)
        ],
        templates=[],
        css="",
        deck_id=1,
        modification_time=datetime.now(),
        type=0,
        usn=-1,
        version=1
    )

@pytest.fixture
def model_change(sample_model) -> Change:
    """Fixture providing a model update change."""
    return Change(
        type=ChangeType.MODEL_UPDATED,
        data={
            'models': {
                '1': sample_model.to_dict()
            }
        }
    )

@pytest.fixture
def note_fields_change() -> Change:
    """Fixture providing a note fields update change."""
    return Change(
        type=ChangeType.NOTE_FIELDS_UPDATED,
        data={
            'note_id': 1,
            'model_id': 1,
            'fields': {
                'Front': 'New Front',
                'Back': 'New Back'
            }
        }
    )

@pytest.fixture
def note_migration_change() -> Change:
    """Fixture providing a note migration change."""
    return Change(
        type=ChangeType.NOTE_MIGRATED,
        data={
            'note_id': 1,
            'source_model_id': 1,
            'target_model_id': 2,
            'fields': {
                'Question': 'Front Content',
                'Answer': 'Back Content'
            }
        }
    )

class TestDBOperationV2:
    """Tests for the DBOperation class with v2 format."""
    
    def test_operation_creation(self):
        """Test creating a DB operation."""
        op = DBOperation(
            type=DBOperationType.UPDATE_MODEL,
            table='col',
            where={'id': 1},
            values={'models': '{}'},
            metadata={'field_separator': '\u001f'}
        )
        assert op.type == DBOperationType.UPDATE_MODEL
        assert op.table == 'col'
        assert op.where == {'id': 1}
        assert op.values == {'models': '{}'}
        assert op.metadata == {'field_separator': '\u001f'}

class TestAnkiV2OperationGenerator:
    """Tests for the AnkiV2OperationGenerator class."""
    
    def setup_method(self):
        self.generator = AnkiV2OperationGenerator()

    def test_model_update(self, model_change):
        """Test generating operations for model updates."""
        operations = self.generator.generate_operations(model_change)
        assert len(operations) == 1
        op = operations[0]
        assert op.type == DBOperationType.UPDATE_MODEL
        assert op.table == 'col'
        assert op.where == {'id': 1}
        assert isinstance(op.values['models'], str)  # Should be JSON string
        assert op.metadata['field_separator'] == '\u001f'

    def test_note_fields_update(self, note_fields_change):
        """Test generating operations for note field updates."""
        operations = self.generator.generate_operations(note_fields_change)
        assert len(operations) == 1
        op = operations[0]
        assert op.type == DBOperationType.UPDATE_NOTE
        assert op.table == 'notes'
        assert op.where == {'id': 1}
        assert '\u001f' in op.values['flds']  # Fields should be joined with separator
        assert op.metadata['field_separator'] == '\u001f'

    def test_note_migration(self, note_migration_change):
        """Test generating operations for note migrations."""
        operations = self.generator.generate_operations(note_migration_change)
        assert len(operations) == 1
        op = operations[0]
        assert op.type == DBOperationType.UPDATE_NOTE_MODEL
        assert op.table == 'notes'
        assert op.where == {'id': 1}
        assert 'mid' in op.values
        assert op.values['mid'] == 2  # Target model ID
        assert '\u001f' in op.values['flds']  # Fields should be joined with separator
        assert op.metadata['field_separator'] == '\u001f'

    def test_invalid_change_type(self):
        """Test handling of invalid change types."""
        invalid_change = Change(type="INVALID", data={})
        with pytest.raises(ValueError, match="Unsupported change type"):
            self.generator.generate_operations(invalid_change) 