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