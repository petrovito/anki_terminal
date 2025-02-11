import pytest
import json
from datetime import datetime
from typing import Dict, Any
from anki_types import Collection, Card, Note, Model, Deck, DeckConfig
from collection_factories import CollectionV2Factory, CollectionV21Factory

@pytest.fixture
def v2_table_data() -> Dict[str, Any]:
    """Fixture providing sample Anki v2 table data."""
    return {
        'col': {
            'id': 1,
            'crt': 1577836800,  # 2020-01-01
            'mod': 1577836800,
            'scm': 1577836800,
            'ver': 11,
            'dty': 0,
            'usn': -1,
            'ls': 1577836800,
            'conf': '{"nextPos": 1}',
            'models': json.dumps({
                "1234": {
                    "id": 1234,
                    "name": "Basic",
                    "flds": [
                        {"name": "Front", "ord": 0},
                        {"name": "Back", "ord": 1}
                    ],
                    "tmpls": [
                        {
                            "name": "Card 1",
                            "qfmt": "{{Front}}",
                            "afmt": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}",
                            "ord": 0
                        }
                    ],
                    "css": ".card { font-family: arial; }",
                    "mod": 1577836800,
                    "usn": -1,
                    "vers": 1
                }
            }),
            'decks': json.dumps({
                "1": {
                    "id": 1,
                    "name": "Default",
                    "mod": 1577836800,
                    "conf": 1
                }
            }),
            'dconf': json.dumps({
                "1": {
                    "id": 1,
                    "name": "Default",
                    "mod": 1577836800,
                    "usn": -1
                }
            })
        },
        'cards': [
            {
                'id': 1,
                'nid': 1,
                'did': 1,
                'ord': 0,
                'mod': 1577836800,
                'usn': -1,
                'type': 0,
                'queue': 0,
                'due': 0,
                'ivl': 0,
                'factor': 2500,
                'reps': 0,
                'lapses': 0,
                'left': 1000,
                'odue': 0,
                'odid': 0,
                'flags': 0,
                'data': '{}'
            }
        ],
        'notes': [
            {
                'id': 1,
                'guid': 'abc123',
                'mid': 1234,
                'mod': 1577836800,
                'usn': -1,
                'tags': 'tag1 tag2',
                'flds': 'Question\x1fAnswer',
                'sfld': 'Question',
                'csum': 1234567890,
                'flags': 0,
                'data': '{}'
            }
        ]
    }

