import pytest
from typing import Dict, Any

from ops.read.list_fields import ListFieldsOperation
from tests.ops.test_base import OperationTestBase
from anki_types import Collection, Model, Field

class TestListFieldsOperation(OperationTestBase):
    """Unit tests for ListFieldsOperation."""
    
    operation_class = ListFieldsOperation
    
    def test_validation(self, mock_collection):
        """Test operation validation.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Test with valid model name
        op = ListFieldsOperation(model_name="Basic")
        op.validate(mock_collection)
        
        # Test with non-existent model
        op = ListFieldsOperation(model_name="NonExistent")
        with pytest.raises(ValueError, match="Model not found"):
            op.validate(mock_collection)
        
        # Test with no model name when multiple models exist
        op = ListFieldsOperation()
        with pytest.raises(ValueError, match="Multiple models found"):
            op.validate(mock_collection)
    
    def test_execution(self, mock_collection):
        """Test operation execution.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Create and validate operation
        op = ListFieldsOperation(model_name="Basic")
        op.validate(mock_collection)
        
        # Execute operation
        result = op.execute()
        
        # Verify result
        assert result.success
        assert "fields" in result.data
        fields = result.data["fields"]
        assert isinstance(fields, list)
        assert len(fields) > 0
        assert all(isinstance(f, dict) for f in fields)
        assert all("name" in f and "type" in f for f in fields)

@pytest.fixture
def mock_collection() -> Collection:
    """Fixture providing a mock collection for testing."""
    return Collection(
        id=1,
        creation_time=0,
        modification_time=0,
        schema_modification=0,
        version=11,
        dirty=0,
        usn=-1,
        last_sync=0,
        models={
            1: Model(
                id=1,
                name="Basic",
                fields=[
                    Field(name="Front", ordinal=0),
                    Field(name="Back", ordinal=1)
                ],
                templates=[],
                css="",
                deck_id=1,
                modification_time=0,
                type=0,
                usn=-1,
                version=1
            ),
            2: Model(
                id=2,
                name="Advanced",
                fields=[
                    Field(name="Question", ordinal=0),
                    Field(name="Answer", ordinal=1),
                    Field(name="Notes", ordinal=2)
                ],
                templates=[],
                css="",
                deck_id=1,
                modification_time=0,
                type=0,
                usn=-1,
                version=1
            )
        },
        decks={},
        notes={},
        cards={},
        config={},
        deck_configs={},
        tags=[]
    ) 