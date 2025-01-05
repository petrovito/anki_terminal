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

logger = logging.getLogger('anki_inspector')

class CollectionReader:
    def __init__(self, apkg_path: Path):
        self.apkg_path = apkg_path
        self.temp_dir = tempfile.mkdtemp()
        self.conn = None

    def extract_and_connect(self) -> None:
        """Extract the .apkg file and connect to the SQLite database."""
        logger.debug(f"Extracting {self.apkg_path}...")
        
        with zipfile.ZipFile(self.apkg_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
            logger.debug(f"Contents extracted: {os.listdir(self.temp_dir)}")
        
        db_path = os.path.join(self.temp_dir, 'collection.anki2')
        logger.debug(f"Connecting to database at: {db_path}")
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def cleanup(self) -> None:
        """Close connection and remove temporary files."""
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                logger.warning(f"Error closing database: {str(e)}")
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def read_collection(self) -> Collection:
        """Read and parse the collection data from the database."""
        try:
            logger.debug("Loading collection data from database")
            cursor = self.conn.cursor()
            
            # Load collection metadata
            logger.debug("Loading collection metadata")
            cursor.execute("SELECT * FROM col")
            col_data = cursor.fetchone()
            
            # Parse JSON data
            logger.debug("Parsing collection JSON data")
            models_dict = json.loads(col_data['models'])
            decks_dict = json.loads(col_data['decks'])
            conf = json.loads(col_data['conf'])
            dconf = json.loads(col_data['dconf'])
            
            models = self._parse_models(models_dict)
            decks = self._parse_decks(decks_dict)
            notes = self._load_notes(cursor, models)
            cards = self._load_cards(cursor)
            
            # Create Collection object
            logger.debug("Creating Collection object")
            collection = Collection(
                id=col_data['id'],
                creation_time=datetime.fromtimestamp(col_data['crt']),
                modification_time=datetime.fromtimestamp(col_data['mod'] / 1000),
                schema_modification=col_data['scm'],
                version=col_data['ver'],
                dirty=col_data['dty'],
                usn=col_data['usn'],
                last_sync=datetime.fromtimestamp(col_data['ls']),
                models=models,
                decks=decks,
                notes=notes,
                cards=cards,
                config=conf,
                deck_config=dconf,
                tags=col_data['tags'].split()
            )
            
            logger.debug("Collection loading complete")
            return collection
            
        except Exception as e:
            logger.error(f"Error loading collection: {str(e)}")
            raise

    def _parse_models(self, models_dict: dict) -> Dict[int, Model]:
        """Parse models data into Model objects."""
        logger.debug("Converting models data to Model objects")
        models: Dict[int, Model] = {}
        for model_id, model_data in models_dict.items():
            templates = [
                Template(
                    name=t['name'],
                    question_format=t['qfmt'],
                    answer_format=t['afmt'],
                    browser_question_format=t.get('bqfmt'),
                    browser_answer_format=t.get('bafmt'),
                    deck_override=t.get('did'),
                    ordinal=t['ord']
                ) for t in model_data['tmpls']
            ]
            
            models[int(model_id)] = Model(
                id=int(model_id),
                name=model_data['name'],
                fields=[f['name'] for f in model_data['flds']],
                templates=templates,
                css=model_data['css'],
                deck_id=model_data['did'],
                modification_time=datetime.fromtimestamp(model_data['mod']),
                type=model_data['type'],
                usn=model_data['usn'],
                version=model_data['vers']
            )
        return models

    def _parse_decks(self, decks_dict: dict) -> Dict[int, Deck]:
        """Parse decks data into Deck objects."""
        logger.debug("Converting decks data to Deck objects")
        decks: Dict[int, Deck] = {}
        for deck_id, deck_data in decks_dict.items():
            logger.debug(f"Processing deck {deck_id}: {deck_data}")
            try:
                # Convert timestamp to datetime only for 'mod' field
                mod_time = datetime.fromtimestamp(deck_data['mod'])
                
                # For today tuples, just pass them directly
                decks[int(deck_id)] = Deck(
                    id=int(deck_id),
                    name=deck_data['name'],
                    description=deck_data.get('desc', ''),
                    modification_time=mod_time,  # Only convert this timestamp
                    usn=deck_data['usn'],
                    collapsed=deck_data.get('collapsed', False),
                    browser_collapsed=deck_data.get('browserCollapsed', False),
                    dynamic=bool(deck_data.get('dyn', 0)),
                    new_today=tuple(deck_data.get('newToday', [0, 0])),
                    review_today=tuple(deck_data.get('revToday', [0, 0])),
                    learn_today=tuple(deck_data.get('lrnToday', [0, 0])),
                    conf_id=deck_data.get('conf')
                )
                logger.debug(f"Successfully created deck object for {deck_id}")
            except Exception as e:
                logger.error(f"Error processing deck {deck_id}: {str(e)}")
                logger.debug(f"Deck data: {deck_data}")
                raise
        return decks

    def _load_notes(self, cursor: sqlite3.Cursor, models: Dict[int, Model]) -> List[Note]:
        """Load notes from database."""
        logger.debug("Loading notes from database")
        cursor.execute("SELECT * FROM notes")
        notes = []
        for note_row in cursor.fetchall():
            fields_list = note_row['flds'].split('\x1f')
            model = models[note_row['mid']]
            fields_dict = dict(zip(model.fields, fields_list))
            
            notes.append(Note(
                id=note_row['id'],
                guid=note_row['guid'],
                model_id=note_row['mid'],
                modification_time=datetime.fromtimestamp(note_row['mod']),
                usn=note_row['usn'],
                tags=[tag for tag in note_row['tags'].split() if tag],
                fields=fields_dict,
                sort_field=note_row['sfld'],
                checksum=note_row['csum']
            ))
        return notes

    def _load_cards(self, cursor: sqlite3.Cursor) -> List[Card]:
        """Load cards from database."""
        logger.debug("Loading cards from database")
        cursor.execute("SELECT * FROM cards")
        cards = []
        for card_row in cursor.fetchall():
            cards.append(Card(
                id=card_row['id'],
                note_id=card_row['nid'],
                deck_id=card_row['did'],
                ordinal=card_row['ord'],
                modification_time=datetime.fromtimestamp(card_row['mod']),
                usn=card_row['usn'],
                type=card_row['type'],
                queue=card_row['queue'],
                due=card_row['due'],
                interval=card_row['ivl'],
                factor=card_row['factor'],
                reps=card_row['reps'],
                lapses=card_row['lapses'],
                left=card_row['left'],
                original_due=card_row['odue'],
                original_deck_id=card_row['odid'],
                flags=card_row['flags']
            ))
        return cards 