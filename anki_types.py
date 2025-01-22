from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import IntEnum

@dataclass
class Template:
    name: str
    question_format: str  # qfmt
    answer_format: str    # afmt
    browser_question_format: Optional[str] = None  # bqfmt
    browser_answer_format: Optional[str] = None    # bafmt
    deck_override: Optional[int] = None  # did
    ordinal: int = 0     # ord

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to Anki's JSON format."""
        result = {
            'name': self.name,
            'qfmt': self.question_format,
            'afmt': self.answer_format,
            'ord': self.ordinal,
        }
        if self.browser_question_format:
            result['bqfmt'] = self.browser_question_format
        if self.browser_answer_format:
            result['bafmt'] = self.browser_answer_format
        if self.deck_override:
            result['did'] = self.deck_override
        return result

@dataclass
class Model:
    id: int              # mid
    name: str
    fields: List[str]
    templates: List[Template]
    css: str
    deck_id: int         # did
    modification_time: datetime  # mod
    type: int            # 0 for standard, 1 for cloze
    usn: int            # update sequence number
    version: int        # vers

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to Anki's JSON format."""
        return {
            'id': self.id,
            'name': self.name,
            'flds': [{'name': name, 'ord': i} for i, name in enumerate(self.fields)],
            'tmpls': [t.to_dict() for t in self.templates],
            'css': self.css,
            'did': self.deck_id,
            'mod': int(self.modification_time.timestamp()),
            'type': self.type,
            'usn': self.usn,
            'vers': self.version
        }

@dataclass
class Note:
    id: int             # nid
    guid: str           # globally unique id
    model_id: int       # mid
    modification_time: datetime  # mod
    usn: int           # update sequence number
    tags: List[str]    # space-separated string in DB
    fields: Dict[str, str]  # field values mapped to field names
    sort_field: int    # sfld
    checksum: int      # csum - first 8 digits of sha1 of first field

@dataclass
class Card:
    id: int
    note_id: int       # nid
    deck_id: int       # did
    ordinal: int       # ord
    modification_time: datetime  # mod
    usn: int          # update sequence number
    type: int         # 0=new, 1=learning, 2=review, 3=relearning
    queue: int        # -3=user buried, -2=sched buried, -1=suspended, 0=new, 1=learning
    due: int          # due date or position
    interval: int     # ivl - space between reviews
    factor: int       # ease factor
    reps: int        # number of reviews
    lapses: int      # number of times card went from correct to incorrect
    left: int        # reps left today * 1000 + reps left till graduation
    original_due: int  # odue
    original_deck_id: int  # odid
    flags: int       # flag color (0-4)

@dataclass
class Deck:
    id: int
    name: str
    description: str
    modification_time: datetime  # This is a real timestamp
    usn: int
    collapsed: bool
    browser_collapsed: bool
    dynamic: bool
    # These are tuples of (day_number, count), not timestamps
    new_today: tuple[int, int]      # (day_number, count)
    review_today: tuple[int, int]   # (day_number, count)
    learn_today: tuple[int, int]    # (day_number, count)
    conf_id: Optional[int] = None

@dataclass
class Collection:
    id: int
    creation_time: datetime     # crt - timestamp of creation date
    modification_time: datetime  # mod - last modified in milliseconds
    schema_modification: int    # scm - schema modification time
    version: int               # ver - version number
    dirty: int                # dty - unused, set to 0
    usn: int                  # update sequence number
    last_sync: datetime       # ls - last sync time
    
    # Main components
    models: Dict[int, Model]  # note types, keyed by model id
    decks: Dict[int, Deck]    # decks, keyed by deck id
    notes: List[Note]         # all notes in the collection
    cards: List[Card]         # all cards in the collection
    
    # Configuration
    config: Dict             # conf - json object containing configuration
    deck_config: Dict        # dconf - json object containing deck options groups
    tags: List[str]         # tags - cache of tags used in the collection 

class CardType(IntEnum):
    NEW = 0
    LEARNING = 1
    REVIEW = 2
    RELEARNING = 3

class CardQueue(IntEnum):
    USER_BURIED = -3
    SCHED_BURIED = -2
    SUSPENDED = -1
    NEW = 0
    LEARNING = 1 