#!/usr/bin/env python3

import argparse
import sys
import logging
from anki_inspector import AnkiInspector
from operations import OperationType, OperationRecipe

logger = logging.getLogger('anki_inspector')

def setup_logging(verbose=False):
    """Setup logging configuration."""
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)

def parse_args():
    parser = argparse.ArgumentParser(description='Inspect Anki .apkg files')
    parser.add_argument('apkg_file', help='Path to the .apkg file')
    parser.add_argument('command', type=OperationType, choices=list(OperationType),
                        help='Command to execute')
    parser.add_argument('--model', help='Model name for print_template command', default=None)
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(args.verbose)
    inspector = None

    try:
        inspector = AnkiInspector(args.apkg_file)
        recipe = OperationRecipe(args.command, args.model)
        inspector.operations.run(recipe)

    except Exception as e:
        logger.error(str(e))
        sys.exit(1)
    finally:
        if inspector:
            inspector.cleanup()

if __name__ == '__main__':
    main() 