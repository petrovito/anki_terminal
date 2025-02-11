#!/usr/bin/env python3

import logging
import json
from datetime import datetime
from typing import Dict, List, Set, Any

from anki_types import (
    Collection, Card, Note, Model, Deck, DeckConfig, 
    Field, Template
)

logger = logging.getLogger('anki_inspector')

class CollectionFactoryBase:
    """Base class for collection factories."""
    
    def create_collection(self, table_data: Dict[str, Any]) -> Collection:
        """Create a collection from raw table data.
        
        Args:
            table_data: Dictionary mapping table names to their raw rows
            
        Returns:
            Collection object populated with data
        """
        raise NotImplementedError("Subclasses must implement create_collection")
    
    def _create_cards(self, cards_data: List[Dict]) -> Dict[int, Card]:
        """Create Card objects from raw data."""
        cards = {}
        for row in cards_data:
            # Handle empty data string by defaulting to empty dict
            data = json.loads(row.get('data', '{}') or '{}')
            cards[row['id']] = Card(
                id=row['id'],
                note_id=row['nid'],
                deck_id=row['did'],
                ordinal=row['ord'],
                modification_time=datetime.fromtimestamp(row['mod']),
                usn=row['usn'],
                type=row['type'],
                queue=row['queue'],
                due=row['due'],
                interval=row['ivl'],
                factor=row['factor'],
                reps=row['reps'],
                lapses=row['lapses'],
                left=row['left'],
                original_due=row['odue'],
                original_deck_id=row['odid'],
                flags=row['flags'],
                data=data
            )
        return cards

    def _create_notes(self, notes_data: List[Dict]) -> Dict[int, Note]:
        """Create Note objects from raw data."""
        notes = {}
        for row in notes_data:
            data = json.loads(row.get('data', '{}'))
            tags = row['tags'].split()
            notes[row['id']] = Note(
                id=row['id'],
                guid=row['guid'],
                model_id=row['mid'],
                modification_time=datetime.fromtimestamp(row['mod']),
                usn=row['usn'],
                tags=tags,
                fields=self._parse_fields(row['flds']),
                sort_field=row['sfld'],
                checksum=row['csum'],
                flags=row.get('flags', 0),
                data=data
            )
        return notes
    
    def _parse_fields(self, fields_str: str) -> Dict[str, str]:
        """Parse fields string into dictionary."""
        raise NotImplementedError("Subclasses must implement _parse_fields")

