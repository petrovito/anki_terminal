#!/usr/bin/env python3

import logging
from pathlib import Path
from typing import Optional

from apkg_manager import ApkgManager
from database_manager import DatabaseManager
from operations import UserOperations

logger = logging.getLogger('anki_inspector')

class AnkiContext:
    def __init__(self, apkg_path, output_path: Optional[Path] = None):
        self.logger = logging.getLogger('anki_inspector')
        self.apkg_path = Path(apkg_path)
        self.output_path = output_path
        self.extractor = None
        self.db_reader = None
        self.collection = None
        self.operations = None
        self.is_destroyed = False

    def __enter__(self):
        """Setup and maintain context of extractor and db reader."""
        if self.is_destroyed:
            raise RuntimeError("This context has been destroyed and cannot be reused")
        try:
            self.extractor = ApkgManager(self.apkg_path).__enter__()
            self.db_reader = DatabaseManager(self.extractor.db_path).__enter__()
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
        try:
            # If we have writes and an output path, package the changes
            if self.operations and self.operations.has_writes:
                if self.output_path:
                    logger.info("Changes detected, packaging new .apkg file")
                    self._package()
                else:
                    logger.warning("Changes were made but no output path specified, changes will be lost")
        finally:
            # Always clean up resources
            if self.db_reader:
                self.db_reader.__exit__(None, None, None)
            if self.extractor:
                self.extractor.__exit__(None, None, None)
            self.is_destroyed = True
            if self.operations:
                self.operations.mark_destroyed()

    def package(self) -> None:
        """Package the current state of the collection into a new .apkg file."""
        if self.is_destroyed:
            raise RuntimeError("This context has been destroyed and cannot package files")
        self._package()
        self.is_destroyed = True
        if self.operations:
            self.operations.mark_destroyed()

    def _package(self) -> None:
        """Internal method to package the current state of the collection."""
        if not self.output_path:
            raise ValueError("No output path specified")
        if not self.extractor or not self.db_reader:
            raise RuntimeError("Cannot package: no collection is loaded")
        if self.output_path.exists():
            raise ValueError(f"Output file already exists: {self.output_path}")
        
        # Apply any pending changes to the database
        if self.operations and self.operations.write_ops.changelog.changes:
            logger.info("Applying changes to database before packaging")
            self.db_reader.apply_changes(self.operations.write_ops.changelog)
        
        # Close the database connection
        self.db_reader.__exit__(None, None, None)
        self.db_reader = None
        
        # Create the new package
        self.extractor.package(self.output_path)

