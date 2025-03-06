from typing import Any, Dict, List, Optional

from anki_terminal.anki_types import Collection, Model, Template
from anki_terminal.ops.op_base import (Operation, OperationArgument,
                                       OperationResult)


class ReadOperation(Operation):
    """Base class for all read operations."""
    
    readonly = True
    
    def __init__(self, printer=None, **kwargs):
        super().__init__(printer, **kwargs) 