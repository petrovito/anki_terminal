import pytest
from pathlib import Path
from anki_terminal.apkg_manager import ApkgManager
from tests.fixtures.test_data_fixtures import apkg_v2_path, apkg_v21_path

def test_version_selection_with_test_files(apkg_v2_path, apkg_v21_path):
    """Test version selection using actual test data files."""
    
    # Test jap2.apkg (v2 file)
    with ApkgManager(apkg_v2_path, read_only=True) as manager:
        assert manager.db_version == 2
        assert manager.db_path.name == 'collection.anki2'
    
    # Test jap21.apkg (v21 file)
    with ApkgManager(apkg_v21_path, read_only=True) as manager:
        assert manager.db_version == 21
        assert manager.db_path.name == 'collection.anki21' 