import pytest
from pathlib import Path
from anki_terminal.script_manager import ScriptManager

def test_list_builtin_scripts():
    """Test listing built-in scripts."""
    manager = ScriptManager()
    scripts = manager.list_builtin_scripts()
    assert isinstance(scripts, list)
    assert "jap_anime_reformat" in scripts

def test_get_builtin_script_path():
    """Test getting path to built-in script."""
    manager = ScriptManager()
    
    # Test with .txt extension
    path = manager.get_builtin_script_path("jap_anime_reformat.txt")
    assert path is not None
    assert path.exists()
    assert path.name == "jap_anime_reformat.txt"
    
    # Test without .txt extension
    path = manager.get_builtin_script_path("jap_anime_reformat")
    assert path is not None
    assert path.exists()
    assert path.name == "jap_anime_reformat.txt"
    
    # Test non-existent script
    path = manager.get_builtin_script_path("nonexistent")
    assert path is None

def test_resolve_script_path(tmp_path):
    """Test resolving script paths."""
    manager = ScriptManager()
    
    # Test built-in script
    path = manager.resolve_script_path("jap_anime_reformat")
    assert path.exists()
    assert path.name == "jap_anime_reformat.txt"
    
    # Test filesystem path
    test_script = tmp_path / "test_script.txt"
    test_script.write_text("# Test script")
    path = manager.resolve_script_path(str(test_script))
    assert path.exists()
    assert path == test_script
    
    # Test non-existent script
    with pytest.raises(ValueError) as exc_info:
        manager.resolve_script_path("nonexistent")
    assert "Script not found" in str(exc_info.value)
    assert "Available built-in scripts" in str(exc_info.value)
    assert "jap_anime_reformat" in str(exc_info.value)

def test_expand_variables():
    """Test variable expansion in script lines."""
    manager = ScriptManager()
    
    # Test basic variable expansion
    variables = {"model": "Test Model", "field": "Test Field"}
    line = "add-model --model ${model} --field ${field}"
    expanded = manager.expand_variables(line, variables)
    assert expanded == "add-model --model Test Model --field Test Field"
    
    # Test default values
    line = "add-model --model ${model:Default Model} --field ${field:Default Field}"
    expanded = manager.expand_variables(line, {})
    assert expanded == "add-model --model Default Model --field Default Field"
    
    # Test mix of defined and default values
    variables = {"model": "Test Model"}
    line = "add-model --model ${model} --field ${field:Default Field}"
    expanded = manager.expand_variables(line, variables)
    assert expanded == "add-model --model Test Model --field Default Field"
    
    # Test invalid variable names
    with pytest.raises(ValueError, match="Invalid variable name"):
        manager.expand_variables("add-model ${invalid-name}", {})
    
    # Test missing variable without default
    with pytest.raises(ValueError, match="No value provided for variable"):
        manager.expand_variables("add-model ${required_var}", {})

def test_read_script_with_variables(tmp_path):
    """Test reading a script file with variable expansion."""
    manager = ScriptManager()
    
    # Create test script with variables
    script_path = tmp_path / "test_script.txt"
    script_content = """
# Test script with variables
add-model --model ${model_name:Basic} --field ${field_name}
add-field --model ${model_name:Basic} --field ${new_field:Extra}
"""
    script_path.write_text(script_content)
    
    # Test with all variables provided
    variables = {
        "model_name": "Test Model",
        "field_name": "Test Field"
    }
    lines = list(manager.read_script(str(script_path), variables))
    assert len(lines) == 2
    assert lines[0] == "add-model --model Test Model --field Test Field"
    assert lines[1] == "add-field --model Test Model --field Extra"
    
    # Test with missing variable (should use default)
    variables = {"field_name": "Test Field"}
    lines = list(manager.read_script(str(script_path), variables))
    assert len(lines) == 2
    assert lines[0] == "add-model --model Basic --field Test Field"
    assert lines[1] == "add-field --model Basic --field Extra"
    
    # Test with missing required variable
    variables = {"model_name": "Test Model"}
    with pytest.raises(ValueError, match="No value provided for variable"):
        list(manager.read_script(str(script_path), variables)) 