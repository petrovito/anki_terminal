import argparse
import sys
import shlex
from pathlib import Path
from typing import Optional, List
from operation_models import UserOperationType

def operation_type(value: str) -> UserOperationType:
    """Convert string to UserOperationType, using the operation's value."""
    try:
        return next(op for op in UserOperationType if op.value == value)
    except StopIteration:
        raise argparse.ArgumentTypeError(f"Invalid operation: {value}")

def create_arg_parser(require_apkg_file: bool = True, exit_on_error: bool = True) -> argparse.ArgumentParser:
    """Create and return the argument parser with all supported arguments.
    
    Args:
        require_apkg_file: Whether to require the apkg_file argument. Set to False when parsing script lines.
        exit_on_error: Whether to exit on error or raise an exception. Set to False when parsing script lines.
    """
    # Get list of available commands
    commands = [op.value for op in UserOperationType]
    command_help = f"Command to execute. Available commands: {', '.join(commands)}"

    parser = argparse.ArgumentParser(description='Inspect Anki .apkg files', exit_on_error=exit_on_error)
    if require_apkg_file:
        parser.add_argument('apkg_file', help='Path to the .apkg file')
    parser.add_argument('command', type=operation_type,
                       help=command_help,
                       metavar='COMMAND')
    parser.add_argument('--model', help='Model name for operations (source model for migrate-notes)', default=None)
    parser.add_argument('--target-model', help='Target model name for migrate-notes', default=None)
    parser.add_argument('--field-mapping', help='JSON field mapping for migrate-notes ({"source_field": "target_field", ...})', default=None)
    parser.add_argument('--template', help='Template name for question/answer operations', default=None)
    parser.add_argument('--old-field', help='Old field name for rename operation', default=None)
    parser.add_argument('--new-field', help='New field name for rename operation', default=None)
    parser.add_argument('--output', help='Output path for package operation', default=None)
    parser.add_argument('--fields', help='JSON array of field names for add-model (["field1", "field2", ...])', default=None)
    parser.add_argument('--question-format', help='Question template format for add-model', default=None)
    parser.add_argument('--answer-format', help='Answer template format for add-model', default=None)
    parser.add_argument('--css', help='Card CSS styling for add-model', default=None)
    parser.add_argument('--populator-class', help='Python class path for field populator (e.g. "populators.copy_field.CopyFieldPopulator")', default=None)
    parser.add_argument('--populator-config', help='Path to JSON configuration file for the field populator', default=None)
    parser.add_argument('--log-level', choices=['error', 'info', 'debug'], 
                       default='error', help='Set logging level')
    parser.add_argument('--batch-size', type=int, help='Batch size for populate-fields operation')
    parser.add_argument('--config', type=Path, help='Path to JSON config file containing operation arguments', default=None)
    parser.add_argument('--script-file', type=Path, help='Path to script file containing one operation per line', default=None)
    
    return parser

def parse_command_line(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.
    
    Args:
        args: List of command line arguments. If None, sys.argv[1:] is used.
        
    Returns:
        Parsed arguments namespace
        
    Raises:
        SystemExit: If required arguments are missing or invalid
    """
    parser = create_arg_parser(require_apkg_file=True, exit_on_error=True)
    
    if args is None:
        if len(sys.argv) < 3:
            parser.print_help()
            sys.exit(1)
        return parser.parse_args()
    
    return parser.parse_args(args)

def parse_script_line(line: str) -> Optional[argparse.Namespace]:
    """Parse a single line from a script file.
    
    Args:
        line: A single line from the script file
        
    Returns:
        Parsed arguments namespace, or None for empty lines and comments
        
    Raises:
        ValueError: If the line cannot be parsed
    """
    # Skip empty lines and comments
    line = line.strip()
    if not line or line.startswith('#'):
        return None
        
    try:
        # Split the line into arguments, respecting quoted strings
        args = shlex.split(line)
        if not args:
            return None
            
        # Parse the arguments using a parser that doesn't require apkg_file and doesn't exit on error
        parser = create_arg_parser(require_apkg_file=False, exit_on_error=False)
        try:
            return parser.parse_args(args)
        except (argparse.ArgumentError, argparse.ArgumentTypeError) as e:
            raise ValueError(str(e))
        except SystemExit as e:
            if e.code == 2:  # argparse exits with code 2 for argument errors
                raise ValueError("Missing required argument: COMMAND")
            raise ValueError(f"Error parsing line '{line}': {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing line '{line}': {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing line '{line}': {str(e)}") 