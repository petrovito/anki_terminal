import pytest
from ops.write.add_model import AddModelOperation
from tests.ops.test_base import OperationTestBase

class TestAddModelOperation(OperationTestBase):
    """Unit tests for AddModelOperation."""
    
    operation_class = AddModelOperation
    valid_args = {
        "model_name": "Test Model",
        "fields": ["Question", "Answer", "Notes"],
        "template_name": "Forward Card",
        "question_format": "{{Question}}\n\n{{Notes}}",
        "answer_format": "{{FrontSide}}\n\n<hr id='answer'>\n\n{{Answer}}",
        "css": ".card { font-family: arial; font-size: 20px; }"
    }
    
    def test_validation(self, mock_collection):
        """Test operation validation.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Test with valid arguments
        op = AddModelOperation(**self.valid_args)
        op.validate(mock_collection)
        
        # Test with existing model name
        op = AddModelOperation(
            **{**self.valid_args, "model_name": "Basic"}  # Basic model exists in mock
        )
        with pytest.raises(ValueError, match="Model already exists"):
            op.validate(mock_collection)
        
        # Test with empty fields list
        op = AddModelOperation(
            **{**self.valid_args, "fields": []}
        )
        with pytest.raises(ValueError, match="At least one field is required"):
            op.validate(mock_collection)
        
        # Test with duplicate field names
        op = AddModelOperation(
            **{**self.valid_args, "fields": ["Field1", "Field1", "Field2"]}
        )
        with pytest.raises(ValueError, match="Field names must be unique"):
            op.validate(mock_collection)
        
        # Test with non-list fields argument
        op = AddModelOperation(
            **{**self.valid_args, "fields": "not a list"}
        )
        with pytest.raises(ValueError, match="Fields must be a list"):
            op.validate(mock_collection)
    
    def test_execution(self, mock_collection):
        """Test operation execution.
        
        Args:
            mock_collection: Pytest fixture providing a mock collection
        """
        # Create and validate operation
        op = AddModelOperation(**self.valid_args)
        op.validate(mock_collection)
        
        # Get initial model count
        initial_count = len(mock_collection.models)
        
        # Execute operation
        result = op.execute()
        
        # Verify result
        assert result.success
        assert result.changes  # Should have recorded changes
        
        # Verify model was added
        assert len(mock_collection.models) == initial_count + 1
        
        # Find the new model
        new_model = next(
            model for model in mock_collection.models.values()
            if model.name == self.valid_args["model_name"]
        )
        
        # Verify model properties
        assert new_model.name == self.valid_args["model_name"]
        assert len(new_model.fields) == len(self.valid_args["fields"])
        assert [f.name for f in new_model.fields] == self.valid_args["fields"]
        assert len(new_model.templates) == 1
        assert new_model.templates[0].name == self.valid_args["template_name"]
        assert new_model.templates[0].question_format == self.valid_args["question_format"]
        assert new_model.templates[0].answer_format == self.valid_args["answer_format"]
        assert new_model.css == self.valid_args["css"]
        assert new_model.type == 0  # Standard model
        assert new_model.usn == -1  # Needs sync 