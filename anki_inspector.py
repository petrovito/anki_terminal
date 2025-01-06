#!/usr/bin/env python3

import logging
from pathlib import Path

from collection_reader import CollectionReader
from operations import Operations

logger = logging.getLogger('anki_inspector')

class AnkiInspector:
    def __init__(self, apkg_path):
        self.logger = logging.getLogger('anki_inspector')
        self.reader = CollectionReader(Path(apkg_path))
        self.collection = None
        self.operations = None

    def __enter__(self):
        """Setup when entering 'with' context."""
        try:
            self._load_collection()
            return self
        except Exception:
            self.cleanup()  # Clean up if initialization fails
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when exiting 'with' context."""
        self.cleanup()
        return False

    def _load_collection(self):
        """Load the collection using the reader."""
        self.reader.extract_and_connect()
        self.collection = self.reader.read_collection()
        self.operations = Operations(self.collection)

    def cleanup(self):
        """Cleanup temporary files."""
        self.reader.cleanup()

    # Delegate operations to Operations class
    def num_cards(self):
        return self.operations.num_cards()

    def list_fields(self):
        return self.operations.list_fields()

    def print_template(self, model_name=None):
        return self.operations.print_template(model_name) 