@pytest.fixture
def v21_table_data() -> Dict[str, Any]:
    """Fixture providing sample Anki v21 table data."""
    return {
        'col': {
            'id': 1,
            'crt': 1577836800,  # 2020-01-01
            'mod': 1577836800,
            'scm': 1577836800,
            'ver': 11,
            'dty': 0,
            'usn': -1,
            'ls': 1577836800,
            'conf': json.dumps({
                "curDeck": 1,
                "newSpread": 0,
                "collapseTime": 1200,
                "timeLim": 0,
                "estTimes": True,
                "dueCounts": True,
                "curModel": 1234567890,
                "nextPos": 1,
                "sortType": "noteFld",
                "sortBackwards": False,
                "addToCur": True,
                "dayLearnFirst": False,
                "schedVer": 1
            }),
            'models': json.dumps({
                "1234": {
                    "id": 1234,
                    "name": "Basic",
                    "type": 0,
                    "mod": 1577836800,
                    "usn": -1,
                    "sortf": 0,
                    "did": 1,
                    "tmpls": [{
                        "name": "Card 1",
                        "ord": 0,
                        "qfmt": "{{Front}}",
                        "afmt": "{{Back}}",
                        "bqfmt": "",
                        "bafmt": "",
                        "did": None,
                        "bfont": "",
                        "bsize": 0
                    }],
                    "flds": [{
                        "name": "Front",
                        "ord": 0,
                        "sticky": False,
                        "rtl": False,
                        "font": "Arial",
                        "size": 20,
                        "plainText": False,
                        "excludeFromSearch": False,
                        "preventDeletion": False,
                        "description": "",
                        "media": [],
                        "tag": None,
                        "id": None
                    }, {
                        "name": "Back",
                        "ord": 1,
                        "sticky": False,
                        "rtl": False,
                        "font": "Arial",
                        "size": 20,
                        "plainText": False,
                        "excludeFromSearch": False,
                        "preventDeletion": False,
                        "description": "",
                        "media": [],
                        "tag": None,
                        "id": None
                    }],
                    "css": ".card { }",
                    "latexPre": "",
                    "latexPost": "",
                    "latexsvg": False,
                    "req": [[0, "any", [0]]]
                }
            }),
            'decks': json.dumps({
                "1": {
                    "id": 1,
                    "name": "Default",
                    "mod": 1577836800,
                    "usn": -1,
                    "lrnToday": [0, 0],
                    "revToday": [0, 0],
                    "newToday": [0, 0],
                    "timeToday": [0, 0],
                    "collapsed": False,
                    "desc": "",
                    "dyn": 0,
                    "conf": 1
                }
            }),
            'dconf': json.dumps({
                "1": {
                    "id": 1,
                    "name": "Default",
                    "maxTaken": 60,
                    "autoplay": True,
                    "timer": 0,
                    "replayq": True,
                    "dyn": False,
                    "new": {
                        "bury": False,
                        "delays": [1, 10],
                        "initialFactor": 2500,
                        "perDay": 20,
                        "order": 1
                    },
                    "rev": {
                        "bury": False,
                        "ease4": 1.3,
                        "ivlFct": 1.0,
                        "maxIvl": 36500,
                        "perDay": 200,
                        "hardFactor": 1.2
                    },
                    "lapse": {
                        "delays": [10],
                        "leechAction": 1,
                        "leechFails": 8,
                        "minInt": 1,
                        "mult": 0
                    }
                }
            })
        },
        'cards': [
            {
                'id': 1,
                'nid': 1,
                'did': 1,
                'ord': 0,
                'mod': 1577836800,
                'usn': -1,
                'type': 0,  # 0=new
                'queue': 0,  # 0=new
                'due': 0,
                'ivl': 0,
                'factor': 2500,
                'reps': 0,
                'lapses': 0,
                'left': 1000,
                'odue': 0,
                'odid': 0,
                'flags': 0,
                'data': '{}'
            }
        ],
        'notes': [
            {
                'id': 1,
                'guid': 'abc123',
                'mid': 1234,
                'mod': 1577836800,
                'usn': -1,
                'tags': 'tag1 tag2',
                'flds': 'Question\tAnswer',
                'sfld': 'Question',
                'csum': 1234567890,
                'flags': 0,
                'data': '{}'
            }
        ],
        'notetypes': [
            {
                'id': 1234,
                'name': 'Basic',
                'mod': 1577836800,
                'usn': -1,
                'config': json.dumps({
                    'css': '.card { }',
                    'latexPre': '',
                    'latexPost': '',
                    'latexsvg': False,
                    'req': [[0, "any", [0]]],
                    'version': 1
                })
            }
        ],
        'templates': [
            {
                'ntid': 1234,
                'ord': 0,
                'name': 'Card 1',
                'config': json.dumps({
                    'qfmt': '{{Front}}',
                    'afmt': '{{Back}}',
                    'bqfmt': '',
                    'bafmt': '',
                    'bfont': '',
                    'bsize': 0
                })
            }
        ],
        'fields': [
            {
                'ntid': 1234,
                'ord': 0,
                'name': 'Front',
                'config': json.dumps({
                    'sticky': False,
                    'rtl': False,
                    'font': 'Arial',
                    'size': 20,
                    'plainText': False,
                    'excludeFromSearch': False,
                    'preventDeletion': False,
                    'description': ''
                })
            },
            {
                'ntid': 1234,
                'ord': 1,
                'name': 'Back',
                'config': json.dumps({
                    'sticky': False,
                    'rtl': False,
                    'font': 'Arial',
                    'size': 20,
                    'plainText': False,
                    'excludeFromSearch': False,
                    'preventDeletion': False,
                    'description': ''
                })
            }
        ],
        'decks': [
            {
                'id': 1,
                'name': 'Default',
                'mod': 1577836800,
                'conf': 1,
                'config': json.dumps({
                    'collapsed': False,
                    'browserCollapsed': False,
                    'desc': '',
                    'dyn': 0,
                    'newToday': [0, 0],
                    'revToday': [0, 0],
                    'lrnToday': [0, 0],
                    'timeToday': [0, 0]
                })
            }
        ],
        'deck_config': [
            {
                'id': 1,
                'name': 'Default',
                'mod': 1577836800,
                'usn': -1,
                'config': json.dumps({
                    'maxTaken': 60,
                    'autoplay': True,
                    'timer': 0,
                    'replayq': True,
                    'dyn': False,
                    'new': {
                        'bury': False,
                        'delays': [1, 10],
                        'initialFactor': 2500,
                        'perDay': 20,
                        'order': 1
                    },
                    'rev': {
                        'bury': False,
                        'ease4': 1.3,
                        'ivlFct': 1.0,
                        'maxIvl': 36500,
                        'perDay': 200,
                        'hardFactor': 1.2
                    },
                    'lapse': {
                        'delays': [10],
                        'leechAction': 1,
                        'leechFails': 8,
                        'minInt': 1,
                        'mult': 0
                    }
                })
            }
        ],
        'tags': [
            {
                'id': 1,
                'tag': 'tag1',
                'config': '{}'
            },
            {
                'id': 2,
                'tag': 'tag2',
                'config': '{}'
            }
        ]
    }

