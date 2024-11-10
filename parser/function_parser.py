from typing import List
from .interfaces.parser_interface import BaseParser
from lexer.token_type import TokenType
from utils.error_handler import ParserError
from .parser_utils import ParserUtils
from .declaration_parser import DeclarationParser

class FunctionParser(BaseParser):
    """
    Implementa el parsing de funciones.
    Maneja las siguientes reglas:
    Function → Type ID '(' ParameterList ')' CompoundStmt
    ParameterList → Parameter ParameterListTail | ε
    ParameterListTail → ',' Parameter ParameterListTail | ε
    Parameter → Type ID
    CompoundStmt → '{' StmtList '}'
    """
    
    def __init__(self, tokens):
        super().__init__(tokens)
        self.utils = ParserUtils()
        self.declaration_parser = DeclarationParser(tokens)
    
    def parse(self) -> None:
        """Punto de entrada del parser de funciones"""
        self.parse_function()
    
    def parse_function(self) -> None:
        """Function → Type ID '(' ParameterList ')' CompoundStmt"""
        # Parsear el tipo de retorno
        if not self.is_type_token(self.peek()):
            raise ParserError(
                "Se esperaba un tipo de retorno para la función",
                self.peek().line,
                self.peek().column
            )
        return_type = self.advance()
        
        # Parsear el nombre de la función
        if not self.utils.check_token(self.peek(), TokenType.ID):
            raise ParserError(
                f"Se esperaba un identificador después de '{return_type.value}'",
                self.peek().line,
                self.peek().column
            )
        function_name = self.advance()
        
        # Parsear paréntesis de apertura
        self.utils.consume(self.peek(), TokenType.LPAREN, 
            f"Se esperaba '(' después de '{function_name.value}'")
        self.advance()
        
        # Parsear lista de parámetros
        self.parse_parameter_list()
        
        # Parsear paréntesis de cierre
        self.utils.consume(self.peek(), TokenType.RPAREN,
            "Se esperaba ')' después de la lista de parámetros")
        self.advance()
        
        # Parsear el cuerpo de la función
        self.parse_compound_stmt()
    
    def parse_parameter_list(self) -> None:
        """ParameterList → Parameter ParameterListTail | ε"""
        if self.is_type_token(self.peek()):
            self.parse_parameter()
            self.parse_parameter_list_tail()
    
    def parse_parameter(self) -> None:
        """Parameter → Type ID"""
        # Parsear el tipo del parámetro
        if not self.is_type_token(self.peek()):
            raise ParserError(
                "Se esperaba un tipo para el parámetro",
                self.peek().line,
                self.peek().column
            )
        param_type = self.advance()
        
        # Parsear el nombre del parámetro
        if not self.utils.check_token(self.peek(), TokenType.ID):
            raise ParserError(
                f"Se esperaba un identificador después de '{param_type.value}'",
                self.peek().line,
                self.peek().column
            )
        self.advance()
    
    def parse_parameter_list_tail(self) -> None:
        """ParameterListTail → ',' Parameter ParameterListTail | ε"""
        if self.utils.check_token(self.peek(), TokenType.COMMA):
            self.advance()  # Consumir la coma
            self.parse_parameter()
            self.parse_parameter_list_tail()
    
    def parse_compound_stmt(self) -> None:
        """CompoundStmt → '{' StmtList '}'"""
        # Parsear llave de apertura
        self.utils.consume(self.peek(), TokenType.LBRACE,
            "Se esperaba '{' para iniciar el cuerpo de la función")
        self.advance()
        
        # Parsear lista de statements
        self.parse_stmt_list()
        
        # Parsear llave de cierre
        self.utils.consume(self.peek(), TokenType.RBRACE,
            "Se esperaba '}' para cerrar el cuerpo de la función")
        self.advance()
    
    def parse_stmt_list(self) -> None:
        """
        StmtList → Statement StmtList | ε
        Por ahora solo manejamos declaraciones y statements vacíos
        """
        while not self.utils.check_token(self.peek(), TokenType.RBRACE):
            # Ignorar comentarios
            if self.peek().type == TokenType.COMMENT:
                self.advance()
                continue
                
            # Ignorar saltos de línea
            if self.peek().type == TokenType.NEWLINE:
                self.advance()
                continue
            
            # Por ahora solo manejamos:
            # 1. Declaraciones de variables
            # 2. Statements vacíos (solo punto y coma)
            if self.is_type_token(self.peek()):
                self.declaration_parser.parse_declaration()
            elif self.utils.check_token(self.peek(), TokenType.SEMICOLON):
                self.advance()
            else:
                raise ParserError(
                    "Statement no soportado todavía",
                    self.peek().line,
                    self.peek().column
                )
    
    def is_type_token(self, token) -> bool:
        """Verifica si el token es un tipo de dato válido"""
        return token.type in {
            TokenType.INT,
            TokenType.CHAR,
            TokenType.FLOAT,
            TokenType.VOID
        }