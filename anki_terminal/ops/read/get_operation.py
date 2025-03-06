from typing import Dict, Optional

from anki_terminal.ops.op_base import OperationResult
from anki_terminal.ops.read.path_operation import PathOperation


class GetOperation(PathOperation):
    """Operation to get specific Anki objects or their properties."""
    
    name = "get"
    description = "Get specific Anki objects or their properties"
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed."""
        super()._validate_impl()
        
        # Get operation works on specific items or properties
        if self.path.object_type not in ['model', 'fields', 'templates', 'css', 'example']:
            if not self.path.is_item:
                raise ValueError(f"Path must refer to a specific item: {self.path}")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation."""
        try:
            if self.path.object_type == 'model':
                return self._get_model_info()
            elif self.path.object_type == 'fields' and self.path.item_name:
                return self._get_field_info()
            elif self.path.object_type == 'templates' and self.path.item_name:
                return self._get_template_info()
            elif self.path.object_type == 'css':
                return self._get_css()
            elif self.path.object_type == 'example':
                return self._get_note_example()
            else:
                raise ValueError(f"Cannot get information for path: {self.path}")
        except ValueError as e:
            self.printer.print_error(str(e))
            return OperationResult(
                success=False,
                message=str(e)
            )
    
    def _get_model_info(self) -> OperationResult:
        """Get information about a specific model."""
        model = self._get_model(self.path.model_name)
        
        model_info = {
            "name": model.name,
            "id": model.id,
            "type": "Standard" if model.type == 0 else "Cloze",
            "field_count": len(model.fields),
            "template_count": len(model.templates)
        }
        
        self.printer.print_result({"model": model_info})
        
        return OperationResult(
            success=True,
            message=f"Retrieved information for model '{model.name}'",
            data={"model": model_info}
        )
    
    def _get_field_info(self) -> OperationResult:
        """Get information about a specific field."""
        model = self._get_model(self.path.model_name)
        
        # Find field by name
        field = None
        for f in model.fields:
            if f.name == self.path.item_name:
                field = f
                break
        
        if field is None:
            raise ValueError(f"Field not found: {self.path.item_name} in model {model.name}")
        
        field_info = {
            "name": field.name,
            "type": "text",
            "ordinal": field.ordinal
        }
        
        self.printer.print_result({"field": field_info})
        
        return OperationResult(
            success=True,
            message=f"Retrieved information for field '{field.name}' in model '{model.name}'",
            data={"field": field_info}
        )
    
    def _get_template_info(self) -> OperationResult:
        """Get information about a specific template."""
        model = self._get_model(self.path.model_name)
        
        # Find template by name
        template = None
        for t in model.templates:
            if t.name == self.path.item_name:
                template = t
                break
        
        if template is None:
            raise ValueError(f"Template not found: {self.path.item_name} in model {model.name}")
        
        template_info = {
            "name": template.name,
            "ordinal": template.ordinal,
            "question_format": template.question_format,
            "answer_format": template.answer_format
        }
        
        self.printer.print_result({"template": template_info})
        
        return OperationResult(
            success=True,
            message=f"Retrieved information for template '{template.name}' in model '{model.name}'",
            data={"template": template_info}
        )
    
    def _get_css(self) -> OperationResult:
        """Get the CSS for the specified model."""
        model = self._get_model(self.path.model_name)
        
        self.printer.print_result({"css": model.css})
        
        return OperationResult(
            success=True,
            message=f"Retrieved CSS for model '{model.name}'",
            data={"css": model.css}
        )
    
    def _get_note_example(self) -> OperationResult:
        """Get an example note from the specified model."""
        model = self._get_model(self.path.model_name)
        
        # Find the first note that uses this model
        example_note = None
        example_fields = {}
        
        for note in self.collection.notes.values():
            if note.model_id == model.id:
                example_note = note
                break
        
        # If no notes found, return empty fields
        if example_note is None:
            # Create empty fields based on the model's field definitions
            for field in model.fields:
                example_fields[field.name] = ""
            message = f"No notes found for model '{model.name}', returning empty fields"
        else:
            # Debug: Print raw note to understand the structure
            self.printer.print_result({"debug_raw_note": str(example_note.__dict__)})
            
            # Parse the fields based on the model's field definitions
            # The fields might be stored as a string with \x1f separators or as a dictionary
            if isinstance(example_note.fields, dict):
                # Fields are already a dictionary
                raw_fields = example_note.fields
            elif isinstance(example_note.fields, str):
                # Fields are a string with separators
                field_values = example_note.fields.split('\x1f')
                raw_fields = {}
                for i, field in enumerate(model.fields):
                    if i < len(field_values):
                        raw_fields[field.name] = field_values[i]
                    else:
                        raw_fields[field.name] = ""
            else:
                # Unknown format, try to convert to string
                self.printer.print_error(f"Unknown field format: {type(example_note.fields)}")
                raw_fields = {}
                for field in model.fields:
                    raw_fields[field.name] = ""
            
            # Format the fields for display
            for field in model.fields:
                field_name = field.name
                field_content = raw_fields.get(field_name, "")
                
                # Truncate very long field content
                if len(field_content) > 100:
                    field_content = field_content[:97] + "..."
                
                # Replace special characters for better display
                field_content = field_content.replace("\u001f", " | ")
                
                example_fields[field_name] = field_content
            
            message = f"Retrieved example note for model '{model.name}'"
        
        self.printer.print_result({"example": example_fields})
        
        return OperationResult(
            success=True,
            message=message,
            data={"example": example_fields}
        ) 