class CollectionV2Factory(CollectionFactoryBase):
    """Factory for creating collections from Anki 2 database format."""
    
    def _parse_fields(self, fields_str: str) -> Dict[str, str]:
        """Parse fields string into dictionary.
        
        In Anki 2, fields are separated by \x1f character.
        """
        return dict(enumerate(fields_str.split('\x1f')))

    def create_collection(self, table_data: Dict[str, Any]) -> Collection:
        """Create a Collection from v2 table data."""
        col_data = table_data['col']
        
        # Parse JSON data from collection
        conf = json.loads(col_data.get('conf', '{}'))
        models_json = json.loads(col_data.get('models', '{}'))
        decks_json = json.loads(col_data.get('decks', '{}'))
        dconf_json = json.loads(col_data.get('dconf', '{}'))
        
        # Create components
        cards = self._create_cards(table_data['cards'])
        notes = {}
        for row in table_data['notes']:
            # Handle empty data string
            data = json.loads(row.get('data', '{}') or '{}')
            model = models_json.get(str(row['mid']), {})
            field_names = [f['name'] for f in model.get('flds', [])]
            field_values = self._parse_fields(row['flds'])
            # Map numeric field indices to names
            fields = {
                field_names[idx]: value 
                for idx, value in field_values.items()
                if idx < len(field_names)
            }
            notes[row['id']] = Note(
                id=row['id'],
                guid=row['guid'],
                model_id=row['mid'],
                modification_time=datetime.fromtimestamp(row['mod']),
                usn=row['usn'],
                tags=row['tags'].split() if row['tags'] else [],
                fields=fields,
                sort_field=row['sfld'],
                checksum=row['csum'],
                flags=row['flags'],
                data=data
            )

        # Create models, decks, and deck configs
        models = self._create_models_v2(models_json)
        decks = self._create_decks_v2(decks_json)
        deck_configs = self._create_deck_configs_v2(dconf_json)
        tags = self._create_tags_v2(notes)
        
        # Update note fields with model field names
        self._update_note_fields(notes, models)
        
        return Collection(
            id=col_data['id'],
            creation_time=datetime.fromtimestamp(col_data['crt']),
            modification_time=datetime.fromtimestamp(col_data['mod']),
            schema_modification=col_data['scm'],
            version=col_data['ver'],
            dirty=bool(col_data['dty']),
            usn=col_data['usn'],
            last_sync=datetime.fromtimestamp(col_data['ls']),
            cards=cards,
            notes=notes,
            decks=decks,
            models=models,
            deck_configs=deck_configs,
            tags=tags,
            config=conf
        )
    
    def _create_models_v2(self, models_dict: Dict) -> Dict[int, Model]:
        """Create Model objects from v2 format data."""
        models = {}
        for mid, data in models_dict.items():
            mid = int(mid)
            models[mid] = Model(
                id=mid,
                name=data['name'],
                fields=self._create_fields_v2(data['flds']),
                templates=self._create_templates_v2(data['tmpls']),
                css=data['css'],
                deck_id=data.get('did', 1),  # Default to deck 1 if not specified
                modification_time=datetime.fromtimestamp(data['mod']),
                type=data.get('type', 0),
                usn=data['usn'],
                version=data.get('vers', 1),
                latex_pre=data.get('latexPre', ''),
                latex_post=data.get('latexPost', ''),
                latex_svg=data.get('latexsvg', False),
                required=data.get('req', [[0, "all", [0]]]),
                tags=data.get('tags', [])
            )
        return models
    
    def _create_fields_v2(self, fields_data: List[Dict]) -> List[Field]:
        """Create Field objects from v2 format data."""
        return [
            Field(
                name=f['name'],
                ordinal=i,
                sticky=f.get('sticky', False),
                rtl=f.get('rtl', False),
                font=f.get('font', 'Arial'),
                font_size=f.get('size', 20),
                description=f.get('description', ''),
                plain_text=True,
                collapsed=False
            )
            for i, f in enumerate(fields_data)
        ]
    
    def _create_templates_v2(self, templates_data: List[Dict]) -> List[Template]:
        """Create Template objects from v2 format data."""
        return [
            Template(
                name=t['name'],
                ordinal=t['ord'],
                question_format=t['qfmt'],
                answer_format=t['afmt'],
                browser_question_format=t.get('bqfmt', ''),
                browser_answer_format=t.get('bafmt', '')
            )
            for t in templates_data
        ]
    
    def _create_decks_v2(self, decks_dict: Dict) -> Dict[int, Deck]:
        """Create Deck objects from v2 format data."""
        decks = {}
        for did, data in decks_dict.items():
            did = int(did)
            decks[did] = Deck(
                id=did,
                name=data['name'],
                modification_time=datetime.fromtimestamp(data['mod']),
                conf_id=data['conf'],
                description=data.get('desc', ''),
                dynamic=bool(data.get('dyn', 0)),
                collapsed=data.get('collapsed', False),
                browser_collapsed=data.get('browserCollapsed', False),
                usn=data.get('usn', -1),
                new_today=(0, 0),
                review_today=(0, 0),
                learn_today=(0, 0),
                time_today=(0, 0)
            )
        return decks
    
    def _create_deck_configs_v2(self, dconf: Dict) -> Dict[int, DeckConfig]:
        """Create DeckConfig objects from v2 format data."""
        configs = {}
        for conf_id, data in dconf.items():
            conf_id = int(conf_id)
            configs[conf_id] = DeckConfig(
                id=conf_id,
                name=data['name'],
                modification_time=datetime.fromtimestamp(data['mod']),
                usn=data['usn'],
                max_taken=data.get('maxTaken', 60),
                autoplay=data.get('autoplay', True),
                timer=data.get('timer', 0),
                replay_question=data.get('replayq', True),
                dynamic=bool(data.get('dyn', False)),
                new_cards=data.get('new', {
                    "bury": False,
                    "delays": [1.0, 10.0],
                    "initialFactor": 2500,
                    "ints": [1, 4, 0],
                    "order": 1,
                    "perDay": 20
                }),
                review_cards=data.get('rev', {
                    "bury": False,
                    "ease4": 1.3,
                    "ivlFct": 1.0,
                    "maxIvl": 36500,
                    "perDay": 200,
                    "hardFactor": 1.2
                }),
                lapse_cards=data.get('lapse', {
                    "delays": [10.0],
                    "leechAction": 1,
                    "leechFails": 8,
                    "minInt": 1,
                    "mult": 0.0
                })
            )
        return configs
    

    def _update_note_fields(self, notes: Dict[int, Note], models: Dict[int, Model]):
        """Update note fields with proper field names from models."""
        for note in notes.values():
            model = models[note.model_id]
            field_names = [f.name for f in model.fields]
            field_values = list(note.fields.values())
            note.fields = dict(zip(field_names, field_values))

    def _create_tags_v2(self, notes: Dict[int, Note]) -> List[str]:
        """Create list of unique tags from notes."""
        tags = set()
        for note in notes.values():
            tags.update(note.tags)
        return sorted(list(tags))

