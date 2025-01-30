#!/usr/bin/env python3

import logging
from pathlib import Path
from typing import Optional

from apkg_manager import ApkgManager
from database_manager import DatabaseManager
from changelog import ChangeLog
from operation_models import UserOperationRecipe
from operation_executor import OperationExecutor
from operations import UserOperationParser, ReadOperations, WriteOperations

logger = logging.getLogger('anki_inspector')

class AnkiContext:
    def __init__(self, apkg_path: Path, output_path: Optional[Path] = None, read_only: bool = False):
        self._logger = logging.getLogger('anki_inspector')
        self._apkg_path = Path(apkg_path)
        self._output_path = output_path
        self._read_only = read_only
        
        # Validate read-only mode and output path
        if not read_only and not output_path:
            raise ValueError("Output path must be specified for write operations")
        
        self._extractor = None
        self._db_reader = None
        self._collection = None
        self._changelog = None
        self._read_ops = None
        self._write_ops = None
        self._parser = None
        self._executor = None
        self._is_destroyed = False

    def __enter__(self):
        """Setup and maintain context of extractor and db reader."""
        if self._is_destroyed:
            raise RuntimeError("This context has been destroyed and cannot be reused")
        try:
            self._extractor = ApkgManager(self._apkg_path, read_only=self._read_only).__enter__()
            self._db_reader = DatabaseManager(self._extractor.db_path).__enter__()
            self._collection = self._db_reader.read_collection()
            self._changelog = ChangeLog()
            self._read_ops = ReadOperations(self._collection)
            self._write_ops = None if self._read_only else WriteOperations(self._collection, self._changelog)
            self._parser = UserOperationParser()
            self._executor = OperationExecutor(self._read_ops, self._write_ops)
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
                if not self._read_only:
                    logger.info("Changes detected, packaging new .apkg file")
                    self._package()
                else:
                    logger.warning("Changes were made in read-only mode, changes will be lost")
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

    def run(self, user_recipe: UserOperationRecipe) -> None:
        """Parse user operation and execute the operation plan."""
        if self._is_destroyed:
            raise RuntimeError("This context has been destroyed and cannot run operations")
        
        # Validate operation against read-only mode
        if self._read_only and not user_recipe.is_read_only:
            raise RuntimeError("Cannot perform write operation in read-only mode")
        
        # Parse user operation into an operation plan
        plan = self._parser.parse(user_recipe)

        # Execute the operation plan
        for operation in plan.operations:
            self._executor.execute(operation)

    def _package(self) -> None:
        """Internal method to package the current state of the collection."""
        if self._read_only:
            raise RuntimeError("Cannot package in read-only mode")
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

