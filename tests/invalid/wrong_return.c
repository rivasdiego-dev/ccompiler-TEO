// Este programa debe fallar por tipo de retorno incorrecto
int getNumber() {
    return;  // Error: función int debe retornar un valor
}

void main() {
    int x = getNumber();
    printInt(x);
}