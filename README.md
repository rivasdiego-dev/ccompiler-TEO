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

## Técnicas de Construcción de la Gramática LL(1)

### 1. Eliminación de Recursión por la Izquierda

La recursión por la izquierda ocurre cuando un no terminal deriva una producción que comienza con sí mismo. Este tipo de recursión no puede ser manejada por un parser LL(1) ya que causaría un bucle infinito.

#### Problema

Considere la siguiente gramática recursiva por la izquierda para expresiones:

```text
Expression → Expression + Term | Expression - Term | Term
```

#### Solución

La eliminación se realiza introduciendo un no terminal auxiliar (ExpressionTail):

```text
Expression → Term ExpressionTail
ExpressionTail → + Term ExpressionTail 
                | - Term ExpressionTail 
                | ε
```

#### Ejemplo en Nuestra Gramática

```text
// Antes (con recursión izquierda)
AddExpr → AddExpr + MultExpr | AddExpr - MultExpr | MultExpr

// Después (eliminada la recursión)
AddExpr → MultExpr AddExprTail
AddExprTail → + MultExpr AddExprTail 
            | - MultExpr AddExprTail 
            | ε
```

### 2. Precedencia de Operadores

La precedencia de operadores se implementa estructurando la gramática en niveles, donde cada nivel representa una precedencia diferente. Los operadores de mayor precedencia se encuentran en las producciones más profundas.

#### Jerarquía Implementada

1. **Nivel más alto**: Paréntesis y llamadas a funciones

   ```text
   Factor → '(' Expression ')' | ID '(' ArgumentList ')'
   ```

2. **Multiplicación/División**

   ```text
   MultExpr → Factor MultExprTail
   MultExprTail → ('*' | '/') Factor MultExprTail | ε
   ```

3. **Suma/Resta**

   ```text
   AddExpr → MultExpr AddExprTail
   AddExprTail → ('+' | '-') MultExpr AddExprTail | ε
   ```

4. **Operadores de Comparación**

   ```text
   CompExpr → AddExpr CompExprTail
   CompExprTail → ('==' | '!=' | '<' | '<=') AddExpr CompExprTail | ε
   ```

5. **Operadores Lógicos**

   ```text
   LogicExpr → CompExpr LogicExprTail
   LogicExprTail → ('&&' | '||') CompExpr LogicExprTail | ε
   ```

### 3. Factorización por la Izquierda

La factorización por la izquierda es necesaria cuando dos o más producciones de una misma regla comparten un prefijo común, lo que haría imposible para un parser LL(1) decidir qué producción elegir.

#### Problema

```text
Declaration → Type ID ; 
            | Type ID = Expression ;
```

#### Solución

```text
Declaration → Type ID DeclarationTail
DeclarationTail → = Expression ; | ;
```

#### Ejemplo en Nuestra Gramática

```text
// Antes (sin factorizar)
PrintStmt → printInt '(' Expression ')' ';'
          | printFloat '(' Expression ')' ';'
          | printChar '(' Expression ')' ';'
          | printStr '(' Expression ')' ';'

// Después (factorizado)
PrintStmt → PrintFunction '(' Expression ')' ';'
PrintFunction → printInt | printFloat | printChar | printStr
```

### 4. Problema del Dangling Else

El "dangling else" es un problema de ambigüedad común en lenguajes de programación donde no está claro a qué `if` corresponde un `else` cuando hay múltiples `if`s anidados.

#### Problema

```text
if (c1) if (c2) s1 else s2
```

¿El `else` corresponde al primer `if` o al segundo?

#### Solución

Nuestra gramática resuelve esto usando una producción específica para la parte del else:

```text
IfStmt → 'if' '(' Expression ')' Statement ElsePart
ElsePart → 'else' Statement | ε
```

Esta estructura garantiza que el `else` se asocie con el `if` más cercano, que es el comportamiento estándar en C.

### Prueba de la Gramática LL(1)

Para verificar que una gramática es LL(1), se deben cumplir tres condiciones:

1. **No recursión por la izquierda**: Eliminada mediante las técnicas mostradas arriba.

2. **No ambigüedad**: Asegurada mediante la factorización y el manejo específico de casos como el dangling else.

3. **Conjuntos FIRST disjuntos**: Para cada no terminal A, si A → α | β son dos producciones diferentes, entonces FIRST(α) ∩ FIRST(β) = ∅.
