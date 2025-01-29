import pytest
import json
import tempfile
from pathlib import Path
from anki_context import AnkiContext
from operations import OperationType, OperationRecipe
from populators.copy_field import CopyFieldPopulator
from populators.concat_fields import ConcatFieldsPopulator
from anki_types import Note

def create_test_config(tmp_path: Path, config: dict) -> Path:
    """Helper to create a temporary config file."""
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
    return config_path

def test_copy_field_populator(tmp_path):
    """Test that copy field populator works correctly."""
    # Create test config
    config = {
        "source_field": "Front",
        "target_field": "Back"
    }
    config_path = create_test_config(tmp_path, config)
    
    # Create output file
    output_path = tmp_path / "output.apkg"
    
    # Run populate fields operation
    with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as context:
        recipe = OperationRecipe(
            operation_type=OperationType.POPULATE_FIELDS,
            model_name="Basic Card",
            populator_class="populators.copy_field.CopyFieldPopulator",
            populator_config=str(config_path)
        )
        context.run(recipe)
    
    # Verify changes
    with AnkiContext(output_path, read_only=True) as context:
        example = context._operations._read_ops.get_note_example("Basic Card")
        assert example["Back"] == example["Front"]

def test_concat_fields_populator(tmp_path):
    """Test that concat fields populator works correctly."""
    # First add a new field to copy into
    output1 = tmp_path / "with_new_field.apkg"
    with AnkiContext("test_data/jap.apkg", output1, read_only=False) as context:
        # Add new model with extra field
        context.run(OperationRecipe(
            operation_type=OperationType.ADD_MODEL,
            model_name="Test Model",
            fields=["Front", "Back", "Combined"],
            template_name="Card 1",
            question_format="{{Front}}",
            answer_format="{{Back}}",
            css=".card { font-family: arial; }"
        ))
        
        # Migrate notes to new model
        context.run(OperationRecipe(
            operation_type=OperationType.MIGRATE_NOTES,
            model_name="Basic Card",
            target_model_name="Test Model",
            field_mapping='{"Front": "Front", "Back": "Back"}'
        ))
    
    # Now test concatenation
    config = {
        "source_fields": ["Front", "Back"],
        "target_field": "Combined",
        "separator": " - "
    }
    config_path = create_test_config(tmp_path, config)
    output2 = tmp_path / "populated.apkg"
    
    with AnkiContext(output1, output2, read_only=False) as context:
        recipe = OperationRecipe(
            operation_type=OperationType.POPULATE_FIELDS,
            model_name="Test Model",
            populator_class="populators.concat_fields.ConcatFieldsPopulator",
            populator_config=str(config_path)
        )
        context.run(recipe)
    
    # Verify changes
    with AnkiContext(output2, read_only=True) as context:
        example = context._operations._read_ops.get_note_example("Test Model")
        assert example["Combined"] == f"{example['Front']} - {example['Back']}"

def test_copy_field_populator_missing_source(tmp_path):
    """Test that copy field populator handles missing source field."""
    config = {
        "source_field": "NonExistent",
        "target_field": "Back"
    }
    config_path = create_test_config(tmp_path, config)
    
    # Create output file
    output_path = tmp_path / "output.apkg"
    
    # Run populate fields operation
    with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as context:
        recipe = OperationRecipe(
            operation_type=OperationType.POPULATE_FIELDS,
            model_name="Basic Card",
            populator_class="populators.copy_field.CopyFieldPopulator",
            populator_config=str(config_path)
        )
        # Should log warning and skip notes, but not fail
        context.run(recipe)

def test_concat_fields_populator_missing_source(tmp_path):
    """Test that concat fields populator handles missing source field."""
    config = {
        "source_fields": ["Front", "NonExistent"],
        "target_field": "Back"
    }
    config_path = create_test_config(tmp_path, config)
    
    # Create output file
    output_path = tmp_path / "output.apkg"
    
    # Run populate fields operation
    with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as context:
        recipe = OperationRecipe(
            operation_type=OperationType.POPULATE_FIELDS,
            model_name="Basic Card",
            populator_class="populators.concat_fields.ConcatFieldsPopulator",
            populator_config=str(config_path)
        )
        # Should log warning and skip notes, but not fail
        context.run(recipe)

def test_invalid_populator_class(tmp_path):
    """Test that invalid populator class is handled gracefully."""
    config_path = create_test_config(tmp_path, {})
    output_path = tmp_path / "output.apkg"
    
    with pytest.raises(ValueError, match="Could not load populator class"):
        with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as context:
            recipe = OperationRecipe(
                operation_type=OperationType.POPULATE_FIELDS,
                model_name="Basic Card",
                populator_class="nonexistent.populator.Class",
                populator_config=str(config_path)
            )
            context.run(recipe)

