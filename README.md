# Compilador de C Simplificado

![Static Badge](https://img.shields.io/badge/estado-en_revisi%C3%B3n-blue)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![anytree](https://img.shields.io/badge/anytree-2.12.1+-blue.svg)
![Licencia](https://img.shields.io/badge/licencia-MIT-green.svg)

## Descripción del Proyecto

Este proyecto implementa un compilador para un subconjunto del lenguaje C estándar, desarrollado como parte del curso de Teoría de Lenguajes de Programación, Ciclo 02/2024. El compilador incluye análisis léxico, sintáctico y semántico.

## Delimitación del Lenguaje

El lenguaje implementado es una versión simplificada de C con las siguientes características y limitaciones:

### Tipos de Datos
- Tipos básicos soportados: `int`, `float`, `char`, `void`
- No se soportan tipos compuestos (structs, unions)
- No se soportan punteros ni referencias
- No se soportan arreglos

### Control de Flujo
- Estructuras soportadas: `if`, `else`, `while`, `do-while`
- No se soportan: `for`, `switch`, `break`, `continue`, `goto`
- `return` solo puede devolver tipos básicos

### Funciones
- Funciones con múltiples parámetros
- Recursividad permitida
- No se soporta sobrecarga de funciones
- No se soportan funciones variádicas
- Todas las funciones deben declararse antes de su uso
- Debe existir una función `main` como punto de entrada

### Variables
- Solo variables de tipos básicos
- Ámbito de variables global y local
- Shadowing permitido en bloques anidados
- No se soportan variables estáticas
- No se soportan modificadores `const`, `volatile`, etc.

### Simplificaciones de E/S

El lenguaje implementa un sistema simplificado de entrada/salida con funciones predefinidas:

#### Funciones de Salida
- `printInt(int x)`: Imprime un número entero
- `printFloat(float x)`: Imprime un número de punto flotante
- `printChar(char x)`: Imprime un carácter
- `printStr(char* s)`: Imprime una cadena de caracteres

#### Funciones de Entrada
- `scanInt()`: Lee un número entero desde la entrada estándar
- `scanFloat()`: Lee un número de punto flotante
- `scanChar()`: Lee un carácter

Características de las funciones de E/S:
- No requieren inclusión de bibliotecas
- Son funciones built-in del lenguaje
- No soportan formato string como printf/scanf
- Los tipos de datos deben coincidir exactamente (no hay conversión implícita)
- No se maneja el buffer de entrada
- No se manejan errores de formato en la entrada

## Estructura del Proyecto

El proyecto está organizado en varios módulos que separan las diferentes responsabilidades del compilador:

```text
compilador/
├── lexer/                  # Análisis léxico
│   ├── lexer.py           # Implementación del analizador léxico
│   ├── token.py           # Definición de tokens
│   └── token_type.py      # Tipos de tokens soportados
│
├── parser/                 # Análisis sintáctico básico
│   └── parser.py          # Parser principal sin árbol
│
├── parse_tree/            # Análisis sintáctico con árbol
│   ├── parse_tree.py      # Implementación del árbol de parseo
│   └── tree_parser.py     # Parser con generación de árbol
│
├── semantic/              # Análisis semántico
│   ├── analyzer.py        # Analizador semántico
│   ├── symbol_table.py    # Tabla de símbolos
│   └── types.py          # Sistema de tipos
│
├── tests/                 # Casos de prueba
│   ├── invalid/          # Programas con errores
│   │   ├── type_error.c
│   │   ├── undeclared_var.c
│   │   └── wrong_return.c
│   └── valid/           # Programas correctos
│       ├── factorial.c
│       ├── fibonacci.c
│       └── hello_world.c
│
├── utils/                # Utilidades
│   └── error_handler.py  # Manejo de errores
│
├── main.py              # Punto de entrada para análisis básico
├── remain.py            # Punto de entrada para análisis con árbol
├── README.md           # Documentación del proyecto
└── LICENSE             # Licencia MIT
```

### Descripción de Componentes

1. **Analizador Léxico (`lexer/`):**
   - `lexer.py`: Implementa la tokenización del código fuente
   - `token.py`: Define la estructura de los tokens
   - `token_type.py`: Enumera todos los tipos de tokens soportados

2. **Analizador Sintáctico (`parser/` y `parse_tree/`):**
   - `parser.py`: Implementación del parser básico
   - `parse_tree.py`: Implementación de la estructura del árbol
   - `tree_parser.py`: Parser que genera el árbol de parseo

3. **Analizador Semántico (`semantic/`):**
   - `analyzer.py`: Realiza el análisis semántico
   - `symbol_table.py`: Maneja la tabla de símbolos
   - `types.py`: Define el sistema de tipos

4. **Pruebas (`tests/`):**
   - `invalid/`: Programas que deben generar errores
   - `valid/`: Programas que deben compilar correctamente

5. **Utilidades (`utils/`):**
   - `error_handler.py`: Sistema de manejo de errores

6. **Archivos Principales:**
   - `main.py`: Ejecuta el análisis sin generación de árbol
   - `remain.py`: Ejecuta el análisis con generación de árbol
   - `README.md`: Documentación completa del proyecto
   - `LICENSE`: Términos de la licencia MIT

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

## Implementación del Árbol de Parseo

El compilador incluye ahora la capacidad de generar y visualizar el árbol de parseo del programa analizado. Esta funcionalidad permite una mejor comprensión de la estructura sintáctica del código fuente.

### Modos de Ejecución

El compilador ofrece dos modos de operación diferentes:

1. **Análisis Básico (main.py)**
   - Realiza el análisis léxico, sintáctico y semántico tradicional
   - No genera visualización del árbol

   ```bash
   python main.py [archivo_fuente]
   ```

2. **Análisis con Árbol (remain.py)**
   - Realiza el análisis completo
   - Genera una visualización del árbol de parseo
   - Guarda el árbol en un archivo de texto

   ```bash
   python remain.py [archivo_fuente]
   ```

### Requisitos Adicionales

Para utilizar la funcionalidad del árbol de parseo, es necesario instalar la biblioteca `anytree`:

```bash
pip install anytree
```

### Estructura del Árbol

El árbol de parseo generado muestra la estructura jerárquica del programa, incluyendo:

- Declaraciones de funciones
- Parámetros y tipos
- Expresiones y operaciones
- Estructuras de control
- Declaraciones de variables
- Llamadas a funciones

### Archivos Generados

El árbol de parseo se guarda en archivos con el formato:

- Para archivos individuales: `parser_tree_YYYYMMDD_HHMMSS.txt`
- Para casos de prueba: `parser_tree_testN_YYYYMMDD_HHMMSS.txt`

Ejemplo de estructura del árbol generado:

```text
└── Program
    ├── FunctionList
    │   └── Function
    │       ├── Type [void]
    │       ├── FunctionName [main]
    │       ├── Parameters
    │       └── Body
    │           └── CompoundStatement
    │               ├── Statement
    │               │   └── Declaration
    │               │       ├── Type [int]
    │               │       └── Identifier [x]
    │               └── ...
```

La visualización del árbol permite una mejor comprensión de cómo el compilador interpreta la estructura del código fuente, facilitando la depuración y el análisis del programa.