def test_v2_factory_creates_collection(v2_table_data):
    """Test that V2 factory correctly creates a collection from table data."""
    factory = CollectionV2Factory()
    collection = factory.create_collection(v2_table_data)
    
    # Test collection metadata
    assert isinstance(collection, Collection)
    assert collection.id == 1
    assert collection.creation_time == datetime.fromtimestamp(1577836800)
    assert collection.schema_modification == 1577836800
    
    # Test cards
    assert len(collection.cards) == 1
    card = collection.cards[1]
    assert isinstance(card, Card)
    assert card.id == 1
    assert card.note_id == 1
    assert card.deck_id == 1
    
    # Test notes
    assert len(collection.notes) == 1
    note = collection.notes[1]
    assert isinstance(note, Note)
    assert note.id == 1
    assert note.model_id == 1234
    assert note.fields == {'Front': 'Question', 'Back': 'Answer'}
    assert note.tags == ['tag1', 'tag2']
    
    # Test models
    assert len(collection.models) == 1
    model = collection.models[1234]
    assert isinstance(model, Model)
    assert model.name == 'Basic'
    assert len(model.fields) == 2
    assert model.fields[0].name == 'Front'
    assert model.fields[1].name == 'Back'
    assert len(model.templates) == 1
    assert model.templates[0].name == 'Card 1'
    
    # Test decks
    assert len(collection.decks) == 1
    deck = collection.decks[1]
    assert isinstance(deck, Deck)
    assert deck.name == 'Default'
    
    # Test deck configs
    assert len(collection.deck_configs) == 1
    config = collection.deck_configs[1]
    assert isinstance(config, DeckConfig)
    assert config.name == 'Default'

