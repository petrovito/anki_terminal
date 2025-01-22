#!/usr/bin/env python3

import logging
from pathlib import Path
from typing import Optional

from apkg_extractor import ApkgExtractor
from database_reader import DatabaseReader
from operations import UserOperations

logger = logging.getLogger('anki_inspector')

class AnkiInspector:
    def __init__(self, apkg_path, output_path: Optional[Path] = None):
        self.logger = logging.getLogger('anki_inspector')
        self.apkg_path = Path(apkg_path)
        self.output_path = output_path
        self.extractor = None
        self.db_reader = None
        self.collection = None
        self.operations = None

    def __enter__(self):
        """Setup and maintain context of extractor and db reader."""
        try:
            self.extractor = ApkgExtractor(self.apkg_path).__enter__()
            self.db_reader = DatabaseReader(self.extractor.db_path).__enter__()
            self.collection = self.db_reader.read_collection()
            self.operations = UserOperations(self.collection)
            return self
        except Exception:
            self.cleanup()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup all resources."""
        self.cleanup()
        return False

    def cleanup(self):
        """Clean up resources in reverse order of creation."""
        if self.db_reader:
            self.db_reader.__exit__(None, None, None)
        if self.extractor:
            self.extractor.__exit__(None, None, None)

    def package(self) -> None:
        """Package the current state of the collection into a new .apkg file."""
        if not self.output_path:
            raise ValueError("No output path specified")
        if not self.extractor or not self.db_reader:
            raise RuntimeError("Cannot package: no collection is loaded")
        if self.output_path.exists():
            raise ValueError(f"Output file already exists: {self.output_path}")
        
        # Close the database connection
        self.db_reader.__exit__(None, None, None)
        self.db_reader = None
        
        # Create the new package
        self.extractor.package(self.output_path)
        
        # The context is now invalid and should be exited
        raise RuntimeError("Context is no longer valid after packaging. Please exit the context and create a new one if needed.")

