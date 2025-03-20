from typing import Dict, List, Type, Any
from anki_terminal.ops.op_base import Operation, OperationArgument
from anki_terminal.metaops.metaop_recipe import MetaOpArgument, FundamentalMetaOpRecipe

class RecipeFactory:
    """Factory for creating meta operation recipes from various sources."""
    
    def create_from_operation(self, operation_class: Type[Operation]) -> FundamentalMetaOpRecipe:
        return FundamentalMetaOpRecipe(
            op_type=operation_class
        ) 