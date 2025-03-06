import importlib
import inspect
from pathlib import Path
from typing import Dict, Set, Type

import pytest

from anki_terminal.ops.op_base import Operation
from tests.ops.test_base import OperationTestBase


def get_all_operations() -> Dict[str, Type[Operation]]:
    """Find all operation classes in the ops directory."""
    ops_dir = Path(__file__).parent.parent.parent / 'ops'
    operations = {}
    
    # Walk through all python files in ops directory
    for py_file in ops_dir.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        # Convert path to module name
        relative_path = py_file.relative_to(ops_dir.parent)
        module_name = str(relative_path.with_suffix('')).replace('/', '.')
        
        # Import module and find Operation subclasses
        try:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Operation) and 
                    obj != Operation and
                    obj.__module__ != 'ops.read.base_read' and
                    obj.__name__ != 'ReadOperation' and
                    obj.__name__ != 'PathOperation'):
                    operations[obj.name] = obj
        except Exception as e:
            print(f"Warning: Could not load operations from {module_name}: {e}")
            
    return operations

def get_test_classes() -> Dict[str, Set[Type]]:
    """Find all operation test classes."""
    test_dir = Path(__file__).parent
    test_classes = {}
    
    # Walk through all python files in tests/ops directory recursively
    for py_file in test_dir.rglob('test_*.py'):
        if py_file.name in ['test_base.py', 'test_coverage.py']:
            continue
            
        # Import module and find test classes
        module_name = f"tests.ops.{py_file.relative_to(test_dir).with_suffix('').as_posix().replace('/', '.')}"
        try:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, OperationTestBase) and 
                    obj != OperationTestBase):
                    op_name = obj.operation_class.name if obj.operation_class else None
                    if op_name:
                        test_classes.setdefault(op_name, set()).add(obj)
        except Exception as e:
            print(f"Warning: Could not load tests from {module_name}: {e}")
            
    return test_classes

def test_operation_test_coverage():
    """Verify that all operations have unit tests."""
    operations = get_all_operations()
    test_classes = get_test_classes()
    
    # Check each operation has tests
    missing_tests = []
    for op_name, op_class in operations.items():
        if op_name not in test_classes:
            missing_tests.append(f"{op_name} is missing tests")
    
    if missing_tests:
        pytest.fail("\n".join(missing_tests)) 