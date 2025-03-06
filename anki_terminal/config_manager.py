#!/usr/bin/env python3

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from anki_terminal.template_manager import TemplateManager

logger = logging.getLogger('anki_inspector')

class ConfigManager:
    """Manages access to configuration files."""
    
    def __init__(self, builtin_configs_dir: Optional[Path] = None, builtin_templates_dir: Optional[Path] = None):
        """Initialize config manager.
        
        Args:
            builtin_configs_dir: Optional override for builtin configs directory
            builtin_templates_dir: Optional override for builtin templates directory
        """
        self.package_dir = Path(__file__).parent
        self.builtin_configs_dir = (
            builtin_configs_dir
            if builtin_configs_dir is not None
            else self.package_dir / "builtin" / "configs"
        )
        self.template_manager = TemplateManager(builtin_templates_dir)
        
    def get_builtin_config_path(self, config_name: str) -> Optional[Path]:
        """Get the path to a built-in configuration.
        
        Args:
            config_name: Name of the config (with or without .json extension)
            
        Returns:
            Path to the config if found, None otherwise
        """
        # Normalize config name
        if not config_name.endswith('.json'):
            config_name += '.json'
            
        config_path = self.builtin_configs_dir / config_name
        return config_path if config_path.exists() else None
    
    def list_builtin_configs(self) -> List[str]:
        """List all available built-in configurations.
        
        Returns:
            List of config names (without .json extension)
        """
        if not self.builtin_configs_dir.exists():
            return []
            
        return [
            path.stem for path in self.builtin_configs_dir.glob('*.json')
            if path.is_file()
        ]
    
    def resolve_config_path(self, config_path: str) -> Path:
        """Resolve a config path, checking both built-in configs and filesystem.
        
        Args:
            config_path: Path or name of config to resolve
            
        Returns:
            Resolved Path object
            
        Raises:
            ValueError: If config cannot be found
        """
        # First check if it's a built-in config
        builtin_path = self.get_builtin_config_path(config_path)
        if builtin_path:
            return builtin_path
            
        # Then check if it's a valid filesystem path
        path = Path(config_path)
        if path.exists():
            return path
            
        raise ValueError(
            f"Configuration not found: {config_path}. "
            f"Available built-in configurations: {', '.join(self.list_builtin_configs())}"
        )
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load and parse a configuration file.
        
        Args:
            config_path: Path or name of config to load
            
        Returns:
            Parsed configuration as a dictionary
            
        Raises:
            ValueError: If config cannot be found or is invalid JSON
        """
        try:
            path = self.resolve_config_path(config_path)
            with open(path) as f:
                config = json.load(f)
            
            # Handle template files if specified
            if 'question_format_file' in config:
                config['question_format'] = self.template_manager.load_template(config['question_format_file'])
            if 'answer_format_file' in config:
                config['answer_format'] = self.template_manager.load_template(config['answer_format_file'])
            if 'css_file' in config:
                config['css'] = self.template_manager.load_template(config['css_file'])
            
            return config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file {config_path}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading configuration {config_path}: {str(e)}") 