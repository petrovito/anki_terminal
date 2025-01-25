#!/usr/bin/env python3

import argparse
import sys
import logging
from pathlib import Path
from anki_context import AnkiContext
from operations import OperationType, OperationRecipe
import json

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

def operation_type(value: str) -> OperationType:
    """Convert string to OperationType, using the operation's value."""
    try:
        return next(op for op in OperationType if op.value == value)
    except StopIteration:
        raise argparse.ArgumentTypeError(f"Invalid operation: {value}")

def parse_args():
    # Get list of available commands
    commands = [op.value for op in OperationType]
    command_help = f"Command to execute. Available commands: {', '.join(commands)}"

    parser = argparse.ArgumentParser(description='Inspect Anki .apkg files')
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
    parser.add_argument('--log-level', choices=['error', 'info', 'debug'], 
                       default='error', help='Set logging level')

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()

def main():
    args = parse_args()
    setup_logging(args.log_level)

    # Parse fields JSON if provided
    fields = None
    if args.fields:
        try:
            fields = json.loads(args.fields)
            if not isinstance(fields, list):
                raise ValueError("Fields must be a JSON array")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid fields JSON: {e}")
            sys.exit(1)

    # Create recipe from arguments
    recipe = OperationRecipe(
        operation_type=args.command,
        model_name=args.model,
        template_name=args.template,
        old_field_name=args.old_field,
        new_field_name=args.new_field,
        target_model_name=args.target_model,
        field_mapping=args.field_mapping,
        fields=fields,
        question_format=args.question_format,
        answer_format=args.answer_format,
        css=args.css
    )

    # Create output path if specified
    output_path = Path(args.output) if args.output else None

    # Validate output path against operation type
    if not recipe.is_read_only and not output_path:
        logger.error("Output path must be specified for write operations")
        sys.exit(1)
    if recipe.is_read_only and output_path:
        logger.warning("Output path will be ignored for read-only operation")
        output_path = None

    # Run operation in context
    with AnkiContext(args.apkg_file, output_path, read_only=recipe.is_read_only) as context:
        context.run(recipe)

if __name__ == '__main__':
    main() 