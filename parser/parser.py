from typing import List, Optional, Set
from lexer.token import Token
from lexer.token_type import TokenType
from utils.error_handler import ParserError, SemanticError
from semantic.analyzer import SemanticAnalyzer
from semantic.types import DataType, Variable, Function

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.has_main_function = False
        self.semantic_analyzer = SemanticAnalyzer()
    
    def function_list(self) -> None:
        """FunctionList → Function FunctionList | ε"""
        while not self.is_at_end():
            if self.is_function_declaration():
                # Verificar si es la función main antes de parsearla
                if self.is_main_function():
                    self.has_main_function = True
                self.function()
            else:
                break

    def is_main_function(self) -> bool:
        """Verifica si la siguiente función es main()"""
        if not self.is_type_token(self.peek()):
            return False
        
        # Guardar posición actual
        saved_pos = self.current
        try:
            self.advance()  # tipo (void, int, etc)
            if not self.check(TokenType.ID):
                return False
            return self.peek().value == "main"
        finally:
            self.current = saved_pos
    
    def program(self) -> None:
        """Program → GlobalDeclaration* FunctionList"""
        if self.is_at_end():
            raise ParserError(
                "El programa está vacío",
                self.peek().line,
                self.peek().column
            )
        
        # Iniciar ámbito global
        self.semantic_analyzer.enter_global_scope()
        
        # Procesar declaraciones globales
        while not self.is_at_end() and self.is_global_declaration():
            self.global_declaration()

        # Procesar funciones
        self.function_list()

        # Verificar que existe una función main
        if not self.has_main_function:
            raise ParserError(
                "No se encontró la función 'main'",
                self.previous().line,
                self.previous().column
            )

    def is_global_declaration(self) -> bool:
        """
        Verifica si los siguientes tokens forman una declaración global.
        """
        if not self.is_type_token(self.peek()):
            return False
        
        # Necesitamos ver más adelante sin consumir tokens
        saved_pos = self.current
        try:
            self.advance()  # tipo
            if not self.check(TokenType.ID):
                return False
            self.advance()  # identificador
            # Si sigue un paréntesis, es una función, no una declaración global
            return not self.check(TokenType.LPAREN)
        finally:
            self.current = saved_pos

    def global_declaration(self) -> None:
        """GlobalDeclaration → Type ID ['=' Expression] ';'"""
        # Obtener el tipo
        type_token = self.peek()
        data_type = self.get_data_type(type_token.type)
        self.type()  # Consume el tipo
        
        # Consumir el identificador
        id_token = self.consume(TokenType.ID, 
            f"Se esperaba un identificador después de '{type_token.value}'")
        
        # Registrar la variable en la tabla de símbolos
        initialized = False
        
        # Inicialización opcional
        if self.match(TokenType.ASSIGN):
            expr_type = self.expression()
            self.semantic_analyzer.check_types(
                data_type, 
                expr_type,
                id_token.line,
                id_token.column
            )
            initialized = True
        
        # Declarar la variable global
        self.semantic_analyzer.declare_variable(
            data_type,
            id_token.value,
            initialized,
            id_token.line,
            id_token.column
        )
        
        # Verificar punto y coma
        self.consume(TokenType.SEMICOLON, 
            f"Se esperaba ';' después de la declaración de '{id_token.value}'")
    
    def parse(self) -> None:
        """
        Punto de entrada principal del parser.
        """
        try:
            self.program()
        except ParserError as e:
            raise e
        except Exception as e:
            current_token = self.peek()
            raise ParserError(str(e), current_token.line, current_token.column)

    def is_function_declaration(self) -> bool:
        """Verifica si los tokens siguientes forman una declaración de función"""
        if not self.is_type_token(self.peek()):
            return False
        
        # Necesitamos ver más adelante sin consumir tokens
        saved_pos = self.current
        try:
            self.advance()  # tipo
            if not self.check(TokenType.ID):
                return False
            self.advance()  # identificador
            return self.check(TokenType.LPAREN)
        finally:
            self.current = saved_pos

    def is_statement_start(self) -> bool:
        """Verifica si el token actual puede iniciar un statement"""
        return self.peek().type in {
            TokenType.IF,
            TokenType.WHILE,
            TokenType.DO,
            TokenType.RETURN,
            TokenType.LBRACE,
            TokenType.ID,
            TokenType.PRINT_INT,
            TokenType.PRINT_FLOAT,
            TokenType.PRINT_CHAR,
            TokenType.PRINT_STR,
            TokenType.SCAN_INT,
            TokenType.SCAN_FLOAT,
            TokenType.SCAN_CHAR
        }

    def is_function_call(self) -> bool:
        """Verifica si los tokens siguientes forman una llamada a función"""
        if not self.check(TokenType.ID):
            return False

        # Necesitamos ver más adelante sin consumir tokens
        saved_pos = self.current
        try:
            self.advance()  # identificador
            return self.check(TokenType.LPAREN)
        finally:
            self.current = saved_pos

    def function_call_stmt(self) -> None:
        """FunctionCallStmt → ID '(' ArgumentList ')' ';'"""
        self.consume(TokenType.ID, "Se esperaba un identificador")
        self.consume(TokenType.LPAREN, "Se esperaba '(' después del identificador")
        self.argument_list()
        self.consume(TokenType.RPAREN, "Se esperaba ')'")
        self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de la llamada a función")

    # Utilidades básicas del parser
    def peek(self) -> Token:
        return self.tokens[self.current]

    def get_data_type(self, token_type: TokenType) -> DataType:
        """Convierte un TokenType a DataType"""
        type_map = {
            TokenType.INT: DataType.INT,
            TokenType.FLOAT: DataType.FLOAT,
            TokenType.CHAR: DataType.CHAR,
            TokenType.VOID: DataType.VOID
        }
        if token_type not in type_map:
            raise ParserError(
                f"Tipo de dato no válido: {token_type}",
                self.peek().line,
                self.peek().column
            )
        return type_map[token_type]

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
        """Sincroniza el parser y el analizador semántico después de un error"""
        self.advance()

        # Sincronización sintáctica
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                # Si encontramos el fin de una declaración, podemos recuperarnos
                self.semantic_analyzer.synchronize()
                return

            if self.peek().type in {
                TokenType.INT, TokenType.CHAR, TokenType.FLOAT, TokenType.VOID,
                TokenType.IF, TokenType.WHILE, TokenType.DO, TokenType.RETURN
            }:
                # Si encontramos el inicio de una nueva construcción
                self.semantic_analyzer.synchronize()
                return

            self.advance()

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
    
    def verify_type_compatibility(self, expected: DataType, found: DataType, token: Token) -> None:
        """Verifica la compatibilidad de tipos usando el analizador semántico"""
        try:
            self.semantic_analyzer.check_types(expected, found, token.line, token.column)
        except SemanticError as e:
            # Opcionalmente, podemos manejar el error aquí o dejarlo propagar
            raise e
    
    def get_expression_type(self, token: Token) -> DataType:
        """Determina el tipo de dato de un token literal o identificador"""
        if token.type == TokenType.INTEGER_LITERAL:
            return DataType.INT
        elif token.type == TokenType.FLOAT_LITERAL:
            return DataType.FLOAT
        elif token.type == TokenType.CHAR_LITERAL:
            return DataType.CHAR
        elif token.type == TokenType.ID:
            # Buscar el tipo en la tabla de símbolos
            variable = self.semantic_analyzer.check_variable_exists(
                token.value, 
                token.line, 
                token.column
            )
            return variable.type
        else:
            raise ParserError(
                f"No se puede determinar el tipo de '{token.value}'",
                token.line,
                token.column
            )
    
    def verify_variable_initialization(self, var_name: str, token: Token) -> None:
        """Verifica que una variable esté inicializada antes de su uso"""
        try:
            variable = self.semantic_analyzer.check_variable_exists(
                var_name,
                token.line,
                token.column
            )
            if not variable.initialized:
                raise SemanticError(
                    f"Variable '{var_name}' usada sin inicializar",
                    token.line,
                    token.column
                )
        except SemanticError as e:
            raise e
    
    # Implementación de expresiones (nivel más bajo)
    def expression(self) -> DataType:
        """Expression → LogicExpr"""
        return self.logic_expr()

    def logic_expr(self) -> DataType:
        """LogicExpr → CompExpr LogicExprTail"""
        expr_type = self.comp_expr()
        return self.logic_expr_tail(expr_type)

    def logic_expr_tail(self, left_type: DataType) -> DataType:
        """LogicExprTail → ('&&' | '||') CompExpr LogicExprTail | ε"""
        if self.match(TokenType.AND, TokenType.OR):
            operator = self.previous()
            right_type = self.comp_expr()
            
            # Verificar que ambos operandos sean de tipo INT
            self.verify_type_compatibility(DataType.INT, left_type, operator)
            self.verify_type_compatibility(DataType.INT, right_type, operator)
            
            # Expresiones lógicas siempre retornan INT
            result_type = DataType.INT
            return self.logic_expr_tail(result_type)
        return left_type

    def comp_expr(self) -> DataType:
        """CompExpr → AddExpr CompExprTail"""
        expr_type = self.add_expr()
        return self.comp_expr_tail(expr_type)

    def comp_expr_tail(self, left_type: DataType) -> DataType:
        """CompExprTail → ('==' | '!=' | '<' | '<=' | '>' | '>=') AddExpr CompExprTail | ε"""
        if self.match(TokenType.EQUALS, TokenType.NOT_EQUALS,
                    TokenType.LESS, TokenType.LESS_EQUAL,
                    TokenType.GREATER, TokenType.GREATER_EQUAL):
            operator = self.previous()
            right_type = self.add_expr()
            
            # Verificar compatibilidad de tipos
            if not self.semantic_analyzer.can_compare(left_type, right_type):
                raise SemanticError(
                    f"No se pueden comparar tipos {left_type.name} y {right_type.name}",
                    operator.line,
                    operator.column
                )
            
            # Comparaciones siempre retornan INT
            result_type = DataType.INT
            return self.comp_expr_tail(result_type)
        return left_type

    def add_expr(self) -> DataType:
        """AddExpr → MultExpr AddExprTail"""
        expr_type = self.mult_expr()
        return self.add_expr_tail(expr_type)

    def add_expr_tail(self, left_type: DataType) -> DataType:
        """AddExprTail → ('+' | '-') MultExpr AddExprTail | ε"""
        if self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right_type = self.mult_expr()
            
            # Obtener el tipo resultante de la operación
            result_type = self.semantic_analyzer.get_operation_type(
                left_type,
                operator.type,
                right_type,
                operator.line,
                operator.column
            )
            
            return self.add_expr_tail(result_type)
        return left_type

    def mult_expr(self) -> DataType:
        """MultExpr → Factor MultExprTail"""
        expr_type = self.factor()
        return self.mult_expr_tail(expr_type)

    def mult_expr_tail(self, left_type: DataType) -> DataType:
        """MultExprTail → ('*' | '/') Factor MultExprTail | ε"""
        if self.match(TokenType.TIMES, TokenType.DIVIDE):
            operator = self.previous()
            right_type = self.factor()
            
            result_type = self.semantic_analyzer.get_operation_type(
                left_type,
                operator.type,
                right_type,
                operator.line,
                operator.column
            )
            
            return self.mult_expr_tail(result_type)
        return left_type

    def factor(self) -> DataType:
        """
        Factor → '(' Expression ')'
            | ID FactorTail
            | INTEGER_LITERAL
            | FLOAT_LITERAL
            | CHAR_LITERAL
            | STRING_LITERAL
        """
        if self.match(TokenType.LPAREN):
            expr_type = self.expression()
            self.consume(TokenType.RPAREN, "Se esperaba ')'")
            return expr_type
            
        elif self.match(TokenType.ID):
            id_token = self.previous()
            # Verificar que la variable existe
            variable = self.semantic_analyzer.check_variable_exists(
                id_token.value,
                id_token.line,
                id_token.column
            )
            # Verificar si es una llamada a función
            if self.check(TokenType.LPAREN):
                return self.factor_tail(id_token)
            return variable.type
            
        elif self.match(TokenType.INTEGER_LITERAL):
            return DataType.INT
        elif self.match(TokenType.FLOAT_LITERAL):
            return DataType.FLOAT
        elif self.match(TokenType.CHAR_LITERAL):
            return DataType.CHAR
        elif self.match(TokenType.STRING_LITERAL):
            # Típicamente tratado como array de char o tipo especial
            return DataType.CHAR
            
        raise ParserError(
            "Se esperaba una expresión",
            self.peek().line,
            self.peek().column
        )

    def factor_tail(self, id_token: Token) -> DataType:
        """FactorTail → '(' ArgumentList ')' | ε"""
        if self.match(TokenType.LPAREN):
            arg_types = self.argument_list()
            self.consume(TokenType.RPAREN, "Se esperaba ')'")
            
            # Verificar la llamada a función
            return self.semantic_analyzer.check_function_call(
                id_token.value,
                arg_types,
                id_token.line,
                id_token.column
            )
        return DataType.VOID

    def argument_list(self) -> List[DataType]:
        """ArgumentList → Expression ArgumentListTail | ε"""
        arg_types = []
        if not self.check(TokenType.RPAREN):
            arg_types.append(self.expression())
            arg_types.extend(self.argument_list_tail())
        return arg_types

    def argument_list_tail(self) -> List[DataType]:
        """ArgumentListTail → ',' Expression ArgumentListTail | ε"""
        arg_types = []
        if self.match(TokenType.COMMA):
            arg_types.append(self.expression())
            arg_types.extend(self.argument_list_tail())
        return arg_types

    # Statements

    def statement(self) -> None:
        """
        Statement → DeclarationStmt
                 | AssignmentStmt
                 | FunctionCallStmt
                 | IfStmt
                 | WhileStmt
                 | DoWhileStmt
                 | ReturnStmt
                 | IOStmt
                 | CompoundStmt
                 | ';'
        """
        if self.is_type_token(self.peek()):
            self.declaration_stmt()
        elif self.check(TokenType.ID):
            if self.is_function_call():
                self.function_call_stmt()
            else:
                self.assignment_stmt()
        elif self.check(TokenType.IF):
            self.if_stmt()
        elif self.check(TokenType.WHILE):
            self.while_stmt()
        elif self.check(TokenType.DO):
            self.do_while_stmt()
        elif self.check(TokenType.RETURN):
            self.return_stmt()
        elif self.is_io_function(self.peek()):
            self.io_stmt()
        elif self.check(TokenType.LBRACE):
            self.compound_stmt()
        elif self.match(TokenType.SEMICOLON):
            pass  # Statement vacío
        else:
            raise ParserError(
                "Se esperaba el inicio de una declaración",
                self.peek().line,
                self.peek().column
            )

    def type(self) -> None:
        """Type → 'int' | 'char' | 'float' | 'void'"""
        if not self.match(TokenType.INT, TokenType.CHAR, TokenType.FLOAT, TokenType.VOID):
            raise ParserError(
                "Se esperaba un tipo de dato (int, char, float, void)",
                self.peek().line,
                self.peek().column
            )

    def declaration_stmt(self) -> None:
        """DeclarationStmt → Type ID ['=' Expression] ';'"""
        self.type()  # Consume el tipo
        id_token = self.consume(TokenType.ID, "Se esperaba un identificador")
        
        # Inicialización opcional
        if self.match(TokenType.ASSIGN):
            self.expression()
        
        self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de la declaración")

    def assignment_stmt(self) -> None:
        """AssignmentStmt → ID '=' Expression ';'"""
        self.consume(TokenType.ID, "Se esperaba un identificador")
        self.consume(TokenType.ASSIGN, "Se esperaba '=' después del identificador")
        self.expression()
        self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de la asignación")

    def if_stmt(self) -> None:
        """IfStmt → 'if' '(' Expression ')' Statement ['else' Statement]"""
        self.consume(TokenType.IF, "Se esperaba 'if'")
        self.consume(TokenType.LPAREN, "Se esperaba '(' después de 'if'")
        self.expression()
        self.consume(TokenType.RPAREN, "Se esperaba ')' después de la condición")
        self.statement()
        
        # Parte else opcional
        if self.match(TokenType.ELSE):
            self.statement()

    def while_stmt(self) -> None:
        """WhileStmt → 'while' '(' Expression ')' Statement"""
        self.consume(TokenType.WHILE, "Se esperaba 'while'")
        self.consume(TokenType.LPAREN, "Se esperaba '(' después de 'while'")
        self.expression()
        self.consume(TokenType.RPAREN, "Se esperaba ')' después de la condición")
        self.statement()

    def do_while_stmt(self) -> None:
        """DoWhileStmt → 'do' Statement 'while' '(' Expression ')' ';'"""
        self.consume(TokenType.DO, "Se esperaba 'do'")
        self.statement()
        self.consume(TokenType.WHILE, "Se esperaba 'while'")
        self.consume(TokenType.LPAREN, "Se esperaba '(' después de 'while'")
        self.expression()
        self.consume(TokenType.RPAREN, "Se esperaba ')' después de la condición")
        self.consume(TokenType.SEMICOLON, "Se esperaba ';' después del do-while")

    def return_stmt(self) -> None:
        """ReturnStmt → 'return' [Expression] ';'"""
        self.consume(TokenType.RETURN, "Se esperaba 'return'")
        
        # Expresión opcional
        if not self.check(TokenType.SEMICOLON):
            self.expression()
            
        self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de return")
    
    def function(self) -> None:
        """Function → Type ID '(' ParameterList ')' CompoundStmt"""
        # Obtener tipo de retorno
        return_type = self.get_data_type(self.peek().type)
        self.type()  # Consume el tipo
        
        # Obtener nombre de la función
        function_name = self.consume(TokenType.ID, 
            "Se esperaba un nombre de función")
        
        # Registrar la función y entrar en su ámbito
        self.semantic_analyzer.enter_function(
            return_type,
            function_name.value,
            function_name.line,
            function_name.column
        )
        
        self.consume(TokenType.LPAREN, 
            f"Se esperaba '(' después de '{function_name.value}'")
        self.parameter_list()
        self.consume(TokenType.RPAREN, 
            "Se esperaba ')' después de los parámetros")
        
        # Procesar el cuerpo de la función
        self.compound_stmt()
        
        # Salir del ámbito de la función
        self.semantic_analyzer.exit_function()

    def parameter_list(self) -> None:
        """ParameterList → Parameter ParameterListTail | ε"""
        if self.is_type_token(self.peek()):
            self.parameter()
            self.parameter_list_tail()

    def parameter(self) -> None:
        """Parameter → Type ID"""
        self.type()
        self.consume(TokenType.ID, "Se esperaba un nombre de parámetro")

    def parameter_list_tail(self) -> None:
        """ParameterListTail → ',' Parameter ParameterListTail | ε"""
        if self.match(TokenType.COMMA):
            self.parameter()
            self.parameter_list_tail()

    def expression(self) -> None:
        """Expression → LogicExpr"""
        if self.check(TokenType.SCAN_INT) or self.check(TokenType.SCAN_FLOAT) or \
           self.check(TokenType.SCAN_CHAR):
            # Manejar funciones de scan como expresiones
            self.advance()  # Consumir el token de scan
            self.consume(TokenType.LPAREN, "Se esperaba '(' después de la función scan")
            self.consume(TokenType.RPAREN, "Se esperaba ')' después de scan")
        else:
            # Continuar con el análisis normal de expresiones
            self.logic_expr()

    def io_stmt(self) -> None:
        """
        IOStmt → PrintStmt | ScanStmt
        PrintStmt → PrintFunction '(' Expression ')' ';'
        ScanStmt → ScanFunction '(' ')' ';'
        """
        io_token = self.advance()  # Consumir el token de I/O
        
        self.consume(TokenType.LPAREN, f"Se esperaba '(' después de {io_token.value}")
        
        # Las funciones print requieren una expresión, las scan no
        if io_token.type in {TokenType.PRINT_INT, TokenType.PRINT_FLOAT,
                           TokenType.PRINT_CHAR, TokenType.PRINT_STR}:
            self.expression()
            
        self.consume(TokenType.RPAREN, f"Se esperaba ')' después de {io_token.value}")
        self.consume(TokenType.SEMICOLON, f"Se esperaba ';' después de {io_token.value}")

    def compound_stmt(self) -> None:
        """CompoundStmt → '{' {Statement} '}'"""
        self.consume(TokenType.LBRACE, "Se esperaba '{'")
        
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            self.statement()
            
        self.consume(TokenType.RBRACE, "Se esperaba '}'")

    def return_stmt(self) -> None:
        """ReturnStmt → 'return' [Expression] ';'"""
        self.consume(TokenType.RETURN, "Se esperaba 'return'")
        
        # Expresión opcional
        if not self.check(TokenType.SEMICOLON):
            self.expression()
            
        self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de return")
    
    # Métodos auxiliares
    def is_type_token(self, token: Token) -> bool:
        """Verifica si el token es un tipo de dato"""
        return token.type in {
            TokenType.INT,
            TokenType.CHAR,
            TokenType.FLOAT,
            TokenType.VOID
        }

    def is_print_token(self, token: Token) -> bool:
        """Verifica si el token es una función de impresión"""
        return token.type in {
            TokenType.PRINT_INT,
            TokenType.PRINT_FLOAT,
            TokenType.PRINT_CHAR,
            TokenType.PRINT_STR
        }

    def is_io_function(self, token: Token) -> bool:
        """Verifica si el token es una función de I/O"""
        return token.type in {
            TokenType.PRINT_INT, TokenType.PRINT_FLOAT,
            TokenType.PRINT_CHAR, TokenType.PRINT_STR,
            TokenType.SCAN_INT, TokenType.SCAN_FLOAT,
            TokenType.SCAN_CHAR
        }

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
