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
    browser_font: Optional[str] = None  # bfont (Anki 21)
    browser_font_size: Optional[int] = None  # bsize (Anki 21)
    template_id: Optional[int] = None  # id (Anki 21)

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
        if self.browser_font:
            result['bfont'] = self.browser_font
        if self.browser_font_size:
            result['bsize'] = self.browser_font_size
        if self.template_id:
            result['id'] = self.template_id
        return result

@dataclass
class Field:
    name: str
    ordinal: int = 0
    sticky: bool = False
    rtl: bool = False
    font: str = "Arial"
    font_size: int = 20
    description: str = ""  # Anki 21
    media: List[str] = None  # Media references
    plain_text: bool = False  # Anki 21
    exclude_from_search: bool = False  # Anki 21
    prevent_deletion: bool = False  # Anki 21
    collapsed: bool = False  # Anki 21
    tag: Optional[str] = None  # Anki 21
    field_id: Optional[int] = None  # Anki 21

    def __post_init__(self):
        if self.media is None:
            self.media = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert field to Anki's JSON format."""
        result = {
            'name': self.name,
            'ord': self.ordinal,
            'sticky': self.sticky,
            'rtl': self.rtl,
            'font': self.font,
            'size': self.font_size,
            'media': self.media
        }
        # Add Anki 21 specific fields if they're set
        if self.description:
            result['description'] = self.description
        if self.plain_text:
            result['plainText'] = self.plain_text
        if self.exclude_from_search:
            result['excludeFromSearch'] = self.exclude_from_search
        if self.prevent_deletion:
            result['preventDeletion'] = self.prevent_deletion
        if self.collapsed:
            result['collapsed'] = self.collapsed
        if self.tag:
            result['tag'] = self.tag
        if self.field_id:
            result['id'] = self.field_id
        return result

@dataclass
class Model:
    id: int              # mid
    name: str
    fields: List[Field]  # Changed from List[str] to List[Field]
    templates: List[Template]
    css: str
    deck_id: int         # did
    modification_time: datetime  # mod
    type: int            # 0 for standard, 1 for cloze
    usn: int            # update sequence number
    version: int        # vers
    latex_pre: str = "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n"
    latex_post: str = "\\end{document}"
    latex_svg: bool = False  # Anki 21
    required: List[List[Any]] = None  # Required fields configuration
    tags: List[str] = None  # Model-specific tags

    def __post_init__(self):
        if self.required is None:
            self.required = [[0, "all", [0]]]
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to Anki's JSON format."""
        result = {
            'id': self.id,
            'name': self.name,
            'flds': [f.to_dict() for f in self.fields],
            'tmpls': [t.to_dict() for t in self.templates],
            'css': self.css,
            'did': self.deck_id,
            'mod': int(self.modification_time.timestamp()),
            'type': self.type,
            'usn': self.usn,
            'vers': self.version,
            'latexPre': self.latex_pre,
            'latexPost': self.latex_post,
            'latexsvg': self.latex_svg,
            'req': self.required,
            'tags': self.tags
        }
        return result

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
    flags: int = 0     # flags
    data: Dict[str, Any] = None     # Additional data stored as dict

    def __post_init__(self):
        if self.data is None:
            self.data = {}
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary format for database storage.
        
        Returns:
            Dictionary containing note data
        """
        return {
            'id': self.id,
            'guid': self.guid,
            'mid': self.model_id,
            'mod': int(self.modification_time.timestamp()),
            'usn': self.usn,
            'tags': ' '.join(self.tags),  # Convert tags list to space-separated string
            'flds': self.fields,  # Field values
            'sfld': self.sort_field,
            'csum': self.checksum,
            'flags': self.flags,
            'data': self.data
        }

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
    data: Dict[str, Any] = None   # Additional data stored as dict

    def __post_init__(self):
        if self.data is None:
            self.data = {}

@dataclass
class Deck:
    id: int
    name: str
    description: str
    modification_time: datetime
    usn: int
    collapsed: bool
    browser_collapsed: bool
    dynamic: bool
    new_today: tuple[int, int]      # [day_number, count]
    review_today: tuple[int, int]   # [day_number, count]
    learn_today: tuple[int, int]    # [day_number, count]
    time_today: tuple[int, int]     # [time in ms, count]
    conf_id: Optional[int] = None
    extend_new: int = 0             # Extend new card limit
    extend_rev: int = 0             # Extend review card limit

@dataclass
class DeckConfig:
    id: int
    name: str
    modification_time: datetime
    usn: int
    max_taken: int = 60            # Maximum answer time to record
    autoplay: bool = True          # Automatically play audio
    timer: int = 0                 # Show timer
    replay_question: bool = True   # Replay question audio
    dynamic: bool = False          # Is a filtered deck
    new_cards: Dict[str, Any] = None  # New card settings
    review_cards: Dict[str, Any] = None  # Review card settings
    lapse_cards: Dict[str, Any] = None  # Lapse card settings

    def __post_init__(self):
        if self.new_cards is None:
            self.new_cards = {
                "bury": False,
                "delays": [1.0, 10.0],
                "initialFactor": 2500,
                "ints": [1, 4, 0],
                "order": 1,
                "perDay": 20
            }
        if self.review_cards is None:
            self.review_cards = {
                "bury": False,
                "ease4": 1.3,
                "ivlFct": 1.0,
                "maxIvl": 36500,
                "perDay": 200,
                "hardFactor": 1.2
            }
        if self.lapse_cards is None:
            self.lapse_cards = {
                "delays": [10.0],
                "leechAction": 1,
                "leechFails": 8,
                "minInt": 1,
                "mult": 0.0
            }

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
    notes: Dict[int, Note]    # notes, keyed by note id
    cards: Dict[int, Card]    # cards, keyed by card id
    
    # Configuration
    config: Dict             # conf - json object containing configuration
    deck_configs: Dict[int, DeckConfig]  # deck configurations, keyed by config id
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