from typing import List, Optional, Set
from lexer.token import Token
from lexer.token_type import TokenType
from utils.error_handler import ParserError

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    # Utilidades básicas del parser
    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type

    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        
        raise ParserError(
            f"{message}. Se encontró '{self.peek().value}'",
            self.peek().line,
            self.peek().column
        )

    def synchronize(self) -> None:
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            if self.peek().type in {
                TokenType.INT, TokenType.CHAR, TokenType.FLOAT, TokenType.VOID,
                TokenType.IF, TokenType.WHILE, TokenType.DO, TokenType.RETURN
            }:
                return

            self.advance()

    # Punto de entrada
    def parse(self) -> None:
        try:
            self.program()
            if not self.is_at_end():
                raise ParserError(
                    "Se esperaba fin de archivo",
                    self.peek().line,
                    self.peek().column
                )
        except ParserError as e:
            raise e
        except Exception as e:
            current_token = self.peek()
            raise ParserError(str(e), current_token.line, current_token.column)

    # Implementación de expresiones (nivel más bajo)
    def expression(self) -> None:
        """Expression → LogicExpr"""
        self.logic_expr()

    def logic_expr(self) -> None:
        """LogicExpr → CompExpr LogicExprTail"""
        self.comp_expr()
        self.logic_expr_tail()

    def logic_expr_tail(self) -> None:
        """LogicExprTail → ('&&' | '||') CompExpr LogicExprTail | ε"""
        if self.match(TokenType.AND, TokenType.OR):
            self.comp_expr()
            self.logic_expr_tail()

    def comp_expr(self) -> None:
        """CompExpr → AddExpr CompExprTail"""
        self.add_expr()
        self.comp_expr_tail()

    def comp_expr_tail(self) -> None:
        """CompExprTail → ('==' | '!=' | '<' | '<=' | '>' | '>=') AddExpr CompExprTail | ε"""
        if self.match(TokenType.EQUALS, TokenType.NOT_EQUALS,
                     TokenType.LESS, TokenType.LESS_EQUAL,
                     TokenType.GREATER, TokenType.GREATER_EQUAL):
            self.add_expr()
            self.comp_expr_tail()

    def add_expr(self) -> None:
        """AddExpr → MultExpr AddExprTail"""
        self.mult_expr()
        self.add_expr_tail()

    def add_expr_tail(self) -> None:
        """AddExprTail → ('+' | '-') MultExpr AddExprTail | ε"""
        if self.match(TokenType.PLUS, TokenType.MINUS):
            self.mult_expr()
            self.add_expr_tail()

    def mult_expr(self) -> None:
        """MultExpr → Factor MultExprTail"""
        self.factor()
        self.mult_expr_tail()

    def mult_expr_tail(self) -> None:
        """MultExprTail → ('*' | '/') Factor MultExprTail | ε"""
        if self.match(TokenType.TIMES, TokenType.DIVIDE):
            self.factor()
            self.mult_expr_tail()

    def factor(self) -> None:
        """
        Factor → '(' Expression ')'
               | ID FactorTail
               | INTEGER_LITERAL
               | FLOAT_LITERAL
               | CHAR_LITERAL
               | STRING_LITERAL
        """
        if self.match(TokenType.LPAREN):
            self.expression()
            self.consume(TokenType.RPAREN, "Se esperaba ')'")
        elif self.match(TokenType.ID):
            self.factor_tail()
        elif self.match(TokenType.INTEGER_LITERAL,
                       TokenType.FLOAT_LITERAL,
                       TokenType.CHAR_LITERAL,
                       TokenType.STRING_LITERAL):
            # Después de un literal, debe venir un operador o un token de cierre
            if not self.is_at_end() and \
               not self.is_operator(self.peek()) and \
               not self.is_closing_token(self.peek()):
                raise ParserError(
                    f"Se esperaba un operador después de '{self.previous().value}'",
                    self.peek().line,
                    self.peek().column
                )
        else:
            raise ParserError(
                "Se esperaba una expresión",
                self.peek().line,
                self.peek().column
            )

    def is_operator(self, token: Token) -> bool:
        """Verifica si el token es un operador"""
        return token.type in {
            TokenType.PLUS, TokenType.MINUS,
            TokenType.TIMES, TokenType.DIVIDE,
            TokenType.AND, TokenType.OR,
            TokenType.EQUALS, TokenType.NOT_EQUALS,
            TokenType.LESS, TokenType.LESS_EQUAL,
            TokenType.GREATER, TokenType.GREATER_EQUAL
        }

    def is_closing_token(self, token: Token) -> bool:
        """Verifica si el token es un token de cierre"""
        return token.type in {
            TokenType.RPAREN,    # )
            TokenType.COMMA,     # ,
            TokenType.SEMICOLON, # ;
            TokenType.EOF       # fin de archivo
        }
    
    def factor_tail(self) -> None:
        """FactorTail → '(' ArgumentList ')' | ε"""
        if self.match(TokenType.LPAREN):
            self.argument_list()
            self.consume(TokenType.RPAREN, "Se esperaba ')'")

    def argument_list(self) -> None:
        """ArgumentList → Expression ArgumentListTail | ε"""
        if not self.check(TokenType.RPAREN):
            self.expression()
            self.argument_list_tail()

    def argument_list_tail(self) -> None:
        """ArgumentListTail → ',' Expression ArgumentListTail | ε"""
        if self.match(TokenType.COMMA):
            self.expression()
            self.argument_list_tail()

    # El resto de la implementación seguirá en la siguiente parte
    # para mantener el código organizado y legible