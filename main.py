#!/usr/bin/env python3

import sys
import logging
from arg_parser import parse_args
from anki_context import AnkiContext

logger = logging.getLogger(__name__)

def main():
    try:
        # Parse arguments into apkg_file, output_path, and operation
        apkg_file, output_path, operation = parse_args()
        
        
        # Open the Anki context and run the operation
        with AnkiContext(apkg_file, output_path, read_only=operation.readonly) as context:
            results = context.run(operation)
            
            # Process results
            for result in results:
                if result.success:
                    if result.data:
                        # Pretty print data for read operations
                        for key, value in result.data.items():
                            if isinstance(value, list):
                                print(f"\n{key}:")
                                for item in value:
                                    print(f"  {item}")
                            else:
                                print(f"{key}: {value}")
                    else:
                        print(result.message)
                else:
                    logger.error(result.message)
                    sys.exit(1)
                    
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 