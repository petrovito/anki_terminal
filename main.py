#!/usr/bin/env python3

import argparse
import sys
import logging
from anki_inspector import AnkiInspector
from operations import OperationType, OperationRecipe
from pathlib import Path

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

    try:
        output_path = Path(args.output) if args.output else None
        with AnkiInspector(args.apkg_file, output_path) as inspector:
            recipe = OperationRecipe(args.command, args.model, args.template)
            inspector.operations.run(recipe)
    except Exception as e:
        logger.error(str(e))
        sys.exit(1) 

if __name__ == '__main__':
    main() 