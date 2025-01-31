#!/usr/bin/env python3

import argparse
import sys
import logging
import json
from pathlib import Path
from anki_context import AnkiContext
from operation_models import UserOperationRecipe, UserOperationType
from user_operation_parser import UserOperationParser

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

def operation_type(value: str) -> UserOperationType:
    """Convert string to UserOperationType, using the operation's value."""
    try:
        return next(op for op in UserOperationType if op.value == value)
    except StopIteration:
        raise argparse.ArgumentTypeError(f"Invalid operation: {value}")

def parse_args():
    # Get list of available commands
    commands = [op.value for op in UserOperationType]
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
    parser.add_argument('--populator-class', help='Python class path for field populator (e.g. "populators.copy_field.CopyFieldPopulator")', default=None)
    parser.add_argument('--populator-config', help='Path to JSON configuration file for the field populator', default=None)
    parser.add_argument('--log-level', choices=['error', 'info', 'debug'], 
                       default='error', help='Set logging level')
    parser.add_argument('--batch-size', type=int, help='Batch size for populate-fields operation')
    parser.add_argument('--config', type=Path, help='Path to JSON config file containing operation arguments', default=None)

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()

def main():
    args = parse_args()
    setup_logging(args.log_level)

    try:
        # Parse user operation into an operation plan
        parser = UserOperationParser()
        op_plan = parser.parse_from_args(args)

        # Execute the operation plan in the AnkiContext
        with AnkiContext(args.apkg_file, op_plan.output_path, read_only=op_plan.read_only) as context:
            context.run(op_plan)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

if __name__ == '__main__':
    main() 