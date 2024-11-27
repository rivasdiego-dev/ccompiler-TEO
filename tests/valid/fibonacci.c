// Programa que genera la secuencia de Fibonacci
int fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

void main() {
    int i = 0;
    int limit = 10;
    
    printStr("Secuencia de Fibonacci: ");
    while (i < limit) {
        printInt(fibonacci(i));
        printStr(" ");
        i = i + 1;
    }
}