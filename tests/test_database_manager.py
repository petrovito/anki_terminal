import pytest
from pathlib import Path
from database_manager import DatabaseManager

def test_read_anki2_database():
    """Test reading an Anki 2 database."""
    db_path = Path("test_data/collection.anki2")
    
    with DatabaseManager(db_path, anki_version=2) as db:
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
        assert len(table_data['cards']) > 0
        card = table_data['cards'][0]
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
        assert len(table_data['notes']) > 0
        note = table_data['notes'][0]
        assert isinstance(note['id'], int)
        assert isinstance(note['guid'], str)  # globally unique id
        assert isinstance(note['mid'], int)  # model id
        assert isinstance(note['mod'], int)  # modification time
        assert isinstance(note['flds'], str)  # fields
        # Note: sfld is defined as INTEGER in schema but actually contains text data
        # SQLite's type affinity allows this - schema and actual data types can differ
        assert isinstance(note['sfld'], str)  # sort field
        assert isinstance(note['csum'], int)  # checksum
        assert isinstance(note['flags'], int)  # flags
        assert isinstance(note['data'], str)  # additional data

def test_read_anki21_database():
    """Test reading an Anki 21 database."""
    db_path = Path("test_data/collection.anki21")
    
    with DatabaseManager(db_path, anki_version=21) as db:
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
        assert len(table_data['cards']) > 0
        card = table_data['cards'][0]
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
        assert len(table_data['notes']) > 0
        note = table_data['notes'][0]
        assert isinstance(note['id'], int)
        assert isinstance(note['guid'], str)  # globally unique id
        assert isinstance(note['mid'], int)  # model id
        assert isinstance(note['mod'], int)  # modification time
        assert isinstance(note['flds'], str)  # fields
        # Note: sfld is defined as INTEGER in schema but actually contains text data
        # SQLite's type affinity allows this - schema and actual data types can differ
        assert isinstance(note['sfld'], str)  # sort field
        assert isinstance(note['csum'], int)  # checksum
        assert isinstance(note['flags'], int)  # flags
        assert isinstance(note['data'], str)  # additional data 