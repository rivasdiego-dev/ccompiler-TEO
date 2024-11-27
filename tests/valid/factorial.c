// Programa que calcula el factorial de un número
int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

void main() {
    int num = 5;
    printStr("Factorial de 5 es: ");
    printInt(factorial(num));
}