from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List

class DataType(Enum):
    INT = auto()
    FLOAT = auto()
    CHAR = auto()
    VOID = auto()

@dataclass
class Variable:
    name: str
    type: DataType
    initialized: bool = False
    line: int = 0
    column: int = 0

@dataclass
class Function:
    name: str
    return_type: DataType
    parameters: List[Variable] = field(default_factory=list)
    line: int = 0
    column: int = 0