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
        
    def extract(self) -> Path:
        """Extract the .apkg file and return path to the database."""
        logger.debug(f"Extracting {self.apkg_path}...")
        
        with zipfile.ZipFile(self.apkg_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
            logger.debug(f"Extracted {self.apkg_path} to {self.temp_dir}")
        
        db_path = Path(self.temp_dir) / 'collection.anki2'
        return db_path

    def cleanup(self) -> None:
        """Remove temporary files."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir) 