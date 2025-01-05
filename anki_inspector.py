#!/usr/bin/env python3

import sqlite3
import json
import zipfile
import tempfile
import os
import shutil
import logging
from pathlib import Path

class AnkiInspector:
    def __init__(self, apkg_path):
        self.logger = logging.getLogger('anki_inspector')
        self.apkg_path = Path(apkg_path)
        self.temp_dir = tempfile.mkdtemp()
        self.conn = None
        self._extract_and_connect()

    def _extract_and_connect(self):
        """Extract the .apkg file and connect to the SQLite database."""
        self.logger.debug(f"Extracting {self.apkg_path}...")
        
        with zipfile.ZipFile(self.apkg_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
            self.logger.debug(f"Contents extracted: {os.listdir(self.temp_dir)}")
        
        db_path = os.path.join(self.temp_dir, 'collection.anki2')
        self.logger.debug(f"Connecting to database at: {db_path}")
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def cleanup(self):
        """Close connection and remove temporary files."""
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                self.logger.warning(f"Error closing database: {str(e)}")
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def num_cards(self):
        """Get the total number of cards in the deck."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cards")
            return cursor.fetchone()[0]
        except Exception as e:
            self.logger.error(f"Error counting cards: {str(e)}")
            raise

    def list_fields(self):
        """List all fields from all note types."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT models FROM col")
            models_row = cursor.fetchone()
            models = json.loads(models_row[0])
            
            fields_by_model = {}
            for model_id, model in models.items():
                fields = [field['name'] for field in model['flds']]
                fields_by_model[model['name']] = fields
                
            return fields_by_model
        except Exception as e:
            self.logger.error(f"Error listing fields: {str(e)}")
            raise

    def print_template(self, model_name=None):
        """Print the templates (card types) for the specified model or all models."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT models FROM col")
            models_row = cursor.fetchone()
            models = json.loads(models_row[0])
            
            templates = {}
            for model_id, model in models.items():
                if model_name is None or model['name'] == model_name:
                    templates[model['name']] = {
                        'templates': [t['name'] for t in model['tmpls']],
                        'fields': [f['name'] for f in model['flds']]
                    }
            return templates
        except Exception as e:
            self.logger.error(f"Error getting templates: {str(e)}")
            raise 