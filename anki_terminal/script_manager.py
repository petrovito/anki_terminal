#!/usr/bin/env python3

import logging
import re
from pathlib import Path
from typing import Optional, List, Dict, Iterator

logger = logging.getLogger('anki_inspector')

class ScriptManager:
    """Manages access to script files."""
    
    def __init__(self, builtin_scripts_dir: Optional[Path] = None):
        """Initialize script manager.
        
        Args:
            builtin_scripts_dir: Optional override for builtin scripts directory
        """
        self.package_dir = Path(__file__).parent
        self.builtin_scripts_dir = (
            builtin_scripts_dir
            if builtin_scripts_dir is not None
            else self.package_dir / "builtin" / "scripts"
        )
        
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
    
    def expand_variables(self, line: str, variables: Dict[str, str]) -> str:
        """Expand variables in a script line.
        
        Variables can be specified in two forms:
        1. ${variable_name} - Required variable
        2. ${variable_name:default_value} - Variable with default value
        
        Args:
            line: Script line containing variables
            variables: Dictionary of variable names and values
            
        Returns:
            Line with variables expanded
            
        Raises:
            ValueError: If a required variable is missing or variable name is invalid
        """
        def replace_var(match: re.Match) -> str:
            var_spec = match.group(1)
            if ':' in var_spec:
                var_name, default = var_spec.split(':', 1)
            else:
                var_name, default = var_spec, None
                
            # Validate variable name
            if not re.match(r'^[a-zA-Z0-9_]+$', var_name):
                raise ValueError(f"Invalid variable name: {var_name}. Only letters, numbers, and underscores are allowed.")
                
            # Get value
            if var_name in variables:
                return variables[var_name]
            elif default is not None:
                return default
            else:
                raise ValueError(f"No value provided for variable: {var_name}")
        
        return re.sub(r'\${([^}]+)}', replace_var, line)
    
    def read_script(self, script_path: str, variables: Dict[str, str]) -> Iterator[str]:
        """Read and process a script file, expanding variables.
        
        Args:
            script_path: Path to script file
            variables: Dictionary of variable names and values
            
        Yields:
            Processed script lines
            
        Raises:
            ValueError: If script cannot be found or variables cannot be expanded
        """
        path = self.resolve_script_path(script_path)
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    yield self.expand_variables(line, variables) 