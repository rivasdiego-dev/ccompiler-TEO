// Este programa debe fallar por error de tipos
void main() {
    int x = 5;
    float y = 3.14;
    x = y;  // Error: no se puede asignar float a int sin conversión
    printInt(x);
}