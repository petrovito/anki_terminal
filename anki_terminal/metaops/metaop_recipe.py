from typing import Any, Dict, Tuple, Type, List
from abc import ABC, abstractmethod

from anki_terminal.ops.op_base import Operation

class MetaOpArgument:
    """Argument for a meta operation."""

    def __init__(self, name: str, description: str, required: bool, default: Any) -> None:
        self.name: str = name
        self.description: str = description
        self.required: bool = required
        self.default: Any = default


ArgumentMapping = Dict[str, str]
"""Mapping of an argument of a meta operation to an argument of a target meta operation."""

TargetRecipe = Tuple['MetaOpRecipe', ArgumentMapping]
"""
Target recipe for a meta operation:
    - The first element of the tuple is the recipe for a target meta operation
    - The second element of the tuple is a mapping of the arguments of the composite meta operation
        to the arguments of the target meta operation
"""

class MetaOpRecipe(ABC):
    """
    A recipe for a meta operation, i.e. a description of how to resolve a meta operation into
       A) a base operation, or
       B) a list of other meta operations using the arguments of the composite meta operation.
    """

    @abstractmethod
    def is_fundamental(self) -> bool:
        """Whether the recipe is fundamental, i.e. whether it maps one-to-one with a regular operation."""
        pass

class FundamentalMetaOpRecipe(MetaOpRecipe):
    """
    A recipe for a fundamental meta operation, i.e. a meta operation that maps one-to-one with a regular operation.
    """
    
    def __init__(self, op_type: Type[Operation]):
        """ Names of these arguments have to map one-to-one with the names of the arguments of the operation """
        self.op_type: Type[Operation] = op_type
        self.args: List[MetaOpArgument] = [
            MetaOpArgument(arg.name, arg.description, arg.required, arg.default)
            for arg in op_type.arguments
        ]
        self.name: str = op_type.name
        self.description: str = op_type.description
        self.readonly: bool = op_type.readonly

    def is_fundamental(self) -> bool:
        return True
    
class CompositeMetaOpRecipe(MetaOpRecipe):
    """
    A recipe for a composite meta operation, i.e. a meta operation that resolves into a list of other meta operations.
    """
    
    def __init__(self, name: str, args: List[MetaOpArgument], targets: List[TargetRecipe]):
        self.name: str = name
        self.args: List[MetaOpArgument] = args
        self.targets: List[TargetRecipe] = targets

    def is_fundamental(self) -> bool:
        return False
