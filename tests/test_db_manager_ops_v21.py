import pytest
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

from database_manager import DatabaseManager
from changelog import ChangeLog
from anki_types import Collection, Model, Field, Note

@pytest.fixture
def temp_db_v21():
    """Create a temporary v21 database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.anki21', delete=False) as f:
        db_path = Path(f.name)
    
    # Create test database schema
    conn = sqlite3.connect(db_path)
    conn.executescript('''
        CREATE TABLE col (
            id INTEGER PRIMARY KEY,
            crt INTEGER NOT NULL,
            mod INTEGER NOT NULL,
            scm INTEGER NOT NULL,
            ver INTEGER NOT NULL,
            dty INTEGER NOT NULL,
            usn INTEGER NOT NULL,
            ls INTEGER NOT NULL,
            conf TEXT NOT NULL,
            models TEXT NOT NULL,
            decks TEXT NOT NULL,
            dconf TEXT NOT NULL,
            tags TEXT NOT NULL
        );
        
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY,
            guid TEXT NOT NULL,
            mid INTEGER NOT NULL,
            mod INTEGER NOT NULL,
            usn INTEGER NOT NULL,
            tags TEXT NOT NULL,
            flds TEXT NOT NULL,
            sfld INTEGER NOT NULL,
            csum INTEGER NOT NULL,
            flags INTEGER NOT NULL,
            data TEXT NOT NULL
        );
        
        CREATE TABLE cards (
            id INTEGER PRIMARY KEY,
            nid INTEGER NOT NULL,
            did INTEGER NOT NULL,
            ord INTEGER NOT NULL,
            mod INTEGER NOT NULL,
            usn INTEGER NOT NULL,
            type INTEGER NOT NULL,
            queue INTEGER NOT NULL,
            due INTEGER NOT NULL,
            ivl INTEGER NOT NULL,
            factor INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            lapses INTEGER NOT NULL,
            left INTEGER NOT NULL,
            odue INTEGER NOT NULL,
            odid INTEGER NOT NULL,
            flags INTEGER NOT NULL,
            data TEXT NOT NULL
        );
    ''')
    
    # Insert initial test data
    now = int(datetime.now().timestamp())
    conn.execute(
        "INSERT INTO col VALUES (1, ?, ?, 0, 11, 0, -1, 0, '{}', '{}', '{}', '{}', '{}')",
        (now, now)
    )
    conn.commit()
    conn.close()
    
    yield db_path
    db_path.unlink()  # Cleanup

@pytest.fixture
def sample_model() -> Model:
    """Create a sample model for testing."""
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

class TestDatabaseManagerOperationsV21:
    """Integration tests for DatabaseManager v21 operations."""
    
    def test_model_update_v21(self, temp_db_v21, sample_model):
        """Test model update operation in v21 database."""
        with DatabaseManager(temp_db_v21, anki_version=21) as db:
            # Create changelog with model update
            changelog = ChangeLog()
            changelog.add_model_change({1: sample_model})
            
            # Apply changes
            db.apply_changes(changelog)
            
            # Verify changes in database
            cursor = db._conn.cursor()
            cursor.execute("SELECT models FROM col WHERE id = 1")
            models_json = cursor.fetchone()[0]
            assert '"name": "Basic"' in models_json
            assert '"Front"' in models_json
            assert '"Back"' in models_json
            assert '\t' not in models_json  # Should use JSON, not field separator

    def test_note_update_v21(self, temp_db_v21, sample_model):
        """Test note field update operation in v21 database."""
        with DatabaseManager(temp_db_v21, anki_version=21) as db:
            # Insert test note
            cursor = db._conn.cursor()
            cursor.execute(
                "INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data) "
                "VALUES (1, 'test', 1, 0, -1, '', 'old front\x1fold back', 'old front', 0, 0, '')"
            )
            
            # Create changelog with note update
            changelog = ChangeLog()
            note = Note(
                id=1,
                guid="test",
                model_id=1,
                modification_time=datetime.now(),
                usn=-1,
                tags=[],
                fields={"Front": "new front", "Back": "new back"},
                sort_field=0,
                checksum=0,
                flags=0
            )
            changelog.add_note_fields_change(note, sample_model)
            
            # Apply changes
            db.apply_changes(changelog)
            
            # Verify changes in database
            cursor.execute("SELECT flds FROM notes WHERE id = 1")
            fields = cursor.fetchone()[0]
            assert fields == "new front\x1fnew back"  # Using \x1f separator

    def test_note_migration_v21(self, temp_db_v21, sample_model):
        """Test note migration operation in v21 database."""
        with DatabaseManager(temp_db_v21, anki_version=21) as db:
            # Insert test note
            cursor = db._conn.cursor()
            cursor.execute(
                "INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data) "
                "VALUES (1, 'test', 1, 0, -1, '', 'old front\x1fold back', 'old front', 0, 0, '')"
            )
            
            # Create target model
            target_model = Model(
                id=2,
                name="Advanced",
                fields=[
                    Field(name="Question", ordinal=0),
                    Field(name="Answer", ordinal=1),
                    Field(name="Notes", ordinal=2)
                ],
                templates=[],
                css="",
                deck_id=1,
                modification_time=datetime.now(),
                type=0,
                usn=-1,
                version=1
            )
            
            # Create changelog with note migration
            changelog = ChangeLog()
            note = Note(
                id=1,
                guid="test",
                model_id=2,  # Target model ID
                modification_time=datetime.now(),
                usn=-1,
                tags=[],
                fields={"Question": "old front", "Answer": "old back", "Notes": ""},
                sort_field=0,
                checksum=0,
                flags=0
            )
            changelog.add_note_migration_change(sample_model, target_model, note)
            
            # Apply changes
            db.apply_changes(changelog)
            
            # Verify changes in database
            cursor.execute("SELECT mid, flds FROM notes WHERE id = 1")
            row = cursor.fetchone()
            assert row[0] == 2  # Should be migrated to target model
            assert row[1] == "old front\x1fold back\x1f"  # Using \x1f separator for empty Notes field 