def test_invalid_config_file(tmp_path):
    """Test that invalid config file is handled gracefully."""
    # Create invalid JSON file
    config_path = tmp_path / "invalid.json"
    with open(config_path, "w") as f:
        f.write("invalid json")
    
    output_path = tmp_path / "output.apkg"
    
    with pytest.raises(ValueError, match="Invalid populator configuration"):
        with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as context:
            recipe = OperationRecipe(
                operation_type=OperationType.POPULATE_FIELDS,
                model_name="Basic Card",
                populator_class="populators.copy_field.CopyFieldPopulator",
                populator_config=str(config_path)
            )
            context.run(recipe)

def test_missing_config_fields(tmp_path):
    """Test that missing required config fields are handled gracefully."""
    config = {}  # Missing required fields
    config_path = create_test_config(tmp_path, config)
    output_path = tmp_path / "output.apkg"
    
    with pytest.raises(ValueError, match="Config must specify"):
        with AnkiContext("test_data/jap.apkg", output_path, read_only=False) as context:
            recipe = OperationRecipe(
                operation_type=OperationType.POPULATE_FIELDS,
                model_name="Basic Card",
                populator_class="populators.copy_field.CopyFieldPopulator",
                populator_config=str(config_path)
            )
            context.run(recipe)

def test_concat_fields_batch_populator(tmp_path):
    """Test batch processing with ConcatFieldsPopulator."""
    # Create config file
    config_path = tmp_path / "concat_config.json"
    config = {
        "source_fields": ["Front", "Back"],
        "target_field": "Combined",
        "separator": " | "
    }
    with open(config_path, "w") as f:
        json.dump(config, f)
    
    # Create test notes
    notes = [
        Note(
            id=1,
            guid="abc123",
            model_id=1000,
            modification_time=0,
            usn=-1,
            tags="",
            fields={"Front": "Hello", "Back": "World"},
            sort_field=0,
            checksum=0
        ),
        Note(
            id=2,
            guid="def456",
            model_id=1000,
            modification_time=0,
            usn=-1,
            tags="",
            fields={"Front": "Test", "Back": "Note"},
            sort_field=0,
            checksum=0
        ),
        Note(
            id=3,
            guid="ghi789",
            model_id=1000,
            modification_time=0,
            usn=-1,
            tags="",
            fields={"Front": "Missing", "Other": "Field"},  # Missing Back field
            sort_field=0,
            checksum=0
        ),
        Note(
            id=4,
            guid="jkl012",
            model_id=1000,
            modification_time=0,
            usn=-1,
            tags="",
            fields={"Front": "Another", "Back": "One"},
            sort_field=0,
            checksum=0
        )
    ]
    
    # Create populator
    populator = ConcatFieldsPopulator(str(config_path))
    
    # Test batch population
    updates = populator.populate_batch(notes)
    
    # Verify updates
    assert len(updates) == 3  # Should skip note with missing field
    assert updates[1] == {"Combined": "Hello | World"}
    assert updates[2] == {"Combined": "Test | Note"}
    assert updates[4] == {"Combined": "Another | One"}
    assert 3 not in updates  # Note 3 should be skipped

def test_concat_fields_batch_all_missing(tmp_path):
    """Test batch processing when all notes are missing required fields."""
    # Create config file
    config_path = tmp_path / "concat_config.json"
    config = {
        "source_fields": ["Field1", "Field2"],
        "target_field": "Combined"
    }
    with open(config_path, "w") as f:
        json.dump(config, f)
    
    # Create test notes with missing fields
    notes = [
        Note(
            id=1,
            guid="abc123",
            model_id=1000,
            modification_time=0,
            usn=-1,
            tags="",
            fields={"Other": "Field"},
            sort_field=0,
            checksum=0
        ),
        Note(
            id=2,
            guid="def456",
            model_id=1000,
            modification_time=0,
            usn=-1,
            tags="",
            fields={"Another": "Field"},
            sort_field=0,
            checksum=0
        )
    ]
    
    # Create populator
    populator = ConcatFieldsPopulator(str(config_path))
    
    # Test batch population
    with pytest.raises(ValueError, match="Source fields not found in any note: \\['Field1', 'Field2'\\]"):
        populator.populate_batch(notes)

