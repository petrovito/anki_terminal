from typing import Any, Dict, Optional, Type

from anki_terminal.commons.config_manager import ConfigManager
from anki_terminal.populators.populator_base import FieldPopulator
from anki_terminal.populators.populator_registry import PopulatorRegistry


class PopulatorFactory:
    """Factory for creating field populators with configuration."""
    
    def __init__(self, 
                 registry: Optional[PopulatorRegistry] = None,
                 config_manager: Optional[ConfigManager] = None):
        """Initialize the populator factory.
        
        Args:
            registry: Registry of available populators
            config_manager: Manager for loading configuration files
        """
        self.registry = registry or PopulatorRegistry()
        self.config_manager = config_manager or ConfigManager()
    
    def _process_file_arguments(self, args_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Process file:// arguments in the args dictionary.
        
        Args:
            args_dict: Dictionary of arguments
            
        Returns:
            Updated dictionary with file:// arguments processed
        """
        result = args_dict.copy()
        
        # Process any file:// arguments
        for key, value in args_dict.items():
            if isinstance(value, str) and value.startswith("file://"):
                # Load the file and replace the value with its contents
                file_path = value[7:]  # Remove the file:// prefix
                try:
                    file_contents = self.config_manager.load_config(file_path)
                    result[key] = file_contents
                except Exception as e:
                    raise ValueError(f"Failed to load file {file_path}: {str(e)}")
        
        return result
    
    def create_populator(self, 
                        populator_name: str, 
                        config_file: Optional[str] = None,
                        **kwargs) -> FieldPopulator:
        """Create a populator instance with the given configuration.
        
        Args:
            populator_name: Name of the populator to create
            config_file: Path to a configuration file
            **kwargs: Additional configuration arguments
            
        Returns:
            Initialized populator instance
            
        Raises:
            ValueError: If the populator cannot be created
        """
        # Get the populator class
        try:
            populator_cls = self.registry.get(populator_name)
        except KeyError:
            raise ValueError(f"Populator not found: {populator_name}")
        
        # Prepare configuration
        config = {}
        
        # Load configuration from file if provided
        if config_file:
            try:
                file_config = self.config_manager.load_config(config_file)
                config.update(file_config)
            except Exception as e:
                raise ValueError(f"Failed to load config file {config_file}: {str(e)}")
        
        # Add additional arguments
        config.update(kwargs)
        
        # Process any file:// arguments
        config = self._process_file_arguments(config)
        
        # Create and return the populator
        return populator_cls(config)
    
    def create_populator_from_args(self, args_dict: Dict[str, Any]) -> FieldPopulator:
        """Create a populator from a dictionary of arguments.
        
        Args:
            args_dict: Dictionary of arguments
            
        Returns:
            Initialized populator instance
            
        Raises:
            ValueError: If the populator cannot be created
        """
        # Extract populator name
        populator_name = args_dict.get("populator")
        if not populator_name:
            raise ValueError("Populator name is required")
        
        # Get the populator class
        try:
            populator_cls = self.registry.get(populator_name)
        except KeyError:
            raise ValueError(f"Populator not found: {populator_name}")
        
        # Prepare configuration
        config = {}
        
        # Extract populator-specific arguments
        for arg in populator_cls.get_config_arguments():
            arg_name = arg.name
            if arg_name in args_dict and args_dict[arg_name] is not None:
                config[arg_name] = args_dict[arg_name]
        
        # Load configuration from file if provided
        config_file = args_dict.get("populator_config_file")
        if config_file:
            try:
                file_config = self.config_manager.load_config(config_file)
                config.update(file_config)
            except Exception as e:
                raise ValueError(f"Failed to load config file {config_file}: {str(e)}")
        
        # Process any file:// arguments in the config
        config = self._process_file_arguments(config)
        
        # Create and return the populator
        return populator_cls(config) 