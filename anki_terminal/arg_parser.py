import argparse
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from anki_terminal.metaops.metaop_recipe import MetaOpRecipe
from anki_terminal.metaops.metaop_manager import MetaOpManager
from anki_terminal.metaops.recipe_registry import RecipeRegistry



def create_meta_op_subparser(
        subparsers: argparse._SubParsersAction,
        meta_op_recipe: MetaOpRecipe,
        metaop_manager: MetaOpManager
    ) -> None:
    """Create a subparser for a specific operation.
    
    Args:
        subparsers: The subparsers action to add to
        meta_op: The meta operation
    """
    subparser = subparsers.add_parser(
        meta_op_recipe.name,
        help=meta_op_recipe.description
    )
    
    # Add config file option
    subparser.add_argument(
        "--config-file",
        help="Path to a configuration file (JSON)",
        dest="config_file"
    )
    
    # Let the operation set up its own subparser
    metaop_manager.setup_subparser(recipe=meta_op_recipe, subparser=subparser)


def create_parser(metaop_manager: MetaOpManager) -> argparse.ArgumentParser:
    """Create the argument parser with all operations.
    
    Returns:
        Configured argument parser
    """
    # Create main parser
    parser = argparse.ArgumentParser(
        description="Anki collection inspector and modifier",
        prog="anki-terminal"
    )

    # Only for pre-parser, but added so it is included in help
    parser.add_argument(
        "--op-folder",
        type=Path,
        action="append",
        help="Path to a folder containing the operations",
        dest="op_folders"
    )
    
    # Add common arguments
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging (INFO level)",
        dest="verbose"
    )
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
    
    # Add config file option
    parser.add_argument(
        "--config-file",
        help="Path to a configuration file (JSON)",
        dest="config_file"
    )
    
    # Create subparsers for operations
    subparsers = parser.add_subparsers(
        dest="operation",
        help="Operation to perform"
    )
    
    # Add operation subparsers
    for meta_op_recipe in metaop_manager.recipe_registry.get_all().values():
        create_meta_op_subparser(subparsers, meta_op_recipe, metaop_manager)

    #TODO Add custom metaop
    
    return parser

def create_preparser() -> argparse.ArgumentParser:
    """Create the pre-parser with all operations.
    
    Returns:
        Configured pre-parser
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--op-folder",
        type=Path,
        action="append",
        help="Path to a folder containing the operations",
        dest="op_folders"
    )
    return parser


def parse_args() -> Tuple[MetaOpRecipe, Optional[Path], Optional[Path]]:
    """Parse command line arguments.
    
    Returns:
        Tuple of (operation instance, output file path, printer)
    """
    pre_parser = create_preparser()
    pre_args, unknown_args = pre_parser.parse_known_args()

    metaop_manager = MetaOpManager()
    for op_folder in pre_args.op_folders or []:
        metaop_manager.load_from_folder(op_folder)
    metaop_manager.initialize()

    parser = create_parser(metaop_manager)
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create operation using factory
    metaop = metaop_manager.create_metaop(vars(args))
    
    return metaop, args.apkg_file, args.output_file 