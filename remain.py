import sys
from datetime import datetime
from lexer.lexer import Lexer
from parse_tree.tree_parser import TreeParser
from utils.error_handler import CompilerError
from semantic.analyzer import SemanticAnalyzer

def compile_file(file_path: str) -> None:
    """
    Compila un archivo fuente completo y genera el árbol de parseo.
    """
    try:
        # Leer el archivo
        with open(file_path, 'r') as file:
            code = file.read()
        
        print(f"\nCompilando archivo: {file_path}")
        print("="*50)
        
        # Análisis léxico
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        # Análisis sintáctico y semántico con árbol de parseo
        print("\nAnálisis Sintáctico y Semántico:")
        print("-"*20)
        semantic_analyzer = SemanticAnalyzer()
        tree_parser = TreeParser(tokens)
        semantic_analyzer.analyze(tree_parser)
        parse_tree = tree_parser.parse()
        
        # Generar archivo del árbol de parseo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tree_file = f"parser_tree_{timestamp}.txt"
        tree_parser.tree.visualize(tree_file)
        
        print("✓ Programa sintáctica y semánticamente correcto")
        print(f"✓ Árbol de parseo generado en: {tree_file}")
        
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo '{file_path}'")
        sys.exit(1)
    except CompilerError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

def run_tests() -> None:
    """
    Ejecuta la suite de pruebas incorporada.
    """
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
    
    print("="*50)
    
    for i, code in enumerate(test_cases, 1):
        print(f"\nCaso de prueba #{i}")
        print("="*50)
        
        try:
            # Análisis léxico
            print("\n1. Análisis Léxico:")
            print("-"*20)
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            for token in tokens:
                print(f"  {token}")
            
            # Análisis sintáctico y semántico con árbol
            print("\nAnálisis Sintáctico y Semántico:")
            print("-"*20)
            semantic_analyzer = SemanticAnalyzer()
            tree_parser = TreeParser(tokens)
            semantic_analyzer.analyze(tree_parser)
            parse_tree = tree_parser.parse()
            
            # Generar archivo del árbol para cada caso de prueba
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            tree_file = f"parser_tree_test{i}_{timestamp}.txt"
            tree_parser.tree.visualize(tree_file)
            
            print("✓ Programa sintáctica y semánticamente correcto")
            print(f"✓ Árbol de parseo generado en: {tree_file}")
            
        except CompilerError as e:
            print(f"\n❌ Error: {e}")

def main():
    if len(sys.argv) == 1:
        # Sin argumentos, ejecutar suite de pruebas
        print("No se proporcionó archivo. Ejecutando suite de pruebas...")
        run_tests()
    else:
        # Compilar el archivo proporcionado
        file_path = sys.argv[1]
        compile_file(file_path)

if __name__ == "__main__":
    main()