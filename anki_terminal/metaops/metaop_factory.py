from typing import Dict, Any, Optional
from anki_terminal.metaops.metaop import MetaOp, MetaOpFromRecipe
from anki_terminal.metaops.recipe_registry import RecipeRegistry
from anki_terminal.commons.config_manager import ConfigManager
from anki_terminal.ops.op_base import Operation
from anki_terminal.ops.printer import OperationPrinter, HumanReadablePrinter, JsonPrinter

class MetaOpFactory:
    """Factory for creating meta operation instances with configuration support."""
    
    def __init__(self, 
                 recipe_registry: Optional[RecipeRegistry] = None,
                 config_manager: Optional[ConfigManager] = None):
        """Initialize the meta operation factory.
        
        Args:
            recipe_registry: Optional recipe registry, creates a new one if not provided
            config_manager: Optional config manager, creates a new one if not provided
        """
        self.recipe_registry = recipe_registry or RecipeRegistry()
        self.config_manager = config_manager or ConfigManager()
    
    def create_from_args(self, args_dict: Dict[str, Any]) -> MetaOp:
        """Create a meta operation instance from a dictionary of arguments.
        
        Args:
            args_dict: Dictionary of arguments
            
        Returns:
            Initialized meta operation instance
            
        Raises:
            ValueError: If meta operation cannot be created
        """
        # Create printer
        format_type = args_dict.get('format', 'human')
        pretty = args_dict.get('pretty', False)
        if format_type == "json":
            printer = JsonPrinter(pretty=pretty)
        else:
            printer = HumanReadablePrinter()
        
        # Get recipe name
        recipe_name = args_dict.get('operation')
        if not recipe_name:
            raise ValueError("Operation name is required")
        
        # Get recipe
        recipe = self.recipe_registry.get(recipe_name)
        
        # Process config file if provided
        op_args = args_dict.copy()
        config_file = op_args.get('config_file')
        if config_file:
            config = self.config_manager.load_config(config_file)
            # Override command line arguments with config file values
            for key, value in config.items():
                if key not in op_args or op_args[key] is None:
                    op_args[key] = value
        
        # Create meta operation instance
        return MetaOpFromRecipe(recipe=recipe, args=op_args)
    
    def create_from_op(self, op: Operation) -> MetaOp:
        """Create a meta operation instance from an operation instance.
        
        Args:
            op: Operation instance
        """
        
        return MetaOpFromRecipe(recipe=op.recipe, args=op.args)
        