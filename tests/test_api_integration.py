import pytest
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from anki_terminal.anki_types import Note
from anki_terminal.populators.jap_llm import JapLlmPopulator

# Load environment variables from .env file
load_dotenv()

def create_test_config(tmp_path: Path, config: dict) -> Path:
    """Helper to create a temporary config file."""
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
    return config_path

def requires_api_key(func):
    """Decorator to skip tests if API key is not available."""
    return pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not found in environment variables"
    )(func)

@pytest.mark.skip(reason="Skipping test due to API key issue")
@pytest.mark.api
@requires_api_key
def test_jap_llm_api_single_note(tmp_path):
    """Test the Japanese LLM populator with a single note using the real OpenAI API."""
    # Create test config without API key (will use from env)
    config = {
        "source_field": "Japanese",
        "translation_field": "Translation",
        "breakdown_field": "Breakdown",
        "nuance_field": "Nuance"
    }
    config_path = create_test_config(tmp_path, config)

    # Create a test note with a real Japanese sentence
    note = Note(
        id=1,
        guid="test1",
        model_id=1000,
        modification_time=0,
        usn=-1,
        tags=[],
        fields={
            "Japanese": "お前を守りたい",  # "I want to protect you"
            "Translation": "",
            "Breakdown": "",
            "Nuance": ""
        },
        sort_field=0,
        checksum=0
    )

    # Create and run populator
    populator = JapLlmPopulator(str(config_path))
    updates = populator.populate_fields(note)

    # Verify the structure and content of the response
    assert "Translation" in updates
    assert "Breakdown" in updates
    assert "Nuance" in updates
    assert updates["Translation"], "Translation should not be empty"
    assert updates["Breakdown"], "Breakdown should not be empty"
    assert updates["Nuance"], "Nuance should not be empty"
    
    # Verify content matches expectations
    assert "protect" in updates["Translation"].lower()
    assert "守" in updates["Breakdown"]  # Should contain the kanji for "protect"
    assert "たい" in updates["Breakdown"]  # Should mention the desire form

@pytest.mark.api
@requires_api_key
def test_jap_llm_api_batch(tmp_path):
    """Test the Japanese LLM populator with multiple notes using the real OpenAI API."""
    # Create test config without API key (will use from env)
    config = {
        "source_field": "Japanese",
        "translation_field": "Translation",
        "breakdown_field": "Breakdown",
        "nuance_field": "Nuance"
    }
    config_path = create_test_config(tmp_path, config)

    # Create test notes with real Japanese sentences
    notes = [
        Note(
            id=1,
            guid="test1",
            model_id=1000,
            modification_time=0,
            usn=-1,
            tags=[],
            fields={
                "Japanese": "お前を守りたい",  # "I want to protect you"
                "Translation": "",
                "Breakdown": "",
                "Nuance": ""
            },
            sort_field=0,
            checksum=0
        ),
        Note(
            id=2,
            guid="test2",
            model_id=1000,
            modification_time=0,
            usn=-1,
            tags=[],
            fields={
                "Japanese": "ありがとうございました",  # "Thank you very much (polite past)"
                "Translation": "",
                "Breakdown": "",
                "Nuance": ""
            },
            sort_field=0,
            checksum=0
        ),
        Note(
            id=3,
            guid="test3",
            model_id=1000,
            modification_time=0,
            usn=-1,
            tags=[],
            fields={"Other": "Field"},  # Missing Japanese field
            sort_field=0,
            checksum=0
        )
    ]

    # Create and run populator
    populator = JapLlmPopulator(str(config_path))
    updates = populator.populate_batch(notes)

    # Verify basic structure
    assert len(updates) == 2  # Should skip note with missing field
    assert 1 in updates
    assert 2 in updates
    assert 3 not in updates  # Should skip note with missing field

    # Verify first note (protect)
    assert "protect" in updates[1]["Translation"].lower()
    assert "守" in updates[1]["Breakdown"]
    assert updates[1]["Nuance"]

    # Verify second note (thank you)
    assert "thank" in updates[2]["Translation"].lower()
    assert "ありがとう" in updates[2]["Breakdown"]
    assert "polite" in updates[2]["Nuance"].lower()