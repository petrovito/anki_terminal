import pytest
import json
from pathlib import Path
from config_manager import ConfigManager

def test_list_builtin_configs():
    """Test listing built-in configs."""
    manager = ConfigManager()
    configs = manager.list_builtin_configs()
    assert isinstance(configs, list)
    assert "jap_anime_reformat" in configs

def test_get_builtin_config_path():
    """Test getting path to built-in config."""
    manager = ConfigManager()
    
    # Test with .json extension
    path = manager.get_builtin_config_path("jap_anime_reformat.json")
    assert path is not None
    assert path.exists()
    assert path.name == "jap_anime_reformat.json"
    
    # Test without .json extension
    path = manager.get_builtin_config_path("jap_anime_reformat")
    assert path is not None
    assert path.exists()
    assert path.name == "jap_anime_reformat.json"
    
    # Test non-existent config
    path = manager.get_builtin_config_path("nonexistent")
    assert path is None

def test_resolve_config_path(tmp_path):
    """Test resolving config paths."""
    manager = ConfigManager()
    
    # Test built-in config
    path = manager.resolve_config_path("jap_anime_reformat")
    assert path.exists()
    assert path.name == "jap_anime_reformat.json"
    
    # Test filesystem path
    test_config = tmp_path / "test_config.json"
    test_config.write_text('{"test": true}')
    path = manager.resolve_config_path(str(test_config))
    assert path.exists()
    assert path == test_config
    
    # Test non-existent config
    with pytest.raises(ValueError) as exc_info:
        manager.resolve_config_path("nonexistent")
    assert "Configuration not found" in str(exc_info.value)
    assert "Available built-in configurations" in str(exc_info.value)
    assert "jap_anime_reformat" in str(exc_info.value)

def test_load_config(tmp_path):
    """Test loading and parsing config files."""
    manager = ConfigManager()
    
    # Test loading built-in config
    config = manager.load_config("jap_anime_reformat")
    assert isinstance(config, dict)
    assert "model_name" in config
    assert config["model_name"] == "Japanese Anime Card"
    
    # Test loading filesystem config
    test_config = {
        "test": True,
        "name": "Test Config"
    }
    config_path = tmp_path / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(test_config, f)
    
    loaded_config = manager.load_config(str(config_path))
    assert loaded_config == test_config
    
    # Test invalid JSON
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text('{"invalid": true')  # Missing closing brace
    with pytest.raises(ValueError) as exc_info:
        manager.load_config(str(invalid_path))
    assert "Invalid JSON" in str(exc_info.value) 