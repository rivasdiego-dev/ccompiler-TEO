from dataclasses import dataclass
from typing import Any
from .token_type import TokenType

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int
    
    def __str__(self) -> str:
        return f"Token(type={self.type.name}, value='{self.value}', line={self.line}, column={self.column})"