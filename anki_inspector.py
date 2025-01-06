#!/usr/bin/env python3

import logging
from pathlib import Path

from apkg_extractor import ApkgExtractor
from database_reader import DatabaseReader
from operations import Operations

logger = logging.getLogger('anki_inspector')

class AnkiInspector:
    def __init__(self, apkg_path):
        self.logger = logging.getLogger('anki_inspector')
        self.apkg_path = Path(apkg_path)
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
            self.operations = Operations(self.collection)
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

