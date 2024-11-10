from abc import ABC, abstractmethod
from typing import List
from lexer.token import Token
from lexer.token_type import TokenType

class BaseParser(ABC):
    """Interfaz base para todos los componentes del parser"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    @abstractmethod
    def parse(self) -> None:
        """Método principal de parsing para cada componente"""
        pass

    def peek(self) -> Token:
        """Retorna el token actual sin consumirlo"""
        return self.tokens[self.current]

    def previous(self) -> Token:
        """Retorna el token anterior"""
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        """Consume y retorna el token actual"""
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        """Verifica si hemos llegado al final de los tokens"""
        return self.peek().type == TokenType.EOF