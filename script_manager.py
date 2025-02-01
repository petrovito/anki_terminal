#!/usr/bin/env python3

import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger('anki_inspector')

class ScriptManager:
    """Manages access to built-in and user scripts."""
    
    def __init__(self):
        # Get the directory where this file is located
        self.package_dir = Path(__file__).parent
        self.builtin_scripts_dir = self.package_dir / "scripts" / "builtin"
        
    def get_builtin_script_path(self, script_name: str) -> Optional[Path]:
        """Get the path to a built-in script.
        
        Args:
            script_name: Name of the script (with or without .txt extension)
            
        Returns:
            Path to the script if found, None otherwise
        """
        # Normalize script name
        if not script_name.endswith('.txt'):
            script_name += '.txt'
            
        script_path = self.builtin_scripts_dir / script_name
        return script_path if script_path.exists() else None
    
    def list_builtin_scripts(self) -> List[str]:
        """List all available built-in scripts.
        
        Returns:
            List of script names (without .txt extension)
        """
        if not self.builtin_scripts_dir.exists():
            return []
            
        return [
            path.stem for path in self.builtin_scripts_dir.glob('*.txt')
            if path.is_file()
        ]
    
    def resolve_script_path(self, script_path: str) -> Path:
        """Resolve a script path, checking both built-in scripts and filesystem.
        
        Args:
            script_path: Path or name of script to resolve
            
        Returns:
            Resolved Path object
            
        Raises:
            ValueError: If script cannot be found
        """
        # First check if it's a built-in script
        builtin_path = self.get_builtin_script_path(script_path)
        if builtin_path:
            return builtin_path
            
        # Then check if it's a valid filesystem path
        path = Path(script_path)
        if path.exists():
            return path
            
        raise ValueError(
            f"Script not found: {script_path}. "
            f"Available built-in scripts: {', '.join(self.list_builtin_scripts())}"
        ) 