def test_jap_llm_populator(tmp_path, monkeypatch):
    """Test that Japanese LLM populator works correctly for a single note."""
    # Mock OpenAI API response
    class MockResponse:
        def __init__(self, content):
            self.choices = [
                type('Choice', (), {
                    'message': type('Message', (), {
                        'content': content
                    })()
                })
            ]

    class MockOpenAI:
        def __init__(self, api_key):
            self.chat = type('Chat', (), {
                'completions': type('Completions', (), {
                    'create': self.mock_create
                })()
            })()

        def mock_create(self, **kwargs):
            # Return a string that matches what the OpenAI API would return
            return MockResponse('{"analyses":[{"translation":"I want to protect you.","words":[{"jap":"守りたい (mamoritai)","eng":"want to protect"}],"nuance":"Expresses a strong desire to protect someone, showing care and determination"}]}')

    # Mock OpenAI client
    monkeypatch.setattr("populators.jap_llm.OpenAI", MockOpenAI)

    # Create test config
    config = {
        "source_field": "Japanese",
        "translation_field": "Translation",
        "breakdown_field": "Breakdown",
        "nuance_field": "Nuance",
        "api_key": "dummy-key"
    }
    config_path = create_test_config(tmp_path, config)

    # Create test note
    note = Note(
        id=1,
        guid="test123",
        model_id=1000,
        modification_time=0,
        usn=-1,
        tags=[],
        fields={
            "Japanese": "助けられてばっか",
            "Translation": "",
            "Breakdown": "",
            "Nuance": ""
        },
        sort_field=0,
        checksum=0
    )

    # Create and run populator
    from populators.jap_llm import JapLlmPopulator
    populator = JapLlmPopulator(str(config_path))
    updates = populator.populate_fields(note)

    # Verify updates
    assert updates["Translation"] == "I want to protect you."
    assert "守りたい (mamoritai): want to protect" in updates["Breakdown"]
    assert updates["Nuance"] == "Expresses a strong desire to protect someone, showing care and determination"

def test_jap_llm_populator_batch(tmp_path, monkeypatch):
    """Test that Japanese LLM populator works correctly for batch processing."""
    # Mock OpenAI API response
    class MockResponse:
        def __init__(self, content):
            self.choices = [
                type('Choice', (), {
                    'message': type('Message', (), {
                        'content': content
                    })()
                })
            ]

    class MockOpenAI:
        def __init__(self, api_key):
            self.chat = type('Chat', (), {
                'completions': type('Completions', (), {
                    'create': self.mock_create
                })()
            })()

        def mock_create(self, **kwargs):
            # Return a string that matches what the OpenAI API would return for multiple sentences
            return MockResponse('{"analyses":[{"translation":"I want to protect you.","words":[{"jap":"守りたい (mamoritai)","eng":"want to protect"}],"nuance":"Expresses a strong desire to protect someone, showing care and determination"},{"translation":"Thank you very much.","words":[{"jap":"ありがとうございました (arigatou gozaimashita)","eng":"thank you very much (polite past)"}],"nuance":"A very polite expression of gratitude for a past action"}]}')

    # Mock OpenAI client
    monkeypatch.setattr("populators.jap_llm.OpenAI", MockOpenAI)

    # Create test config
    config = {
        "source_field": "Japanese",
        "translation_field": "Translation",
        "breakdown_field": "Breakdown",
        "nuance_field": "Nuance",
        "api_key": "dummy-key"
    }
    config_path = create_test_config(tmp_path, config)

    # Create test notes
    notes = [
        Note(
            id=1,
            guid="abc123",
            model_id=1000,
            modification_time=0,
            usn=-1,
            tags=[],
            fields={
                "Japanese": "助けられて",
                "Translation": "",
                "Breakdown": "",
                "Nuance": ""
            },
            sort_field=0,
            checksum=0
        ),
        Note(
            id=2,
            guid="def456",
            model_id=1000,
            modification_time=0,
            usn=-1,
            tags=[],
            fields={
                "Japanese": "ありがとう",
                "Translation": "",
                "Breakdown": "",
                "Nuance": ""
            },
            sort_field=0,
            checksum=0
        ),
        Note(
            id=3,
            guid="ghi789",
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
    from populators.jap_llm import JapLlmPopulator
    populator = JapLlmPopulator(str(config_path))
    updates = populator.populate_batch(notes)

    # Verify updates
    assert len(updates) == 2  # Should skip note with missing field
    assert updates[1]["Translation"] == "I want to protect you."
    assert "守りたい (mamoritai): want to protect" in updates[1]["Breakdown"]
    assert updates[1]["Nuance"] == "Expresses a strong desire to protect someone, showing care and determination"
    assert updates[2]["Translation"] == "Thank you very much."
    assert "ありがとうございました (arigatou gozaimashita): thank you very much (polite past)" in updates[2]["Breakdown"]
    assert updates[2]["Nuance"] == "A very polite expression of gratitude for a past action"
    assert 3 not in updates  # Note 3 should be skipped 