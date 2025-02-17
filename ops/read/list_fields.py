from typing import Dict, List, Optional

from ops.base import Operation, OperationResult
from anki_types import Model

class ListFieldsOperation(Operation):
    """Operation to list all fields in a model."""
    
    name = "list_fields"
    description = "List all fields in the specified model"
    readonly = True
    required_args = set()  # No required args since model_name is optional
    optional_args = {
        "model_name": None  # If None, uses default/only model
    }
    
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