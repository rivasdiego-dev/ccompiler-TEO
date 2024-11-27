// Programa simple que demuestra entrada/salida
void main() {
    int age;
    printStr("¡Hola, mundo!");
    printStr("\nPor favor, ingresa tu edad: ");
    age = scanInt();
    
    if (age >= 18) {
        printStr("Eres mayor de edad");
    } else {
        printStr("Eres menor de edad");
    }
}