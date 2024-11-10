from typing import List, Optional, Set
from lexer.token import Token
from lexer.token_type import TokenType
from utils.error_handler import ParserError

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.has_main_function = False
    
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
        """
        Program → GlobalDeclaration* FunctionList
        Un programa puede tener declaraciones globales seguidas de funciones.
        """
        # Verificar que el programa no esté vacío
        if self.is_at_end():
            raise ParserError(
                "El programa está vacío",
                self.peek().line,
                self.peek().column
            )

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
        # Guardar el token de tipo para mensajes de error
        type_token = self.peek()
        self.type()  # Consume el tipo
        
        # Consumir el identificador
        id_token = self.consume(TokenType.ID, 
            f"Se esperaba un identificador después de '{type_token.value}'")
        
        # Inicialización opcional
        if self.match(TokenType.ASSIGN):
            self.expression()
        
        # Toda declaración global debe terminar en punto y coma
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
        self.type()  # Retorno de la función
        function_name = self.consume(TokenType.ID, "Se esperaba un nombre de función")
        
        self.consume(TokenType.LPAREN, f"Se esperaba '(' después de '{function_name.value}'")
        self.parameter_list()
        self.consume(TokenType.RPAREN, "Se esperaba ')' después de los parámetros")
        
        # Cuerpo de la función
        self.compound_stmt()

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
