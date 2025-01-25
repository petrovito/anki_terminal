#!/usr/bin/env python3

import logging
import tempfile
import zipfile
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger('anki_inspector')

class ApkgManager:
    """Manages extraction and packaging of .apkg files."""
    def __init__(self, apkg_path: Path, read_only: bool = False):
        self.apkg_path = Path(apkg_path)
        self.read_only = read_only
        self.temp_dir = None
        self.db_path = None

    def __enter__(self):
        """Extract .apkg file to temporary directory."""
        if not self.apkg_path.exists():
            raise FileNotFoundError(f"Apkg file not found: {self.apkg_path}")

        logger.debug(f"Processing apkg file: {self.apkg_path}")
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        logger.debug(f"Created temporary directory: {self.temp_dir}")

        try:
            if self.read_only:
                # For read-only operations, only extract collection.anki2
                with zipfile.ZipFile(self.apkg_path, 'r') as zf:
                    zf.extract('collection.anki2', self.temp_dir)
            else:
                # For write operations, extract everything
                with zipfile.ZipFile(self.apkg_path, 'r') as zf:
                    zf.extractall(self.temp_dir)

            self.db_path = Path(self.temp_dir) / 'collection.anki2'
            if not self.db_path.exists():
                raise ValueError("No collection.anki2 file found in apkg")

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
                    logger.debug(f"Added file to package: {arcname}")

        logger.debug("Packaging complete") 