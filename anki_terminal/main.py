#!/usr/bin/env python3

import sys
import logging
from anki_terminal.arg_parser import parse_args
from anki_terminal.anki_context import AnkiContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Parse arguments into operation, output file, and printer
        operation, apkg_file, output_path = parse_args()
        
        # Check if APKG file is provided for operations that need it
        if not hasattr(operation, 'args') or 'apkg_file' not in operation.args:
            logger.error("Error: --apkg argument is required for this operation")
            sys.exit(1)
        
        # Open the Anki context and run the operation
        with AnkiContext(apkg_file, output_path, read_only=operation.readonly) as context:
            context.run(operation)
                    
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 