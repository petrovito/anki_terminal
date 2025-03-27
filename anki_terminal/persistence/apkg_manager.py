#!/usr/bin/env python3

import logging
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger('anki_inspector')

class ApkgManager:
    """Manages extraction and packaging of .apkg files.
    
    An Anki package can contain either collection.anki2 (version 2) or collection.anki21 (version 21),
    or both versions. When both versions are present, version 21 should be preferred.
    """
    
    # Supported database filenames
    ANKI21_DB = 'collection.anki21'
    ANKI2_DB = 'collection.anki2'
    
    def __init__(self, apkg_path: Path, read_only: bool = False):
        self.apkg_path = Path(apkg_path)
        self.read_only = read_only
        self.temp_dir = None
        self.db_path = None
        self.db_version = None  # Will be set to 21 or 2 based on the file found

    def __enter__(self):
        """Extract .apkg file to temporary directory."""
        if not self.apkg_path.exists():
            raise FileNotFoundError(f"Apkg file not found: {self.apkg_path}")

        logger.debug(f"Processing apkg file: {self.apkg_path}")
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        logger.debug(f"Created temporary directory: {self.temp_dir}")

        try:
            with zipfile.ZipFile(self.apkg_path, 'r') as zf:
                # List all files in the archive
                files = zf.namelist()
                
                # Check for database files - prefer version 21 if both exist
                has_anki21 = self.ANKI21_DB in files
                has_anki2 = self.ANKI2_DB in files
                
                if has_anki21:
                    db_file = self.ANKI21_DB
                    self.db_version = 21
                elif has_anki2:
                    db_file = self.ANKI2_DB
                    self.db_version = 2
                else:
                    raise ValueError("No valid Anki database file found in apkg")
                
                logger.debug(f"Found Anki {self.db_version} database: {db_file}")
                
                if self.read_only:
                    # For read-only operations, only extract the database file
                    zf.extract(db_file, self.temp_dir)
                else:
                    # For write operations, extract everything
                    zf.extractall(self.temp_dir)

                self.db_path = Path(self.temp_dir) / db_file
                if not self.db_path.exists():
                    raise ValueError(f"Failed to extract {db_file}")

            return self

        except Exception as e:
            # Clean up on error
            if self.temp_dir:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary directory."""
        if self.temp_dir:
            try:
                shutil.rmtree(self.temp_dir)
                logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Error cleaning up temporary directory: {str(e)}")
        return False

    def package(self, output_path: Path) -> None:
        """Package the current state into a new .apkg file."""
        if self.read_only:
            raise RuntimeError("Cannot package in read-only mode")
            
        if not self.temp_dir:
            raise RuntimeError("No files to package")
        if output_path.exists():
            raise ValueError(f"Output file already exists: {output_path}")

        logger.debug(f"Packaging to: {output_path}")
        
        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create new zip file
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add all files from temp directory
            temp_dir_path = Path(self.temp_dir)
            for file_path in temp_dir_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir_path)
                    zf.write(file_path, arcname)

        logger.debug("Packaging complete") 