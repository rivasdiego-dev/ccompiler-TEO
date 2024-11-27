from typing import Dict, Optional, List
from .types import Variable, Function
from utils.error_handler import SemanticError

class Scope:
    def __init__(self, parent: Optional['Scope'] = None):
        self.variables: Dict[str, Variable] = {}
        self.functions: Dict[str, Function] = {}
        self.parent = parent

    def define_variable(self, var: Variable) -> None:
        if var.name in self.variables:
            raise SemanticError(
                f"Variable '{var.name}' ya declarada en este ámbito",
                var.line,
                var.column
            )
        self.variables[var.name] = var

    def define_function(self, func: Function) -> None:
        if func.name in self.functions:
            raise SemanticError(
                f"Función '{func.name}' ya declarada",
                func.line,
                func.column
            )
        self.functions[func.name] = func

    def get_variable(self, name: str, line: int, column: int) -> Variable:
        scope = self
        while scope:
            if name in scope.variables:
                return scope.variables[name]
            scope = scope.parent
        raise SemanticError(
            f"Variable '{name}' no declarada",
            line,
            column
        )

    def get_function(self, name: str, line: int, column: int) -> Function:
        scope = self
        while scope:
            if name in scope.functions:
                return scope.functions[name]
            scope = scope.parent
        raise SemanticError(
            f"Función '{name}' no declarada",
            line,
            column
        )

class SymbolTable:
    def __init__(self):
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.current_function: Optional[Function] = None

    def enter_scope(self) -> None:
        """Crea un nuevo ámbito hijo del actual"""
        self.current_scope = Scope(self.current_scope)

    def exit_scope(self) -> None:
        """Regresa al ámbito padre"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent

    def enter_function(self, func: Function) -> None:
        """Entra al ámbito de una función"""
        self.define_function(func)
        self.current_function = func
        self.enter_scope()

    def exit_function(self) -> None:
        """Sale del ámbito de la función actual"""
        self.exit_scope()
        self.current_function = None

    def define_variable(self, var: Variable) -> None:
        """Define una variable en el ámbito actual"""
        self.current_scope.define_variable(var)

    def define_function(self, func: Function) -> None:
        """Define una función en el ámbito global"""
        self.global_scope.define_function(func)

    def get_variable(self, name: str, line: int, column: int) -> Variable:
        """Busca una variable en todos los ámbitos accesibles"""
        return self.current_scope.get_variable(name, line, column)

    def get_function(self, name: str, line: int, column: int) -> Function:
        """Busca una función (solo en ámbito global)"""
        return self.global_scope.get_function(name, line, column)