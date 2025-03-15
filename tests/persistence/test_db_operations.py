from datetime import datetime

import pytest

from anki_terminal.commons.anki_types import Field, Model
from anki_terminal.commons.changelog import Change, ChangeType
from anki_terminal.persistence.db_operations import DBOperation, DBOperationGenerator


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
                'Front': 'Test front',
                'Back': 'Test back'
            }
        }
    )

@pytest.fixture
def note_migration_change() -> Change:
    """Fixture providing a note migration change."""
    return Change(
        type=ChangeType.NOTE_MIGRATED,
        data={
            'note_guid': 'test-guid',
            'source_model_id': 1,
            'target_model_id': 2,
            'fields': {
                'Question': 'Test front',
                'Answer': 'Test back'
            }
        }
    )

class TestDBOperation:
    """Tests for the DBOperation class."""
    
    def test_operation_creation(self):
        """Test creating a DB operation."""
        op = DBOperation(
            table='col',
            where={'id': 1},
            values={'models': '{}'}
        )
        assert op.table == 'col'
        assert op.where == {'id': 1}
        assert op.values == {'models': '{}'}

class TestAnkiOperationGenerator:
    """Tests for the AnkiOperationGenerator class."""
    
    def setup_method(self):
        self.generator = DBOperationGenerator()

    def test_model_update(self, model_change):
        """Test generating operations for model updates."""
        operations = self.generator.generate_operations(model_change)
        assert len(operations) == 1
        op = operations[0]
        assert op.table == 'col'
        assert op.where == {'id': 1}
        assert isinstance(op.values['models'], str)  # Should be JSON string

    def test_note_fields_update(self, note_fields_change):
        """Test generating operations for note field updates."""
        operations = self.generator.generate_operations(note_fields_change)
        assert len(operations) == 1
        op = operations[0]
        assert op.table == 'notes'
        assert op.where == {'id': 1}
        assert 'flds' in op.values

    def test_note_migration(self, note_migration_change):
        """Test generating operations for note migration."""
        operations = self.generator.generate_operations(note_migration_change)
        assert len(operations) == 1
        op = operations[0]
        assert op.table == 'notes'
        assert op.where == {'guid': 'test-guid'}
        assert 'mid' in op.values
        assert 'flds' in op.values

