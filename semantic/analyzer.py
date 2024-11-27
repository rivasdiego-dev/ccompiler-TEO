from typing import Optional
from .types import DataType, Variable, Function
from .symbol_table import SymbolTable
from utils.error_handler import SemanticError
from lexer.token_type import TokenType

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_return_type: Optional[DataType] = None

    def analyze(self, parser) -> None:
        """
        Realiza el análisis semántico mientras el parser realiza el análisis sintáctico.
        """
        self.parser = parser
        parser.semantic_analyzer = self

    def check_types(self, expected: DataType, found: DataType, line: int, column: int) -> None:
        """Verifica que los tipos sean compatibles"""
        if expected == found:
            return
        if expected == DataType.FLOAT and found == DataType.INT:
            return  # Conversión implícita permitida
        raise SemanticError(
            f"Tipo incompatible: se esperaba {expected.name} pero se encontró {found.name}",
            line,
            column
        )
    
    def enter_global_scope(self) -> None:
        """Inicializa el ámbito global"""
        self.symbol_table = SymbolTable()
        self.current_return_type = None

    def enter_scope(self) -> None:
        """Entra a un nuevo ámbito"""
        self.symbol_table.enter_scope()

    def exit_scope(self) -> None:
        """Sale del ámbito actual"""
        self.symbol_table.exit_scope()

    def synchronize(self) -> None:
        """Sincroniza el estado del analizador semántico después de un error"""
        # Por ahora solo reiniciamos el estado
        self.current_return_type = None

    def enter_function(self, return_type: DataType, name: str, line: int, column: int) -> None:
        """Llamado cuando el parser entra a una función"""
        func = Function(name, return_type, line=line, column=column)
        self.symbol_table.enter_function(func)
        self.current_return_type = return_type

    def exit_function(self) -> None:
        """Llamado cuando el parser sale de una función"""
        self.symbol_table.exit_function()
        self.current_return_type = None

    def add_parameter(self, type: DataType, name: str, line: int, column: int) -> None:
        """Llamado cuando el parser procesa un parámetro de función"""
        var = Variable(name, type, initialized=True, line=line, column=column)
        self.symbol_table.define_variable(var)
        if self.symbol_table.current_function:
            self.symbol_table.current_function.parameters.append(var)

    def declare_variable(self, type: DataType, name: str, initialized: bool, line: int, column: int) -> None:
        """Llamado cuando el parser encuentra una declaración de variable"""
        var = Variable(name, type, initialized, line, column)
        self.symbol_table.define_variable(var)

    def check_variable_exists(self, name: str, line: int, column: int) -> Variable:
        """Verifica que una variable exista cuando se usa"""
        return self.symbol_table.get_variable(name, line, column)

    def check_function_exists(self, name: str, line: int, column: int) -> Function:
        """Verifica que una función exista cuando se llama"""
        return self.symbol_table.get_function(name, line, column)

    def can_compare(self, type1: DataType, type2: DataType) -> bool:
        """Verifica si dos tipos pueden ser comparados entre sí"""
        # Tipos iguales siempre pueden compararse
        if type1 == type2:
            return True
        
        # INT y FLOAT pueden compararse entre sí
        if (type1 in {DataType.INT, DataType.FLOAT} and 
            type2 in {DataType.INT, DataType.FLOAT}):
            return True
        
        return False

    def check_function_call(self, name: str, args: list, line: int, column: int) -> DataType:
        """Verifica una llamada a función"""
        func = self.check_function_exists(name, line, column)
        
        if len(args) != len(func.parameters):
            raise SemanticError(
                f"Número incorrecto de argumentos para '{name}'. "
                f"Se esperaban {len(func.parameters)}, se recibieron {len(args)}",
                line, column
            )
        
        for i, (param, arg_type) in enumerate(zip(func.parameters, args)):
            self.check_types(param.type, arg_type, line, column)
        
        return func.return_type

    def check_return(self, return_type: Optional[DataType], line: int, column: int) -> None:
        """Verifica que el tipo de retorno coincida con la declaración de la función"""
        if not self.current_return_type:
            raise SemanticError("return fuera de una función", line, column)
        
        if self.current_return_type == DataType.VOID:
            if return_type is not None:
                raise SemanticError(
                    "función void no debe retornar un valor",
                    line, column
                )
        elif return_type is None:
            raise SemanticError(
                f"función de tipo {self.current_return_type.name} debe retornar un valor",
                line, column
            )
        else:
            self.check_types(self.current_return_type, return_type, line, column)

    def check_condition(self, type: DataType, line: int, column: int) -> None:
        """Verifica que una condición sea de tipo entero"""
        if type != DataType.INT:
            raise SemanticError(
                "La condición debe ser de tipo int",
                line, column
            )

    def get_operation_type(self, left: DataType, op: TokenType, right: DataType, line: int, column: int) -> DataType:
        """Determina el tipo resultante de una operación binaria"""
        
        # Operaciones aritméticas
        if op in {TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE}:
            if left == DataType.FLOAT or right == DataType.FLOAT:
                return DataType.FLOAT
            return DataType.INT

        # Operaciones de comparación y lógicas
        if op in {TokenType.EQUALS, TokenType.NOT_EQUALS, TokenType.LESS,
                TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL,
                TokenType.AND, TokenType.OR}:
            
            # Verificar que los operandos sean compatibles
            if left == right:
                pass  # OK
            elif left == DataType.FLOAT and right == DataType.INT:
                pass  # OK
            elif left == DataType.INT and right == DataType.FLOAT:
                pass  # OK
            else:
                raise SemanticError(
                    f"Operandos incompatibles: {left.name} {op.name} {right.name}",
                    line, column
                )
            
            # Operaciones lógicas solo con enteros
            if op in {TokenType.AND, TokenType.OR} and (left != DataType.INT or right != DataType.INT):
                raise SemanticError(
                    f"Operadores lógicos requieren operandos enteros",
                    line, column
                )
            
            return DataType.INT

        raise SemanticError(
            f"Operador no soportado: {op.name}",
            line, column
        )

    def analyze_assignment(self, var_name: str, value_type: DataType, line: int, column: int) -> None:
        """Verifica una asignación"""
        var = self.check_variable_exists(var_name, line, column)
        self.check_types(var.type, value_type, line, column)
        var.initialized = True