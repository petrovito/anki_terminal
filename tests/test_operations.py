import pytest
from pathlib import Path
from anki_inspector import AnkiInspector
from operations import OperationType, OperationRecipe
from read_operations import ReadOperations

@pytest.fixture
def operations():
    """Fixture that provides an Operations instance with loaded test data."""
    apkg_path = Path("test_data/jap.apkg")
    with AnkiInspector(apkg_path) as inspector:
        yield inspector.operations.read_ops  # Now yielding read_ops directly

def test_num_cards(operations):
    """Test counting total number of cards."""
    assert operations.num_cards() == 46

def test_list_models(operations):
    """Test listing all models."""
    models = operations.list_models()
    assert len(models) == 1
    assert models[0] == {
        "name": "Basic Card",
        "id": 1195811629,
        "type": "Standard"
    }

def test_list_templates(operations):
    """Test listing templates for a model."""
    # Test with default model (only one exists)
    templates = operations.list_templates()
    assert len(templates) == 1
    assert templates[0] == {
        "name": "Japanese Character",
        "ordinal": 0
    }

    # Test with explicit model name
    templates = operations.list_templates("Basic Card")
    assert len(templates) == 1
    assert templates[0] == {
        "name": "Japanese Character",
        "ordinal": 0
    }

    # Test with non-existent model
    with pytest.raises(ValueError, match="Model not found: NonExistent"):
        operations.list_templates("NonExistent")

def test_list_fields(operations):
    """Test listing fields for a model."""
    # Test with default model
    fields = operations.list_fields()
    assert fields == [
        {"name": "Front", "type": "text"},
        {"name": "Back", "type": "text"}
    ]

    # Test with explicit model name
    fields = operations.list_fields("Basic Card")
    assert fields == [
        {"name": "Front", "type": "text"},
        {"name": "Back", "type": "text"}
    ]

    # Test with non-existent model
    with pytest.raises(ValueError, match="Model not found: NonExistent"):
        operations.list_fields("NonExistent")

def test_get_question_format(operations):
    """Test getting question format."""
    expected = "{{Front}}\n<br>\n{{type:Back}}\n"
    
    # Test with default model/template
    assert operations.get_question_format() == expected
    
    # Test with explicit model
    assert operations.get_question_format("Basic Card") == expected
    
    # Test with explicit model and template
    assert operations.get_question_format("Basic Card", "Japanese Character") == expected
    
    # Test with non-existent model
    with pytest.raises(ValueError, match="Model not found: NonExistent"):
        operations.get_question_format("NonExistent")
    
    # Test with non-existent template
    with pytest.raises(ValueError, match="Template not found: NonExistent"):
        operations.get_question_format("Basic Card", "NonExistent")

def test_get_answer_format(operations):
    """Test getting answer format."""
    expected = "{{FrontSide}}\n<hr id=answer>\n<hr id=answer>\n\n<div \nfont-size: 4px;\ncolor: white;\n{{Back}}\n</div>"
    
    # Test with default model/template
    assert operations.get_answer_format() == expected
    
    # Test with explicit model
    assert operations.get_answer_format("Basic Card") == expected
    
    # Test with explicit model and template
    assert operations.get_answer_format("Basic Card", "Japanese Character") == expected

def test_get_css(operations):
    """Test getting CSS."""
    expected = ".card {\n font-family: arial;\n font-size: 60px;\n text-align: center;\n color: black;\n background-color: white;\n}\n\n\n"
    
    # Test with default model
    assert operations.get_css() == expected
    
    # Test with explicit model
    assert operations.get_css("Basic Card") == expected 