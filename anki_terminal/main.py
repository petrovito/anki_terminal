#!/usr/bin/env python3

import traceback
import logging
import sys

from anki_terminal.anki_context import AnkiContext
from anki_terminal.arg_parser import parse_args

# Configure logging with ERROR as default level
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Parse arguments into operation, output file, and printer
        metaop, apkg_file, output_path = parse_args()
        
        # Check if APKG file is provided for operations that need it
        if not metaop.readonly and (not apkg_file):
            logger.error("Error: --output argument is required for write operations")
            sys.exit(1)
        
        # Open the Anki context and run the operation
        with AnkiContext(apkg_file, output_path, read_only=metaop.readonly) as context:
            context.run(metaop)
                    
    except ValueError as e:
        logger.error(str(e))
        logger.debug(traceback.format_exc())
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main() 