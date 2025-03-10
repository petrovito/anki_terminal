import re
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from anki_terminal.anki_types import Card, Deck, Note
from anki_terminal.changelog import Change, ChangeType
from anki_terminal.ops.op_base import Operation, OperationArgument, OperationResult


class DivideIntoDecksByTagsOperation(Operation):
    """Operation to divide cards into multiple decks based on note tags."""
    
    name = "divide-decks-by-tags"
    description = "Divide cards into multiple decks based on note tags"
    readonly = False
    
    @classmethod
    def setup_subparser(cls, subparser):
        """Set up the subparser for this operation."""
        subparser.add_argument(
            "--source-deck",
            required=True,
            help="Name of the source deck containing all cards"
        )
        subparser.add_argument(
            "--tag-prefix",
            required=True,
            help="Prefix of the tags to use for dividing (e.g., 'Episode')"
        )
        subparser.add_argument(
            "--tag-pattern",
            required=True,
            help="Regular expression pattern to extract episode numbers from tags"
        )
        subparser.add_argument(
            "--episodes-per-deck",
            type=int,
            required=True,
            help="Number of episodes to include in each deck"
        )
        subparser.add_argument(
            "--target-deck-prefix",
            default="",
            help="Prefix for the target deck names (default: source deck name)"
        )
    
    def __init__(self, printer=None, **kwargs):
        """Initialize the operation.
        
        Args:
            **kwargs: Operation-specific arguments
        """
        super().__init__(printer, **kwargs)
        self.args = {
            "source_deck": kwargs["source_deck"],
            "tag_prefix": kwargs["tag_prefix"],
            "tag_pattern": kwargs["tag_pattern"],
            "episodes_per_deck": kwargs["episodes_per_deck"],
            "target_deck_prefix": kwargs.get("target_deck_prefix", "")
        }
        self.changes = []
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed.
        
        Raises:
            ValueError: If validation fails
        """
        # Check if source deck exists
        source_deck = self._get_deck_by_name(self.args["source_deck"])
        if not source_deck:
            raise ValueError(f"Source deck '{self.args['source_deck']}' not found")
        
        # Validate tag pattern
        try:
            pattern = re.compile(self.args["tag_pattern"])
            if pattern.groups == 0:
                raise ValueError("Tag pattern must contain at least one capture group")
        except re.error as e:
            raise ValueError(f"Invalid regular expression pattern: {str(e)}")
        
        # Validate episodes per deck
        if self.args["episodes_per_deck"] <= 0:
            raise ValueError("Episodes per deck must be a positive integer")
    
    def _get_deck_by_name(self, name: str) -> Optional[Deck]:
        """Get a deck by name.
        
        Args:
            name: Name of the deck
            
        Returns:
            The deck, or None if not found
        """
        for deck in self.collection.decks.values():
            if deck.name == name:
                return deck
        return None
    
    def _get_or_create_deck(self, name: str) -> Deck:
        """Get a deck by name, or create it if it doesn't exist.
        
        Args:
            name: Name of the deck
            
        Returns:
            The deck
        """
        deck = self._get_deck_by_name(name)
        if deck:
            return deck
        
        # Create a new deck
        deck_id = max(self.collection.decks.keys(), default=0) + 1
        
        # Create a new deck with current timestamp
        from datetime import datetime
        now = datetime.now()
        
        deck = Deck(
            id=deck_id,
            name=name,
            description="",
            modification_time=now,
            usn=-1,  # -1 indicates a new object
            collapsed=False,
            browser_collapsed=False,
            dynamic=False,
            new_today=(0, 0),
            review_today=(0, 0),
            learn_today=(0, 0),
            time_today=(0, 0),
            conf_id=1  # Default configuration
        )
        
        self.collection.decks[deck_id] = deck
        
        # Record the deck creation
        decks_dict = {}
        for d_id, d in self.collection.decks.items():
            decks_dict[str(d_id)] = {
                "id": d.id,
                "name": d.name,
                "mod": int(d.modification_time.timestamp() * 1000),  # Convert to milliseconds
                "conf": d.conf_id,
                "desc": d.description,
                "dyn": 1 if d.dynamic else 0,
                "collapsed": d.collapsed,
                "browserCollapsed": d.browser_collapsed,
                "usn": d.usn,
                "newToday": list(d.new_today),
                "revToday": list(d.review_today),
                "lrnToday": list(d.learn_today),
                "timeToday": list(d.time_today)
            }
        
        # Add the change to the changelog
        self.changes.append(Change(
            type=ChangeType.DECK_CREATED,
            data={
                'decks': decks_dict
            }
        ))
        
        return deck
    
    def _get_episode_number(self, tag: str) -> Optional[int]:
        """Extract the episode number from a tag.
        
        Args:
            tag: The tag to extract from
            
        Returns:
            The episode number, or None if not found
        """
        pattern = re.compile(self.args["tag_pattern"])
        match = pattern.search(tag)
        if not match:
            return None
        
        try:
            return int(match.group(1))
        except (ValueError, IndexError):
            return None
    
    def _get_episode_range_for_card(self, card: Card) -> Optional[Tuple[int, int]]:
        """Get the episode range for a card based on its note's tags.
        
        Args:
            card: The card to get the episode range for
            
        Returns:
            Tuple of (min_episode, max_episode), or None if no matching tags found
        """
        note = self.collection.notes.get(card.note_id)
        if not note:
            return None
        
        # Find tags with the specified prefix
        episode_numbers = []
        prefix = self.args["tag_prefix"]
        for tag in note.tags:
            if tag.startswith(f"{prefix}_"):
                episode_number = self._get_episode_number(tag)
                if episode_number is not None:
                    episode_numbers.append(episode_number)
        
        if not episode_numbers:
            return None
        
        # Return the range of episode numbers
        return (min(episode_numbers), max(episode_numbers))
    
    def _get_target_deck_name(self, min_episode: int, max_episode: int) -> str:
        """Get the name of the target deck for a range of episodes.
        
        Args:
            min_episode: Minimum episode number in the range
            max_episode: Maximum episode number in the range
            
        Returns:
            Name of the target deck
        """
        episodes_per_deck = self.args["episodes_per_deck"]
        deck_index = (min_episode - 1) // episodes_per_deck
        start_episode = deck_index * episodes_per_deck + 1
        end_episode = (deck_index + 1) * episodes_per_deck
        
        prefix = self.args["target_deck_prefix"] or self.args["source_deck"]
        return f"{prefix} {start_episode}-{end_episode}"
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult indicating success/failure and containing changes
        """
        source_deck = self._get_deck_by_name(self.args["source_deck"])
        
        # Get all cards in the source deck
        source_cards = [
            card for card in self.collection.cards.values()
            if card.deck_id == source_deck.id
        ]
        
        # Group cards by episode range
        cards_by_deck: Dict[str, List[Card]] = defaultdict(list)
        skipped_cards = []
        
        for card in source_cards:
            episode_range = self._get_episode_range_for_card(card)
            if episode_range:
                min_episode, max_episode = episode_range
                target_deck_name = self._get_target_deck_name(min_episode, max_episode)
                cards_by_deck[target_deck_name].append(card)
            else:
                skipped_cards.append(card)
        
        # Create target decks and move cards
        moved_count = 0
        
        for deck_name, cards in cards_by_deck.items():
            target_deck = self._get_or_create_deck(deck_name)
            
            for card in cards:
                # Update card's deck ID
                card.deck_id = target_deck.id
                
                # Record the change
                self.changes.append(Change.card_moved(
                    card.id, source_deck.id, target_deck.id
                ))
                
                moved_count += 1
        
        return OperationResult(
            success=True,
            message=f"Moved {moved_count} cards to {len(cards_by_deck)} decks, skipped {len(skipped_cards)} cards",
            changes=self.changes
        ) 