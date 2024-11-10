from typing import List
from lexer.token import Token
from lexer.token_type import TokenType
from .expression_parser import ExpressionParser
from .statement_parser import StatementParser
from .declaration_parser import DeclarationParser
from .function_parser import FunctionParser
from .parser_utils import ParserUtils
from .interfaces.parser_interface import BaseParser
from utils.error_handler import ParserError

class Parser(BaseParser):
    def __init__(self, tokens: List[Token]):
        super().__init__(tokens)
        # Inicializar sub-parsers
        self.expression_parser = ExpressionParser(tokens)
        self.statement_parser = StatementParser(tokens)
        self.declaration_parser = DeclarationParser(tokens)
        self.function_parser = FunctionParser(tokens)
        self.utils = ParserUtils()

    def parse(self) -> None:
        """
        Punto de entrada del parser.
        Implementa la regla: Program → FunctionList
        """
        try:
            self.function_list()
            if not self.is_at_end():
                raise ParserError(
                    "Se esperaba fin de archivo",
                    self.peek().line,
                    self.peek().column
                )
        except ParserError as e:
            # Propagar el error con la información de línea y columna
            raise e
        except Exception as e:
            # Para errores inesperados, crear un ParserError con la posición actual
            current_token = self.peek()
            raise ParserError(str(e), current_token.line, current_token.column)

    def function_list(self) -> None:
        """FunctionList → Function FunctionList | ε"""
        while not self.is_at_end() and self.is_type_token(self.peek()):
            self.function_parser.parse_function()

    def is_type_token(self, token: Token) -> bool:
        """Verifica si el token es un tipo de dato"""
        return token.type in {
            TokenType.INT,
            TokenType.CHAR,
            TokenType.FLOAT,
            TokenType.VOID
        }