# Ensamblador RISC-V

Un ensamblador de dos pasadas para la arquitectura **RV32I (RISC-V 32-bit Integer)** implementado en Python. Este proyecto traduce código assembly RISC-V a código máquina binario y hexadecimal.

## Características

- **Ensamblado de dos pasadas** - Primera pasada para etiquetas, segunda para código máquina
- **Soporte completo RV32I** - Todas las instrucciones base de RISC-V 32-bit Integer
- **Pseudo-instrucciones** - Expansión automática de 19 pseudo-instrucciones comunes
- **Directivas de segmento** - Soporte para `.text` y `.data` con enteros
- **Manejo de errores** - Reportes detallados con formato visual usando Rich
- **Múltiples formatos de salida** - Binario (.bin) y hexadecimal (.hex) para cada segmento
- **Tabla de símbolos** - Soporte para etiquetas y referencias entre segmentos
- **Tests unitarios** - Cobertura completa con 70+ tests

## Estructura del Proyecto

```
Assembler/
├── assembler.py              # Script principal de entrada
├── program.asm              # Archivo de ejemplo
├── core/                    # Núcleo del ensamblador
│   ├── ensamblador.py      # Clase principal Ensamblador
│   ├── directivas.py       # Manejo de directivas .text y .data
│   └── error_handler.py    # Manejo de errores
├── isa/                     # Definiciones de la arquitectura
│   ├── riscv.py            # Constantes y formatos RISC-V
│   └── pseudo_instrucciones.py # Expansión de pseudo-instrucciones
├── utils/                   # Utilidades
│   └── file_writer.py      # Escritura de archivos de salida
└── tests/                   # Tests unitarios
    ├── test_ensamblador.py
    ├── test_directivas.py
    ├── test_error_handler.py
    ├── test_pseudo_instrucciones.py
    ├── test_riscv.py
    └── run_all_tests.py
```

## Instalación

### Requisitos

- Python 3.7+
- Rich (para formateo de errores)

### Instalación de dependencias

```bash
pip install rich
```

### Clonar el repositorio

```bash
git clone https://github.com/SantiagoJaramilloDuque/Assembler.git
cd Assembler
```

## Uso

### Uso básico

```bash
python assembler.py input.asm
```

### Ejemplo de archivo assembly con directivas

```assembly
# Programa de ejemplo con segmentos .data y .text
.data
    numero1: .word 42
    numero2: .word 100
    array: .word 1, 2, 3, 4, 5

.text
main:
    # Cargar constantes inmediatas
    addi x1, x0, 10      # x1 = 10
    addi x2, x0, 20      # x2 = 20
    add x3, x1, x2       # x3 = x1 + x2 (30)

    # Usando pseudo-instrucciones
    li x4, 1000          # Cargar inmediato grande
    mv x5, x3            # Copiar registro
    nop                  # No operación

    # Salto condicional
    beqz x3, end         # Saltar si x3 es cero
    j main               # Salto incondicional

end:
    ret                  # Retornar
```

### Archivos de salida generados

Para el archivo `programa.asm`, se generan:

- `programa.bin` - Segmento de texto en formato binario
- `programa.hex` - Segmento de texto en formato hexadecimal
- `programa_data.bin` - Segmento de datos en formato binario (si existe)
- `programa_data.hex` - Segmento de datos en formato hexadecimal (si existe)

## Directivas Soportadas

### Directivas de Segmento

| Directiva | Descripción                                              | Ejemplo |
| --------- | -------------------------------------------------------- | ------- |
| `.text`   | Cambia al segmento de código (dirección base 0x00000000) | `.text` |
| `.data`   | Cambia al segmento de datos (dirección base 0x10000000)  | `.data` |

### Directivas de Datos (solo en segmento .data)

| Directiva | Descripción               | Ejemplo              |
| --------- | ------------------------- | -------------------- |
| `.word`   | Define enteros de 32 bits | `.word 42, 100, -50` |

## Ejemplos de Uso

### Programa Básico

```assembly
# Suma simple
.text
main:
    addi x1, x0, 10
    addi x2, x0, 20
    add x3, x1, x2
    ret
```

### Programa con Datos

```assembly
# Programa con segmento de datos
.data
    numeros: .word 1, 2, 3, 4, 5
    constante: .word 42

.text
main:
    li x1, 42          # Cargar constante
    li x2, 100         # Otro valor
    add x3, x1, x2     # Suma
    ret
```

## Mejores Prácticas

1. **Organización del código**: Siempre coloca el segmento `.data` antes del `.text`
2. **Comentarios**: Usa comentarios descriptivos con `#`
3. **Etiquetas**: Usa nombres descriptivos para etiquetas (`main:`, `loop:`, etc.)
4. **Indentación**: Mantén indentación consistente para legibilidad
5. **Valores inmediatos**: Los valores `.word` deben estar en el rango de 32 bits con signo

