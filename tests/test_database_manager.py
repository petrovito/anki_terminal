import pytest
import json
from pathlib import Path
from datetime import datetime
from database_manager import DatabaseManager
from anki_types import Collection, Card, Note, Model, Deck, DeckConfig

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

def test_read_collection_from_anki21_database():
    """Test reading a collection from an Anki 21 database."""
    db_path = Path("test_data/collection.anki21")
    
    with DatabaseManager(db_path, anki_version=21) as db:
        collection = db.read_collection()
        
        # Test collection metadata
        assert isinstance(collection, Collection)
        assert collection.id == 1
        assert isinstance(collection.creation_time, datetime)
        assert isinstance(collection.modification_time, datetime)
        assert isinstance(collection.schema_modification, int)
        assert collection.version == 11
        
        # Test cards
        assert len(collection.cards) > 0
        card = next(iter(collection.cards.values()))
        assert isinstance(card, Card)
        assert isinstance(card.id, int)
        assert isinstance(card.note_id, int)
        assert isinstance(card.deck_id, int)
        
        # Test notes
        assert len(collection.notes) > 0
        note = next(iter(collection.notes.values()))
        assert isinstance(note, Note)
        assert isinstance(note.id, int)
        assert isinstance(note.model_id, int)
        assert isinstance(note.fields, dict)
        assert len(note.fields) > 0  # Should have at least one field
        assert isinstance(note.tags, list)
        
        # Test models
        assert len(collection.models) > 0
        model = next(iter(collection.models.values()))
        assert isinstance(model, Model)
        assert isinstance(model.name, str)
        assert len(model.fields) > 0
        assert len(model.templates) > 0
        
        # Test decks
        assert len(collection.decks) > 0
        deck = next(iter(collection.decks.values()))
        assert isinstance(deck, Deck)
        assert isinstance(deck.name, str)
        
        # Test deck configs
        assert len(collection.deck_configs) > 0
        config = next(iter(collection.deck_configs.values()))
        assert isinstance(config, DeckConfig)
        assert isinstance(config.name, str)
        
        # Test tags
        assert isinstance(collection.tags, list)
        if collection.tags:  # If there are any tags
            assert isinstance(collection.tags[0], str)

@pytest.mark.skip(reason="Temporary test for dumping sample data structure")
def test_dump_sample_data():
    """Temporary test to dump sample data from both Anki versions into JSON files."""
    # Anki 2
    with DatabaseManager(Path("test_data/collection.anki2"), anki_version=2) as db:
        table_data = db._read_table_data()
        sample_data = {
            'col': table_data['col'],  # col table always has one row
            'cards': [table_data['cards'][0]] if table_data['cards'] else [],  # first card
            'notes': [table_data['notes'][0]] if table_data['notes'] else []  # first note
        }
        with open('test_data/sample_anki2.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, default=str)  # default=str handles datetime objects
    
    # Anki 21
    with DatabaseManager(Path("test_data/collection.anki21"), anki_version=21) as db:
        table_data = db._read_table_data()
        sample_data = {
            'col': table_data['col'],  # col table always has one row
            'cards': [table_data['cards'][0]] if table_data['cards'] else [],  # first card
            'notes': [table_data['notes'][0]] if table_data['notes'] else []  # first note
        }
        with open('test_data/sample_anki21.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, default=str)  # default=str handles datetime objects 