import pytest
from pathlib import Path
from script_manager import ScriptManager

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