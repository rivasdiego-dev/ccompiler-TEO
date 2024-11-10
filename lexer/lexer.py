import re
from typing import List, Tuple, Pattern
from .token import Token
from .token_type import TokenType
from utils.error_handler import LexicalError

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        
        # Palabras reservadas actualizadas
        self.keywords = {
            'int': TokenType.INT,
            'char': TokenType.CHAR,
            'float': TokenType.FLOAT,
            'void': TokenType.VOID,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'do': TokenType.DO,
            'return': TokenType.RETURN,
            'printInt': TokenType.PRINT_INT,
            'printFloat': TokenType.PRINT_FLOAT,
            'printChar': TokenType.PRINT_CHAR,
            'printStr': TokenType.PRINT_STR,
            'scanInt': TokenType.SCAN_INT,
            'scanFloat': TokenType.SCAN_FLOAT,
            'scanChar': TokenType.SCAN_CHAR
        }
        
        # Compilar patrones de tokens
        self.token_specs: List[Tuple[Pattern, TokenType]] = self._compile_token_patterns()
    
    def _compile_token_patterns(self) -> List[Tuple[Pattern, TokenType]]:
        token_patterns = [
            # Espacios en blanco (ignorar)
            (r'[ \t]+', None),
            # Saltos de línea
            (r'\n', TokenType.NEWLINE),
            # Comentarios
            (r'//[^\n]*', TokenType.COMMENT),
            (r'/\*[\s\S]*?\*/', TokenType.COMMENT),
            # Operadores aritméticos
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.TIMES),
            (r'/', TokenType.DIVIDE),
            # Operadores lógicos
            (r'&&', TokenType.AND),
            (r'\|\|', TokenType.OR),
            # Operadores de comparación
            (r'==', TokenType.EQUALS),
            (r'!=', TokenType.NOT_EQUALS),
            (r'<=', TokenType.LESS_EQUAL),
            (r'>=', TokenType.GREATER_EQUAL),
            (r'<', TokenType.LESS),
            (r'>', TokenType.GREATER),
            # Asignación
            (r'=', TokenType.ASSIGN),
            # Símbolos especiales
            (r';', TokenType.SEMICOLON),
            (r',', TokenType.COMMA),
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),
            # Literales
            (r'\d+\.\d+', TokenType.FLOAT_LITERAL),
            (r'\d+', TokenType.INTEGER_LITERAL),
            (r'\'[^\']*\'', TokenType.CHAR_LITERAL),
            (r'"[^"]*"', TokenType.STRING_LITERAL),
            # Identificadores
            (r'[A-Za-z_][A-Za-z0-9_]*', TokenType.ID),
        ]
        
        return [(re.compile(pattern), token_type) 
                for pattern, token_type in token_patterns]
    
    def tokenize(self) -> List[Token]:
        tokens = []
        pos = 0
        
        while pos < len(self.text):
            match = None
            match_token_type = None
            match_length = 0
            
            # Buscar el patrón más largo que coincida
            for pattern, token_type in self.token_specs:
                regex_match = pattern.match(self.text, pos)
                if regex_match:
                    current_match = regex_match.group(0)
                    if len(current_match) > match_length:
                        match = current_match
                        match_token_type = token_type
                        match_length = len(current_match)
            
            if match:
                if match_token_type:  # Ignorar si el token_type es None
                    if match_token_type == TokenType.ID and match in self.keywords:
                        # Si es un identificador pero coincide con una palabra reservada
                        token_type = self.keywords[match]
                    else:
                        token_type = match_token_type
                    
                    if token_type != TokenType.NEWLINE and token_type != TokenType.COMMENT:
                        tokens.append(Token(token_type, match, self.line, self.column))
                
                # Actualizar posición y columna
                if match_token_type == TokenType.NEWLINE:
                    self.line += 1
                    self.column = 1
                else:
                    self.column += len(match)
                pos += len(match)
            else:
                # Carácter no reconocido
                raise LexicalError(
                    f"Carácter no reconocido: {self.text[pos]}", 
                    self.line, 
                    self.column
                )
        
        # Agregar token de fin de archivo
        tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return tokens