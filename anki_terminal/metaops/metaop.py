from abc import ABC, abstractmethod
from typing import Generator, List, Dict, Any
from anki_terminal.metaops.metaop_recipe import MetaOpRecipe
from anki_terminal.ops.op_base import Operation
from anki_terminal.ops.operation_factory import OperationFactory


class MetaOp(ABC):
    """
    A meta operation is an adapter that allows for the execution of a collection of sub-operations,
    making it easier to manage and execute them for users.
    There are two types of meta operations:
      - Fundamental: map one-to-one with a regular operation
      - Composite: resolve into a list of other meta operations
    """
    
    @abstractmethod
    def is_fundamental(self) -> bool:
        """Whether the meta operation is fundamental."""
        pass
    
    @abstractmethod
    def resolve(self) -> Generator['MetaOp', None, None]:
        """
        Resolve the meta operation into a list of other meta operations.
        Raises ValueError if the meta operation is fundamental.
        """
        pass

    @abstractmethod
    def resolve_op(self, op_factory: OperationFactory) -> Operation:
        """
        Resolve the meta operation into a regular operation.
        Raises ValueError if the meta operation is composite.
        """
        pass

    @property
    @abstractmethod
    def readonly(self) -> bool:
        """Whether the meta operation is read-only."""
        pass


class MetaOpFromRecipe(MetaOp):
    """
    A composite meta operation that is built from a recipe.
    """
    
    def __init__(self, recipe: MetaOpRecipe, args: Dict[str, Any] = {}):
        self.recipe: MetaOpRecipe = recipe
        self.args: Dict[str, Any] = args
        # validate args
        for arg in self.recipe.args:
            if arg.required and arg.name not in self.args:
                raise ValueError(f"Argument {arg.name} is required")
    
    def is_fundamental(self) -> bool:
        return self.recipe.is_fundamental()
    
    def resolve(self) -> Generator['MetaOp', None, None]:
        if self.is_fundamental():
            raise ValueError("Meta operation is fundamental, cannot resolve into a list of other meta operations")
        for target_recipe, arg_mapping in self.recipe.targets:
            target_args = {}
            for arg_name, target_arg_name in arg_mapping.items():
                target_args[target_arg_name] = self.args[arg_name]
            yield MetaOpFromRecipe(target_recipe, target_args)
    
    def resolve_op(self, op_factory: OperationFactory) -> Operation:
        if not self.is_fundamental():
            raise ValueError("Meta operation is composite, cannot resolve into a regular operation")
        return op_factory.create_from_args(self.recipe.op_type, self.args)
    
    @property
    def readonly(self) -> bool:
        """Whether the meta operation is read-only."""
        return self.recipe.readonly
    
class MetaOpFromOpInstance(MetaOp):
    """
    A meta operation that is built from an operation instance.
    """
    
    def __init__(self, op: Operation):
        self.op: Operation = op
    
    def is_fundamental(self) -> bool:
        return True
    
    def resolve(self) -> Generator['MetaOp', None, None]:
        raise ValueError("Meta operation is fundamental, cannot resolve into a list of other meta operations")
    
    def resolve_op(self, op_factory: OperationFactory) -> Operation:
        return self.op
    
    @property
    def readonly(self) -> bool:
        """Whether the meta operation is read-only."""
        return self.op.readonly