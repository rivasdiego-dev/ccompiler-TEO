class CompilerError(Exception):
    """Clase base para errores del compilador"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.get_error_message())
    
    def get_error_message(self) -> str:
        return f"Error en línea {self.line}, columna {self.column}: {self.message}"

class LexicalError(CompilerError):
    """Error específico para el análisis léxico"""
    pass

class ParserError(CompilerError):
    """Error específico para el análisis sintáctico"""
    pass