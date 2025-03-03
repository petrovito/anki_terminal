from typing import Dict, List, Optional, Any, Union

from anki_terminal.ops.base import Operation, OperationResult, OperationArgument
from anki_terminal.ops.read.base_read import ReadOperation
from anki_terminal.ops.anki_path import AnkiPath

class PathOperation(ReadOperation):
    """Base class for operations that work with AnkiPath."""
    
    arguments = [
        OperationArgument(
            name="path",
            description="Path to the Anki object(s)",
            required=True
        )
    ]
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed."""
        try:
            self.path = AnkiPath(self.args["path"])
            
            # If path requires a model, validate it exists
            if self.path.model_name:
                self._get_model(self.path.model_name)  # This will raise ValueError if model doesn't exist
                
        except ValueError as e:
            raise ValueError(f"Invalid path: {e}")
        
        # Additional validation can be added in subclasses 
    
    @classmethod
    def get_examples(cls) -> List[Dict[str, str]]:
        """Get examples of how to use this operation.
        
        Returns:
            List of examples with description and command
        """
        operation_name = cls.name
        return [
            {
                "description": "List all models",
                "command": f"{operation_name} --path /models"
            },
            {
                "description": "List all fields in a model",
                "command": f"{operation_name} --path /models/Basic/fields"
            },
            {
                "description": "List all templates in a model",
                "command": f"{operation_name} --path /models/Basic/templates"
            },
            {
                "description": "Get information about a specific model",
                "command": f"{operation_name} --path /models/Basic"
            },
            {
                "description": "Get information about a specific field",
                "command": f"{operation_name} --path /models/Basic/fields/Front"
            },
            {
                "description": "Get information about a specific template",
                "command": f"{operation_name} --path /models/Basic/templates/Card 1"
            },
            {
                "description": "Get CSS for a model",
                "command": f"{operation_name} --path /models/Basic/css"
            },
            {
                "description": "Get an example note for a model",
                "command": f"{operation_name} --path /models/Basic/example"
            },
            {
                "description": "List all cards",
                "command": f"{operation_name} --path /cards"
            },
            {
                "description": "List all notes",
                "command": f"{operation_name} --path /notes"
            },
            {
                "description": "List notes for a specific model",
                "command": f"{operation_name} --path /notes/Basic"
            }
        ] 