#!/usr/bin/env python3

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Type

from anki_terminal.commons.config_manager import ConfigManager
from anki_terminal.ops.op_base import Operation
from anki_terminal.ops.op_registry import OperationRegistry
from anki_terminal.ops.printer import (HumanReadablePrinter, JsonPrinter,
                                       OperationPrinter)
from anki_terminal.commons.template_manager import TemplateManager

logger = logging.getLogger('anki_inspector')

class OperationFactory:
    """Factory for creating operation instances with configuration and template support."""
    
    def __init__(self, 
                 registry: Optional[OperationRegistry] = None,
                 config_manager: Optional[ConfigManager] = None,
                 template_manager: Optional[TemplateManager] = None):
        """Initialize the operation factory.
        
        Args:
            registry: Optional operation registry, creates a new one if not provided
            config_manager: Optional config manager, creates a new one if not provided
            template_manager: Optional template manager, creates a new one if not provided
        """
        # Find the root directory of the project
        root_dir = Path(__file__).parent.parent
        builtin_configs_dir = root_dir / "builtin" / "configs"
        builtin_templates_dir = root_dir / "builtin" / "templates"
        
        self.registry = registry or OperationRegistry()
        self.template_manager = template_manager or TemplateManager(builtin_templates_dir=builtin_templates_dir)
        self.config_manager = config_manager or ConfigManager(builtin_configs_dir=builtin_configs_dir, 
                                                             builtin_templates_dir=builtin_templates_dir)
    
    def _process_file_arguments(self, args_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Process arguments that have file:// prefix to load their contents.
        
        Args:
            args_dict: Dictionary of arguments
            
        Returns:
            Updated dictionary with file contents loaded
        """
        result = args_dict.copy()
        for key, value in args_dict.items():
            if isinstance(value, str) and value.startswith("file://"):
                file_path = value[7:]  # Remove file:// prefix
                try:
                    # Use template manager to load the file
                    file_content = self.template_manager.load_template(file_path)
                    result[key] = file_content
                    logger.info(f"Loaded file content for argument '{key}' from {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to load file for argument '{key}' from {file_path}: {str(e)}")
        return result
    

    def create_operation_from_args(self, args_dict: Dict[str, Any]) -> Operation:
        # Get operation class
        operation_name = args_dict.get('operation')
        if not operation_name:
            raise ValueError("Operation name is required")
        
        op_class = self.registry.get(operation_name)
        return self.create_from_args(op_class, args_dict)

    def create_from_args(self, op_class: Type[Operation], args_dict: Dict[str, Any]) -> Operation:
        """Create an operation instance from a dictionary of arguments.
        
        Args:
            args_dict: Dictionary of arguments
            
        Returns:
            Initialized operation instance
            
        Raises:
            ValueError: If operation cannot be created
        """
        # Create printer
        format_type = args_dict.get('format', 'human')
        pretty = args_dict.get('pretty', False)
        if format_type == "json":
            printer = JsonPrinter(pretty=pretty)
        else:
            printer = HumanReadablePrinter()
        
        # Process config file if provided
        op_args = args_dict.copy()
        config_file = op_args.get('config_file')
        if config_file:
            config = self.config_manager.load_config(config_file)
            # Override command line arguments with config file values
            for key, value in config.items():
                if key not in op_args or op_args[key] is None:
                    op_args[key] = value
        
        # Process file:// prefixes in arguments
        op_args = self._process_file_arguments(op_args)
        
        # Create operation instance
        return op_class(printer=printer, **op_args)
    