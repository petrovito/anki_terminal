import json
from pathlib import Path

import pytest

from anki_terminal.config_manager import ConfigManager


@pytest.fixture
def config_manager(test_configs_dir, test_templates_dir):
    """Get a config manager instance configured for testing."""
    return ConfigManager(
        builtin_configs_dir=test_configs_dir / "builtin" / "configs",
        builtin_templates_dir=test_templates_dir / "builtin" / "templates"
    )

def test_list_builtin_configs(config_manager):
    """Test listing built-in configs."""
    configs = config_manager.list_builtin_configs()
    assert isinstance(configs, list)
    assert "jap_anime_reformat" in configs

def test_get_builtin_config_path(config_manager):
    """Test getting path to built-in config."""
    # Test with .json extension
    path = config_manager.get_builtin_config_path("jap_anime_reformat.json")
    assert path is not None
    assert path.exists()
    assert path.name == "jap_anime_reformat.json"
    
    # Test without .json extension
    path = config_manager.get_builtin_config_path("jap_anime_reformat")
    assert path is not None
    assert path.exists()
    assert path.name == "jap_anime_reformat.json"
    
    # Test non-existent config
    path = config_manager.get_builtin_config_path("nonexistent")
    assert path is None

def test_resolve_config_path(config_manager, tmp_path):
    """Test resolving config paths."""
    # Test built-in config
    path = config_manager.resolve_config_path("jap_anime_reformat")
    assert path.exists()
    assert path.name == "jap_anime_reformat.json"
    
    # Test filesystem path
    test_config = tmp_path / "test_config.json"
    test_config.write_text('{"test": true}')
    path = config_manager.resolve_config_path(str(test_config))
    assert path.exists()
    assert path == test_config
    
    # Test non-existent config
    with pytest.raises(ValueError) as exc_info:
        config_manager.resolve_config_path("nonexistent")
    assert "Configuration not found" in str(exc_info.value)
    assert "Available built-in configurations" in str(exc_info.value)
    assert "jap_anime_reformat" in str(exc_info.value)

def test_load_config(config_manager, tmp_path):
    """Test loading and parsing config files."""
    # Test loading built-in config
    config = config_manager.load_config("jap_anime_reformat")
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
    
    loaded_config = config_manager.load_config(str(config_path))
    assert loaded_config == test_config
    
    # Test invalid JSON
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text('{"invalid": true')  # Missing closing brace
    with pytest.raises(ValueError) as exc_info:
        config_manager.load_config(str(invalid_path))
    assert "Invalid JSON" in str(exc_info.value) 