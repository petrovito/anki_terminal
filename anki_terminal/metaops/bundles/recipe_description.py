

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Union

from anki_terminal.metaops.metaop_recipe import MetaOpArgument


class TargetDescriptionType(Enum):
    """Type of a target."""
    NAME = str
    BASE_OP_TYPE = type

class TargetDescription:
    def __init__(self, type: TargetDescriptionType, description: Union[str, type]):
        self.type: TargetDescriptionType = type
        self.description: Union[str, type] = description

ArgumentTransformationRecipe = Dict[str, str]
"""
A recipe for a transformation of an argument.
The key is the name of the argument of the source recipe.
The value is the name of the argument of the target recipe.
"""

class TargetRecipeDescription:
    def __init__(self, 
                    target_description: TargetDescription,
                 argument_transformation_recipe: ArgumentTransformationRecipe):
        self.target_description: TargetDescription = target_description
        self.argument_transformation_recipe: ArgumentTransformationRecipe = argument_transformation_recipe


class RecipeDescription:
    """    
    The purpose of this class is to create a way for recipes to be described via python code.
    Describing recipes in code can be helpful as this may allow IDEs to help create and maintain recipes.
    """
    
    def get_name(self) -> str:
        """Get the name of the recipe."""
        return self.name
    
    def get_args(self) -> List[MetaOpArgument]:
        """Get the arguments of the recipe."""
        return self.args
    
    def get_targets(self) -> List[TargetRecipeDescription]:
        """Get the targets of the recipe."""
        return self.targets
    
    def get_help_message(self) -> str:
        """Get the help message of the recipe."""
        return self.help_message