import pytest

from anki_terminal.commons.anki_types import Note
from anki_terminal.populators.remove_brackets import RemoveBracketsPopulator


class TestRemoveBracketsPopulator:
    """Tests for the RemoveBracketsPopulator."""
    
    def test_initialization(self):
        """Test populator initialization."""
        # Test with source field only
        config = {"source_field": "Expression"}
        populator = RemoveBracketsPopulator(config)
        assert populator.config["source_field"] == "Expression"
        assert populator.config["target_field"] == "Expression"  # Should default to source field
        
        # Test with source and target fields
        config = {"source_field": "Expression", "target_field": "CleanExpression"}
        populator = RemoveBracketsPopulator(config)
        assert populator.config["source_field"] == "Expression"
        assert populator.config["target_field"] == "CleanExpression"
    
    def test_populate_fields_update_source(self):
        """Test populating fields when updating the source field."""
        # Create populator
        config = {"source_field": "Expression"}
        populator = RemoveBracketsPopulator(config)
        
        # Create test notes
        note1 = Note(
            id=1,
            guid="test_guid_1",
            model_id=1,
            modification_time=None,
            usn=-1,
            tags=[],
            fields={"Expression": "（鯉登）キエ～！", "Meaning": "Test"},
            sort_field=0,
            checksum=0,
            flags=0
        )
        
        note2 = Note(
            id=2,
            guid="test_guid_2",
            model_id=1,
            modification_time=None,
            usn=-1,
            tags=[],
            fields={"Expression": "Normal text without brackets", "Meaning": "Test"},
            sort_field=0,
            checksum=0,
            flags=0
        )
        
        note3 = Note(
            id=3,
            guid="test_guid_3",
            model_id=1,
            modification_time=None,
            usn=-1,
            tags=[],
            fields={"Expression": "（野間直明(のまなおあき)）早く塹壕(ざんごう)へ！", "Meaning": "Test"},
            sort_field=0,
            checksum=0,
            flags=0
        )
        
        # Test populating fields
        result1 = populator._populate_fields_impl(note1)
        result2 = populator._populate_fields_impl(note2)
        result3 = populator._populate_fields_impl(note3)
        # Verify results
        assert result1 == {"Expression": "キエ～！"}
        assert result2 == {}  # No changes for note without brackets
        assert result3 == {"Expression": "早く塹壕へ！"}

        
    def test_populate_fields_update_target(self):
        """Test populating fields when updating a target field."""
        # Create populator
        config = {"source_field": "Expression", "target_field": "CleanExpression"}
        populator = RemoveBracketsPopulator(config)
        
        # Create test note
        note = Note(
            id=1,
            guid="test_guid_1",
            model_id=1,
            modification_time=None,
            usn=-1,
            tags=[],
            fields={"Expression": "（鯉登）キエ～！", "CleanExpression": "", "Meaning": "Test"},
            sort_field=0,
            checksum=0,
            flags=0
        )
        
        # Test populating fields
        result = populator._populate_fields_impl(note)
        
        # Verify result
        assert result == {"CleanExpression": "キエ～！"}
    
    def test_populate_fields_mixed_brackets(self):
        """Test populating fields with mixed bracket types."""
        # Create populator
        config = {"source_field": "Expression"}
        populator = RemoveBracketsPopulator(config)
        
        # Create test notes with different bracket types
        note1 = Note(
            id=1,
            guid="test_guid_1",
            model_id=1,
            modification_time=None,
            usn=-1,
            tags=[],
            fields={"Expression": "（鯉登）キエ～！", "Meaning": "Test"},
            sort_field=0,
            checksum=0,
            flags=0
        )
        
        note2 = Note(
            id=2,
            guid="test_guid_2",
            model_id=1,
            modification_time=None,
            usn=-1,
            tags=[],
            fields={"Expression": "(キロランケ)うわ！", "Meaning": "Test"},
            sort_field=0,
            checksum=0,
            flags=0
        )
        
        note3 = Note(
            id=3,
            guid="test_guid_3",
            model_id=1,
            modification_time=None,
            usn=-1,
            tags=[],
            fields={"Expression": "Mixed (English) and （Japanese） brackets", "Meaning": "Test"},
            sort_field=0,
            checksum=0,
            flags=0
        )
        
        # Test populating fields
        result1 = populator._populate_fields_impl(note1)
        result2 = populator._populate_fields_impl(note2)
        result3 = populator._populate_fields_impl(note3)
        
        # Verify results
        assert result1 == {"Expression": "キエ～！"}
        assert result2 == {"Expression": "うわ！"}
        assert result3 == {"Expression": "Mixed  and  brackets"} 