class CollectionV21Factory(CollectionFactoryBase):
    """Factory for creating collections from Anki 21 database format."""
    
    def create_collection(self, table_data: Dict[str, Any]) -> Collection:
        """Create a Collection from v21 table data."""
        # Create field name mapping for each notetype
        field_maps = {}
        for field in table_data['fields']:
            ntid = field['ntid']
            if ntid not in field_maps:
                field_maps[ntid] = {}
            field_maps[ntid][field['ord']] = field['name']

        # Create cards and notes with proper field mapping
        cards = self._create_cards(table_data['cards'])
        notes = {}
        for row in table_data['notes']:
            # Handle empty data string
            data = json.loads(row.get('data', '{}') or '{}')
            field_values = self._parse_fields(row['flds'])
            # Map numeric field indices to names using the field map
            fields = {
                field_maps[row['mid']][idx]: value 
                for idx, value in field_values.items()
            }
            notes[row['id']] = Note(
                id=row['id'],
                guid=row['guid'],
                model_id=row['mid'],
                modification_time=datetime.fromtimestamp(row['mod']),
                usn=row['usn'],
                tags=row['tags'].split() if row['tags'] else [],
                fields=fields,
                sort_field=row['sfld'],
                checksum=row['csum'],
                flags=row['flags'],
                data=data
            )

        # Create models, decks, and deck configs
        models = self._create_models_v21(table_data)
        decks = self._create_decks_v21(table_data['decks'])
        deck_configs = self._create_deck_configs_v21(table_data.get('deck_config', []))  # Handle both deck_config and deck_configs
        tags = self._create_tags_v21(table_data.get('tags', []))

        return Collection(
            id=table_data['col']['id'],
            creation_time=datetime.fromtimestamp(table_data['col']['crt']),
            modification_time=datetime.fromtimestamp(table_data['col']['mod']),
            schema_modification=table_data['col']['scm'],
            version=table_data['col']['ver'],
            dirty=bool(table_data['col']['dty']),
            usn=table_data['col']['usn'],
            last_sync=datetime.fromtimestamp(table_data['col']['ls']),
            cards=cards,
            notes=notes,
            decks=decks,
            models=models,
            deck_configs=deck_configs,
            tags=tags,
            config=json.loads(table_data['col'].get('conf', '{}'))
        )
    
    def _create_models_v21(self, table_data: Dict[str, Any]) -> Dict[int, Model]:
        """Create Model objects from v21 format data."""
        models = {}
        fields_by_model = self._group_by_model_id(table_data['fields'])
        templates_by_model = self._group_by_model_id(table_data['templates'])
        
        for row in table_data['notetypes']:
            model_id = row['id']
            config = json.loads(row['config'])
            
            models[model_id] = Model(
                id=model_id,
                name=row['name'],
                fields=self._create_fields_v21(fields_by_model.get(model_id, [])),
                templates=self._create_templates_v21(templates_by_model.get(model_id, [])),
                css=config.get('css', ''),
                deck_id=row.get('did', 1),  # Default to deck 1 if not specified
                modification_time=datetime.fromtimestamp(row['mod']),
                type=row.get('type', 0),
                usn=row['usn'],
                version=row.get('ver', 1),
                latex_pre=config.get('latexPre', ''),
                latex_post=config.get('latexPost', ''),
                latex_svg=config.get('latexsvg', False),
                required=config.get('req', [[0, "all", [0]]]),
                tags=config.get('tags', [])
            )
        return models
    
    def _group_by_model_id(self, rows: List[Dict]) -> Dict[int, List[Dict]]:
        """Group rows by their model ID (ntid)."""
        grouped = {}
        for row in rows:
            model_id = row['ntid']
            if model_id not in grouped:
                grouped[model_id] = []
            grouped[model_id].append(row)
        return grouped
    
    def _create_fields_v21(self, fields_data: List[Dict]) -> List[Field]:
        """Create Field objects from v21 format data."""
        fields = []
        for row in sorted(fields_data, key=lambda x: x['ord']):
            config = json.loads(row['config'])
            fields.append(Field(
                name=row['name'],
                ordinal=row['ord'],
                sticky=config.get('sticky', False),
                rtl=config.get('rtl', False),
                font=config.get('font', 'Arial'),
                font_size=config.get('size', 20),
                description=config.get('description', ''),
                plain_text=config.get('plainText', True),
                collapsed=config.get('collapsed', False)
            ))
        return fields
    
    def _create_templates_v21(self, templates_data: List[Dict]) -> List[Template]:
        """Create Template objects from v21 format data."""
        templates = []
        for row in sorted(templates_data, key=lambda x: x['ord']):
            config = json.loads(row['config'])
            templates.append(Template(
                name=row['name'],
                ordinal=row['ord'],
                question_format=config['qfmt'],
                answer_format=config['afmt'],
                browser_question_format=config.get('bqfmt', ''),
                browser_answer_format=config.get('bafmt', ''),
                browser_font=config.get('bfont', ''),
                browser_font_size=config.get('bsize', 0)
            ))
        return templates
    
    def _create_decks_v21(self, decks_data: List[Dict]) -> Dict[int, Deck]:
        """Create Deck objects from v21 format data."""
        decks = {}
        for row in decks_data:
            config = json.loads(row['config'])
            decks[row['id']] = Deck(
                id=row['id'],
                name=row['name'],
                modification_time=datetime.fromtimestamp(row['mod']),
                conf_id=row['conf'],
                description=row.get('desc', ''),
                dynamic=bool(config.get('dyn', 0)),
                collapsed=config.get('collapsed', False),
                browser_collapsed=config.get('browserCollapsed', False),
                usn=row.get('usn', -1),
                new_today=(0, 0),
                review_today=(0, 0),
                learn_today=(0, 0),
                time_today=(0, 0)
            )
        return decks
    
    def _create_deck_configs_v21(self, configs_data: List[Dict]) -> Dict[int, DeckConfig]:
        """Create DeckConfig objects from v21 format data."""
        configs = {}
        for row in configs_data:
            config = json.loads(row['config'])
            configs[row['id']] = DeckConfig(
                id=row['id'],
                name=row['name'],
                modification_time=datetime.fromtimestamp(row['mod']),
                usn=row['usn'],
                max_taken=config.get('maxTaken', 60),
                autoplay=config.get('autoplay', True),
                timer=config.get('timer', 0),
                replay_question=config.get('replayq', True),
                dynamic=bool(config.get('dyn', False)),
                new_cards=config.get('new', {
                    "bury": False,
                    "delays": [1.0, 10.0],
                    "initialFactor": 2500,
                    "ints": [1, 4, 0],
                    "order": 1,
                    "perDay": 20
                }),
                review_cards=config.get('rev', {
                    "bury": False,
                    "ease4": 1.3,
                    "ivlFct": 1.0,
                    "maxIvl": 36500,
                    "perDay": 200,
                    "hardFactor": 1.2
                }),
                lapse_cards=config.get('lapse', {
                    "delays": [10.0],
                    "leechAction": 1,
                    "leechFails": 8,
                    "minInt": 1,
                    "mult": 0.0
                })
            )
        return configs
    
    def _create_tags_v21(self, tags_data: List[Dict]) -> List[str]:
        """Create list of unique tags from tags data."""
        return sorted(list({tag['tag'] for tag in tags_data}))
    
    def _parse_fields(self, fields_str: str) -> Dict[str, str]:
        """Parse fields string into dictionary.
        
        In Anki 21, fields are tab-separated rather than using \x1f as in Anki 2.
        """
        return dict(enumerate(fields_str.split('\t')))
    