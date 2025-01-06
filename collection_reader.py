#!/usr/bin/env python3

import sqlite3
import json
import zipfile
import tempfile
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

from anki_types import Collection, Model, Note, Card, Deck, Template
from apkg_extractor import ApkgExtractor
from database_reader import DatabaseReader

logger = logging.getLogger('anki_inspector')

class CollectionReader:
    def __init__(self, apkg_path: Path):
        self.extractor = ApkgExtractor(apkg_path)
        self.db_reader = None

    def extract_and_connect(self) -> None:
        """Extract the .apkg file and connect to the database."""
        db_path = self.extractor.extract()
        self.db_reader = DatabaseReader(db_path)
        self.db_reader.connect()

    def read_collection(self) -> Collection:
        """Read the collection from the database."""
        return self.db_reader.read_collection()

    def cleanup(self) -> None:
        """Clean up all resources."""
        if self.db_reader:
            self.db_reader.close()
        self.extractor.cleanup() 