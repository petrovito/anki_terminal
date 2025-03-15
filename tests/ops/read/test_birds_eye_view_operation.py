import pytest

from anki_terminal.commons.anki_types import Card, Deck, Field, Model, Note, Template
from anki_terminal.ops.read.birds_eye_view_operation import BirdsEyeViewOperation
from tests.ops.test_base import OperationTestBase


class TestBirdsEyeViewOperation(OperationTestBase):
    """Tests for the BirdsEyeViewOperation."""
    
    operation_class = BirdsEyeViewOperation
    valid_args = {}  # No required arguments
    
    def test_validation(self, mock_collection):
        """Test operation validation."""
        # Test with default arguments
        operation = self.operation_class()
        operation.validate(mock_collection)
        
        # Test with explicit arguments
        operation = self.operation_class(
            show_empty_models=True,
            show_empty_decks=True,
            example_count=5
        )
        operation.validate(mock_collection)
    
    def test_execution(self, mock_collection):
        """Test operation execution."""
        # Add an additional model with no notes
        empty_model = Model(
            id=3,
            name="Empty Model",
            fields=[
                Field(name="Field1", ordinal=0, sticky=False, rtl=False, font="Arial", font_size=20, description="", plain_text=True),
                Field(name="Field2", ordinal=1, sticky=False, rtl=False, font="Arial", font_size=20, description="", plain_text=True)
            ],
            templates=[],
            css=".card {}",
            deck_id=1,  # Required parameter
            modification_time=mock_collection.modification_time,
            usn=-1,
            type=0,
            version=1,  # Required parameter
            latex_pre="",
            latex_post="",
            latex_svg=False,
            required=[]
        )
        mock_collection.models[3] = empty_model
        
        # Add a deck with cards
        deck = Deck(
            id=1,
            name="Test Deck",
            description="Test deck description",
            modification_time=mock_collection.modification_time,
            usn=-1,
            collapsed=False,
            browser_collapsed=False,
            dynamic=False,
            new_today=(0, 0),
            review_today=(0, 0),
            learn_today=(0, 0),
            time_today=(0, 0),
            conf_id=1
        )
        mock_collection.decks[1] = deck
        
        # Add an empty deck
        empty_deck = Deck(
            id=2,
            name="Empty Deck",
            description="Empty deck description",
            modification_time=mock_collection.modification_time,
            usn=-1,
            collapsed=False,
            browser_collapsed=False,
            dynamic=False,
            new_today=(0, 0),
            review_today=(0, 0),
            learn_today=(0, 0),
            time_today=(0, 0),
            conf_id=1
        )
        mock_collection.decks[2] = empty_deck
        
        # Add a card to the deck
        card = Card(
            id=1,
            note_id=1,  # Link to existing note
            deck_id=1,  # Link to Test Deck
            ordinal=0,
            modification_time=mock_collection.modification_time,
            usn=-1,
            type=0,
            queue=0,
            due=0,
            interval=0,
            factor=0,
            reps=0,
            lapses=0,
            left=0,
            original_due=0,
            original_deck_id=0,
            flags=0
        )
        mock_collection.cards[1] = card
        
        # Test with default arguments (hide empty models and decks)
        operation = self.operation_class()
        operation.validate(mock_collection)
        result = operation.execute()
        
        # Verify result
        assert result.success
        assert "models" in result.data
        assert "decks" in result.data
        assert "examples" in result.data
        
        # Check models data
        models_data = result.data["models"]
        assert "Basic" in models_data  # Basic model should be included (has notes)
        assert "Empty Model" not in models_data  # Empty model should be excluded
        
        # Check decks data
        decks_data = result.data["decks"]
        assert "Test Deck" in decks_data  # Test Deck should be included (has cards)
        assert "Empty Deck" not in decks_data  # Empty Deck should be excluded
        
        # Check examples data
        examples_data = result.data["examples"]
        assert "Basic" in examples_data  # Should have examples for Basic model
        assert len(examples_data["Basic"]) <= 3  # Should have at most 3 examples
        
        # Test with show_empty_models=True and show_empty_decks=True
        operation = self.operation_class(show_empty_models=True, show_empty_decks=True)
        operation.validate(mock_collection)
        result = operation.execute()
        
        # Verify result
        models_data = result.data["models"]
        assert "Basic" in models_data  # Basic model should be included
        assert "Empty Model" in models_data  # Empty model should now be included
        
        decks_data = result.data["decks"]
        assert "Test Deck" in decks_data  # Test Deck should be included
        assert "Empty Deck" in decks_data  # Empty Deck should now be included
        
        # Test with custom example_count
        operation = self.operation_class(example_count=1)
        operation.validate(mock_collection)
        result = operation.execute()
        
        # Verify result
        examples_data = result.data["examples"]
        assert len(examples_data["Basic"]) <= 1  # Should have at most 1 example 