from lexer.lexer import Lexer
from utils.error_handler import CompilerError

def main():
    # Ejemplo actualizado usando las nuevas funciones de I/O
    code = """
    /* Este es un programa de prueba */
    int factorial(int n) {
        // Calcula el factorial de n
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
    
    void main() {
        int num;
        float result;
        
        printStr("Ingrese un numero: ");
        num = scanInt();
        result = factorial(num);
        
        printStr("El factorial de ");
        printInt(num);
        printStr(" es ");
        printFloat(result);
    }
    """
    
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        for token in tokens:
            print(token)
    except CompilerError as e:
        print(e)

if __name__ == "__main__":
    main()