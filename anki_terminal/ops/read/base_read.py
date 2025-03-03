from typing import Dict, List, Optional, Any

from anki_terminal.ops.base import Operation, OperationResult, OperationArgument
from anki_terminal.anki_types import Collection, Model, Template

class ReadOperation(Operation):
    """Base class for all read operations."""
    
    readonly = True
    
    def __init__(self, printer=None, **kwargs):
        super().__init__(printer, **kwargs) 