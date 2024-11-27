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
    # Programas de prueba para el analizador semántico
    test_cases = [
        # 1. Verificación de tipos en asignaciones
        """
        void main() {
            int x = 5;
            float y = 3.14;
            x = y;  // Error: asignación de float a int
        }
        """,
        
        # 2. Variables no declaradas
        """
        void main() {
            x = 10;  // Error: variable no declarada
        }
        """,
        
        # 3. Variables no inicializadas
        """
        void main() {
            int x;
            int y = x + 1;  // Error: uso de variable no inicializada
        }
        """,
        
        # 4. Verificación de tipos en expresiones
        """
        void main() {
            int x = 5;
            float y = 3.14;
            if (x && y) {  // Error: operador lógico con float
                printInt(x);
            }
        }
        """,
        
        # 5. Verificación de retorno de funciones
        """
        int suma(int a, int b) {
            // Error: falta return
        }
        
        void main() {
            int x = suma(1, 2);
        }
        """,
        
        # 6. Tipo de retorno incorrecto
        """
        int getNumber() {
            return 3.14;  // Error: retorno float en función int
        }
        
        void main() {
            int x = getNumber();
        }
        """,
        
        # 7. Verificación de parámetros de función
        """
        void printNumber(int x) {
            printInt(x);
        }
        
        void main() {
            printNumber(3.14);  // Error: argumento float en parámetro int
        }
        """,
        
        # 8. Múltiples declaraciones de variable
        """
        void main() {
            int x = 5;
            int x = 10;  // Error: variable ya declarada
        }
        """,
        
        # 9. Ámbitos y shadowing
        """
        int x = 10;  // Variable global
        
        void main() {
            int x = 5;  // OK: shadowing permitido
            {
                x = 20;  // OK: modifica x local
                int x = 30;  // OK: nuevo ámbito
            }
        }
        """,
        
        # 10. Verificación de tipos en funciones de I/O
        """
        void main() {
            int x = 5;
            printFloat(x);  // Error: tipo incorrecto en función de I/O
        }
        """,
        
        # 11. Condiciones en estructuras de control
        """
        void main() {
            float x = 3.14;
            while (x) {  // Error: condición debe ser int
                printFloat(x);
            }
        }
        """,
        
        # 12. Programa semánticamente correcto
        """
        int factorial(int n) {
            if (n <= 1) {
                return 1;
            }
            return n * factorial(n - 1);
        }

        void main() {
            int num = 5;
            printStr("El factorial es: ");
            printInt(factorial(num));
        }
        """
    ]
    
    # Prueba cada caso
    for i, code in enumerate(test_cases, 1):
        print(f"\nCaso de prueba #{i}")
        print("="*50)
        test_parser(code)
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    print("Pruebas del Analizador Semántico - Presiona Ctrl+C para salir")
    main()