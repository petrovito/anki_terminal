from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from anki_terminal.anki_types import Field, Model, Note
from anki_terminal.populators.furigana_populator import FuriganaPopulator


@pytest.fixture
def sample_model():
    """Create a sample model for testing."""
    return Model(
        id=1,
        name="Japanese",
        fields=[
            Field(name="Japanese", ordinal=0),
            Field(name="Reading", ordinal=1),
            Field(name="Meaning", ordinal=2)
        ],
        templates=[],
        css="",
        deck_id=1,
        modification_time=datetime.now(),
        type=0,
        usn=-1,
        version=1
    )


@pytest.fixture
def sample_note():
    """Create a sample note for testing."""
    return Note(
        id=1,
        guid="test",
        model_id=1,
        modification_time=datetime.now(),
        usn=-1,
        tags=[],
        fields={
            "Japanese": "私は昨日、東京に行きました。",
            "Reading": "",
            "Meaning": "I went to Tokyo yesterday."
        },
        sort_field=0,
        checksum=0,
        flags=0
    )


class MockKakasi:
    """Mock kakasi for testing."""
    
    def convert(self, text):
        """Mock convert method."""
        if text == "私は昨日、東京に行きました。":
            return [
                {'orig': '私', 'hira': 'わたし'},
                {'orig': 'は', 'hira': 'は'},
                {'orig': '昨日', 'hira': 'きのう'},
                {'orig': '、', 'hira': '、'},
                {'orig': '東京', 'hira': 'とうきょう'},
                {'orig': 'に', 'hira': 'に'},
                {'orig': '行き', 'hira': 'いき'},
                {'orig': 'ました', 'hira': 'ました'},
                {'orig': '。', 'hira': '。'}
            ]
        return []


@patch('anki_terminal.populators.furigana_populator.kakasi', return_value=MockKakasi())
def test_furigana_populator(mock_kakasi, sample_model, sample_note):
    """Test the furigana populator."""
    # Create populator
    populator = FuriganaPopulator({
        "source_field": "Japanese",
        "target_field": "Reading"
    })
    
    # Validate populator
    populator.validate(sample_model)
    
    # Populate fields
    result = populator.populate_fields(sample_note)
    
    # Check result
    assert "Reading" in result
    assert result["Reading"] == "私[わたし]は昨日[きのう]、東京[とうきょう]に行き[いき]ました。"


@patch('anki_terminal.populators.furigana_populator.kakasi', return_value=MockKakasi())
def test_furigana_populator_batch(mock_kakasi, sample_model, sample_note):
    """Test the furigana populator with batch processing."""
    # Create populator
    populator = FuriganaPopulator({
        "source_field": "Japanese",
        "target_field": "Reading"
    })
    
    # Validate populator
    populator.validate(sample_model)
    
    # Populate fields in batch
    result = populator.populate_batch([sample_note])
    
    # Check result
    assert 1 in result
    assert "Reading" in result[1]
    assert result[1]["Reading"] == "私[わたし]は昨日[きのう]、東京[とうきょう]に行き[いき]ました。"


def test_furigana_populator_validation(sample_model):
    """Test validation of the furigana populator."""
    # Create populator with invalid source field
    populator = FuriganaPopulator({
        "source_field": "NonExistentField",
        "target_field": "Reading"
    })
    
    # Validation should fail
    with pytest.raises(ValueError, match="Source field 'NonExistentField' not found in model"):
        populator.validate(sample_model)


@patch('anki_terminal.populators.furigana_populator.kakasi', return_value=MockKakasi())
def test_add_furigana(mock_kakasi):
    """Test the _add_furigana method."""
    populator = FuriganaPopulator({
        "source_field": "Japanese",
        "target_field": "Reading"
    })
    
    # Test with Japanese text
    result = populator._add_furigana("私は昨日、東京に行きました。")
    assert result == "私[わたし]は昨日[きのう]、東京[とうきょう]に行き[いき]ました。"
    
    # Test with empty text
    result = populator._add_furigana("")
    assert result == "" 