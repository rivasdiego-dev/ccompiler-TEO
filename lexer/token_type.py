from enum import Enum, auto

class TokenType(Enum):
    # Palabras reservadas
    INT = auto()
    CHAR = auto()
    FLOAT = auto()
    VOID = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    RETURN = auto()
    PRINTF = auto()
    SCANF = auto()
    
    # Operadores aritméticos
    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIVIDE = auto()
    
    # Operadores lógicos
    AND = auto()
    OR = auto()
    
    # Operadores de comparación
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    
    # Asignación
    ASSIGN = auto()
    
    # Símbolos especiales
    SEMICOLON = auto()
    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    
    # Literales e identificadores
    ID = auto()
    INTEGER_LITERAL = auto()
    FLOAT_LITERAL = auto()
    CHAR_LITERAL = auto()
    STRING_LITERAL = auto()
    
    # Comentarios
    COMMENT = auto()
    
    # Especiales
    EOF = auto()
    NEWLINE = auto()