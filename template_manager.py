#!/usr/bin/env python3

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger('anki_inspector')

class TemplateManager:
    """Manages access to built-in and user templates."""
    
    def __init__(self):
        # Get the directory where this file is located
        self.package_dir = Path(__file__).parent
        self.builtin_templates_dir = self.package_dir / "templates" / "builtin"
        
    def get_builtin_template_path(self, template_name: str) -> Optional[Path]:
        """Get the path to a built-in template.
        
        Args:
            template_name: Name of the template (with or without extension)
            
        Returns:
            Path to the template if found, None otherwise
        """
        # Don't modify the extension if it's already .html or .css
        if not (template_name.endswith('.html') or template_name.endswith('.css')):
            template_name += '.html'  # Default to .html for backward compatibility
            
        template_path = self.builtin_templates_dir / template_name
        return template_path if template_path.exists() else None
    
    def resolve_template_path(self, template_path: str) -> Path:
        """Resolve a template path, checking both built-in templates and filesystem.
        
        Args:
            template_path: Path or name of template to resolve
            
        Returns:
            Resolved Path object
            
        Raises:
            ValueError: If template cannot be found
        """
        # First check if it's a built-in template
        builtin_path = self.get_builtin_template_path(template_path)
        if builtin_path:
            return builtin_path
            
        # Then check if it's a valid filesystem path
        path = Path(template_path)
        if path.exists():
            return path
            
        raise ValueError(
            f"Template file not found: {template_path}"
        )
    
    def load_template(self, template_path: str) -> str:
        """Load and return the contents of a template file.
        
        Args:
            template_path: Path or name of template to load
            
        Returns:
            Template contents as string
            
        Raises:
            ValueError: If template cannot be found or read
        """
        try:
            path = self.resolve_template_path(template_path)
            with open(path) as f:
                return f.read().strip()
        except Exception as e:
            raise ValueError(f"Error loading template {template_path}: {str(e)}") 