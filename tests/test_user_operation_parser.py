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
        with pytest.raises(ValueError, match="Configuration error: Invalid JSON in configuration file"):
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

def test_run_script():
    """Test running a script file with multiple operations."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create script file
        script_path = Path(tmp_dir) / "script.txt"
        script_content = """
# This is a comment
list-models
list-templates --model "Basic Card"
num-notes
# Another comment
print-css --model "Basic Card"
"""
        with open(script_path, "w") as f:
            f.write(script_content)

        args = Namespace(
            command=UserOperationType.RUN_SCRIPT,
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
            config=None,
            script_file=script_path
        )

        parser = UserOperationParser()
        plan = parser.parse_from_args(args)

        assert plan.read_only == True
        assert plan.output_path == None
        assert len(plan.operations) == 4  # 4 operations, skipping comments
        # Verify operations are in correct order
        assert plan.operations[0].operation_type == OperationType.LIST_MODELS
        assert plan.operations[1].operation_type == OperationType.LIST_TEMPLATES
        assert plan.operations[1].model_name == "Basic Card"
        assert plan.operations[2].operation_type == OperationType.NUM_NOTES
        assert plan.operations[3].operation_type == OperationType.PRINT_CSS
        assert plan.operations[3].model_name == "Basic Card"

def test_script_with_write_operations():
    """Test script containing write operations sets read_only correctly."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create script file with mix of read and write operations
        script_path = Path(tmp_dir) / "script.txt"
        script_content = """
list-models
add-field --model "Basic Card" --new-field "NewField"
num-notes
"""
        with open(script_path, "w") as f:
            f.write(script_content)

        args = Namespace(
            command=UserOperationType.RUN_SCRIPT,
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
            output=str(Path(tmp_dir) / "output.apkg"),
            config=None,
            script_file=script_path
        )

        parser = UserOperationParser()
        plan = parser.parse_from_args(args)

        assert not plan.read_only  # Should be False because add-field is a write operation
        assert plan.output_path == Path(args.output)
        assert len(plan.operations) == 3

def test_script_with_invalid_command():
    """Test that invalid commands in script file are handled properly."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create script file with invalid command
        script_path = Path(tmp_dir) / "script.txt"
        script_content = """list-models
invalid-command
num-notes"""
        with open(script_path, "w") as f:
            f.write(script_content)

        args = Namespace(
            command=UserOperationType.RUN_SCRIPT,
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
            config=None,
            script_file=script_path
        )

        parser = UserOperationParser()
        with pytest.raises(ValueError, match="Error in script file at line 2"):
            parser.parse_from_args(args)

def test_parse_with_builtin_config():
    """Test parsing arguments with a built-in configuration."""
    args = Namespace(
        command=UserOperationType.ADD_MODEL,
        model=None,  # Should use config value
        template=None,  # Should use config value
        old_field=None,
        new_field=None,
        fields=None,  # Should use config value
        question_format=None,  # Should use config value
        answer_format=None,  # Should use config value
        css=None,  # Should use config value
        batch_size=None,
        populator_class=None,
        populator_config=None,
        target_model=None,
        field_mapping=None,
        output="output.apkg",
        config="jap_anime_reformat"  # Using built-in config
    )

    parser = UserOperationParser()
    plan = parser.parse_from_args(args)

    assert plan.read_only == False
    assert plan.output_path == Path("output.apkg")
    assert len(plan.operations) == 1
    op = plan.operations[0]
    assert op.operation_type == OperationType.ADD_MODEL
    assert op.model_name == "Japanese Anime Card"
    assert op.template_name == "Japanese Card"
    assert op.fields == ["Japanese", "English", "Context", "Audio", "Image"]
    assert "{{Japanese}}" in op.question_format
    assert "{{English}}" in op.answer_format
    assert ".card {" in op.css

def test_script_with_builtin_config():
    """Test running a script that uses built-in configuration."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create script file that uses built-in config
        script_path = Path(tmp_dir) / "script.txt"
        script_content = """
add-model --config jap_anime_reformat
migrate-notes --model "Basic" --target-model "Japanese Anime Card" --config jap_anime_reformat
"""
        with open(script_path, "w") as f:
            f.write(script_content)

        args = Namespace(
            command=UserOperationType.RUN_SCRIPT,
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
            output=str(Path(tmp_dir) / "output.apkg"),
            config=None,
            script_file=script_path
        )

        parser = UserOperationParser()
        plan = parser.parse_from_args(args)

        assert not plan.read_only  # Should be False because add-model is a write operation
        assert plan.output_path == Path(tmp_dir) / "output.apkg"
        assert len(plan.operations) == 2
        
        # Check first operation (add-model)
        assert plan.operations[0].operation_type == OperationType.ADD_MODEL
        assert plan.operations[0].model_name == "Japanese Anime Card"
        
        # Check second operation (migrate-notes)
        assert plan.operations[1].operation_type == OperationType.MIGRATE_NOTES
        assert plan.operations[1].model_name == "Basic"
        assert plan.operations[1].target_model_name == "Japanese Anime Card" 