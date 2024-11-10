# Compilador de C Simplificado

[![Estado del Proyecto](https://img.shields.io/badge/estado-en%20desarrollo-yellow.svg)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![Licencia](https://img.shields.io/badge/licencia-MIT-green.svg)]()

## Descripción del Proyecto

Este proyecto implementa un compilador para un subconjunto del lenguaje C estándar, desarrollado como parte del curso de Teoría de Lenguajes de Programación, Ciclo 02/2024. El compilador incluye análisis léxico, sintáctico y semántico, así como generación de código intermedio.

## Gramática Formal LL(1)

La siguiente gramática define la sintaxis del lenguaje soportado:

```text
// Programa
Program → FunctionList
FunctionList → Function FunctionList | ε

// Funciones
Function → Type ID '(' ParameterList ')' CompoundStmt
ParameterList → Parameter ParameterListTail | ε
ParameterListTail → ',' Parameter ParameterListTail | ε
Parameter → Type ID

// Tipos
Type → 'int' | 'char' | 'float' | 'void'

// Declaraciones
Declaration → Type ID DeclarationTail
DeclarationTail → '=' Expression ';' | ';'

// Statements
CompoundStmt → '{' StmtList '}'
StmtList → Statement StmtList | ε
Statement → DeclarationStmt
         | AssignmentStmt
         | IfStmt
         | WhileStmt
         | DoWhileStmt
         | ReturnStmt
         | IOStmt
         | CompoundStmt
         | ';'

DeclarationStmt → Declaration
AssignmentStmt → ID '=' Expression ';'

// Control de flujo
IfStmt → 'if' '(' Expression ')' Statement ElsePart
ElsePart → 'else' Statement | ε

WhileStmt → 'while' '(' Expression ')' Statement
DoWhileStmt → 'do' Statement 'while' '(' Expression ')' ';'

ReturnStmt → 'return' ReturnExpr ';'
ReturnExpr → Expression | ε

// Entrada/Salida
IOStmt → PrintStmt | ScanStmt
PrintStmt → ('printInt' | 'printFloat' | 'printChar' | 'printStr') '(' Expression ')' ';'
ScanStmt → ('scanInt' | 'scanFloat' | 'scanChar') '(' ')' ';'

// Expresiones
Expression → LogicExpr
LogicExpr → CompExpr LogicExprTail
LogicExprTail → ('&&' | '||') CompExpr LogicExprTail | ε

CompExpr → AddExpr CompExprTail
CompExprTail → ('==' | '!=' | '<' | '<=' | '>' | '>=') AddExpr CompExprTail | ε

AddExpr → MultExpr AddExprTail
AddExprTail → ('+' | '-') MultExpr AddExprTail | ε

MultExpr → Factor MultExprTail
MultExprTail → ('*' | '/') Factor MultExprTail | ε

Factor → '(' Expression ')'
       | ID FactorTail
       | INTEGER_LITERAL
       | FLOAT_LITERAL
       | CHAR_LITERAL
       | STRING_LITERAL

FactorTail → '(' ArgumentList ')' | ε

// Argumentos de función
ArgumentList → Expression ArgumentListTail | ε
ArgumentListTail → ',' Expression ArgumentListTail | ε
```

## Características de la Gramática

- Eliminación de recursión por la izquierda para garantizar parsing LL(1)
- Factorización izquierda para eliminar ambigüedad
- Manejo correcto de precedencia de operadores
- Resolución del problema del "dangling else"
- Soporte para expresiones aritméticas y lógicas anidadas
