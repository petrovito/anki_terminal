#!/usr/bin/env python3

import argparse
import sys
import logging
from anki_inspector import AnkiInspector

logger = logging.getLogger('anki_inspector')

def setup_logging(verbose=False):
    """Setup logging configuration."""
    # Create handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Set log level based on verbose flag
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)

def run_command(inspector, command, model=None):
    """Execute a single command and return its result."""
    logger.info(f"Running command: {command}")
    
    if command == 'num_cards':
        result = inspector.num_cards()
        logger.info(f"Total number of cards: {result}")
        return result

    elif command == 'list_fields':
        fields = inspector.list_fields()
        output = []
        for model_name, field_list in fields.items():
            output.append(f"{model_name}:")
            for field in field_list:
                output.append(f"\t{field}")
        logger.info("Fields by model:\n" + "\n".join(output))
        return fields

    elif command == 'print_template':
        templates = inspector.print_template(model)
        output = []
        for model_name, data in templates.items():
            output.append(f"{model_name}:")
            output.append("\tFields:")
            for field in data['fields']:
                output.append(f"\t\t{field}")
            output.append("\tCard Types:")
            for template in data['templates']:
                output.append(f"\t\t{template}")
        logger.info("Templates:\n" + "\n".join(output))
        return templates

def main():
    parser = argparse.ArgumentParser(description='Inspect Anki .apkg files')
    parser.add_argument('apkg_file', help='Path to the .apkg file')
    parser.add_argument('command', choices=['num_cards', 'list_fields', 'print_template', 'run_all'],
                       help='Command to execute')
    parser.add_argument('--model', help='Model name for print_template command', default=None)
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    setup_logging(args.verbose)
    inspector = None

    try:
        inspector = AnkiInspector(args.apkg_file)

        if args.command == 'run_all':
            logger.info("Running all commands")
            run_command(inspector, 'num_cards')
            run_command(inspector, 'list_fields')
            run_command(inspector, 'print_template')
        else:
            result = run_command(inspector, args.command, args.model)
            if args.command == 'num_cards':
                print(f"{result}")
            elif args.command == 'list_fields':
                for model_name, field_list in result.items():
                    print(f"{model_name}:")
                    for field in field_list:
                        print(f"\t{field}")
            elif args.command == 'print_template':
                for model_name, data in result.items():
                    print(f"{model_name}:")
                    print("\tFields:")
                    for field in data['fields']:
                        print(f"\t\t{field}")
                    print("\tCard Types:")
                    for template in data['templates']:
                        print(f"\t\t{template}")

    except Exception as e:
        logger.error(str(e))
        sys.exit(1)
    finally:
        if inspector:
            inspector.cleanup()

if __name__ == '__main__':
    main() 