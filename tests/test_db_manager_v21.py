import pytest
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

from anki_terminal.database_manager import DatabaseManager
from anki_terminal.anki_types import Collection, Card, Note, Model, Deck, DeckConfig

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

def test_read_anki21_database(temp_db_v21):
    """Test reading an Anki 21 database."""
    with DatabaseManager(temp_db_v21, anki_version=21) as db:
        table_data = db._read_table_data()
        
        # Verify we got all required tables
        assert 'col' in table_data
        assert 'cards' in table_data
        assert 'notes' in table_data
        
        # Verify col table structure
        col = table_data['col']
        assert isinstance(col, dict)
        assert col['id'] == 1  # col table always has id=1
        assert isinstance(col['crt'], int)  # creation time
        assert isinstance(col['mod'], int)  # modification time
        assert isinstance(col['scm'], int)  # schema modification time
        assert col['ver'] == 11  # version
        assert isinstance(col['conf'], str)  # configuration (JSON string)
        assert isinstance(col['models'], str)  # note types (JSON string)
        assert isinstance(col['decks'], str)  # decks (JSON string)
        assert isinstance(col['dconf'], str)  # deck configuration (JSON string)
        
        # Verify cards table structure
        card = table_data['cards'][0] if table_data['cards'] else {}
        if card:
            assert isinstance(card['id'], int)
            assert isinstance(card['nid'], int)  # note id
            assert isinstance(card['did'], int)  # deck id
            assert isinstance(card['ord'], int)  # template ordinal
            assert isinstance(card['mod'], int)  # modification time
            assert isinstance(card['type'], int)  # card type
            assert isinstance(card['queue'], int)  # card queue
            assert isinstance(card['due'], int)  # due date
            assert isinstance(card['ivl'], int)  # interval
            assert isinstance(card['factor'], int)  # ease factor
            assert isinstance(card['reps'], int)  # number of reviews
            assert isinstance(card['lapses'], int)  # number of lapses
        
        # Verify notes table structure
        note = table_data['notes'][0] if table_data['notes'] else {}
        if note:
            assert isinstance(note['id'], int)
            assert isinstance(note['guid'], str)  # globally unique id
            assert isinstance(note['mid'], int)  # model id
            assert isinstance(note['mod'], int)  # modification time
            assert isinstance(note['flds'], str)  # fields
            assert isinstance(note['sfld'], str)  # sort field
            assert isinstance(note['csum'], int)  # checksum
            assert isinstance(note['flags'], int)  # flags
            assert isinstance(note['data'], str)  # additional data

def test_read_collection_from_anki21_database(temp_db_v21):
    """Test reading a collection from an Anki 21 database."""
    with DatabaseManager(temp_db_v21, anki_version=21) as db:
        collection = db.read_collection()
        
        # Test collection metadata
        assert isinstance(collection, Collection)
        assert collection.id == 1
        assert isinstance(collection.creation_time, datetime)
        assert isinstance(collection.modification_time, datetime)
        assert isinstance(collection.schema_modification, int)
        assert collection.version == 11
        
        # Test cards
        if collection.cards:
            card = next(iter(collection.cards.values()))
            assert isinstance(card, Card)
            assert isinstance(card.id, int)
            assert isinstance(card.note_id, int)
            assert isinstance(card.deck_id, int)
        
        # Test notes
        if collection.notes:
            note = next(iter(collection.notes.values()))
            assert isinstance(note, Note)
            assert isinstance(note.id, int)
            assert isinstance(note.model_id, int)
            assert isinstance(note.fields, dict)
            assert isinstance(note.tags, list)
        
        # Test models
        if collection.models:
            model = next(iter(collection.models.values()))
            assert isinstance(model, Model)
            assert isinstance(model.name, str)
            assert len(model.fields) >= 0
            assert len(model.templates) >= 0
        
        # Test decks
        if collection.decks:
            deck = next(iter(collection.decks.values()))
            assert isinstance(deck, Deck)
            assert isinstance(deck.name, str)
        
        # Test deck configs
        if collection.deck_configs:
            config = next(iter(collection.deck_configs.values()))
            assert isinstance(config, DeckConfig)
            assert isinstance(config.name, str)
        
        # Test tags
        assert isinstance(collection.tags, list) 