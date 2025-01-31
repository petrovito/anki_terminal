import pytest
from pathlib import Path
from arg_parser import create_arg_parser, parse_command_line, parse_script_line
from operation_models import UserOperationType

def test_create_arg_parser():
    """Test that the argument parser is created with all expected arguments."""
    parser = create_arg_parser()
    
    # Check that required arguments are present
    actions = {action.dest: action for action in parser._actions}
    assert 'apkg_file' in actions
    assert 'command' in actions
    
    # Check that optional arguments are present with correct defaults
    assert actions['model'].default is None
    assert actions['log_level'].default == 'error'
    assert actions['script_file'].default is None

def test_parse_command_line_valid():
    """Test parsing valid command line arguments."""
    args = ['test.apkg', 'list-models', '--log-level', 'debug']
    parsed = parse_command_line(args)
    
    assert parsed.apkg_file == 'test.apkg'
    assert parsed.command == UserOperationType.LIST_MODELS
    assert parsed.log_level == 'debug'

def test_parse_command_line_invalid_command():
    """Test that invalid commands raise an error."""
    args = ['test.apkg', 'invalid-command']
    with pytest.raises(SystemExit):
        parse_command_line(args)

def test_parse_script_line_valid():
    """Test parsing valid script lines."""
    # Test basic command
    line = 'list-models'
    parsed = parse_script_line(line)
    assert parsed.command == UserOperationType.LIST_MODELS
    
    # Test command with options
    line = 'add-field --model "Basic" --new-field "NewField"'
    parsed = parse_script_line(line)
    assert parsed.command == UserOperationType.ADD_FIELD
    assert parsed.model == "Basic"
    assert parsed.new_field == "NewField"

def test_parse_script_line_empty():
    """Test parsing empty or comment lines."""
    assert parse_script_line('') is None
    assert parse_script_line('  ') is None
    assert parse_script_line('# comment') is None
    assert parse_script_line('  # comment with spaces') is None

def test_parse_script_line_invalid():
    """Test parsing invalid script lines."""
    # Invalid command
    with pytest.raises(ValueError):
        parse_script_line('invalid-command')
    
    # Missing required argument
    with pytest.raises(ValueError):
        parse_script_line('--model "Basic"')

def test_parse_script_line_quoted_strings():
    """Test parsing script lines with quoted strings."""
    line = 'add-model --model "Complex Model" --fields \'["Field 1", "Field 2"]\''
    parsed = parse_script_line(line)
    assert parsed.command == UserOperationType.ADD_MODEL
    assert parsed.model == "Complex Model"
    assert parsed.fields == '["Field 1", "Field 2"]' 