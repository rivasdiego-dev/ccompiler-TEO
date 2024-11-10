from typing import Set, List
from lexer.token import Token
from lexer.token_type import TokenType
from utils.error_handler import ParserError

class ParserUtils:
    @staticmethod
    def check_token(token: Token, type: TokenType) -> bool:
        """Verifica si un token es del tipo esperado"""
        return token.type == type

    @staticmethod
    def match_tokens(token: Token, types: Set[TokenType]) -> bool:
        """Verifica si un token coincide con alguno de los tipos dados"""
        return token.type in types

    @staticmethod
    def consume(token: Token, expected_type: TokenType, message: str) -> None:
        """Verifica que un token sea del tipo esperado o lanza un error"""
        if not ParserUtils.check_token(token, expected_type):
            raise ParserError(
                f"{message}. Se encontró '{token.value}'",
                token.line,
                token.column
            )

    @staticmethod
    def synchronize(tokens: List[Token], current: int) -> int:
        """
        Recuperación de errores: avanza hasta encontrar un punto seguro
        Retorna la nueva posición en los tokens
        """
        current += 1

        while current < len(tokens):
            if tokens[current - 1].type == TokenType.SEMICOLON:
                return current

            if tokens[current].type in {
                TokenType.INT,
                TokenType.CHAR,
                TokenType.FLOAT,
                TokenType.VOID,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.DO,
                TokenType.RETURN
            }:
                return current

            current += 1

        return current