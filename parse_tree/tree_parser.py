from typing import List, Optional
from lexer.token import Token
from lexer.token_type import TokenType
from semantic.analyzer import SemanticAnalyzer
from semantic.types import DataType
from utils.error_handler import ParserError, SemanticError
from parse_tree.parse_tree import ParseTree

class TreeParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.has_main_function = False
        self.semantic_analyzer = SemanticAnalyzer()
        self.tree = ParseTree()
    
    def parse(self) -> ParseTree:
        """
        Punto de entrada principal del parser.
        """
        try:
            self.tree.set_root("Program")
            self.program()
            return self.tree
        except ParserError as e:
            raise e
        except Exception as e:
            current_token = self.peek()
            raise ParserError(str(e), current_token.line, current_token.column)

    # Program and functions

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
            globals_node = self.tree.add_child("GlobalDeclaration")
            self.tree.move_to(globals_node)
            self.global_declaration()
            self.tree.move_to_parent()

        # Procesar funciones
        functions_node = self.tree.add_child("FunctionList")
        self.tree.move_to(functions_node)
        self.function_list()
        self.tree.move_to_parent()

        # Verificar que existe una función main
        if not self.has_main_function:
            raise ParserError(
                "No se encontró la función 'main'",
                self.previous().line,
                self.previous().column
            )

    def function_list(self) -> None:
        """FunctionList → Function FunctionList | ε"""
        while not self.is_at_end():
            if self.is_function_declaration():
                function_node = self.tree.add_child("Function")
                self.tree.move_to(function_node)
                
                # Verificar si es la función main
                if self.is_main_function():
                    self.has_main_function = True
                    self.tree.add_child("MainFunction")
                
                self.function()
                self.tree.move_to_parent()
            else:
                break

    # Global declarations

    def global_declaration(self) -> None:
        """GlobalDeclaration → Type ID ['=' Expression] ';'"""
        # Obtener el tipo
        type_token = self.peek()
        data_type = self.get_data_type(type_token.type)
        self.tree.add_child("Type", type_token)
        self.type()  # Consume el tipo
        
        # Consumir el identificador
        id_token = self.consume(TokenType.ID, 
            f"Se esperaba un identificador después de '{type_token.value}'")
        self.tree.add_child("Identifier", id_token)
        
        initialized = False
        
        # Inicialización opcional
        if self.match(TokenType.ASSIGN):
            assign_node = self.tree.add_child("Assignment")
            self.tree.move_to(assign_node)
            expr_type = self.expression()
            self.tree.move_to_parent()
            
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
        semicolon_token = self.consume(TokenType.SEMICOLON, 
            f"Se esperaba ';' después de la declaración de '{id_token.value}'")
        self.tree.add_child("Semicolon", semicolon_token)

    def function_call_stmt(self) -> None:
        """FunctionCallStmt → ID '(' ArgumentList ')' ';'"""
        call_node = self.tree.add_child("FunctionCall")
        self.tree.move_to(call_node)
        
        id_token = self.consume(TokenType.ID, "Se esperaba un identificador")
        self.tree.add_child("Identifier", id_token)
        
        self.consume(TokenType.LPAREN, "Se esperaba '(' después del identificador")
        
        # Añadir nodo para lista de argumentos
        args_node = self.tree.add_child("ArgumentList")
        self.tree.move_to(args_node)
        arg_types = self.argument_list()
        self.tree.move_to_parent()
        
        self.semantic_analyzer.check_function_call(
            id_token.value,
            arg_types,
            id_token.line,
            id_token.column
        )
        
        self.consume(TokenType.RPAREN, "Se esperaba ')'")
        self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de la llamada a función")
        
        self.tree.move_to_parent()

    # Helper methods

    def is_main_function(self) -> bool:
        """Verifica si la siguiente función es main()"""
        if not self.is_type_token(self.peek()):
            return False
        
        saved_pos = self.current
        try:
            self.advance()  # tipo
            if not self.check(TokenType.ID):
                return False
            return self.peek().value == "main"
        finally:
            self.current = saved_pos

    def is_global_declaration(self) -> bool:
        if not self.is_type_token(self.peek()):
            return False
        
        saved_pos = self.current
        try:
            self.advance()  # tipo
            if not self.check(TokenType.ID):
                return False
            self.advance()  # identificador
            return not self.check(TokenType.LPAREN)
        finally:
            self.current = saved_pos

    def is_function_declaration(self) -> bool:
        if not self.is_type_token(self.peek()):
            return False
        
        saved_pos = self.current
        try:
            self.advance()  # tipo
            if not self.check(TokenType.ID):
                return False
            self.advance()  # identificador
            return self.check(TokenType.LPAREN)
        finally:
            self.current = saved_pos

    def is_function_call(self) -> bool:
        if not self.check(TokenType.ID):
            return False

        saved_pos = self.current
        try:
            self.advance()  # identificador
            return self.check(TokenType.LPAREN)
        finally:
            self.current = saved_pos

    def is_statement_start(self) -> bool:
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

    # Parsers utilities

    def synchronize(self) -> None:
        """Sincroniza el parser y el analizador semántico después de un error"""
        # Crear nodo de error en el árbol
        error_node = self.tree.add_child("SyntaxError")
        self.tree.move_to(error_node)
        
        self.advance()
        
        # Sincronización sintáctica
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                # Si encontramos el fin de una declaración, podemos recuperarnos
                self.semantic_analyzer.synchronize()
                self.tree.add_child("RecoverySemicolon", self.previous())
                self.tree.move_to_parent()
                return

            if self.peek().type in {
                TokenType.INT, TokenType.CHAR, TokenType.FLOAT, TokenType.VOID,
                TokenType.IF, TokenType.WHILE, TokenType.DO, TokenType.RETURN
            }:
                # Si encontramos el inicio de una nueva construcción
                self.semantic_analyzer.synchronize()
                self.tree.add_child("RecoveryKeyword", self.peek())
                self.tree.move_to_parent()
                return

            self.advance()
            
        # Si llegamos aquí, intentar recuperarse con el programa
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
        finally:
            self.tree.move_to_parent()

    def verify_type_compatibility(self, expected: DataType, found: DataType, token: Token) -> None:
        """Verifica la compatibilidad de tipos usando el analizador semántico"""
        try:
            self.semantic_analyzer.check_types(expected, found, token.line, token.column)
        except SemanticError as e:
            # Añadir nodo de error de tipo al árbol
            type_error_node = self.tree.add_child("TypeError")
            self.tree.add_child("Expected", Token(None, expected.name, token.line, token.column))
            self.tree.add_child("Found", Token(None, found.name, token.line, token.column))
            raise e

    def get_expression_type(self, token: Token) -> DataType:
        """Determina el tipo de dato de un token literal o identificador"""
        if token.type == TokenType.INTEGER_LITERAL:
            self.tree.add_child("IntegerLiteral", token)
            return DataType.INT
        elif token.type == TokenType.FLOAT_LITERAL:
            self.tree.add_child("FloatLiteral", token)
            return DataType.FLOAT
        elif token.type == TokenType.CHAR_LITERAL:
            self.tree.add_child("CharLiteral", token)
            return DataType.CHAR
        elif token.type == TokenType.ID:
            id_node = self.tree.add_child("Identifier", token)
            # Buscar el tipo en la tabla de símbolos
            variable = self.semantic_analyzer.check_variable_exists(
                token.value, 
                token.line, 
                token.column
            )
            self.tree.add_child("Type", Token(None, variable.type.name, token.line, token.column))
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
                # Añadir nodo de error de inicialización al árbol
                init_error_node = self.tree.add_child("InitializationError")
                self.tree.add_child("Variable", token)
                raise SemanticError(
                    f"Variable '{var_name}' usada sin inicializar",
                    token.line,
                    token.column
                )
        except SemanticError as e:
            raise e

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

    # Expressions

    def expression(self) -> DataType:
        """Expression → LogicExpr"""
        expr_node = self.tree.add_child("Expression")
        self.tree.move_to(expr_node)
        
        try:
            if self.check(TokenType.SCAN_INT) or self.check(TokenType.SCAN_FLOAT) or \
            self.check(TokenType.SCAN_CHAR):
                scan_node = self.tree.add_child("ScanOperation")
                self.tree.move_to(scan_node)
                
                scan_token = self.advance()
                self.tree.add_child("ScanFunction", scan_token)
                self.consume(TokenType.LPAREN, "Se esperaba '(' después de la función scan")
                self.consume(TokenType.RPAREN, "Se esperaba ')' después de scan")
                
                scan_types = {
                    TokenType.SCAN_INT: DataType.INT,
                    TokenType.SCAN_FLOAT: DataType.FLOAT,
                    TokenType.SCAN_CHAR: DataType.CHAR
                }
                
                # Marcar que este es un valor válido de inicialización
                scan_type = scan_types[scan_token.type]
                self.tree.add_child("ReturnType", Token(None, scan_type.name, scan_token.line, scan_token.column))
                
                self.tree.move_to_parent()
                self.tree.move_to_parent()
                return scan_type
            else:
                result_type = self.logic_expr()
                self.tree.move_to_parent()
                return result_type
        except:
            self.tree.move_to_parent()
            raise

    def logic_expr(self) -> DataType:
        """LogicExpr → CompExpr LogicExprTail"""
        logic_node = self.tree.add_child("LogicExpr")
        self.tree.move_to(logic_node)
        
        try:
            expr_type = self.comp_expr()
            result_type = self.logic_expr_tail(expr_type)
            self.tree.move_to_parent()
            return result_type
        except:
            self.tree.move_to_parent()
            raise

    def logic_expr_tail(self, left_type: DataType) -> DataType:
        """LogicExprTail → ('&&' | '||') CompExpr LogicExprTail | ε"""
        if self.match(TokenType.AND, TokenType.OR):
            tail_node = self.tree.add_child("LogicOperation")
            self.tree.move_to(tail_node)
            
            operator = self.previous()
            self.tree.add_child("Operator", operator)
            
            right_type = self.comp_expr()
            
            # Verificar tipos
            self.verify_type_compatibility(DataType.INT, left_type, operator)
            self.verify_type_compatibility(DataType.INT, right_type, operator)
            
            result_type = DataType.INT
            final_type = self.logic_expr_tail(result_type)
            
            self.tree.move_to_parent()
            return final_type
        return left_type

    def comp_expr(self) -> DataType:
        """CompExpr → AddExpr CompExprTail"""
        comp_node = self.tree.add_child("CompExpr")
        self.tree.move_to(comp_node)
        
        try:
            expr_type = self.add_expr()
            result_type = self.comp_expr_tail(expr_type)
            self.tree.move_to_parent()
            return result_type
        except:
            self.tree.move_to_parent()
            raise

    def comp_expr_tail(self, left_type: DataType) -> DataType:
        """CompExprTail → ('==' | '!=' | '<' | '<=' | '>' | '>=') AddExpr CompExprTail | ε"""
        if self.match(TokenType.EQUALS, TokenType.NOT_EQUALS,
                    TokenType.LESS, TokenType.LESS_EQUAL,
                    TokenType.GREATER, TokenType.GREATER_EQUAL):
            
            tail_node = self.tree.add_child("ComparisonOperation")
            self.tree.move_to(tail_node)
            
            operator = self.previous()
            self.tree.add_child("Operator", operator)
            
            right_type = self.add_expr()
            
            if not self.semantic_analyzer.can_compare(left_type, right_type):
                error_node = self.tree.add_child("TypeError")
                self.tree.add_child("Message", Token(None, 
                    f"No se pueden comparar tipos {left_type.name} y {right_type.name}",
                    operator.line, operator.column))
                raise SemanticError(
                    f"No se pueden comparar tipos {left_type.name} y {right_type.name}",
                    operator.line,
                    operator.column
                )
            
            result_type = DataType.INT
            final_type = self.comp_expr_tail(result_type)
            
            self.tree.move_to_parent()
            return final_type
        return left_type

    def add_expr(self) -> DataType:
        """AddExpr → MultExpr AddExprTail"""
        add_node = self.tree.add_child("AddExpr")
        self.tree.move_to(add_node)
        
        try:
            expr_type = self.mult_expr()
            result_type = self.add_expr_tail(expr_type)
            self.tree.move_to_parent()
            return result_type
        except:
            self.tree.move_to_parent()
            raise

    def add_expr_tail(self, left_type: DataType) -> DataType:
        """AddExprTail → ('+' | '-') MultExpr AddExprTail | ε"""
        if self.match(TokenType.PLUS, TokenType.MINUS):
            tail_node = self.tree.add_child("AddOperation")
            self.tree.move_to(tail_node)
            
            operator = self.previous()
            self.tree.add_child("Operator", operator)
            
            right_type = self.mult_expr()
            
            result_type = self.semantic_analyzer.get_operation_type(
                left_type,
                operator.type,
                right_type,
                operator.line,
                operator.column
            )
            
            final_type = self.add_expr_tail(result_type)
            
            self.tree.move_to_parent()
            return final_type
        return left_type

    def mult_expr(self) -> DataType:
        """MultExpr → Factor MultExprTail"""
        mult_node = self.tree.add_child("MultExpr")
        self.tree.move_to(mult_node)
        
        try:
            expr_type = self.factor()
            result_type = self.mult_expr_tail(expr_type)
            self.tree.move_to_parent()
            return result_type
        except:
            self.tree.move_to_parent()
            raise

    def mult_expr_tail(self, left_type: DataType) -> DataType:
        """MultExprTail → ('*' | '/') Factor MultExprTail | ε"""
        if self.match(TokenType.TIMES, TokenType.DIVIDE):
            tail_node = self.tree.add_child("MultOperation")
            self.tree.move_to(tail_node)
            
            operator = self.previous()
            self.tree.add_child("Operator", operator)
            
            right_type = self.factor()
            
            result_type = self.semantic_analyzer.get_operation_type(
                left_type,
                operator.type,
                right_type,
                operator.line,
                operator.column
            )
            
            final_type = self.mult_expr_tail(result_type)
            
            self.tree.move_to_parent()
            return final_type
        return left_type

    def factor(self) -> DataType:
        """Factor → '(' Expression ')' | ID FactorTail | INTEGER_LITERAL | FLOAT_LITERAL | CHAR_LITERAL | STRING_LITERAL"""
        factor_node = self.tree.add_child("Factor")
        self.tree.move_to(factor_node)
        
        try:
            if self.match(TokenType.LPAREN):
                self.tree.add_child("LeftParen", self.previous())
                expr_type = self.expression()
                self.tree.add_child("RightParen", self.consume(TokenType.RPAREN, "Se esperaba ')'"))
                self.tree.move_to_parent()
                return expr_type
                
            elif self.match(TokenType.ID):
                id_token = self.previous()
                id_node = self.tree.add_child("Identifier", id_token)
                
                if self.check(TokenType.LPAREN):
                    return self.factor_tail(id_token)
                else:
                    variable = self.semantic_analyzer.check_variable_exists(
                        id_token.value,
                        id_token.line,
                        id_token.column
                    )
                    if not variable.initialized:
                        error_node = self.tree.add_child("InitializationError")
                        self.tree.add_child("Message", Token(None,
                            f"Variable '{id_token.value}' usada sin inicializar",
                            id_token.line, id_token.column))
                        raise SemanticError(
                            f"Variable '{id_token.value}' usada sin inicializar",
                            id_token.line,
                            id_token.column
                        )
                    self.tree.move_to_parent()
                    return variable.type
                    
            elif self.match(TokenType.INTEGER_LITERAL, TokenType.FLOAT_LITERAL,
                        TokenType.CHAR_LITERAL, TokenType.STRING_LITERAL):
                token = self.previous()
                literal_type = {
                    TokenType.INTEGER_LITERAL: ("IntegerLiteral", DataType.INT),
                    TokenType.FLOAT_LITERAL: ("FloatLiteral", DataType.FLOAT),
                    TokenType.CHAR_LITERAL: ("CharLiteral", DataType.CHAR),
                    TokenType.STRING_LITERAL: ("StringLiteral", DataType.CHAR)
                }[token.type]
                
                self.tree.add_child(literal_type[0], token)
                self.tree.move_to_parent()
                return literal_type[1]
                
            raise ParserError(
                "Se esperaba una expresión",
                self.peek().line,
                self.peek().column
            )
        except:
            self.tree.move_to_parent()
            raise

    def factor_tail(self, id_token: Token) -> DataType:
        """FactorTail → '(' ArgumentList ')' | ε"""
        tail_node = self.tree.add_child("FunctionCall")
        self.tree.move_to(tail_node)
        
        try:
            if self.match(TokenType.LPAREN):
                args_node = self.tree.add_child("Arguments")
                self.tree.move_to(args_node)
                
                arg_types = self.argument_list()
                self.consume(TokenType.RPAREN, "Se esperaba ')'")
                
                return_type = self.semantic_analyzer.check_function_call(
                    id_token.value,
                    arg_types,
                    id_token.line,
                    id_token.column
                )
                
                self.tree.move_to_parent()
                self.tree.move_to_parent()
                return return_type
                
            self.tree.move_to_parent()
            return DataType.VOID
        except:
            self.tree.move_to_parent()
            raise

    def argument_list(self) -> List[DataType]:
        """ArgumentList → Expression ArgumentListTail | ε"""
        args_node = self.tree.add_child("ArgumentList")
        self.tree.move_to(args_node)
        
        try:
            arg_types = []
            if not self.check(TokenType.RPAREN):
                # Primer argumento
                arg_node = self.tree.add_child("Argument")
                self.tree.move_to(arg_node)
                expr_type = self.expression()
                arg_types.append(expr_type)
                self.tree.move_to_parent()
                
                # Argumentos adicionales
                while self.match(TokenType.COMMA):
                    self.tree.add_child("Comma", self.previous())
                    arg_node = self.tree.add_child("Argument")
                    self.tree.move_to(arg_node)
                    expr_type = self.expression()
                    arg_types.append(expr_type)
                    self.tree.move_to_parent()
            
            self.tree.move_to_parent()
            return arg_types
        except:
            self.tree.move_to_parent()
            raise

    def argument_list_tail(self) -> List[DataType]:
        """ArgumentListTail → ',' Expression ArgumentListTail | ε"""
        tail_node = self.tree.add_child("ArgumentListTail")
        self.tree.move_to(tail_node)
        
        try:
            arg_types = []
            if self.match(TokenType.COMMA):
                self.tree.add_child("Comma", self.previous())
                arg_node = self.tree.add_child("Argument")
                self.tree.move_to(arg_node)
                
                expr_type = self.expression()
                arg_types.append(expr_type)
                
                self.tree.move_to_parent()
                arg_types.extend(self.argument_list_tail())
            
            self.tree.move_to_parent()
            return arg_types
        except:
            self.tree.move_to_parent()
            raise

    # Main Statements

    def statement(self) -> None:
        """
        Statement → DeclarationStmt | AssignmentStmt | FunctionCallStmt | IfStmt | 
                    WhileStmt | DoWhileStmt | ReturnStmt | IOStmt | CompoundStmt | ';'
        """
        stmt_node = self.tree.add_child("Statement")
        self.tree.move_to(stmt_node)
        
        try:
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
                self.tree.add_child("EmptyStatement", self.previous())
            else:
                raise ParserError(
                    "Se esperaba el inicio de una declaración",
                    self.peek().line,
                    self.peek().column
                )
            self.tree.move_to_parent()
        except:
            self.tree.move_to_parent()
            raise

    def type(self) -> None:
        """Type → 'int' | 'char' | 'float' | 'void'"""
        if not self.match(TokenType.INT, TokenType.CHAR, TokenType.FLOAT, TokenType.VOID):
            raise ParserError(
                "Se esperaba un tipo de dato (int, char, float, void)",
                self.peek().line,
                self.peek().column
            )
        self.tree.add_child("Type", self.previous())

    def declaration_stmt(self) -> None:
        """DeclarationStmt → Type ID ['=' Expression] ';'"""
        decl_node = self.tree.add_child("Declaration")
        self.tree.move_to(decl_node)
        
        try:
            # Tipo
            type_token = self.peek()
            data_type = self.get_data_type(type_token.type)
            self.type()
            
            # Identificador
            id_token = self.consume(TokenType.ID, "Se esperaba un identificador")
            self.tree.add_child("Identifier", id_token)
            
            initialized = False
            
            # Inicialización opcional
            if self.match(TokenType.ASSIGN):
                init_node = self.tree.add_child("Initialization")
                self.tree.move_to(init_node)
                expr_type = self.expression()
                self.tree.move_to_parent()
                
                if expr_type is None:
                    raise SemanticError(
                        "No se pudo determinar el tipo de la expresión",
                        id_token.line,
                        id_token.column
                    )
                self.semantic_analyzer.check_types(data_type, expr_type, id_token.line, id_token.column)
                initialized = True
                
            # Registrar en análisis semántico
            self.semantic_analyzer.declare_variable(
                data_type,
                id_token.value,
                initialized,
                id_token.line,
                id_token.column
            )
            
            self.tree.add_child("Semicolon", 
                self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de la declaración"))
            
            self.tree.move_to_parent()
        except:
            self.tree.move_to_parent()
            raise

    def assignment_stmt(self) -> None:
        """AssignmentStmt → ID '=' Expression ';'"""
        assign_node = self.tree.add_child("Assignment")
        self.tree.move_to(assign_node)
        
        try:
            # Identificador
            id_token = self.consume(TokenType.ID, "Se esperaba un identificador")
            self.tree.add_child("Identifier", id_token)
            
            # Operador de asignación
            assign_token = self.consume(TokenType.ASSIGN, "Se esperaba '=' después del identificador")
            self.tree.add_child("Operator", assign_token)
            
            # Verificar que la variable existe
            variable = self.semantic_analyzer.check_variable_exists(
                id_token.value,
                id_token.line,
                id_token.column
            )
            
            # Expresión
            expr_node = self.tree.add_child("Expression")
            self.tree.move_to(expr_node)
            expr_type = self.expression()
            self.tree.move_to_parent()
            
            if expr_type is None:
                error_node = self.tree.add_child("TypeError")
                self.tree.add_child("Message", Token(None,
                    "No se pudo determinar el tipo de la expresión",
                    id_token.line, id_token.column))
                raise SemanticError(
                    "No se pudo determinar el tipo de la expresión",
                    id_token.line,
                    id_token.column
                )
            
            # Verificar compatibilidad de tipos
            self.semantic_analyzer.check_types(
                variable.type,
                expr_type,
                id_token.line,
                id_token.column
            )
            
            # Marcar la variable como inicializada después de la asignación con scan
            variable.initialized = True
            
            # Punto y coma
            semicolon_token = self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de la asignación")
            self.tree.add_child("Semicolon", semicolon_token)
            
            self.tree.move_to_parent()
        except:
            self.tree.move_to_parent()
            raise

    # Control Flow Statements

    def if_stmt(self) -> None:
        """IfStmt → 'if' '(' Expression ')' Statement ['else' Statement]"""
        if_node = self.tree.add_child("IfStatement")
        self.tree.move_to(if_node)
        
        try:
            if_token = self.consume(TokenType.IF, "Se esperaba 'if'")
            self.tree.add_child("If", if_token)
            self.consume(TokenType.LPAREN, "Se esperaba '(' después de 'if'")
            
            # Condición
            cond_node = self.tree.add_child("Condition")
            self.tree.move_to(cond_node)
            cond_type = self.expression()
            self.tree.move_to_parent()
            
            self.semantic_analyzer.check_condition(cond_type, if_token.line, if_token.column)
            self.consume(TokenType.RPAREN, "Se esperaba ')' después de la condición")
            
            # Bloque then
            then_node = self.tree.add_child("Then")
            self.tree.move_to(then_node)
            self.semantic_analyzer.enter_scope()
            self.statement()
            self.semantic_analyzer.exit_scope()
            self.tree.move_to_parent()
            
            # Bloque else opcional
            if self.match(TokenType.ELSE):
                else_node = self.tree.add_child("Else")
                self.tree.move_to(else_node)
                self.semantic_analyzer.enter_scope()
                self.statement()
                self.semantic_analyzer.exit_scope()
                self.tree.move_to_parent()
            
            self.tree.move_to_parent()
        except:
            self.tree.move_to_parent()
            raise

    def while_stmt(self) -> None:
        """WhileStmt → 'while' '(' Expression ')' Statement"""
        while_node = self.tree.add_child("WhileStatement")
        self.tree.move_to(while_node)
        
        try:
            while_token = self.consume(TokenType.WHILE, "Se esperaba 'while'")
            self.tree.add_child("While", while_token)
            self.consume(TokenType.LPAREN, "Se esperaba '(' después de 'while'")
            
            # Condición
            cond_node = self.tree.add_child("Condition")
            self.tree.move_to(cond_node)
            cond_type = self.expression()
            self.tree.move_to_parent()
            
            self.semantic_analyzer.check_condition(cond_type, while_token.line, while_token.column)
            self.consume(TokenType.RPAREN, "Se esperaba ')' después de la condición")
            
            # Cuerpo
            body_node = self.tree.add_child("Body")
            self.tree.move_to(body_node)
            self.semantic_analyzer.enter_scope()
            self.statement()
            self.semantic_analyzer.exit_scope()
            self.tree.move_to_parent()
            
            self.tree.move_to_parent()
        except:
            self.tree.move_to_parent()
            raise

    def do_while_stmt(self) -> None:
        """DoWhileStmt → 'do' Statement 'while' '(' Expression ')' ';'"""
        do_while_node = self.tree.add_child("DoWhileStatement")
        self.tree.move_to(do_while_node)
        
        try:
            do_token = self.consume(TokenType.DO, "Se esperaba 'do'")
            self.tree.add_child("Do", do_token)
            
            # Cuerpo
            body_node = self.tree.add_child("Body")
            self.tree.move_to(body_node)
            self.semantic_analyzer.enter_scope()
            self.statement()
            self.semantic_analyzer.exit_scope()
            self.tree.move_to_parent()
            
            self.consume(TokenType.WHILE, "Se esperaba 'while'")
            self.consume(TokenType.LPAREN, "Se esperaba '(' después de 'while'")
            
            # Condición
            cond_node = self.tree.add_child("Condition")
            self.tree.move_to(cond_node)
            cond_type = self.expression()
            self.tree.move_to_parent()
            
            self.semantic_analyzer.check_condition(cond_type, do_token.line, do_token.column)
            
            self.consume(TokenType.RPAREN, "Se esperaba ')' después de la condición")
            self.tree.add_child("Semicolon", 
                self.consume(TokenType.SEMICOLON, "Se esperaba ';' después del do-while"))
            
            self.tree.move_to_parent()
        except:
            self.tree.move_to_parent()
            raise

    #Function and Return Statements

    def function(self) -> None:
        """Function → Type ID '(' ParameterList ')' CompoundStmt"""
        func_node = self.tree.add_child("Function")
        self.tree.move_to(func_node)
        
        try:
            # Tipo de retorno
            return_type = self.get_data_type(self.peek().type)
            self.type()
            
            # Nombre de la función
            function_name = self.consume(TokenType.ID, "Se esperaba un nombre de función")
            self.tree.add_child("FunctionName", function_name)
            
            self.semantic_analyzer.enter_function(
                return_type,
                function_name.value,
                function_name.line,
                function_name.column
            )
            
            self.consume(TokenType.LPAREN, f"Se esperaba '(' después de '{function_name.value}'")
            
            # Parámetros
            params_node = self.tree.add_child("Parameters")
            self.tree.move_to(params_node)
            self.parameter_list()
            self.tree.move_to_parent()
            
            self.consume(TokenType.RPAREN, "Se esperaba ')' después de los parámetros")
            
            # Cuerpo
            body_node = self.tree.add_child("Body")
            self.tree.move_to(body_node)
            self.compound_stmt()
            self.tree.move_to_parent()
            
            self.semantic_analyzer.exit_function()
            self.tree.move_to_parent()
        except:
            self.tree.move_to_parent()
            raise

    def return_stmt(self) -> None:
        """ReturnStmt → 'return' [Expression] ';'"""
        return_node = self.tree.add_child("ReturnStatement")
        self.tree.move_to(return_node)
        
        try:
            return_token = self.consume(TokenType.RETURN, "Se esperaba 'return'")
            self.tree.add_child("Return", return_token)
            
            # Expresión opcional
            return_type = None
            if not self.check(TokenType.SEMICOLON):
                expr_node = self.tree.add_child("ReturnValue")
                self.tree.move_to(expr_node)
                return_type = self.expression()
                self.tree.move_to_parent()
            
            self.semantic_analyzer.check_return(return_type, return_token.line, return_token.column)
            self.semantic_analyzer.has_return = True
            
            self.tree.add_child("Semicolon", 
                self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de return"))
            
            self.tree.move_to_parent()
        except:
            self.tree.move_to_parent()
            raise

    def parameter_list(self) -> None:
        """ParameterList → Parameter ParameterListTail | ε"""
        params_node = self.tree.add_child("ParameterList")
        self.tree.move_to(params_node)
        
        try:
            if self.is_type_token(self.peek()):
                self.parameter()
                self.parameter_list_tail()
            self.tree.move_to_parent()
        except:
            self.tree.move_to_parent()
            raise

    def parameter(self) -> None:
        """Parameter → Type ID"""
        param_node = self.tree.add_child("Parameter")
        self.tree.move_to(param_node)
        
        try:
            # Tipo del parámetro
            param_type = self.get_data_type(self.peek().type)
            self.type()
            
            # Nombre del parámetro
            param_token = self.consume(TokenType.ID, "Se esperaba un nombre de parámetro")
            self.tree.add_child("Identifier", param_token)
            
            # Registrar el parámetro
            self.semantic_analyzer.add_parameter(
                param_type,
                param_token.value,
                param_token.line,
                param_token.column
            )
            
            self.tree.move_to_parent()
        except:
            self.tree.move_to_parent()
            raise

    def parameter_list_tail(self) -> None:
        """ParameterListTail → ',' Parameter ParameterListTail | ε"""
        if self.match(TokenType.COMMA):
            self.tree.add_child("Comma", self.previous())
            self.parameter()
            self.parameter_list_tail()

    # I/O and Compound Statements

    def io_stmt(self) -> None:
        """IOStmt → PrintStmt | ScanStmt"""
        io_node = self.tree.add_child("IOStatement")
        self.tree.move_to(io_node)
        
        try:
            io_token = self.advance()
            self.tree.add_child("IOFunction", io_token)
            self.consume(TokenType.LPAREN, f"Se esperaba '(' después de {io_token.value}")
            
            if io_token.type in {TokenType.PRINT_INT, TokenType.PRINT_FLOAT,
                            TokenType.PRINT_CHAR, TokenType.PRINT_STR}:
                value_node = self.tree.add_child("Value")
                self.tree.move_to(value_node)
                expr_type = self.expression()
                self.tree.move_to_parent()
                
                expected_type = {
                    TokenType.PRINT_INT: DataType.INT,
                    TokenType.PRINT_FLOAT: DataType.FLOAT,
                    TokenType.PRINT_CHAR: DataType.CHAR,
                    TokenType.PRINT_STR: DataType.CHAR,
                }[io_token.type]
                
                if expected_type != expr_type:
                    error_node = self.tree.add_child("TypeError")
                    self.tree.add_child("Message", Token(None,
                        f"Tipo incompatible en función {io_token.value}: "
                        f"se esperaba {expected_type.name}, se encontró {expr_type.name}",
                        io_token.line, io_token.column))
                    raise SemanticError(
                        f"Tipo incompatible en función {io_token.value}: "
                        f"se esperaba {expected_type.name}, se encontró {expr_type.name}",
                        io_token.line,
                        io_token.column
                    )
            
            self.consume(TokenType.RPAREN, f"Se esperaba ')' después de {io_token.value}")
            self.tree.add_child("Semicolon",
                self.consume(TokenType.SEMICOLON, f"Se esperaba ';' después de {io_token.value}"))
            
            self.tree.move_to_parent()
        except:
            self.tree.move_to_parent()
            raise

    def compound_stmt(self) -> None:
        """CompoundStmt → '{' {Statement} '}'"""
        compound_node = self.tree.add_child("CompoundStatement")
        self.tree.move_to(compound_node)
        
        try:
            self.tree.add_child("LeftBrace",
                self.consume(TokenType.LBRACE, "Se esperaba '{'"))
            
            self.semantic_analyzer.enter_scope()
            
            while not self.check(TokenType.RBRACE) and not self.is_at_end():
                stmt_node = self.tree.add_child("Statement")
                self.tree.move_to(stmt_node)
                self.statement()
                self.tree.move_to_parent()
            
            self.semantic_analyzer.exit_scope()
            
            self.tree.add_child("RightBrace",
                self.consume(TokenType.RBRACE, "Se esperaba '}'"))
            
            self.tree.move_to_parent()
        except:
            self.tree.move_to_parent()
            raise

    # Auxiliary methods

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
            TokenType.RPAREN,
            TokenType.COMMA,
            TokenType.SEMICOLON,
            TokenType.EOF
        }