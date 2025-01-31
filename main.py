#!/usr/bin/env python3

import sys
import logging
from arg_parser import parse_command_line
from user_operation_parser import UserOperationParser
from anki_context import AnkiContext

logger = logging.getLogger(__name__)

def setup_logging(level_str: str):
    """Setup logging with the specified level."""
    level = getattr(logging, level_str.upper())
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')

def main():
    args = parse_command_line()
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