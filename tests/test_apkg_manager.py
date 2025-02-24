import pytest
from pathlib import Path
from apkg_manager import ApkgManager

def test_version_selection_with_test_files():
    """Test version selection using actual test data files."""
    
    # Test jap.apkg (v2 file)
    with ApkgManager("test_data/jap.apkg", read_only=True) as manager:
        assert manager.db_version == 2
        assert manager.db_path.name == 'collection.anki2'
    
    # Test jap21.apkg (v21 file)
    with ApkgManager("test_data/jap21.apkg", read_only=True) as manager:
        assert manager.db_version == 21
        assert manager.db_path.name == 'collection.anki21' 