#!/usr/bin/env python3

import logging
import tempfile
import os
import zipfile
from pathlib import Path

logger = logging.getLogger('anki_inspector')

class ApkgExtractor:
    def __init__(self, apkg_path: Path):
        self.apkg_path = apkg_path
        self.temp_dir = tempfile.mkdtemp()
        
    def __enter__(self):
        """Extract files and return self."""
        logger.debug(f"Extracting {self.apkg_path}...")
        with zipfile.ZipFile(self.apkg_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
            logger.debug(f"Extracted {self.apkg_path} to {self.temp_dir}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary directory."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
        return False

    @property
    def db_path(self) -> Path:
        """Get path to the extracted database."""
        return Path(self.temp_dir) / 'collection.anki2' 

    def package(self, output_path: Path) -> None:
        """Create a new .apkg file with all contents of the temp directory."""
        logger.debug(f"Creating new .apkg file at: {output_path}")
        with zipfile.ZipFile(output_path, 'w') as zip_ref:
            # Add all files from temp directory
            for file_path in Path(self.temp_dir).rglob('*'):
                if file_path.is_file():
                    # Get relative path from temp_dir
                    relative_path = file_path.relative_to(self.temp_dir)
                    logger.debug(f"Adding file to package: {relative_path}")
                    zip_ref.write(file_path, relative_path) 