## Limitaciones Actuales

- **Referencias de datos**: No hay soporte directo para cargar datos del segmento `.data` en instrucciones
- **Solo enteros**: El segmento `.data` solo soporta enteros de 32 bits (`.word`)
- **Un archivo**: Procesa solo un archivo assembly a la vez

## Instrucciones Soportadas

### Instrucciones Base RV32I

| Tipo                     | Instrucciones                                             |
| ------------------------ | --------------------------------------------------------- |
| **Aritméticas**          | `add`, `sub`, `addi`                                      |
| **Lógicas**              | `and`, `or`, `xor`, `andi`, `ori`, `xori`                 |
| **Desplazamiento**       | `sll`, `srl`, `sra`, `slli`, `srli`, `srai`               |
| **Comparación**          | `slt`, `sltu`, `slti`, `sltiu`                            |
| **Carga/Almacenamiento** | `lw`, `lh`, `lb`, `lbu`, `lhu`, `sw`, `sh`, `sb`          |
| **Saltos**               | `jal`, `jalr`, `beq`, `bne`, `blt`, `bge`, `bltu`, `bgeu` |
| **Sistema**              | `lui`, `auipc`, `ecall`, `ebreak`, `fence`                |

### Pseudo-instrucciones Implementadas

| Pseudo-instrucción | Expansión           | Descripción              |
| ------------------ | ------------------- | ------------------------ |
| `nop`              | `addi x0, x0, 0`    | No operación             |
| `mv rd, rs`        | `addi rd, rs, 0`    | Copiar registro          |
| `not rd, rs`       | `xori rd, rs, -1`   | Complemento lógico       |
| `neg rd, rs`       | `sub rd, x0, rs`    | Negación aritmética      |
| `li rd, imm`       | `addi/lui + addi`   | Cargar inmediato         |
| `j label`          | `jal x0, label`     | Salto incondicional      |
| `ret`              | `jalr x0, ra, 0`    | Retorno de función       |
| `call label`       | `auipc + jalr`      | Llamada a función        |
| `beqz rs, label`   | `beq rs, x0, label` | Salto si igual a cero    |
| `bnez rs, label`   | `bne rs, x0, label` | Salto si no igual a cero |
| Y más...           |                     |                          |

## Testing

### Ejecutar todos los tests

```bash
python tests/run_all_tests.py
```

### Ejecutar tests específicos

```bash
# Test del núcleo del ensamblador
python -m unittest tests.test_ensamblador

# Test de directivas .data y .text
python -m unittest tests.test_directivas

# Test de pseudo-instrucciones
python -m unittest tests.test_pseudo_instrucciones

# Test de manejo de errores
python -m unittest tests.test_error_handler
```

### Cobertura de Tests

- **Directivas**: Segmentos `.text` y `.data`, directiva `.word`
- **Instrucciones**: Todas las instrucciones base RV32I
- **Pseudo-instrucciones**: 19+ pseudo-instrucciones implementadas
- **Manejo de errores**: Validación de sintaxis y operandos
- **Archivos de salida**: Generación correcta de archivos .bin/.hex

### Ejecutar tests específicos

```bash
python -m unittest tests.test_ensamblador -v
python -m unittest tests.test_pseudo_instrucciones -v
```

### Cobertura de tests

- **test_ensamblador.py** - Tests del núcleo del ensamblador
- **test_error_handler.py** - Tests del manejo de errores
- **test_pseudo_instrucciones.py** - Tests de expansión de pseudo-instrucciones
- **test_riscv.py** - Tests de definiciones de la arquitectura

## API Principal

### Clase `Ensamblador`

```python
from core.ensamblador import Ensamblador

ensamblador = Ensamblador()
codigo_maquina = ensamblador.ensamblar(lineas_codigo)
```

### Métodos principales

- `ensamblar(lineas_codigo)` - Ejecuta el ensamblado completo
- `_primera_pasada()` - Construye tabla de símbolos
- `_segunda_pasada()` - Genera código máquina

## Ejemplo de Salida

### Entrada (`program.asm`)

```assembly
main:
    addi x1, x0, 10
    add x2, x1, x0
```

### Salida Binaria (`program.bin`)

```
93 00 a0 00 33 01 00 00
```

### Salida Hexadecimal (`program.hex`)

```
00a00093
00001033
```

## Manejo de Errores

El ensamblador proporciona reportes detallados de errores:

```
╭─ Error en la línea 5 ─╮
│ Error: Instrucción no │
│ soportada: 'invalid'  │
│                       │
│ En la línea: invalid  │
│ x1, x2                │
╰───────────────────────╯
```

Tipos de errores detectados:

- Instrucciones no válidas
- Operandos incorrectos
- Registros inexistentes
- Inmediatos fuera de rango
- Símbolos no definidos
- Errores de sintaxis

## Autores

**Santiago Jaramillo Duque**  
**Tomas Marin Ariza**
