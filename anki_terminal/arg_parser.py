import argparse
from pathlib import Path
from typing import Optional, Tuple, Type

from anki_terminal.ops.op_base import Operation
from anki_terminal.ops.op_registry import OperationRegistry
from anki_terminal.ops.printer import (HumanReadablePrinter, JsonPrinter,
                                       OperationPrinter)
from anki_terminal.populators.populator_registry import PopulatorRegistry


def create_operation_subparser(subparsers: argparse._SubParsersAction, op_name: str, op_class: Type[Operation]) -> None:
    """Create a subparser for a specific operation.
    
    Args:
        subparsers: The subparsers action to add to
        op_name: Name of the operation
        op_class: The operation class
    """
    subparser = subparsers.add_parser(
        op_name,
        help=op_class.description
    )
    
    # Let the operation set up its own subparser
    op_class.setup_subparser(subparser)

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
        "--apkg",
        type=Path,
        help="Path to the Anki package file (required for most operations)",
        dest="apkg_file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to write output to (default: stdout)",
        dest="output_file"
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
        help="Pretty print JSON output"
    )
    
    # Create subparsers for operations
    subparsers = parser.add_subparsers(
        dest="operation",
        help="Operation to perform"
    )
    
    # Add operation subparsers
    registry = OperationRegistry()
    for op_name, op_info in registry.list_operations().items():
        op_class = registry.get(op_name)
        create_operation_subparser(subparsers, op_name, op_class)
    
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

def parse_args() -> Tuple[Operation, Optional[Path], Optional[Path]]:
    """Parse command line arguments.
    
    Returns:
        Tuple of (operation instance, output file path, printer)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Create printer
    if args.format == "json":
        printer = JsonPrinter(pretty=args.pretty)
    else:
        printer = HumanReadablePrinter()
    
    # Get operation class and create instance
    registry = OperationRegistry()
    op_class = registry.get(args.operation)
    operation = op_class(printer=printer, **vars(args))
    
    return operation, args.apkg_file, args.output_file 