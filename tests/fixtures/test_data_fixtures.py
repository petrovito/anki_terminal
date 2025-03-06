"""
Test data fixtures for integration testing.

This module provides fixtures for integration testing with real Anki data.
"""

import json
from pathlib import Path

import pytest

from anki_terminal.anki_types import Collection
from anki_terminal.collection_factories import (CollectionV2Factory,
                                                CollectionV21Factory)

# Base path to test data directory
TEST_DATA_DIR = Path("test_data")

@pytest.fixture
def apkg_v2_path():
    """Return the path to the Anki v2 package file.
    
    Returns:
        Path: Path to jap2.apkg
    """
    return TEST_DATA_DIR / "jap2.apkg"

@pytest.fixture
def apkg_v21_path():
    """Return the path to the Anki v21 package file.
    
    Returns:
        Path: Path to jap21.apkg
    """
    return TEST_DATA_DIR / "jap21.apkg"

@pytest.fixture
def db_v2_path():
    """Return the path to the Anki v2 database file.
    
    Returns:
        Path: Path to collection.anki2
    """
    return TEST_DATA_DIR / "collection.anki2"

@pytest.fixture
def db_v21_path():
    """Return the path to the Anki v21 database file.
    
    Returns:
        Path: Path to collection.anki21
    """
    return TEST_DATA_DIR / "collection.anki21"

@pytest.fixture
def raw_table_data_v2():
    """Return the raw table data from the Anki v2 collection.
    
    This fixture loads the raw table data from the JSON file.
    
    Returns:
        dict: Raw table data as a Python dictionary
    """
    json_path = TEST_DATA_DIR / "raw_table_data_v2.json"
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@pytest.fixture
def raw_table_data_v21():
    """Return the raw table data from the Anki v21 collection.
    
    This fixture loads the raw table data from the JSON file.
    
    Returns:
        dict: Raw table data as a Python dictionary
    """
    json_path = TEST_DATA_DIR / "raw_table_data_v21.json"
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@pytest.fixture
def collection_v2(raw_table_data_v2) -> Collection:
    """Return a Collection object for Anki v2.
    
    This fixture creates a Collection object from the raw table data
    using the CollectionV2Factory.
    
    Args:
        raw_table_data_v2: Raw table data from Anki v2
        
    Returns:
        Collection: Collection object for Anki v2
    """
    factory = CollectionV2Factory()
    return factory.create_collection(raw_table_data_v2)

@pytest.fixture
def collection_v21(raw_table_data_v21) -> Collection:
    """Return a Collection object for Anki v21.
    
    This fixture creates a Collection object from the raw table data
    using the CollectionV21Factory.
    
    Args:
        raw_table_data_v21: Raw table data from Anki v21
        
    Returns:
        Collection: Collection object for Anki v21
    """
    factory = CollectionV21Factory()
    return factory.create_collection(raw_table_data_v21)

@pytest.fixture
def anki_context_v2(apkg_v2_path, tmp_path):
    """Return an AnkiContext for Anki v2.
    
    This fixture creates a temporary AnkiContext for testing with Anki v2.
    
    Args:
        apkg_v2_path: Path to the Anki v2 package file
        tmp_path: Temporary directory for the test
        
    Returns:
        AnkiContext: AnkiContext for Anki v2
    """
    from anki_terminal.anki_context import AnkiContext
    output_path = tmp_path / "output_v2.apkg"
    with AnkiContext(apkg_v2_path, output_path=output_path) as context:
        yield context

@pytest.fixture
def anki_context_v21(apkg_v21_path, tmp_path):
    """Return an AnkiContext for Anki v21.
    
    This fixture creates a temporary AnkiContext for testing with Anki v21.
    
    Args:
        apkg_v21_path: Path to the Anki v21 package file
        tmp_path: Temporary directory for the test
        
    Returns:
        AnkiContext: AnkiContext for Anki v21
    """
    from anki_terminal.anki_context import AnkiContext
    output_path = tmp_path / "output_v21.apkg"
    with AnkiContext(apkg_v21_path, output_path=output_path) as context:
        yield context 