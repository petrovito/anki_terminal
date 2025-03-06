from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from anki_terminal.anki_types import Collection, Model, Template
from anki_terminal.changelog import Change
from anki_terminal.ops.printer import HumanReadablePrinter, OperationPrinter


@dataclass
class OperationArgument:
    """Represents an argument for an operation."""
    name: str
    description: str
    required: bool = False
    default: Any = None

@dataclass
class OperationResult:
    """Result of an operation execution."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    changes: List[Change] = None  # Changes to be recorded in changelog

    def __post_init__(self):
        if self.changes is None:
            self.changes = []

class Operation(ABC):
    """Base class for all operations."""
    
    # Class properties that subclasses should override
    name: str = ""  # Name of the operation
    description: str = ""  # Description of what the operation does
    readonly: bool = True  # Whether the operation modifies data
    arguments: List[OperationArgument] = []  # Arguments for the operation
    
    def __init__(self, printer: Optional[OperationPrinter] = None, **kwargs):
        """Initialize the operation.
        
        Args:
            **kwargs: Operation-specific arguments
        """
        self.collection = None
        self.printer = printer or HumanReadablePrinter()
        self.args = self._process_args(kwargs)
    
    @classmethod
    def setup_subparser(cls, subparser):
        """Set up the subparser for this operation.
        
        This method can be overridden by subclasses to customize the subparser.
        By default, it adds arguments based on the operation's arguments list.
        
        Args:
            subparser: The subparser to set up
        """
        # Add arguments from operation
        for arg in cls.arguments:
            subparser.add_argument(
                f"--{arg.name.replace('_', '-')}",
                required=arg.required,
                default=arg.default,
                help=arg.description + (" (required)" if arg.required else f" (default: {arg.default})")
            )
    
    def _process_args(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate input arguments.
        
        Args:
            kwargs: Input arguments
            
        Returns:
            Processed arguments with defaults applied
            
        Raises:
            ValueError: If required arguments are missing or invalid
        """
        # Check required args
        missing_args = [
            arg.name for arg in self.arguments 
            if arg.required and arg.name not in kwargs
        ]
        if missing_args:
            raise ValueError(f"Missing required arguments: {missing_args}")
        
        # Apply defaults for optional args
        args = {
            arg.name: arg.default 
            for arg in self.arguments 
            if not arg.required
        }
        args.update(kwargs)
        
        return args

    def _get_model(self, model_name: Optional[str] = None) -> Model:
        """Get a model by name or return the only model if there's just one.
        
        Args:
            model_name: Name of the model to get, or None to get default
            
        Returns:
            The requested Model
            
        Raises:
            ValueError: If model not found or ambiguous model reference
            RuntimeError: If collection not set
        """
        if not self.collection:
            raise RuntimeError("Collection not set")

        if model_name:
            # Find model by name
            for model in self.collection.models.values():
                if model.name == model_name:
                    return model
            raise ValueError(f"Model not found: {model_name}")
        
        # No model specified
        if len(self.collection.models) == 1:
            return next(iter(self.collection.models.values()))
        
        model_names = [model.name for model in self.collection.models.values()]
        raise ValueError(
            f"Multiple models found, please specify one: {', '.join(model_names)}"
        )

    def _get_template(self, model_name: Optional[str] = None, template_name: Optional[str] = None) -> Template:
        """Get a template from a model, handling multiple template cases.
        
        Args:
            model_name: Name of the model to get template from, or None for default
            template_name: Name of the template to get, or None for default/only
            
        Returns:
            The requested Template
            
        Raises:
            ValueError: If template not found or ambiguous template reference
            RuntimeError: If collection not set
        """
        if not self.collection:
            raise RuntimeError("Collection not set")

        model = self._get_model(model_name)
        
        if template_name:
            # Find template by name
            for template in model.templates:
                if template.name == template_name:
                    return template
            raise ValueError(f"Template not found: {template_name}")
        
        # No template specified
        if len(model.templates) > 1:
            template_names = [t.name for t in model.templates]
            raise ValueError(
                f"Multiple templates found in model {model.name}, please specify one: {', '.join(template_names)}"
            )
        
        return model.templates[0]
    
    def validate(self, collection: Collection) -> None:
        """Validate that the operation can be executed.
        
        This method handles common validation logic, sets the collection,
        and then calls the operation-specific _validate_impl method.
        
        Args:
            collection: The Anki collection to operate on
        
        Raises:
            ValueError: If validation fails
            RuntimeError: If collection is None
        """
        # Check collection is not None
        if collection is None:
            raise RuntimeError("Collection cannot be None")
            
        # Set collection
        self.collection = collection
            
        # Check name is set
        if not self.name:
            raise RuntimeError("Operation name not set")
            
        # Call implementation-specific validation
        self._validate_impl()
    
    def execute(self) -> OperationResult:
        """Execute the operation.
        
        This method handles common execution logic and then calls the
        operation-specific _execute_impl method.
        
        Returns:
            OperationResult indicating success/failure and any output data
            
        Raises:
            RuntimeError: If execution fails or collection not set
        """
        # Check collection is set
        if not self.collection:
            raise RuntimeError("Collection not set")
            
        # Execute implementation-specific logic
        return self._execute_impl()
    
    @abstractmethod
    def _validate_impl(self) -> None:
        """Implementation-specific validation logic.
        
        This method should be overridden by subclasses to provide their
        specific validation logic.
        
        Raises:
            ValueError: If validation fails
        """
        pass
    
    @abstractmethod
    def _execute_impl(self) -> OperationResult:
        """Implementation-specific execution logic.
        
        This method should be overridden by subclasses to provide their
        specific execution logic.
        
        Returns:
            OperationResult indicating success/failure and any output data
            
        Raises:
            RuntimeError: If execution fails
        """
        pass 