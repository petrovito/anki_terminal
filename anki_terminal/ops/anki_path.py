from typing import List, Optional, Tuple, Union
import re

class AnkiPath:
    """Represents a path to an Anki object.
    
    Examples:
        - /models                  - All models
        - /models/Basic            - Basic model
        - /models/Basic/fields     - All fields in Basic model
        - /models/Basic/fields/Front - Front field in Basic model
        - /models/Basic/templates  - All templates in Basic model
        - /models/Basic/templates/Card 1 - Card 1 template in Basic model
        - /models/Basic/css        - CSS for Basic model
        - /models/Basic/example    - Example note for Basic model
        - /cards                   - All cards
        - /notes                   - All notes
        - /notes/Basic             - Notes using Basic model
    """
    
    PATH_REGEX = re.compile(r'^/(?:models(?:/([^/]+)(?:/(?:fields|templates|css|example)(?:/([^/]+))?)?)?|(?:cards|notes)(?:/([^/]+))?)$')
    
    def __init__(self, path: str):
        """Initialize an AnkiPath.
        
        Args:
            path: Path string
            
        Raises:
            ValueError: If path is invalid
        """
        self.path = path
        self._parse_path()
    
    def _parse_path(self) -> None:
        """Parse the path string into components.
        
        Raises:
            ValueError: If path is invalid
        """
        match = self.PATH_REGEX.match(self.path)
        if not match:
            raise ValueError(f"Invalid path: {self.path}")
        
        model_name, item_name, collection_filter = match.groups()
        
        # Determine object type
        if self.path.startswith('/models'):
            if model_name is None:
                # /models
                self.object_type = 'models'
                self.model_name = None
                self.item_type = None
                self.item_name = None
            elif '/fields' in self.path:
                # /models/{model}/fields or /models/{model}/fields/{field}
                self.model_name = model_name
                if item_name:
                    # /models/{model}/fields/{field}
                    self.object_type = 'fields'
                    self.item_type = 'field'
                    self.item_name = item_name
                else:
                    # /models/{model}/fields
                    self.object_type = 'fields'
                    self.item_type = None
                    self.item_name = None
            elif '/templates' in self.path:
                # /models/{model}/templates or /models/{model}/templates/{template}
                self.model_name = model_name
                if item_name:
                    # /models/{model}/templates/{template}
                    self.object_type = 'templates'
                    self.item_type = 'template'
                    self.item_name = item_name
                else:
                    # /models/{model}/templates
                    self.object_type = 'templates'
                    self.item_type = None
                    self.item_name = None
            elif '/css' in self.path:
                # /models/{model}/css
                self.object_type = 'css'
                self.model_name = model_name
                self.item_type = None
                self.item_name = None
            elif '/example' in self.path:
                # /models/{model}/example
                self.object_type = 'example'
                self.model_name = model_name
                self.item_type = None
                self.item_name = None
            else:
                # /models/{model}
                self.object_type = 'model'
                self.model_name = model_name
                self.item_type = None
                self.item_name = None
        elif self.path.startswith('/cards'):
            # /cards or /cards/{model}
            self.object_type = 'cards'
            self.model_name = collection_filter
            self.item_type = None
            self.item_name = None
        elif self.path.startswith('/notes'):
            # /notes or /notes/{model}
            self.object_type = 'notes'
            self.model_name = collection_filter
            self.item_type = None
            self.item_name = None
        else:
            raise ValueError(f"Invalid path: {self.path}")
    
    @property
    def is_collection(self) -> bool:
        """Check if the path refers to a collection of objects."""
        return self.object_type in ['models', 'fields', 'templates', 'cards', 'notes'] and self.item_name is None
    
    @property
    def is_item(self) -> bool:
        """Check if the path refers to a specific item."""
        return self.item_name is not None or self.object_type in ['model', 'css', 'example']
    
    def __str__(self) -> str:
        return self.path 