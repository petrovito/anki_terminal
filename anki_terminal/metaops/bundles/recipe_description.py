

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Union

from anki_terminal.metaops.metaop_recipe import MetaOpArgument


class TargetDescriptionType(Enum):
    """Type of a target."""
    NAME = str
    BASE_OP_TYPE = type

class TargetDescription:
    def __init__(self, type: TargetDescriptionType, description: Union[str, type]):
        self.type: TargetDescriptionType = type
        self.description: Union[str, type] = description

class RecipeDescription(ABC):
    """Description of a recipe."""
    
    def get_name(self) -> str:
        """Get the name of the recipe."""
        return self.name
    
    def get_args(self) -> List[MetaOpArgument]:
        """Get the arguments of the recipe."""
        return self.args
    
    def get_targets(self) -> List[TargetDescription]:
        """Get the targets of the recipe."""
        return self.targets