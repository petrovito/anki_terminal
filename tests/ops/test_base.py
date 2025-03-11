from abc import ABC, abstractmethod
from datetime import datetime
from typing import Type

import pytest

from anki_terminal.commons.anki_types import Collection, Deck, Field, Model, Note
from anki_terminal.ops.op_base import Operation


class OperationTestBase(ABC):
    """Base class for operation unit tests."""
    
    # Subclasses must define these
    operation_class: Type[Operation] = None
    
    def test_operation_metadata(self):
        """Test that the operation has all required metadata."""
        assert self.operation_class is not None, "operation_class must be defined"
        assert self.operation_class.name, "Operation must have a name"
        assert self.operation_class.description, "Operation must have a description"
        assert isinstance(self.operation_class.readonly, bool), "Operation must define readonly status"
        assert isinstance(self.operation_class.arguments, list), "Operation must define arguments list"
    
    @abstractmethod
    def test_validation(self, mock_collection):
        """Test operation validation.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        pass
    
    @abstractmethod
    def test_execution(self, mock_collection):
        """Test operation execution.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        pass

    @pytest.fixture
    def mock_collection(self) -> Collection:
        """Fixture providing a mock collection for testing.
        
        This creates a fresh collection for each test to prevent test interference.
        The collection includes:
        - A Basic model with Front and Back fields
        - A sample note using the Basic model
        - An Advanced model with Question, Answer, and Notes fields
        - A default deck
        """
        # Create a note that uses the Basic model
        basic_note = Note(
            id=1,
            guid="test_guid",
            model_id=1,
            modification_time=datetime.fromtimestamp(0),
            usn=-1,
            tags=[],
            fields={"Front": "test front", "Back": "test back"},
            sort_field=0,
            checksum=0,
            flags=0
        )
        
        # Create a default deck
        default_deck = Deck(
            id=1,
            name="Default",
            description="Default deck",
            modification_time=datetime.fromtimestamp(0),
            usn=-1,
            collapsed=False,
            browser_collapsed=False,
            dynamic=False,
            new_today=(0, 0),
            review_today=(0, 0),
            learn_today=(0, 0),
            time_today=(0, 0)
        )
        
        return Collection(
            id=1,
            creation_time=datetime.fromtimestamp(0),
            modification_time=datetime.fromtimestamp(0),
            schema_modification=0,
            version=11,
            dirty=0,
            usn=-1,
            last_sync=datetime.fromtimestamp(0),
            models={
                1: Model(
                    id=1,
                    name="Basic",
                    fields=[
                        Field(name="Front", ordinal=0),
                        Field(name="Back", ordinal=1)
                    ],
                    templates=[],
                    css="",
                    deck_id=1,
                    modification_time=datetime.fromtimestamp(0),
                    type=0,
                    usn=-1,
                    version=1
                ),
                2: Model(
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
                    modification_time=datetime.fromtimestamp(0),
                    type=0,
                    usn=-1,
                    version=1
                )
            },
            decks={1: default_deck},
            notes={1: basic_note},
            cards={},
            config={},
            deck_configs={},
            tags=[]
        ) 