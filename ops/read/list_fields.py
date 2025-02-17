from typing import Dict, List, Optional

from ops.base import Operation, OperationResult, OperationArgument
from anki_types import Model

class ListFieldsOperation(Operation):
    """Operation to list all fields in a model."""
    
    name = "list-fields"
    description = "List all fields in the specified model"
    readonly = True
    arguments = [
        OperationArgument(
            name="model_name",
            description="Name of the model to list fields from",
            required=False,
            default=None
        )
    ]
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed.
        
        Raises:
            ValueError: If model_name is invalid
        """
        # This will raise ValueError if model is not found
        self._get_model(self.args["model_name"])
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult with list of fields
        """
        model = self._get_model(self.args["model_name"])
        
        fields = [
            {"name": field.name, "type": "text"}
            for field in model.fields
        ]
        
        return OperationResult(
            success=True,
            message=f"Listed {len(fields)} fields from model '{model.name}'",
            data={"fields": fields}
        ) 