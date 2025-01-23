import pytest
from pathlib import Path
from anki_context import AnkiContext
from operations import OperationType, OperationRecipe

@pytest.fixture
def operations():
    """Fixture that provides an Operations instance with loaded test data."""
    apkg_path = Path("test_data/jap.apkg")
    with AnkiContext(apkg_path) as inspector:
        yield inspector._operations  # Now yielding the full operations object

@pytest.fixture
def read_operations(operations):
    """Fixture that provides read operations instance."""
    return operations.read_ops

@pytest.fixture
def write_operations(operations):
    """Fixture that provides write operations instance."""
    return operations.write_ops

def test_num_cards(read_operations):
    """Test counting total number of cards."""
    assert read_operations.num_cards() == 46

def test_list_models(read_operations):
    """Test listing all models."""
    models = read_operations.list_models()
    assert len(models) == 1
    assert models[0] == {
        "name": "Basic Card",
        "id": 1195811629,
        "type": "Standard"
    }

def test_list_templates(read_operations):
    """Test listing templates for a model."""
    # Test with default model (only one exists)
    templates = read_operations.list_templates()
    assert len(templates) == 1
    assert templates[0] == {
        "name": "Japanese Character",
        "ordinal": 0
    }

    # Test with explicit model name
    templates = read_operations.list_templates("Basic Card")
    assert len(templates) == 1
    assert templates[0] == {
        "name": "Japanese Character",
        "ordinal": 0
    }

    # Test with non-existent model
    with pytest.raises(ValueError, match="Model not found: NonExistent"):
        read_operations.list_templates("NonExistent")

def test_list_fields(read_operations):
    """Test listing fields for a model."""
    # Test with default model
    fields = read_operations.list_fields()
    assert fields == [
        {"name": "Front", "type": "text"},
        {"name": "Back", "type": "text"}
    ]

    # Test with explicit model name
    fields = read_operations.list_fields("Basic Card")
    assert fields == [
        {"name": "Front", "type": "text"},
        {"name": "Back", "type": "text"}
    ]

    # Test with non-existent model
    with pytest.raises(ValueError, match="Model not found: NonExistent"):
        read_operations.list_fields("NonExistent")

def test_get_question_format(read_operations):
    """Test getting question format."""
    expected = "{{Front}}\n<br>\n{{type:Back}}\n"
    
    # Test with default model/template
    assert read_operations.get_question_format() == expected
    
    # Test with explicit model
    assert read_operations.get_question_format("Basic Card") == expected
    
    # Test with explicit model and template
    assert read_operations.get_question_format("Basic Card", "Japanese Character") == expected
    
    # Test with non-existent model
    with pytest.raises(ValueError, match="Model not found: NonExistent"):
        read_operations.get_question_format("NonExistent")
    
    # Test with non-existent template
    with pytest.raises(ValueError, match="Template not found: NonExistent"):
        read_operations.get_question_format("Basic Card", "NonExistent")

def test_get_answer_format(read_operations):
    """Test getting answer format."""
    expected = "{{FrontSide}}\n<hr id=answer>\n<hr id=answer>\n\n<div \nfont-size: 4px;\ncolor: white;\n{{Back}}\n</div>"
    
    # Test with default model/template
    assert read_operations.get_answer_format() == expected
    
    # Test with explicit model
    assert read_operations.get_answer_format("Basic Card") == expected
    
    # Test with explicit model and template
    assert read_operations.get_answer_format("Basic Card", "Japanese Character") == expected

def test_get_css(read_operations):
    """Test getting CSS."""
    expected = ".card {\n font-family: arial;\n font-size: 60px;\n text-align: center;\n color: black;\n background-color: white;\n}\n\n\n"
    
    # Test with default model
    assert read_operations.get_css() == expected
    
    # Test with explicit model
    assert read_operations.get_css("Basic Card") == expected

def test_get_note_example(read_operations):
    """Test getting an example note."""
    # Test with default model
    example = read_operations.get_note_example()
    assert isinstance(example, dict)
    assert set(example.keys()) == {"Front", "Back"}
    assert isinstance(example["Front"], str)
    assert isinstance(example["Back"], str)
    
    # Test with explicit model name
    example = read_operations.get_note_example("Basic Card")
    assert isinstance(example, dict)
    assert set(example.keys()) == {"Front", "Back"}
    assert isinstance(example["Front"], str)
    assert isinstance(example["Back"], str)
    
    # Test with non-existent model
    with pytest.raises(ValueError, match="Model not found: NonExistent"):
        read_operations.get_note_example("NonExistent")

def test_rename_field(write_operations):
    """Test renaming a field."""
    # Test with default model
    write_operations.rename_field(None, "Front", "Question")
    
    # Verify the field was renamed in model
    model = next(iter(write_operations.collection.models.values()))
    assert "Question" in model.fields
    assert "Front" not in model.fields
    
    # Verify the field was renamed in notes
    note = write_operations.collection.notes[0]
    assert "Question" in note.fields
    assert "Front" not in note.fields
    
    # Test with non-existent model
    with pytest.raises(ValueError, match="Model not found: NonExistent"):
        write_operations.rename_field("NonExistent", "Back", "Answer")
    
    # Test with non-existent field
    with pytest.raises(ValueError, match="Field 'NonExistent' not found"):
        write_operations.rename_field(None, "NonExistent", "NewField")
    
    # Test with duplicate field name
    with pytest.raises(ValueError, match="Field 'Back' already exists"):
        write_operations.rename_field(None, "Question", "Back") 