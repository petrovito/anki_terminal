import json
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TextIO


class OperationPrinter(ABC):
    """Abstract base class for operation output printers."""
    
    def __init__(self, output: Optional[TextIO] = None):
        """Initialize the printer.
        
        Args:
            output: Output stream to write to. Defaults to sys.stdout.
        """
        self.output = output or sys.stdout
    
    @abstractmethod
    def print_result(self, result: Dict[str, Any]) -> None:
        """Print operation result.
        
        Args:
            result: Dictionary containing operation result data
        """
        pass
    
    @abstractmethod
    def print_error(self, message: str) -> None:
        """Print error message.
        
        Args:
            message: Error message to print
        """
        pass

class JsonPrinter(OperationPrinter):
    """Prints operation output in JSON format."""
    
    def __init__(self, output: Optional[TextIO] = None, pretty: bool = True):
        """Initialize JSON printer.
        
        Args:
            output: Output stream to write to
            pretty: Whether to pretty-print JSON output
        """
        super().__init__(output)
        self.pretty = pretty
    
    def print_result(self, result: Dict[str, Any]) -> None:
        """Print operation result as JSON.
        
        Args:
            result: Dictionary containing operation result data
        """
        indent = 2 if self.pretty else None
        json_str = json.dumps(result, indent=indent)
        print(json_str, file=self.output)
    
    def print_error(self, message: str) -> None:
        """Print error message as JSON.
        
        Args:
            message: Error message to print
        """
        error = {
            "success": False,
            "error": message
        }
        json_str = json.dumps(error, indent=2 if self.pretty else None)
        print(json_str, file=self.output)

class HumanReadablePrinter(OperationPrinter):
    """Prints operation output in a human-readable format."""
    
    def _format_value(self, value: Any, indent: int = 0) -> str:
        """Format a value for human-readable output.
        
        Args:
            value: Value to format
            indent: Current indentation level
            
        Returns:
            Formatted string
        """
        indent_str = "  " * indent
        
        if isinstance(value, dict):
            lines = []
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{indent_str}{k}:")
                    lines.append(self._format_value(v, indent + 1))
                else:
                    lines.append(f"{indent_str}{k}: {v}")
            return "\n".join(lines)
        elif isinstance(value, list):
            if not value:
                return f"{indent_str}(empty list)"
            lines = []
            for item in value:
                if isinstance(item, dict):
                    lines.append(self._format_value(item, indent))
                else:
                    lines.append(f"{indent_str}- {item}")
            return ("\n"+indent_str+"---"+"\n").join(lines)
        else:
            return f"{indent_str}{value}"
    
    def print_result(self, result: Dict[str, Any]) -> None:
        """Print operation result in human-readable format.
        
        Args:
            result: Dictionary containing operation result data
        """
        for key, value in result.items():
            print(f"{key}:", file=self.output)
            print(self._format_value(value, indent=1), file=self.output)
    
    def print_error(self, message: str) -> None:
        """Print error message in human-readable format.
        
        Args:
            message: Error message to print
        """
        print(f"Error: {message}", file=self.output)

class MockPrinter(OperationPrinter):
    """Printer for testing that captures output instead of printing."""
    
    def __init__(self):
        """Initialize mock printer with empty output lists."""
        super().__init__()
        self.results: List[Dict[str, Any]] = []
        self.errors: List[str] = []
    
    def print_result(self, result: Dict[str, Any]) -> None:
        """Store operation result.
        
        Args:
            result: Dictionary containing operation result data
        """
        self.results.append(result)
    
    def print_error(self, message: str) -> None:
        """Store error message.
        
        Args:
            message: Error message to store
        """
        self.errors.append(message)
    
    def clear(self) -> None:
        """Clear stored results and errors."""
        self.results.clear()
        self.errors.clear() 