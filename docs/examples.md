# Ejemplos de Uso

Esta documentación proporciona ejemplos prácticos de cómo usar el ensamblador RISC-V, desde programas simples hasta casos más avanzados con directivas de segmento.

## Tabla de Contenidos

- [Ejemplo Básico](#ejemplo-básico)
- [Uso de Directivas .data y .text](#uso-de-directivas-data-y-text)
- [Programa con Funciones](#programa-con-funciones)
- [Uso de Pseudo-instrucciones](#uso-de-pseudo-instrucciones)
- [Manejo de Datos](#manejo-de-datos)
- [Algoritmos Comunes](#algoritmos-comunes)
- [Detección de Errores](#detección-de-errores)
- [Uso Avanzado](#uso-avanzado)

## Ejemplo Básico

### Suma Simple

**Archivo: `suma_simple.asm`**

```assembly
# Programa que suma dos números
.text
main:
    # Cargar primer número (10)
    addi x1, x0, 10

    # Cargar segundo número (20)
    addi x2, x0, 20

    # Sumar los números
    add x3, x1, x2      # x3 = x1 + x2 = 30

    # Fin del programa
    nop
```

**Ejecución:**

```bash
python assembler.py suma_simple.asm
```

**Salida esperada:**

```
¡Ensamblaje completado exitosamente!
```

**Archivos generados:**

- `suma_simple.bin` - Código máquina binario
- `suma_simple.hex` - Código máquina en hexadecimal

**Contenido de `suma_simple.hex`:**

```
00a00093
01400113
002081b3
00000013
```

**Explicación paso a paso:**

1. `addi x1, x0, 10` → `00a00093`: Carga 10 en registro x1
2. `addi x2, x0, 20` → `01400113`: Carga 20 en registro x2
3. `add x3, x1, x2` → `002081b3`: Suma x1 + x2, resultado en x3
4. `nop` → `00000013`: No operación (pseudo-instrucción)

## Uso de Directivas .data y .text

### Programa con Datos y Código

**Archivo: `programa_completo.asm`**

```assembly
# Programa que demuestra el uso de directivas
.data
    numero1: .word 42
    numero2: .word 100
    resultado: .word 0
    array: .word 1, 2, 3, 4, 5

.text
main:
    # Solo podemos usar valores inmediatos por ahora
    # Las referencias a datos requieren funcionalidad adicional

    # Trabajar con valores inmediatos basados en los datos
    li x1, 42           # Simular carga de numero1
    li x2, 100          # Simular carga de numero2

    # Realizar operación
    add x3, x1, x2      # x3 = numero1 + numero2

    # Usar pseudo-instrucciones
    li x4, 1000
    mv x5, x3

    # Salto condicional
    beqz x3, fin
    nop

fin:
    ret
```

**Ejecución:**

```bash
python assembler.py programa_completo.asm
```

**Archivos generados:**

- `programa_completo.bin` - Código máquina del segmento .text
- `programa_completo.hex` - Código máquina del segmento .text en hex
- `programa_completo_data.bin` - Datos del segmento .data (si existe)
- `programa_completo_data.hex` - Datos del segmento .data en hex (si existe)

**Contenido de `programa_completo_data.hex`:**

```
0000002A
00000064
00000000
00000001
00000002
00000003
00000004
00000005
```

### Solo Segmento de Datos

**Archivo: `solo_datos.asm`**

```assembly
# Archivo que solo define datos
.data
    constantes: .word 10, 20, 30, 40, 50
    valores: .word -1, -2, -3
    grande: .word 0x12345678
```

**Archivos generados:**

- Solo `solo_datos_data.bin` y `solo_datos_data.hex` (sin archivos de texto)

## Programa con Funciones

### Factorial

**Archivo: `factorial.asm`**

```assembly
# Programa que calcula factorial de 5
.text
main:
    # Preparar argumentos
    li a0, 5            # Número para calcular factorial
    call factorial      # Llamar función factorial

    # Resultado en a0
    mv s0, a0           # Guardar resultado en s0
    j end               # Saltar al final

factorial:
    # Función factorial recursiva
    # Entrada: a0 = n
    # Salida: a0 = n!

    # Caso base: si n <= 1, retornar 1
    li t0, 1
    ble a0, t0, factorial_base

    # Guardar registros en pila
    addi sp, sp, -8
    sw ra, 4(sp)        # Guardar dirección de retorno
    sw a0, 0(sp)        # Guardar n

    # Llamada recursiva: factorial(n-1)
    addi a0, a0, -1     # n = n - 1
    call factorial      # factorial(n-1)

    # Restaurar n de la pila
    lw t1, 0(sp)        # t1 = n original

    # n! = n * (n-1)!
    mul a0, t1, a0      # a0 = n * factorial(n-1)

    # Restaurar registros
    lw ra, 4(sp)
    addi sp, sp, 8
    ret

factorial_base:
    li a0, 1            # Retornar 1
    ret

end:
    nop                 # Fin del programa
```

**Nota**: Este ejemplo usa `mul` y `ble` que requieren extensiones adicionales. Versión usando solo RV32I:

**Archivo: `factorial_rv32i.asm`**

```assembly
# Factorial usando solo instrucciones RV32I base
.text
main:
    li a0, 5            # Calcular factorial de 5
    call factorial
    mv s0, a0           # Resultado en s0
    j end

factorial:
    # Caso base: si n <= 1
    addi t0, x0, 1
    blt a0, t0, factorial_base
    beq a0, t0, factorial_base

    # Guardar en pila
    addi sp, sp, -12
    sw ra, 8(sp)
    sw a0, 4(sp)
    sw a1, 0(sp)

    # factorial(n-1)
    addi a0, a0, -1
    call factorial

    # n * factorial(n-1) usando suma repetida
    lw a1, 4(sp)        # a1 = n original
    mv t0, a0           # t0 = factorial(n-1)
    li a0, 0            # a0 = 0 (acumulador)

multiply_loop:
    beqz a1, multiply_done
    add a0, a0, t0      # a0 += factorial(n-1)
    addi a1, a1, -1
    j multiply_loop

multiply_done:
    # Restaurar registros
    lw a1, 0(sp)
    lw ra, 8(sp)
    addi sp, sp, 12
    ret

factorial_base:
    li a0, 1
    ret

end:
    nop
```

## Uso de Pseudo-instrucciones

### Demostración de Pseudo-instrucciones

**Archivo: `pseudo_demo.asm`**

```assembly
# Demostración de pseudo-instrucciones
.text
main:
    # Carga de inmediatos
    li x1, 100          # Inmediato pequeño
    li x2, 0x12345678   # Inmediato grande

    # Movimiento de registros
    mv x3, x1           # x3 = x1

    # Operaciones lógicas
    not x4, x1          # x4 = ~x1
    neg x5, x1          # x5 = -x1

    # Comparaciones con cero
    seqz x6, x1         # x6 = (x1 == 0) ? 1 : 0
    snez x7, x1         # x7 = (x1 != 0) ? 1 : 0
    sltz x8, x5         # x8 = (x5 < 0) ? 1 : 0

    # Saltos condicionales
    beqz x6, no_es_cero
    # Si x1 era cero, x6 = 1, no salta

no_es_cero:
    bnez x7, continuar
    j end               # Si x1 era cero, x7 = 0, salta al final

continuar:
    # Llamadas y saltos
    call subrutina      # Llamada a función
    j end               # Salto incondicional

subrutina:
    # Ejemplo de función simple
    addi x10, x10, 1    # Incrementar a0
    ret                 # Retorno

end:
    nop
```

**Expansión automática** (lo que ve internamente el ensamblador):

```assembly
# li x1, 100 se expande a:
addi x1, x0, 100

# li x2, 0x12345678 se expande a:
lui x2, 0x12346
addi x2, x2, 0x678

# mv x3, x1 se expande a:
addi x3, x1, 0

# not x4, x1 se expande a:
xori x4, x1, -1

# beqz x6, no_es_cero se expande a:
beq x6, x0, no_es_cero

# call subrutina se expande a:
auipc ra, %hi(subrutina)
jalr ra, %lo(subrutina)(ra)

# ret se expande a:
jalr x0, ra, 0
```

## Manejo de Datos

### Operaciones con Arrays (Simulado)

**Archivo: `array_sum.asm`**

```assembly
# Suma de elementos de un array simulado
.text
main:
    # Simular array con registros s1-s5
    li s1, 10           # array[0] = 10
    li s2, 20           # array[1] = 20
    li s3, 30           # array[2] = 30
    li s4, 40           # array[3] = 40
    li s5, 50           # array[4] = 50

    # Inicializar suma y contador
    li t0, 0            # suma = 0
    li t1, 0            # contador = 0
    li t2, 5            # tamaño del array

    # Sumar elementos
    add t0, t0, s1      # suma += array[0]
    addi t1, t1, 1      # contador++

    add t0, t0, s2      # suma += array[1]
    addi t1, t1, 1      # contador++

    add t0, t0, s3      # suma += array[2]
    addi t1, t1, 1      # contador++

    add t0, t0, s4      # suma += array[3]
    addi t1, t1, 1      # contador++

    add t0, t0, s5      # suma += array[4]
    addi t1, t1, 1      # contador++

    # Resultado en t0 = 150
    mv a0, t0           # Retornar resultado en a0

end:
    nop
```

### Búsqueda en Array

**Archivo: `array_search.asm`**

```assembly
# Búsqueda lineal en array simulado
.text
main:
    # Array simulado en registros
    li s1, 5            # array[0] = 5
    li s2, 12           # array[1] = 12
    li s3, 8            # array[2] = 8
    li s4, 15           # array[3] = 15
    li s5, 3            # array[4] = 3

    # Valor a buscar
    li t0, 8            # buscar el valor 8

    # Búsqueda
    li t1, -1           # índice no encontrado

    # Verificar array[0]
    beq s1, t0, found_0

    # Verificar array[1]
    beq s2, t0, found_1

    # Verificar array[2]
    beq s3, t0, found_2

    # Verificar array[3]
    beq s4, t0, found_3

    # Verificar array[4]
    beq s5, t0, found_4

    # No encontrado
    j not_found

found_0:
    li t1, 0
    j search_end

found_1:
    li t1, 1
    j search_end

found_2:
    li t1, 2
    j search_end

found_3:
    li t1, 3
    j search_end

found_4:
    li t1, 4
    j search_end

not_found:
    li t1, -1

search_end:
    mv a0, t1           # Retornar índice en a0
    nop
```

## 🧮 Algoritmos Comunes

### Máximo Común Divisor (Euclides)

**Archivo: `gcd.asm`**

```assembly
# Algoritmo de Euclides para MCD
.text
main:
    li a0, 48           # Primer número
    li a1, 18           # Segundo número
    call gcd
    mv s0, a0           # Resultado en s0
    j end

gcd:
    # Algoritmo de Euclides: gcd(a, b) = gcd(b, a mod b)
    # Entrada: a0 = a, a1 = b
    # Salida: a0 = gcd(a, b)

gcd_loop:
    beqz a1, gcd_done   # Si b == 0, terminar

    # Calcular a mod b usando restas sucesivas
    mv t0, a0           # t0 = a
    mv t1, a1           # t1 = b

mod_loop:
    blt t0, t1, mod_done    # Si a < b, a mod b = a
    sub t0, t0, t1          # a = a - b
    j mod_loop

mod_done:
    # Ahora t0 = a mod b
    mv a0, a1           # a = b
    mv a1, t0           # b = a mod b
    j gcd_loop

gcd_done:
    # a0 ya contiene el resultado
    ret

end:
    nop
```

### Número de Fibonacci

**Archivo: `fibonacci.asm`**

```assembly
# Cálculo de Fibonacci iterativo
.text
main:
    li a0, 10           # Calcular F(10)
    call fibonacci
    mv s0, a0           # Resultado en s0
    j end

fibonacci:
    # Fibonacci iterativo
    # Entrada: a0 = n
    # Salida: a0 = F(n)

    # Casos base
    li t0, 0
    beq a0, t0, fib_zero    # F(0) = 0

    li t0, 1
    beq a0, t0, fib_one     # F(1) = 1

    # Caso general: F(n) = F(n-1) + F(n-2)
    li t1, 0            # F(0) = 0
    li t2, 1            # F(1) = 1
    li t3, 2            # contador = 2

fib_loop:
    blt a0, t3, fib_done    # Si n < contador, terminar

    add t4, t1, t2      # F(i) = F(i-1) + F(i-2)
    mv t1, t2           # F(i-2) = F(i-1)
    mv t2, t4           # F(i-1) = F(i)
    addi t3, t3, 1      # contador++
    j fib_loop

fib_done:
    mv a0, t2           # Retornar F(n)
    ret

fib_zero:
    li a0, 0
    ret

fib_one:
    li a0, 1
    ret

end:
    nop
```

## ❌ Detección de Errores

### Ejemplos de Errores Comunes

**Archivo: `errores.asm`**

```assembly
# Este archivo contiene errores intencionales para demostrar la detección
.text
main:
    # Error 1: Instrucción inexistente
    invalid_instr x1, x2, x3

    # Error 2: Registro inválido
    add x99, x1, x2

    # Error 3: Número incorrecto de operandos
    add x1, x2          # Faltan operandos

    # Error 4: Inmediato fuera de rango
    addi x1, x2, 5000   # Fuera del rango [-2048, 2047]

    # Error 5: Etiqueta no definida
    j etiqueta_inexistente

    # Error 6: Formato de memoria incorrecto
    lw x1, invalid_format

end:
    nop
```

**Salida de errores esperada:**

```
╭─ Error en la línea 4 ─╮
│ Error: Instrucción no │
│ soportada:            │
│ 'invalid_instr'       │
│                       │
│ En la línea:          │
│ invalid_instr x1, x2, │
│ x3                    │
╰───────────────────────╯

╭─ Error en la línea 7 ─╮
│ Error: Registro no    │
│ válido: 'x99'         │
│                       │
│ En la línea: add x99, │
│ x1, x2                │
╰───────────────────────╯

El ensamblaje falló con 6 error(s).
```

## Uso Avanzado

### Integración con Python

**Archivo: `ensamblador_personalizado.py`**

```python
#!/usr/bin/env python3
"""
Ejemplo de uso avanzado del ensamblador RISC-V integrado en Python.
"""

from core.ensamblador import Ensamblador
from utils.file_writer import escribir_binario, escribir_hexadecimal
import sys

def ensamblar_codigo(codigo_assembly):
    """Ensambla código y retorna información detallada."""

    # Crear ensamblador
    ensamblador = Ensamblador()

    # Convertir string a lista de líneas
    if isinstance(codigo_assembly, str):
        lineas = codigo_assembly.strip().split('\n')
    else:
        lineas = codigo_assembly

    # Ensamblar
    codigo_maquina = ensamblador.ensamblar(lineas)

    # Retornar información
    return {
        'exitoso': codigo_maquina is not None,
        'codigo_maquina': codigo_maquina,
        'tabla_simbolos': ensamblador.tabla_de_simbolos.copy(),
        'num_errores': ensamblador.manejador_errores._error_count,
        'tamaño_bytes': len(codigo_maquina) if codigo_maquina else 0,
        'num_instrucciones': len(codigo_maquina) // 4 if codigo_maquina else 0
    }

def analizar_programa(archivo_asm):
    """Analiza un programa assembly y muestra estadísticas."""

    with open(archivo_asm, 'r', encoding='utf-8') as f:
        contenido = f.read()

    resultado = ensamblar_codigo(contenido)

    print(f"Análisis de {archivo_asm}:")
    print(f"  Estado: {'✓ Exitoso' if resultado['exitoso'] else '✗ Fallido'}")
    print(f"  Instrucciones: {resultado['num_instrucciones']}")
    print(f"  Tamaño: {resultado['tamaño_bytes']} bytes")
    print(f"  Símbolos: {len(resultado['tabla_simbolos'])}")

    if resultado['tabla_simbolos']:
        print("  Tabla de símbolos:")
        for simbolo, direccion in resultado['tabla_simbolos'].items():
            print(f"    {simbolo}: 0x{direccion:08x}")

    return resultado

def compilar_multiples_archivos(archivos):
    """Compila múltiples archivos y genera reporte."""

    resultados = []

    for archivo in archivos:
        print(f"\nProcesando {archivo}...")
        try:
            resultado = analizar_programa(archivo)
            resultados.append((archivo, resultado))

            if resultado['exitoso']:
                # Generar archivos de salida
                base_name = archivo.rsplit('.', 1)[0]
                escribir_binario(resultado['codigo_maquina'], base_name)
                escribir_hexadecimal(resultado['codigo_maquina'], base_name)
                print(f"  Archivos generados: {base_name}.bin, {base_name}.hex")

        except FileNotFoundError:
            print(f"  Error: Archivo {archivo} no encontrado")
            resultados.append((archivo, None))

    # Reporte final
    exitosos = sum(1 for _, r in resultados if r and r['exitoso'])
    total = len(resultados)

    print(f"\n{'='*50}")
    print(f"REPORTE FINAL: {exitosos}/{total} archivos compilados exitosamente")

    return resultados

if __name__ == "__main__":
    # Ejemplo de uso
    codigo_ejemplo = """
# Programa de ejemplo
.text
main:
    li a0, 42
    li a1, 8
    call suma
    mv s0, a0
    j end

suma:
    add a0, a0, a1
    ret

end:
    nop
    """

    # Ensamblar código directamente
    resultado = ensamblar_codigo(codigo_ejemplo)
    print("Resultado del ensamblado:")
    print(f"  Exitoso: {resultado['exitoso']}")
    print(f"  Instrucciones: {resultado['num_instrucciones']}")
    print(f"  Símbolos: {list(resultado['tabla_simbolos'].keys())}")

    # Si se pasan archivos como argumentos
    if len(sys.argv) > 1:
        archivos = sys.argv[1:]
        compilar_multiples_archivos(archivos)
```

**Uso del script:**

```bash
# Ensamblar archivos individuales
python ensamblador_personalizado.py programa1.asm programa2.asm

# Solo ejecutar el ejemplo interno
python ensamblador_personalizado.py
```

### Script de Verificación de Sintaxis

**Archivo: `verificar_sintaxis.py`**

```python
#!/usr/bin/env python3
"""
Script para verificar sintaxis de archivos assembly sin generar código.
"""

from core.ensamblador import Ensamblador
import sys
import glob

def verificar_sintaxis(archivo):
    """Verifica solo la sintaxis de un archivo."""

    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()

        ensamblador = Ensamblador()

        # Solo primera pasada para verificar sintaxis básica
        ensamblador._primera_pasada(lineas)

        if ensamblador.manejador_errores.tiene_errores():
            return False

        # Verificar que todas las instrucciones sean válidas
        for num_linea, linea in enumerate(lineas, 1):
            linea = linea.strip()
            if not linea or linea.startswith('#'):
                continue

            # Aquí podrías agregar más verificaciones específicas

        return True

    except Exception as e:
        print(f"Error procesando {archivo}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: python verificar_sintaxis.py <archivo(s).asm>")
        print("     python verificar_sintaxis.py *.asm")
        sys.exit(1)

    # Expandir patrones de archivos
    archivos = []
    for arg in sys.argv[1:]:
        archivos.extend(glob.glob(arg))

    if not archivos:
        print("No se encontraron archivos")
        sys.exit(1)

    errores = 0

    for archivo in archivos:
        print(f"Verificando {archivo}...", end=' ')

        if verificar_sintaxis(archivo):
            print("✓ OK")
        else:
            print("✗ ERROR")
            errores += 1

    print(f"\nResultado: {len(archivos) - errores}/{len(archivos)} archivos válidos")

    if errores > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Estos ejemplos muestran desde uso básico hasta integración avanzada del ensamblador RISC-V en diferentes contextos y aplicaciones.
