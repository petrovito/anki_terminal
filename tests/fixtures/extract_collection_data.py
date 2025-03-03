#!/usr/bin/env python
"""
Script to extract collection data from Anki database files and save to JSON.

This script uses the existing framework in database_manager.py to extract
raw table data and save it to JSON files for use in tests.
"""

import json
import sys
from pathlib import Path
import tempfile
import shutil

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database_manager import DatabaseManager

# Base path to test data directory
TEST_DATA_DIR = Path("test_data")

def extract_and_save_table_data(db_path, version):
    """Extract raw table data using DatabaseManager and save to JSON.
    
    Args:
        db_path: Path to the database file
        version: Anki version (2 or 21)
    """
    print(f"Extracting data from {db_path}...")
    
    # Use DatabaseManager to read the collection
    with DatabaseManager(db_path, anki_version=version) as db:
        # Get raw table data
        raw_table_data = db._read_table_data()
    
    # Save to JSON file
    output_path = TEST_DATA_DIR / f"raw_table_data_v{version}.json"
    print(f"Saving data to {output_path}...")
    
    # Convert non-serializable objects to strings
    def json_serializable(obj):
        if isinstance(obj, dict):
            return {k: json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [json_serializable(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)
    
    # Serialize the data
    serializable_data = json_serializable(raw_table_data)
    
    # Write to file with pretty formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, indent=2, ensure_ascii=False)
    
    print(f"Data saved to {output_path}")

def main():
    """Extract data and save to JSON files."""
    # Extract data from v2 database
    extract_and_save_table_data(TEST_DATA_DIR / "collection.anki2", 2)
    
    # Extract data from v21 database
    extract_and_save_table_data(TEST_DATA_DIR / "collection.anki21", 21)
    
    print("\nDone! The raw table data has been saved to JSON files in the test_data directory.")
    print("You can now use these files in your test fixtures.")

if __name__ == "__main__":
    main() 