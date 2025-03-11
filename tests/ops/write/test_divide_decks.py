import pytest

from anki_terminal.commons.anki_types import Card, Deck, Field, Model, Note, Template
from anki_terminal.ops.write.divide_decks import DivideIntoDecksByTagsOperation
from tests.fixtures.test_data_fixtures import apkg_v21_path
from tests.ops.base_write_test import BaseWriteTest
from tests.ops.test_base import OperationTestBase


class TestDivideIntoDecksByTagsOperation(OperationTestBase):
    """Test the divide decks by tags operation."""
    
    operation_class = DivideIntoDecksByTagsOperation
    
    def test_validation(self, mock_collection):
        """Test operation validation."""
        self.collection = mock_collection
        
        # Create a test model
        self.model = Model(
            id=1,
            name="Test Model",
            fields=[
                Field(name="Front", ordinal=0),
                Field(name="Back", ordinal=1)
            ],
            templates=[
                Template(name="Card 1", question_format="{{Front}}", answer_format="{{Back}}", ordinal=0)
            ],
            css="",
            deck_id=1,
            modification_time=mock_collection.modification_time,
            type=0,
            usn=0,
            version=0
        )
        
        # Create a source deck
        self.source_deck = Deck(
            id=1,
            name="Source Deck",
            description="",
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
        
        # Create test notes with tags
        self.notes = [
            Note(
                id=1,
                guid="guid1",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=["Episode_1", "Episode_2"],
                fields={
                    "Front": "Front 1",
                    "Back": "Back 1"
                },
                sort_field=0,
                checksum=0
            ),
            Note(
                id=2,
                guid="guid2",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=["Episode_5"],
                fields={
                    "Front": "Front 2",
                    "Back": "Back 2"
                },
                sort_field=0,
                checksum=0
            ),
            Note(
                id=3,
                guid="guid3",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=["Episode_10", "Episode_11"],
                fields={
                    "Front": "Front 3",
                    "Back": "Back 3"
                },
                sort_field=0,
                checksum=0
            )
        ]
        
        # Create cards for each note
        self.cards = [
            Card(
                id=1,
                note_id=1,
                deck_id=self.source_deck.id,
                ordinal=0,
                modification_time=mock_collection.modification_time,
                usn=0,
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
            ),
            Card(
                id=2,
                note_id=2,
                deck_id=self.source_deck.id,
                ordinal=0,
                modification_time=mock_collection.modification_time,
                usn=0,
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
            ),
            Card(
                id=3,
                note_id=3,
                deck_id=self.source_deck.id,
                ordinal=0,
                modification_time=mock_collection.modification_time,
                usn=0,
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
        ]
        
        # Add model, deck, notes, and cards to collection
        self.collection.models[self.model.id] = self.model
        self.collection.decks[self.source_deck.id] = self.source_deck
        for note in self.notes:
            self.collection.notes[note.id] = note
        for card in self.cards:
            self.collection.cards[card.id] = card
        
        # Test with valid arguments
        operation = DivideIntoDecksByTagsOperation(
            source_deck="Source Deck",
            tag_prefix="Episode",
            tag_pattern=r"Episode_(\d+)",
            episodes_per_deck=5
        )
        operation.validate(self.collection)
        
        # Test with non-existent source deck
        with pytest.raises(ValueError, match="Source deck 'Non-existent Deck' not found"):
            operation = DivideIntoDecksByTagsOperation(
                source_deck="Non-existent Deck",
                tag_prefix="Episode",
                tag_pattern=r"Episode_(\d+)",
                episodes_per_deck=5
            )
            operation.validate(self.collection)
        
        # Test with invalid tag pattern
        with pytest.raises(ValueError, match="Tag pattern must contain at least one capture group"):
            operation = DivideIntoDecksByTagsOperation(
                source_deck="Source Deck",
                tag_prefix="Episode",
                tag_pattern=r"Episode_\d+",
                episodes_per_deck=5
            )
            operation.validate(self.collection)
        
        # Test with invalid episodes per deck
        with pytest.raises(ValueError, match="Episodes per deck must be a positive integer"):
            operation = DivideIntoDecksByTagsOperation(
                source_deck="Source Deck",
                tag_prefix="Episode",
                tag_pattern=r"Episode_(\d+)",
                episodes_per_deck=0
            )
            operation.validate(self.collection)
    
    def test_execution(self, mock_collection):
        """Test operation execution."""
        self.collection = mock_collection
        
        # Create a test model
        self.model = Model(
            id=1,
            name="Test Model",
            fields=[
                Field(name="Front", ordinal=0),
                Field(name="Back", ordinal=1)
            ],
            templates=[
                Template(name="Card 1", question_format="{{Front}}", answer_format="{{Back}}", ordinal=0)
            ],
            css="",
            deck_id=1,
            modification_time=mock_collection.modification_time,
            type=0,
            usn=0,
            version=0
        )
        
        # Create a source deck
        self.source_deck = Deck(
            id=1,
            name="Source Deck",
            description="",
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
        
        # Create test notes with tags
        self.notes = [
            Note(
                id=1,
                guid="guid1",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=["Episode_1", "Episode_2"],
                fields={
                    "Front": "Front 1",
                    "Back": "Back 1"
                },
                sort_field=0,
                checksum=0
            ),
            Note(
                id=2,
                guid="guid2",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=["Episode_5"],
                fields={
                    "Front": "Front 2",
                    "Back": "Back 2"
                },
                sort_field=0,
                checksum=0
            ),
            Note(
                id=3,
                guid="guid3",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=["Episode_10", "Episode_11"],
                fields={
                    "Front": "Front 3",
                    "Back": "Back 3"
                },
                sort_field=0,
                checksum=0
            ),
            Note(
                id=4,
                guid="guid4",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=["OtherTag"],
                fields={
                    "Front": "Front 4",
                    "Back": "Back 4"
                },
                sort_field=0,
                checksum=0
            )
        ]
        
        # Create cards for each note
        self.cards = [
            Card(
                id=1,
                note_id=1,
                deck_id=self.source_deck.id,
                ordinal=0,
                modification_time=mock_collection.modification_time,
                usn=0,
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
            ),
            Card(
                id=2,
                note_id=2,
                deck_id=self.source_deck.id,
                ordinal=0,
                modification_time=mock_collection.modification_time,
                usn=0,
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
            ),
            Card(
                id=3,
                note_id=3,
                deck_id=self.source_deck.id,
                ordinal=0,
                modification_time=mock_collection.modification_time,
                usn=0,
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
            ),
            Card(
                id=4,
                note_id=4,
                deck_id=self.source_deck.id,
                ordinal=0,
                modification_time=mock_collection.modification_time,
                usn=0,
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
        ]
        
        # Add model, deck, notes, and cards to collection
        self.collection.models[self.model.id] = self.model
        self.collection.decks[self.source_deck.id] = self.source_deck
        for note in self.notes:
            self.collection.notes[note.id] = note
        for card in self.cards:
            self.collection.cards[card.id] = card
        
        # Execute the operation
        operation = DivideIntoDecksByTagsOperation(
            source_deck="Source Deck",
            tag_prefix="Episode",
            tag_pattern=r"Episode_(\d+)",
            episodes_per_deck=5
        )
        operation.collection = self.collection
        result = operation.execute()
        
        assert result.success
        assert "Moved 3 cards to 2 decks, skipped 1 cards" in result.message
        
        # Check that cards were moved to the correct decks
        deck_1_5 = None
        deck_6_10 = None
        
        for deck in self.collection.decks.values():
            if deck.name == "Source Deck 1-5":
                deck_1_5 = deck
            elif deck.name == "Source Deck 6-10":
                deck_6_10 = deck
        
        assert deck_1_5 is not None, "Deck 'Source Deck 1-5' not found"
        assert deck_6_10 is not None, "Deck 'Source Deck 6-10' not found"
        
        # Check that cards 1 and 2 are in deck 1-5
        assert self.cards[0].deck_id == deck_1_5.id, "Card 1 should be in deck 'Source Deck 1-5'"
        assert self.cards[1].deck_id == deck_1_5.id, "Card 2 should be in deck 'Source Deck 1-5'"
        
        # Check that card 3 is in deck 6-10
        assert self.cards[2].deck_id == deck_6_10.id, "Card 3 should be in deck 'Source Deck 6-10'"
        
        # Check that card 4 is still in the source deck
        assert self.cards[3].deck_id == self.source_deck.id, "Card 4 should still be in the source deck"
    
    def test_target_deck_prefix(self, mock_collection):
        """Test operation with target deck prefix."""
        self.collection = mock_collection
        
        # Create a test model
        self.model = Model(
            id=1,
            name="Test Model",
            fields=[
                Field(name="Front", ordinal=0),
                Field(name="Back", ordinal=1)
            ],
            templates=[
                Template(name="Card 1", question_format="{{Front}}", answer_format="{{Back}}", ordinal=0)
            ],
            css="",
            deck_id=1,
            modification_time=mock_collection.modification_time,
            type=0,
            usn=0,
            version=0
        )
        
        # Create a source deck
        self.source_deck = Deck(
            id=1,
            name="Source Deck",
            description="",
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
        
        # Create test notes with tags
        self.notes = [
            Note(
                id=1,
                guid="guid1",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=["Episode_1"],
                fields={
                    "Front": "Front 1",
                    "Back": "Back 1"
                },
                sort_field=0,
                checksum=0
            ),
            Note(
                id=2,
                guid="guid2",
                model_id=self.model.id,
                modification_time=mock_collection.modification_time,
                usn=0,
                tags=["Episode_10"],
                fields={
                    "Front": "Front 2",
                    "Back": "Back 2"
                },
                sort_field=0,
                checksum=0
            )
        ]
        
        # Create cards for each note
        self.cards = [
            Card(
                id=1,
                note_id=1,
                deck_id=self.source_deck.id,
                ordinal=0,
                modification_time=mock_collection.modification_time,
                usn=0,
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
            ),
            Card(
                id=2,
                note_id=2,
                deck_id=self.source_deck.id,
                ordinal=0,
                modification_time=mock_collection.modification_time,
                usn=0,
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
        ]
        
        # Add model, deck, notes, and cards to collection
        self.collection.models[self.model.id] = self.model
        self.collection.decks[self.source_deck.id] = self.source_deck
        for note in self.notes:
            self.collection.notes[note.id] = note
        for card in self.cards:
            self.collection.cards[card.id] = card
        
        # Execute the operation with target deck prefix
        operation = DivideIntoDecksByTagsOperation(
            source_deck="Source Deck",
            tag_prefix="Episode",
            tag_pattern=r"Episode_(\d+)",
            episodes_per_deck=5,
            target_deck_prefix="Custom Prefix"
        )
        operation.collection = self.collection
        result = operation.execute()
        
        assert result.success
        assert "Moved 2 cards to 2 decks, skipped 0 cards" in result.message
        
        # Check that cards were moved to the correct decks
        deck_1_5 = None
        deck_6_10 = None
        
        for deck in self.collection.decks.values():
            if deck.name == "Custom Prefix 1-5":
                deck_1_5 = deck
            elif deck.name == "Custom Prefix 6-10":
                deck_6_10 = deck
        
        assert deck_1_5 is not None, "Deck 'Custom Prefix 1-5' not found"
        assert deck_6_10 is not None, "Deck 'Custom Prefix 6-10' not found"
        
        # Check that card 1 is in deck 1-5
        assert self.cards[0].deck_id == deck_1_5.id, "Card 1 should be in deck 'Custom Prefix 1-5'"
        
        # Check that card 2 is in deck 6-10
        assert self.cards[1].deck_id == deck_6_10.id, "Card 2 should be in deck 'Custom Prefix 6-10'"


class TestDivideIntoDecksByTagsIntegration(BaseWriteTest):
    """Integration tests for the divide decks by tags operation."""
    
    # Use the existing fixture from test_data_fixtures.py
    versions_to_test = ["v21"]
    
    def setup_before_operation(self, context):
        """Set up test data before operation."""
        self.collection = self.get_collection(context)
        
        # Find the existing "golden kamuy s2" deck
        source_deck = None
        for deck in self.collection.decks.values():
            if deck.name == "golden kamuy s2":
                source_deck = deck
                break
        
        assert source_deck is not None, "Source deck 'golden kamuy s2' not found"
        self.source_deck_id = source_deck.id
        
        # Add Episode tags to notes
        for i, note in enumerate(self.collection.notes.values()):
            episode = (i % 20) + 1  # Episodes 1-20
            if "Episode_" + str(episode) not in note.tags:
                note.tags.append("Episode_" + str(episode))
    
    def get_operation(self):
        """Get the operation to test."""
        return DivideIntoDecksByTagsOperation(
            source_deck="golden kamuy s2",
            tag_prefix="Episode",
            tag_pattern=r"Episode_(\d+)",
            episodes_per_deck=5
        )
    
    def verify_changes(self, context):
        """Verify that the changes were applied correctly."""
        collection = self.get_collection(context)
        
        # Check that the expected decks were created
        expected_decks = ["golden kamuy s2 1-5", "golden kamuy s2 6-10", "golden kamuy s2 11-15", "golden kamuy s2 16-20"]
        found_decks = []
        
        for deck_name in expected_decks:
            deck = None
            for d in collection.decks.values():
                if d.name == deck_name:
                    deck = d
                    found_decks.append(deck_name)
                    break
        
        # We should find at least one of the expected decks
        assert len(found_decks) > 0, f"None of the expected decks were found: {expected_decks}"
        
        # Check that cards were moved to the new decks
        cards_in_new_decks = 0
        for deck_name in found_decks:
            deck = None
            for d in collection.decks.values():
                if d.name == deck_name:
                    deck = d
                    break
            
            # Count cards in this deck
            deck_cards = [card for card in collection.cards.values() if card.deck_id == deck.id]
            cards_in_new_decks += len(deck_cards)
        
        # We should have moved at least one card
        assert cards_in_new_decks > 0, "No cards were moved to the new decks" 