def test_v21_factory_creates_collection(v21_table_data):
    """Test that V21 factory correctly creates a collection from table data."""
    factory = CollectionV21Factory()
    collection = factory.create_collection(v21_table_data)
    
    # Test collection metadata
    assert isinstance(collection, Collection)
    assert collection.id == 1
    assert collection.creation_time == datetime.fromtimestamp(1577836800)
    assert collection.schema_modification == 1577836800
    
    # Test cards
    assert len(collection.cards) == 1
    card = collection.cards[1]
    assert isinstance(card, Card)
    assert card.id == 1
    assert card.note_id == 1
    assert card.deck_id == 1
    
    # Test notes
    assert len(collection.notes) == 1
    note = collection.notes[1]
    assert isinstance(note, Note)
    assert note.id == 1
    assert note.model_id == 1234
    assert note.fields == {'Front': 'Question', 'Back': 'Answer'}
    assert note.tags == ['tag1', 'tag2']
    
    # Test models
    assert len(collection.models) == 1
    model = collection.models[1234]
    assert isinstance(model, Model)
    assert model.name == 'Basic'
    assert len(model.fields) == 2
    assert model.fields[0].name == 'Front'
    assert model.fields[1].name == 'Back'
    assert len(model.templates) == 1
    assert model.templates[0].name == 'Card 1'
    
    # Test decks
    assert len(collection.decks) == 1
    deck = collection.decks[1]
    assert isinstance(deck, Deck)
    assert deck.name == 'Default'
    
    # Test deck configs
    assert len(collection.deck_configs) == 1
    config = collection.deck_configs[1]
    assert isinstance(config, DeckConfig)
    assert config.name == 'Default'
    
    # Test tags
    assert len(collection.tags) == 2
    tag1 = collection.tags[0]
    assert isinstance(tag1, str)
    assert tag1 == 'tag1'
    tag2 = collection.tags[1]
    assert tag2 == 'tag2'

def test_v2_factory_handles_missing_data(v2_table_data):
    """Test that V2 factory gracefully handles missing optional data."""
    # Remove optional data
    v2_table_data['col']['dconf'] = '{}'  # Empty deck configs
    v2_table_data['notes'][0]['tags'] = ''  # No tags
    v2_table_data['notes'][0]['data'] = ''  # Empty note data
    v2_table_data['cards'][0]['data'] = ''  # Empty card data
    
    factory = CollectionV2Factory()
    collection = factory.create_collection(v2_table_data)
    
    # Verify everything still works
    assert len(collection.deck_configs) == 0
    assert len(collection.notes[1].tags) == 0
    assert collection.notes[1].data == {}
    assert collection.cards[1].data == {}

def test_v21_factory_handles_missing_data(v21_table_data):
    """Test that V21 factory gracefully handles missing optional data."""
    # Remove optional data
    v21_table_data['deck_config'] = []  # No deck configs
    v21_table_data['tags'] = []  # No tags
    v21_table_data['notes'][0]['data'] = ''  # Empty note data
    v21_table_data['cards'][0]['data'] = ''  # Empty card data
    
    factory = CollectionV21Factory()
    collection = factory.create_collection(v21_table_data)
    
    # Verify everything still works
    assert len(collection.deck_configs) == 0
    assert len(collection.tags) == 0
    assert collection.notes[1].data == {}
    assert collection.cards[1].data == {}

def test_v2_factory_field_parsing():
    """Test that V2 factory correctly parses note fields."""
    factory = CollectionV2Factory()
    
    # Test basic field parsing
    fields = factory._parse_fields('First\x1fSecond\x1fThird')
    assert fields == {0: 'First', 1: 'Second', 2: 'Third'}
    
    # Test empty fields
    fields = factory._parse_fields('\x1f\x1f')
    assert fields == {0: '', 1: '', 2: ''}
    
    # Test single field
    fields = factory._parse_fields('Only')
    assert fields == {0: 'Only'}

def test_v21_factory_field_parsing():
    """Test that V21 factory correctly parses note fields."""
    factory = CollectionV21Factory()
    
    # Test basic field parsing
    fields = factory._parse_fields('First\tSecond\tThird')
    assert fields == {0: 'First', 1: 'Second', 2: 'Third'}
    
    # Test empty fields
    fields = factory._parse_fields('\t\t')
    assert fields == {0: '', 1: '', 2: ''}
    
    # Test single field
    fields = factory._parse_fields('Only')
    assert fields == {0: 'Only'} 