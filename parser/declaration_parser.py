from .interfaces.parser_interface import BaseParser
from lexer.token_type import TokenType
from utils.error_handler import ParserError
from .parser_utils import ParserUtils

class DeclarationParser(BaseParser):
    """
    Implementa el parsing de declaraciones de variables.
    Maneja las siguientes reglas:
    Declaration → Type ID DeclarationTail
    DeclarationTail → '=' Expression ';' | ';'
    """
    
    def __init__(self, tokens):
        super().__init__(tokens)
        self.utils = ParserUtils()
    
    def parse(self) -> None:
        """Punto de entrada para el parsing de declaraciones"""
        while not self.is_at_end():
            # Ignorar comentarios
            if self.peek().type == TokenType.COMMENT:
                self.advance()
                continue
                
            # Ignorar saltos de línea
            if self.peek().type == TokenType.NEWLINE:
                self.advance()
                continue
                
            # Si encontramos un tipo, parseamos la declaración
            if self.is_type_token(self.peek()):
                try:
                    self.parse_declaration()
                except ParserError as e:
                    print(f"Error: {e}")
                    self.synchronize()  # Recuperarnos del error
            else:
                # Si no es un tipo y no es EOF, es un error
                if not self.is_at_end():
                    raise ParserError(
                        f"Token inesperado: {self.peek().value}",
                        self.peek().line,
                        self.peek().column
                    )
    
    def parse_declaration(self) -> None:
        """Declaration → Type ID DeclarationTail"""
        # Guardar el token de tipo para mensajes de error
        type_token = self.advance()
        
        # Verificar que el siguiente token sea un identificador
        if not self.utils.check_token(self.peek(), TokenType.ID):
            raise ParserError(
                f"Se esperaba un identificador después de '{type_token.value}'",
                self.peek().line,
                self.peek().column
            )
        
        # Consumir el identificador
        id_token = self.advance()
        
        # Manejar el resto de la declaración
        self.parse_declaration_tail()
    
    def parse_declaration_tail(self) -> None:
        """DeclarationTail → '=' Expression ';' | ';'"""
        if self.utils.check_token(self.peek(), TokenType.ASSIGN):
            self.advance()  # Consumir '='
            self.parse_expression()
            
        # Debe terminar con punto y coma
        if not self.utils.check_token(self.peek(), TokenType.SEMICOLON):
            raise ParserError(
                "Se esperaba ';' al final de la declaración",
                self.peek().line,
                self.peek().column
            )
        self.advance()  # Consumir ';'
    
    def parse_expression(self) -> None:
        """
        Método temporal para parsear expresiones simples hasta que
        implementemos el ExpressionParser completo
        """
        # Por ahora solo aceptamos literales básicos
        if not self.utils.check_token(self.peek(), TokenType.INTEGER_LITERAL) and \
           not self.utils.check_token(self.peek(), TokenType.FLOAT_LITERAL) and \
           not self.utils.check_token(self.peek(), TokenType.CHAR_LITERAL) and \
           not self.utils.check_token(self.peek(), TokenType.STRING_LITERAL):
            raise ParserError(
                "Se esperaba un valor literal",
                self.peek().line,
                self.peek().column
            )
        self.advance()
    
    def is_type_token(self, token) -> bool:
        """Verifica si el token es un tipo de dato válido"""
        return token.type in {
            TokenType.INT,
            TokenType.CHAR,
            TokenType.FLOAT
        }
    
    def synchronize(self) -> None:
        """Recuperación de errores: avanza hasta el siguiente punto seguro"""
        while not self.is_at_end():
            if self.peek().type == TokenType.SEMICOLON:
                self.advance()
                return
            
            if self.is_type_token(self.peek()):
                return
                
            self.advance()