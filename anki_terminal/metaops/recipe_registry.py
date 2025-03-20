from typing import Dict, Type, List
from anki_terminal.metaops.metaop_recipe import MetaOpRecipe
from anki_terminal.metaops.recipe_factory import RecipeFactory

class RecipeRegistry:
    """Registry of all available meta operation recipes."""
    
    def __init__(self):
        self._recipes: Dict[str, MetaOpRecipe] = {}
        self._factory = RecipeFactory()
    
  
    def register(self, recipe: MetaOpRecipe) -> None:
        """Register a recipe directly.
        
        Args:
            recipe: The recipe to register
            
        Raises:
            ValueError: If the name is already registered
        """
        if recipe.name in self._recipes:
            raise ValueError(f"Recipe '{recipe.name}' already registered")
            
        self._recipes[recipe.name] = recipe
    
    def get(self, name: str) -> MetaOpRecipe:
        """Get a recipe by name.
        
        Args:
            name: Name of the recipe
            
        Returns:
            The recipe
            
        Raises:
            KeyError: If recipe is not registered
        """
        if name not in self._recipes:
            raise KeyError(f"Recipe '{name}' not registered")
            
        return self._recipes[name]
    
    def get_all(self) -> Dict[str, MetaOpRecipe]:
        """Get all registered recipes.
        
        Returns:
            Dictionary of recipe names to recipes
        """
        return self._recipes.copy()
    