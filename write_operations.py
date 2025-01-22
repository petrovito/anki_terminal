import logging
from anki_types import Collection

logger = logging.getLogger('anki_inspector')

class WriteOperations:
    """Low-level write operations on the collection."""
    def __init__(self, collection: Collection):
        self.collection = collection
    # To be implemented later 