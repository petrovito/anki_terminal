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
        # Parse arguments into apkg_file, output_path, and operation
        apkg_file, output_path, operation = parse_args()
        
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