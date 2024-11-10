import argparse
from pathlib import Path
from lexer.lexer import Lexer
from lexer.token_type import TokenType
from parser.declaration_parser import DeclarationParser
from utils.error_handler import CompilerError

def run_lexer(file_path: Path) -> None:
    """Ejecuta solo el análisis léxico"""
    with open(file_path, 'r') as file:
        code = file.read()
    
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        print("\nAnálisis léxico exitoso. Tokens encontrados:")
        print("-" * 50)
        for token in tokens:
            if token.type not in {TokenType.NEWLINE, TokenType.EOF}:
                print(token)
        print("-" * 50)
    except CompilerError as e:
        print(f"\nError en el análisis léxico: {e}")

def run_parser(file_path: Path) -> None:
    """Ejecuta el análisis léxico y sintáctico"""
    with open(file_path, 'r') as file:
        code = file.read()
    
    try:
        # Primero hacemos el análisis léxico
        print("\nIniciando análisis léxico...")
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        print("Análisis léxico completado.")
        
        # Luego el análisis sintáctico
        print("\nIniciando análisis sintáctico...")
        parser = DeclarationParser(tokens)
        parser.parse()
        print("Análisis sintáctico completado exitosamente.")
    except CompilerError as e:
        print(f"\nError en la compilación: {e}")
        return

def run_compiler(file_path: Path) -> None:
    """Ejecuta el proceso completo de compilación"""
    print("Proceso completo de compilación (por implementar)")
    # TODO: Implementar cuando tengamos más componentes

def main():
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(
        description='Compilador de C simplificado',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Agregar argumentos
    parser.add_argument(
        'file',
        type=str,
        help='Archivo fuente a compilar'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['lexer', 'parser', 'compiler'],
        default='compiler',
        help='''Modo de ejecución:
lexer    - Solo análisis léxico
parser   - Análisis léxico y sintáctico
compiler - Proceso completo de compilación (default)'''
    )
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Verificar que el archivo existe
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: No se encontró el archivo '{args.file}'")
        return
    
    # Ejecutar el modo seleccionado
    if args.mode == 'lexer':
        run_lexer(file_path)
    elif args.mode == 'parser':
        run_parser(file_path)
    else:  # compiler
        run_compiler(file_path)

if __name__ == "__main__":
    main()