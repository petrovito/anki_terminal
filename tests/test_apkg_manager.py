import pytest
import tempfile
import zipfile
from pathlib import Path
from apkg_manager import ApkgManager

def create_test_apkg(path: Path, include_v2: bool = True, include_v21: bool = True):
    """Helper function to create a test .apkg file with specified database versions."""
    with zipfile.ZipFile(path, 'w') as zf:
        if include_v2:
            # Add empty collection.anki2
            zf.writestr('collection.anki2', '')
        if include_v21:
            # Add empty collection.anki21
            zf.writestr('collection.anki21', '')
        # Add a dummy media file
        zf.writestr('media', '')

def test_version_selection():
    """Test that version 21 is preferred when both database versions are present."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        
        # Test case 1: Both versions present
        both_versions = tmp_dir / "both_versions.apkg"
        create_test_apkg(both_versions, include_v2=True, include_v21=True)
        
        with ApkgManager(both_versions, read_only=True) as manager:
            assert manager.db_version == 21
            assert manager.db_path.name == 'collection.anki21'
        
        # Test case 2: Only version 2
        only_v2 = tmp_dir / "only_v2.apkg"
        create_test_apkg(only_v2, include_v2=True, include_v21=False)
        
        with ApkgManager(only_v2, read_only=True) as manager:
            assert manager.db_version == 2
            assert manager.db_path.name == 'collection.anki2'
        
        # Test case 3: Only version 21
        only_v21 = tmp_dir / "only_v21.apkg"
        create_test_apkg(only_v21, include_v2=False, include_v21=True)
        
        with ApkgManager(only_v21, read_only=True) as manager:
            assert manager.db_version == 21
            assert manager.db_path.name == 'collection.anki21'
        
        # Test case 4: No database files
        no_db = tmp_dir / "no_db.apkg"
        create_test_apkg(no_db, include_v2=False, include_v21=False)
        
        with pytest.raises(ValueError, match="No valid Anki database file found in apkg"):
            with ApkgManager(no_db, read_only=True) as manager:
                pass

def test_version_property():
    """Test that db_version is properly exposed and initialized."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        
        # Create test package with version 21
        test_pkg = tmp_dir / "test.apkg"
        create_test_apkg(test_pkg, include_v2=False, include_v21=True)
        
        # Test that db_version is None before __enter__
        manager = ApkgManager(test_pkg, read_only=True)
        assert manager.db_version is None
        
        # Test that db_version is set after __enter__
        with manager:
            assert manager.db_version == 21
            assert isinstance(manager.db_version, int)
        
        # Test that db_version persists after __exit__
        assert manager.db_version == 21 