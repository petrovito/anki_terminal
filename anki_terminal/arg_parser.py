import argparse
from pathlib import Path
from typing import Tuple
from anki_terminal.ops.registry import OperationRegistry
from anki_terminal.ops.base import Operation
from anki_terminal.ops.printer import JsonPrinter, HumanReadablePrinter, OperationPrinter



def create_operation_subparser(subparsers: argparse._SubParsersAction, op_name: str, op_info: dict) -> None:
    """Create a subparser for a specific operation.
    
    Args:
        subparsers: The subparsers action to add to
        op_name: Name of the operation
        op_info: Operation metadata including description and arguments
    """
    subparser = subparsers.add_parser(
        op_name,
        help=op_info["description"]
    )
    
    # Add arguments from operation
    for arg in op_info["arguments"]:
        subparser.add_argument(
            f"--{arg.name.replace('_', '-')}",
            required=arg.required,
            default=arg.default,
            help=arg.description + (" (required)" if arg.required else f" (default: {arg.default})")
        )

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all operations.
    
    Returns:
        Configured argument parser
    """
    # Create main parser
    parser = argparse.ArgumentParser(
        description="Anki collection inspector and modifier",
        prog="anki-terminal"
    )
    
    # Add common arguments
    parser.add_argument(
        "apkg_file",
        type=Path,
        help="Path to the Anki package file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for modified Anki package (default: overwrite input file)",
        default=None
    )
    parser.add_argument(
        "--format",
        choices=["human", "json"],
        default="human",
        help="Output format (default: human)"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (only applies to JSON format)"
    )
    
    # Create subparsers for each operation
    subparsers = parser.add_subparsers(
        dest="operation",
        required=True,
        help="Operation to perform"
    )
    
    # Get all available operations from registry
    registry = OperationRegistry()
    operations = registry.list_operations()
    
    # Create a subparser for each operation
    for op_name, op_info in operations.items():
        create_operation_subparser(subparsers, op_name, op_info)
    
    return parser

def get_printer(args: argparse.Namespace) -> OperationPrinter:
    """Get the appropriate printer based on command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Configured printer instance
    """
    if args.format == "json":
        return JsonPrinter(pretty=args.pretty)
    else:
        return HumanReadablePrinter()

def parse_args() -> Tuple[Path, Path, Operation]:
    """Parse command line arguments and create operation instance.
    
    Returns:
        Tuple of (apkg_file_path, output_path, operation_instance)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Get operation class from registry
    registry = OperationRegistry()
    operation_class = registry.get(args.operation)
    
    # Get appropriate printer
    printer = get_printer(args)
    
    # Convert args to dict, removing None values and operation name
    op_args = {
        k.replace('-', '_'): v 
        for k, v in vars(args).items() 
        if k not in ('operation', 'apkg_file', 'output', 'format', 'pretty') and v is not None
    }
    
    # Create operation instance with printer
    operation = operation_class(printer=printer, **op_args)
    
    return args.apkg_file, args.output, operation 