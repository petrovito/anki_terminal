#!/usr/bin/env python3

import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Any

from anki_terminal.anki_types import Collection
from anki_terminal.collection_factories import CollectionV2Factory, CollectionV21Factory
from anki_terminal.changelog import ChangeLog
from anki_terminal.db_operations import (
    DBOperation, DBOperationType, DBOperationGenerator
)

logger = logging.getLogger('anki_inspector')

class DatabaseManager:
    """Manages reading and writing to the Anki SQLite database."""
    
    VALID_VERSIONS = {2, 21}  # Set of valid Anki versions
    
    def __init__(self, db_path: Path, anki_version: int):
        """Initialize database manager.
        
        Args:
            db_path: Path to the SQLite database file
            anki_version: Anki database version (2 or 21)
            
        Raises:
            ValueError: If anki_version is not valid
            FileNotFoundError: If database file doesn't exist
        """
        if anki_version not in self.VALID_VERSIONS:
            raise ValueError(f"Invalid Anki version: {anki_version}. Must be one of {self.VALID_VERSIONS}")
            
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
            
        self.anki_version = anki_version
        self._conn: sqlite3.Connection = None
        self._collection: Collection = None
        
        # Use the consolidated operation generator
        self.op_generator = DBOperationGenerator()
        
    def __enter__(self):
        """Setup database connection and validate version.
        
        Raises:
            RuntimeError: If database connection fails
        """
        try:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
                
            return self
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to connect to database: {str(e)}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
        return False

    def read_collection(self) -> Collection:
        """Read collection data from database."""
        if not self._conn:
            raise RuntimeError("Database not connected")
            
        # Get appropriate factory based on version
        factory = CollectionV21Factory() if self.anki_version == 21 else CollectionV2Factory()
        
        # Read table data (same structure for both versions)
        table_data = self._read_table_data()
            
        # Create collection using factory
        self._collection = factory.create_collection(table_data)
        return self._collection

    def apply_changes(self, changelog: ChangeLog) -> None:
        """Apply changes from changelog to the database.
        
        Args:
            changelog: The changelog containing the changes to apply
            
        Raises:
            RuntimeError: If database is not connected
        """
        if not self._conn:
            raise RuntimeError("Database not connected")
            
        if not changelog.has_changes():
            return

        with self._conn:  # Use transaction
            for change in changelog.changes:
                operations = self.op_generator.generate_operations(change)
                for op in operations:
                    self._execute_operation(op)

    def _execute_operation(self, op: DBOperation) -> None:
        """Execute a single database operation.
        
        Args:
            op: The operation to execute
        """
        cursor = self._conn.cursor()
        
        # Build SET clause and parameters for UPDATE
        set_clause = ', '.join(f"{k} = ?" for k in op.values.keys())
        where_clause = ' AND '.join(f"{k} = ?" for k in op.where.keys())
        
        # Build parameters list
        params = list(op.values.values()) + list(op.where.values())
        
        # Execute the UPDATE statement
        sql = f"UPDATE {op.table} SET {set_clause} WHERE {where_clause}"
        cursor.execute(sql, params)

    def _read_table_data(self) -> Dict[str, Any]:
        """Read table data from database.
        
        Returns:
            Dictionary containing raw table data for:
            - col (collection metadata)
            - cards
            - notes
            
        Raises:
            RuntimeError: If required tables are missing
        """
        cursor = self._conn.cursor()
        try:
            return {
                'col': self._read_table(cursor, 'col')[0],  # col table always has exactly one row
                'cards': self._read_table(cursor, 'cards'),
                'notes': self._read_table(cursor, 'notes')
            }
        except RuntimeError as e:
            raise RuntimeError(f"Failed to read tables: {str(e)}")

    def _read_table(self, cursor: sqlite3.Cursor, table_name: str) -> List[Dict[str, Any]]:
        """Read all rows from a table into a list of dictionaries.
        
        Args:
            cursor: Database cursor
            table_name: Name of the table to read
            
        Returns:
            List of dictionaries, each representing a row
            
        Raises:
            RuntimeError: If table doesn't exist or can't be read
        """
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to read table {table_name}: {str(e)}")

    def save(self):
        """Save changes back to database."""
        if not self._collection:
            raise RuntimeError("No collection loaded")
            
        # TODO: Implement save functionality
        raise NotImplementedError("Save functionality not yet implemented")