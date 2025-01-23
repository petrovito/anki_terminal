#!/usr/bin/env python3

import argparse
import sys
import logging
from pathlib import Path
from anki_context import AnkiContext
from operations import OperationType, OperationRecipe

logger = logging.getLogger('anki_inspector')

def setup_logging(level: str):
    """Setup logging configuration."""
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Convert string level to logging constant
    log_level = getattr(logging, level.upper())
    logger.setLevel(log_level)

def parse_args():
    parser = argparse.ArgumentParser(description='Inspect Anki .apkg files')
    parser.add_argument('apkg_file', help='Path to the .apkg file')
    parser.add_argument('command', type=OperationType, choices=list(OperationType),
                        help='Command to execute')
    parser.add_argument('--model', help='Model name for template operations', default=None)
    parser.add_argument('--template', help='Template name for question/answer operations', default=None)
    parser.add_argument('--old-field', help='Old field name for rename operation', default=None)
    parser.add_argument('--new-field', help='New field name for rename operation', default=None)
    parser.add_argument('--output', help='Output path for package operation', default=None)
    parser.add_argument('--log-level', choices=['error', 'info', 'debug'], 
                       default='error', help='Set logging level')

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()

def main():
    args = parse_args()
    setup_logging(args.log_level)

    # Create recipe from arguments
    recipe = OperationRecipe(
        operation_type=args.command,
        model_name=args.model,
        template_name=args.template,
        old_field_name=args.old_field,
        new_field_name=args.new_field
    )

    # Create output path if specified
    output_path = Path(args.output) if args.output else None

    # Run operation in context
    with AnkiContext(args.apkg_file, output_path) as context:
        context.run(recipe)

if __name__ == '__main__':
    main() 