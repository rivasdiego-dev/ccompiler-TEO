from lexer.lexer import Lexer
from parser.parser import Parser
from utils.error_handler import CompilerError

def test_parser(code: str) -> None:
    """Prueba el análisis de una expresión y muestra el proceso paso a paso"""
    print("\n" + "="*50)
    print(f"Analizando: {code}")
    print("="*50)
    
    try:
        # Análisis léxico
        print("\n1. Análisis Léxico:")
        print("-"*20)
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        for token in tokens:
            print(f"  {token}")
        
        # Análisis sintáctico
        print("\n2. Análisis Sintáctico:")
        print("-"*20)
        parser = Parser(tokens)
        parser.expression()
        print("✓ Expresión sintácticamente correcta")
        
    except CompilerError as e:
        print(f"\n❌ Error: {e}")

def main():
    # Lista de expresiones para probar
    expressions = [
        # Expresiones simples
        "42",
        "3.14",
        "'a'",
        '"hello"',
        
        # Operaciones aritméticas
        "1 + 2",
        "3 - 4",
        "5 * 6",
        "8 / 2",
        "1 + 2 * 3",
        "(1 + 2) * 3",
        
        # Operaciones lógicas
        "x > 0",
        "x >= 1",
        "y < 10",
        "a == b",
        "x > 0 && y < 10",
        
        # Llamadas a funciones
        "foo()",
        "bar(1, 2)",
        "baz(1 + 2, x * y)",
        
        # Expresiones complejas
        "1 + 2 * 3 + (4 * 5) / 2",
        "foo(bar(1, 2 + 3), 4 * 5) + 3",
        "(x > 0 && y < 10) || z == 0",
        
        # Expresiones con errores
        "1 +",
        "foo(,)",
        "(1 + 2",
        "1 2 3",
    ]
    
    # Prueba cada expresión
    for expr in expressions:
        test_parser(expr)
        input("\nPresiona Enter para continuar...")  # Pausa para revisar resultados

if __name__ == "__main__":
    print("Prueba del Parser - Presiona Ctrl+C para salir")
    print("Cada expresión se analizará paso a paso.")
    main()