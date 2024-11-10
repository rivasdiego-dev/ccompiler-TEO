from lexer.lexer import Lexer
from parser.parser import Parser
from utils.error_handler import CompilerError

def test_parser(code: str) -> None:
    """
    Prueba el análisis de un programa completo
    """
    print("\n" + "="*50)
    print(f"Analizando programa:\n{code}")
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
        parser.parse()
        print("✓ Programa sintácticamente correcto")
        
    except CompilerError as e:
        print(f"\n❌ Error: {e}")

def main():
    # Programas de prueba
    test_cases = [
        # Programa simple con una función
        """
        void main() {
            int x = 0;
            printInt(x);
        }
        """,
        
        # Programa con múltiples funciones
        """
        int factorial(int n) {
            if (n <= 1) {
                return 1;
            }
            return n * factorial(n - 1);
        }

        void main() {
            int num;
            printStr("Ingrese un numero: ");
            num = scanInt();
            printInt(factorial(num));
        }
        """,
        # Programa con variables globales
        """
        // Variables globales
        int MAX_SIZE = 100;
        float pi = 3.14159;
        char separator = ';';
        int counter;  // Sin inicialización

        // Funciones que usan las variables globales
        int getMaxSize() {
            return MAX_SIZE;
        }

        void main() {
            counter = 0;
            printInt(getMaxSize());
        }
        """,
        
        # Programa con todas las estructuras de control
        """
        void testControl() {
            int i = 0;
            
            // while loop
            while (i < 5) {
                printInt(i);
                i = i + 1;
            }
            
            // do-while loop
            do {
                i = i - 1;
                printInt(i);
            } while (i > 0);
            
            // if-else
            if (i == 0) {
                printStr("Cero");
            } else {
                printStr("No cero");
            }
        }
        
        void main() {
            testControl();
        }
        """,
        
        # Programa con errores comunes
        """
        void main() {
            int x = ;  // Error: falta expresión
        }
        """,
        
        """
        int test(int x, ) {  // Error: parámetro inválido
            return x;
        }
        """
    ]
    
    # Prueba cada caso
    for code in test_cases:
        test_parser(code)
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    print("Prueba del Parser - Presiona Ctrl+C para salir")
    main()