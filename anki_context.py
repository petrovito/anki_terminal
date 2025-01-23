#!/usr/bin/env python3

import logging
from pathlib import Path
from typing import Optional

from apkg_manager import ApkgManager
from database_manager import DatabaseManager
from operations import UserOperations, OperationRecipe
from changelog import ChangeLog

logger = logging.getLogger('anki_inspector')

class AnkiContext:
    def __init__(self, apkg_path, output_path: Optional[Path] = None):
        self._logger = logging.getLogger('anki_inspector')
        self._apkg_path = Path(apkg_path)
        self._output_path = output_path
        self._extractor = None
        self._db_reader = None
        self._collection = None
        self._changelog = None
        self._operations = None
        self._is_destroyed = False

    def __enter__(self):
        """Setup and maintain context of extractor and db reader."""
        if self._is_destroyed:
            raise RuntimeError("This context has been destroyed and cannot be reused")
        try:
            self._extractor = ApkgManager(self._apkg_path).__enter__()
            self._db_reader = DatabaseManager(self._extractor.db_path).__enter__()
            self._collection = self._db_reader.read_collection()
            self._changelog = ChangeLog(self._collection)
            self._operations = UserOperations(self._collection, self._changelog)
            return self
        except Exception:
            self._cleanup()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup all resources."""
        self._cleanup()
        return False

    def _cleanup(self):
        """Clean up resources in reverse order of creation."""
        try:
            # If we have writes and an output path, package the changes
            if self._has_writes():
                if self._output_path:
                    logger.info("Changes detected, packaging new .apkg file")
                    self._package()
                else:
                    logger.warning("Changes were made but no output path specified, changes will be lost")
        finally:
            # Always clean up resources
            if self._db_reader:
                self._db_reader.__exit__(None, None, None)
            if self._extractor:
                self._extractor.__exit__(None, None, None)
            self._is_destroyed = True

    def _has_writes(self) -> bool:
        """Check if any write operations were performed."""
        return self._changelog is not None and len(self._changelog.changes) > 0

    def run(self, recipe: OperationRecipe) -> None:
        """Run an operation after checking context is valid."""
        if self._is_destroyed:
            raise RuntimeError("This context has been destroyed and cannot run operations")
        self._operations.run(recipe)

    def _package(self) -> None:
        """Internal method to package the current state of the collection."""
        if not self._output_path:
            raise ValueError("No output path specified")
        if not self._extractor or not self._db_reader:
            raise RuntimeError("Cannot package: no collection is loaded")
        if self._output_path.exists():
            raise ValueError(f"Output file already exists: {self._output_path}")
        
        # Apply any pending changes to the database
        if self._has_writes():
            logger.info("Applying changes to database before packaging")
            self._db_reader.apply_changes(self._changelog)
        
        # Close the database connection
        self._db_reader.__exit__(None, None, None)
        self._db_reader = None
        
        # Create the new package
        self._extractor.package(self._output_path)

