import pytest
import json
import tempfile
from pathlib import Path
from argparse import Namespace
from operation_models import UserOperationType, OperationType
from user_operation_parser import UserOperationParser

def test_parse_from_args_basic():
    """Test basic argument parsing without config file."""
    args = Namespace(
        command=UserOperationType.LIST_MODELS,
        model=None,
        template=None,
        old_field=None,
        new_field=None,
        fields=None,
        question_format=None,
        answer_format=None,
        css=None,
        batch_size=None,
        populator_class=None,
        populator_config=None,
        target_model=None,
        field_mapping=None,
        output=None,
        config=None
    )

    parser = UserOperationParser()
    plan = parser.parse_from_args(args)

    assert plan.read_only == True
    assert plan.output_path == None
    assert len(plan.operations) == 1
    assert plan.operations[0].operation_type == OperationType.LIST_MODELS

def test_parse_with_config_file():
    """Test that config file values are used when args are not provided."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create config file
        config = {
            "model_name": "Test Model",
            "template_name": "Test Template",
            "fields": ["Field1", "Field2"]
        }
        config_path = Path(tmp_dir) / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        # Create args with minimal values
        args = Namespace(
            command=UserOperationType.ADD_MODEL,
            model=None,  # Should use config value
            template=None,  # Should use config value
            old_field=None,
            new_field=None,
            fields=None,  # Should use config value
            question_format=None,
            answer_format=None,
            css=None,
            batch_size=None,
            populator_class=None,
            populator_config=None,
            target_model=None,
            field_mapping=None,
            output=str(Path(tmp_dir) / "output.apkg"),
            config=config_path
        )

        parser = UserOperationParser()
        plan = parser.parse_from_args(args)

        assert plan.read_only == False
        assert plan.output_path == Path(tmp_dir) / "output.apkg"
        assert len(plan.operations) == 1
        op = plan.operations[0]
        assert op.operation_type == OperationType.ADD_MODEL
        assert op.model_name == "Test Model"
        assert op.template_name == "Test Template"
        assert op.fields == ["Field1", "Field2"]

def test_args_override_config():
    """Test that command line args override config file values."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create config file with some values
        config = {
            "model_name": "Config Model",
            "template_name": "Config Template",
            "fields": ["Config1", "Config2"]
        }
        config_path = Path(tmp_dir) / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        # Create args that override some config values
        args = Namespace(
            command=UserOperationType.ADD_MODEL,
            model="CLI Model",  # Override config
            template=None,  # Use config
            old_field=None,
            new_field=None,
            fields='["CLI1", "CLI2"]',  # Override config
            question_format=None,
            answer_format=None,
            css=None,
            batch_size=None,
            populator_class=None,
            populator_config=None,
            target_model=None,
            field_mapping=None,
            output=str(Path(tmp_dir) / "output.apkg"),
            config=config_path
        )

        parser = UserOperationParser()
        plan = parser.parse_from_args(args)

        assert len(plan.operations) == 1
        op = plan.operations[0]
        assert op.model_name == "CLI Model"  # Should use CLI value
        assert op.template_name == "Config Template"  # Should use config value
        assert op.fields == ["CLI1", "CLI2"]  # Should use CLI value

def test_invalid_config_file():
    """Test that invalid config file is handled gracefully."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create invalid JSON file
        config_path = Path(tmp_dir) / "config.json"
        with open(config_path, "w") as f:
            f.write("invalid json")

        args = Namespace(
            command=UserOperationType.LIST_MODELS,
            model=None,
            template=None,
            old_field=None,
            new_field=None,
            fields=None,
            question_format=None,
            answer_format=None,
            css=None,
            batch_size=None,
            populator_class=None,
            populator_config=None,
            target_model=None,
            field_mapping=None,
            output=None,
            config=config_path
        )

        parser = UserOperationParser()
        with pytest.raises(ValueError, match="Invalid JSON in config file"):
            parser.parse_from_args(args)

def test_write_operation_requires_output():
    """Test that write operations require an output path."""
    args = Namespace(
        command=UserOperationType.ADD_MODEL,
        model="Test Model",
        template="Test Template",
        old_field=None,
        new_field=None,
        fields='["Field1", "Field2"]',
        question_format=None,
        answer_format=None,
        css=None,
        batch_size=None,
        populator_class=None,
        populator_config=None,
        target_model=None,
        field_mapping=None,
        output=None,  # No output path
        config=None
    )

    parser = UserOperationParser()
    with pytest.raises(ValueError, match="Output path must be specified for write operations"):
        parser.parse_from_args(args)

def test_run_all_operation():
    """Test that RUN_ALL creates multiple read operations."""
    args = Namespace(
        command=UserOperationType.RUN_ALL,
        model=None,
        template=None,
        old_field=None,
        new_field=None,
        fields=None,
        question_format=None,
        answer_format=None,
        css=None,
        batch_size=None,
        populator_class=None,
        populator_config=None,
        target_model=None,
        field_mapping=None,
        output=None,
        config=None
    )

    parser = UserOperationParser()
    plan = parser.parse_from_args(args)

    assert plan.read_only == True
    assert plan.output_path == None
    assert len(plan.operations) > 1  # Should create multiple operations
    # Verify all operations are read-only
    for op in plan.operations:
        assert op.operation_type.is_read_only 