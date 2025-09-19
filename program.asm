# program.asm
# Programa de ejemplo para probar el ensamblador RISC-V
# Este programa suma números desde 1 hasta 10 y luego termina
.text
    # Inicia el programa
    li a0      # Carga el valor 10 en el registro a0 (pseudo-instrucción)
    li a1, 0        # Inicializa un contador en a1
    li a2, 1        # Valor a sumar en cada iteración

bucle:
    add a1, a1, a2  # a1 = a1 + a2
    blt a1, a0, bucle # Si a1 < a0, salta de nuevo a 'bucle'

    # Fin del programa, se queda en un bucle infinito
    # para indicar la finalización en un simulador simple.
fin:
    j fin           # Salta a la etiqueta 'fin' (pseudo-instrucción)

