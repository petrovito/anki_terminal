import argparse
from pathlib import Path
from typing import Dict, Any, Optional, Type
from anki_terminal.metaops.metaop_recipe import MetaOpRecipe
from anki_terminal.ops.op_base import Operation
from anki_terminal.metaops.recipe_factory import RecipeFactory
from anki_terminal.metaops.recipe_registry import RecipeRegistry
from anki_terminal.metaops.metaop_factory import MetaOpFactory
from anki_terminal.metaops.metaop import MetaOp, MetaOpFromRecipe
from anki_terminal.commons.config_manager import ConfigManager
from anki_terminal.ops.op_registry import OperationRegistry

class MetaOpManager:
    """Manager class for meta operations, overseeing recipe creation, registration, and metaop instantiation."""
    
    def __init__(self,
                 recipe_factory: Optional[RecipeFactory] = None,
                 recipe_registry: Optional[RecipeRegistry] = None,
                 metaop_factory: Optional[MetaOpFactory] = None,
                 config_manager: Optional[ConfigManager] = None,
                 op_registry: Optional[OperationRegistry] = None):
        """Initialize the meta operation manager.
        
        Args:
            recipe_factory: Optional recipe factory, creates a new one if not provided
            recipe_registry: Optional recipe registry, creates a new one if not provided
            metaop_factory: Optional metaop factory, creates a new one if not provided
            config_manager: Optional config manager, creates a new one if not provided
        """
        self.recipe_factory = recipe_factory or RecipeFactory()
        self.recipe_registry = recipe_registry or RecipeRegistry()
        self.config_manager = config_manager or ConfigManager()
        self.metaop_factory = metaop_factory or MetaOpFactory(
            recipe_registry=self.recipe_registry,
            config_manager=self.config_manager
        )
        self.op_registry = op_registry or OperationRegistry()


    def initialize(self) -> None:
        """Initialize the meta operation manager."""
        # Add fundamental recipes
        for op_name, op_class in self.op_registry.get_all().items():
            recipe = self.recipe_factory.create_from_operation(op_class)
            self.recipe_registry.register(recipe)
        
        # Add bundles
        # TODO: Implement

    def load_from_folder(self, folder_path: Path) -> None:
        # TODO: Implement
        pass

    def create_metaop(self, kwargs: Dict[str, Any]) -> MetaOp:
        """Create a meta operation by name."""
        return self.metaop_factory.create_from_args(kwargs)
    
    def setup_subparser(self, recipe: MetaOpRecipe, subparser: argparse.ArgumentParser) -> None:
        subparser.add_help = True
        if recipe.is_fundamental():
            recipe.op_type.setup_subparser(subparser)
            return
        # Composite recipe
        for arg in recipe.args:
            subparser.add_argument(
                f"--{arg.name.replace('_', '-')}",
                required=arg.required,
                default=arg.default,
                help=arg.description,
            )
    