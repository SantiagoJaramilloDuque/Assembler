# API Referen### Clase EnsambladorRISCVe

Esta documentación describe la API pública del ensamblador RISC-V, inclu### Clase ManejadorErroresendo todas las clases, métodos y funciones disponibles para su uso.

## Tabla de Contenidos

- [Clase Ensamblador](#clase-ensamblador)
- [Clase ErrorHandler](#clase-errorhandler)
- [Módulo pseudo_instrucciones](#módulo-pseudo_instrucciones)
- [Módulo riscv](#módulo-riscv)
- [Módulo file_writer](#módulo-file_writer)
- [Ejemplos de Uso](#ejemplos-de-uso)

## Clase Ensamblador

La clase principal que implementa la lógica de ensamblado de dos pasadas.

### Construcción

```python
from core.ensamblador import Ensamblador

ensamblador = Ensamblador()
```

### Atributos Públicos

| Atributo            | Tipo             | Descripción                           |
| ------------------- | ---------------- | ------------------------------------- |
| `tabla_de_simbolos` | `Dict[str, int]` | Mapeo de etiquetas a direcciones      |
| `segmento_texto`    | `bytearray`      | Código máquina generado               |
| `direccion_actual`  | `int`            | Dirección actual durante ensamblado   |
| `segmento_actual`   | `str`            | Segmento actual (por defecto ".text") |
| `manejador_errores` | `ErrorHandler`   | Instancia del manejador de errores    |

### Métodos Públicos

#### `ensamblar(lineas_codigo: List[str]) -> Optional[bytearray]`

Método principal que orquesta el proceso completo de ensamblado.

**Parámetros:**

- `lineas_codigo`: Lista de strings, cada uno representando una línea de código assembly

**Retorna:**

- `bytearray`: Código máquina generado si el ensamblado es exitoso
- `None`: Si ocurren errores durante el ensamblado

**Ejemplo:**

```python
ensamblador = Ensamblador()
codigo = [
    "main:",
    "    addi x1, x0, 10",
    "    add x2, x1, x0"
]
codigo_maquina = ensamblador.ensamblar(codigo)

if codigo_maquina:
    print(f"Ensamblado exitoso: {len(codigo_maquina)} bytes generados")
else:
    print("Error en el ensamblado")
```

**Proceso interno:**

1. Ejecuta `_primera_pasada()` para construir tabla de símbolos
2. Si no hay errores, ejecuta `_segunda_pasada()` para generar código
3. Llama `manejador_errores.resumen_final()` para mostrar resultados

### Métodos Privados (Información)

Estos métodos son para uso interno pero su documentación ayuda a entender el funcionamiento:

#### `_primera_pasada(lineas_codigo: List[str]) -> None`

Analiza el código para construir la tabla de símbolos y calcular direcciones.

- Identifica etiquetas y las registra con sus direcciones
- Calcula el tamaño del programa
- Maneja directivas de ensamblador (futuro)

#### `_segunda_pasada(lineas_codigo: List[str]) -> None`

Genera el código máquina real.

- Expande pseudo-instrucciones
- Valida operandos
- Codifica instrucciones en binario
- Resuelve referencias a símbolos

#### `_validar_operandos(mnem: str, ops: List[str]) -> None`

Valida que los operandos sean correctos para la instrucción dada.

**Validaciones:**

- Número correcto de operandos
- Registros válidos
- Rangos de inmediatos

#### `_analizar_registro(operando: str) -> int`

Convierte un nombre de registro a su número correspondiente.

**Acepta:**

- Nombres numéricos: `x0`, `x1`, ..., `x31`
- Nombres ABI: `zero`, `ra`, `sp`, `a0`, etc.

#### Métodos de Ensamblado por Tipo

- `_ensamblar_tipo_R(mnem, ops, pc) -> int`: Instrucciones registro-registro
- `_ensamblar_tipo_I(mnem, ops, pc) -> int`: Instrucciones con inmediato
- `_ensamblar_tipo_S(mnem, ops, pc) -> int`: Instrucciones de almacenamiento
- `_ensamblar_tipo_B(mnem, ops, pc) -> int`: Instrucciones de salto condicional
- `_ensamblar_tipo_U(mnem, ops, pc) -> int`: Instrucciones de inmediato superior
- `_ensamblar_tipo_J(mnem, ops, pc) -> int`: Instrucciones de salto

## Clase ErrorHandler

Gestiona la recolección y visualización de errores durante el ensamblado.

### Construcción

```python
from core.error_handler import ErrorHandler

manejador = ErrorHandler()
```

### Métodos Públicos

#### `reportar(num_linea: int, mensaje: str, linea_original: str = "") -> None`

Reporta un error y lo muestra en la consola con formato visual.

**Parámetros:**

- `num_linea`: Número de línea donde ocurrió el error (1-indexado)
- `mensaje`: Descripción del error
- `linea_original`: (Opcional) Línea de código que causó el error

**Ejemplo:**

```python
manejador = ErrorHandler()
manejador.reportar(5, "Registro no válido: 'x99'", "add x99, x1, x2")
```

**Salida visual:**

```
╭─ Error en la línea 5 ─╮
│ Error: Registro no    │
│ válido: 'x99'         │
│                       │
│ En la línea: add x99, │
│ x1, x2                │
╰───────────────────────╯
```

#### `tiene_errores() -> bool`

Verifica si se han reportado errores.

**Retorna:**

- `True`: Si hay uno o más errores reportados
- `False`: Si no hay errores

**Ejemplo:**

```python
if manejador.tiene_errores():
    print("Se encontraron errores durante el ensamblado")
else:
    print("Ensamblado completado sin errores")
```

#### `resumen_final() -> None`

Muestra un resumen final del proceso de ensamblado.

**Salida exitosa:**

```
¡Ensamblaje completado exitosamente!
```

**Salida con errores:**

```
El ensamblaje falló con 3 error(s).
```

### Atributos Privados

- `_error_count`: Contador interno de errores
- `_console`: Instancia de Rich Console para formateo

## Módulo core/error_handler.py

Funciones para manejo de pseudo-instrucciones.

### Constantes

#### `PSEUDO_INSTRUCCIONES: Set[str]`

Conjunto de pseudo-instrucciones reconocidas:

```python
{'nop', 'mv', 'not', 'neg', 'j', 'ret', 'call', 'li',
 'seqz', 'snez', 'sltz', 'sgtz', 'jr', 'beqz', 'bnez',
 'bltz', 'bgez', 'blez', 'bgtz'}
```

### Funciones

#### `es_pseudo(mnemonico: str) -> bool`

Verifica si un mnemónico corresponde a una pseudo-instrucción.

**Parámetros:**

- `mnemonico`: Nombre de la instrucción a verificar

**Retorna:**

- `True`: Si es una pseudo-instrucción conocida
- `False`: Si es una instrucción base o desconocida

**Ejemplo:**

```python
from isa import pseudo_instrucciones

print(pseudo_instrucciones.es_pseudo('nop'))  # True
print(pseudo_instrucciones.es_pseudo('add'))  # False
```

#### `expandir(mnemonico: str, operandos: List[str]) -> List[Tuple[str, List[str]]]`

Expande una pseudo-instrucción a una o más instrucciones base.

**Parámetros:**

- `mnemonico`: Nombre de la pseudo-instrucción
- `operandos`: Lista de operandos

**Retorna:**

- Lista de tuplas `(mnemónico, operandos)` representando las instrucciones expandidas

**Ejemplos:**

```python
# Pseudo-instrucción simple
resultado = pseudo_instrucciones.expandir('nop', [])
# Resultado: [('addi', ['x0', 'x0', '0'])]

# Pseudo-instrucción con operandos
resultado = pseudo_instrucciones.expandir('mv', ['x1', 'x2'])
# Resultado: [('addi', ['x1', 'x2', '0'])]

# Pseudo-instrucción compleja
resultado = pseudo_instrucciones.expandir('li', ['x1', '0x12345678'])
# Resultado: [('lui', ['x1', '0x12346']), ('addi', ['x1', 'x1', '0x678'])]

# Instrucción no pseudo (se devuelve sin cambios)
resultado = pseudo_instrucciones.expandir('add', ['x1', 'x2', 'x3'])
# Resultado: [('add', ['x1', 'x2', 'x3'])]
```

## Módulo core/ensamblador.py

Definiciones estáticas de la arquitectura RISC-V.

### Constantes Principales

#### `FORMATOS_INSTRUCCION: Dict[str, List[str]]`

Mapeo de formatos de instrucción a listas de mnemónicos:

```python
{
    'R': ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "sra", "or", "and"],
    'I': ["addi", "slli", "slti", "sltiu", "xori", "srli", "srai", "ori", "andi", ...],
    'S': ["sb", "sh", "sw"],
    'B': ["beq", "bne", "blt", "bge", "bltu", "bgeu"],
    'U': ["lui", "auipc"],
    'J': ["jal"]
}
```

#### `MNEMONICO_A_FORMATO: Dict[str, str]`

Mapeo directo de mnemónico a formato (búsqueda O(1)):

```python
{
    'add': 'R', 'addi': 'I', 'sw': 'S', 'beq': 'B',
    'lui': 'U', 'jal': 'J', ...
}
```

#### `OPCODE: Dict[str, int]`

Códigos de operación para cada tipo de instrucción:

```python
{
    'R': 0b0110011,      # Operaciones registro-registro
    'I': 0b0010011,      # Operaciones con inmediato
    'L': 0b0000011,      # Cargas (load)
    'S': 0b0100011,      # Almacenamientos (store)
    'B': 0b1100011,      # Saltos condicionales
    'J': 0b1101111,      # Saltos incondicionales
    'U': 0b0110111,      # LUI
    'auipc': 0b0010111,  # AUIPC
    'jalr': 0b1100111,   # JALR
    'SYSTEM': 0b1110011  # Instrucciones de sistema
}
```

#### `FUNC3: Dict[str, int]`

Códigos de función de 3 bits:

```python
{
    "add": 0b000, "sub": 0b000, "sll": 0b001,
    "addi": 0b000, "beq": 0b000, "lw": 0b010, ...
}
```

#### `FUNC7: Dict[str, int]`

Códigos de función de 7 bits (solo para instrucciones que los requieren):

```python
{
    "sub": 0b0100000,    # Para distinguir de ADD
    "sra": 0b0100000     # Para distinguir de SRL
}
```

#### `REGISTROS: Dict[str, int]`

Mapeo completo de nombres de registros a números:

```python
{
    # Registros numéricos
    'x0': 0, 'x1': 1, ..., 'x31': 31,

    # Nombres ABI
    'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3,
    'a0': 10, 'a1': 11, 's0': 8, 'fp': 8, ...
}
```

### Uso de las Constantes

```python
from isa import riscv

# Verificar formato de instrucción
formato = riscv.MNEMONICO_A_FORMATO.get('add')  # 'R'

# Obtener opcode
opcode = riscv.OPCODE['R']  # 0b0110011

# Convertir registro
num_reg = riscv.REGISTROS['ra']  # 1

# Verificar si es instrucción válida
es_valida = 'add' in riscv.MNEMONICO_A_FORMATO  # True
```

## 📄 Módulo file_writer

Utilidades para escribir archivos de salida.

### Funciones

#### `escribir_binario(codigo_maquina: bytearray, archivo: str) -> None`

Escribe el código máquina en formato binario.

**Parámetros:**

- `codigo_maquina`: Bytearray con el código máquina
- `archivo`: Ruta del archivo de salida (sin extensión)

**Ejemplo:**

```python
from utils.file_writer import escribir_binario

codigo = bytearray([0x93, 0x00, 0xa0, 0x00])
escribir_binario(codigo, "programa")  # Crea programa.bin
```

#### `escribir_hexadecimal(codigo_maquina: bytearray, archivo: str) -> None`

Escribe el código máquina en formato hexadecimal legible.

**Parámetros:**

- `codigo_maquina`: Bytearray con el código máquina
- `archivo`: Ruta del archivo de salida (sin extensión)

**Formato de salida**: Cada instrucción (4 bytes) en una línea como hex de 8 dígitos.

**Ejemplo:**

```python
from utils.file_writer import escribir_hexadecimal

codigo = bytearray([0x93, 0x00, 0xa0, 0x00, 0x33, 0x01, 0x00, 0x00])
escribir_hexadecimal(codigo, "programa")  # Crea programa.hex
```

**Contenido de programa.hex:**

```
00a00093
00001033
```

## 💼 Ejemplos de Uso

### Ejemplo Completo: Ensamblador Personalizado

```python
from core.ensamblador import Ensamblador
from utils.file_writer import escribir_binario, escribir_hexadecimal

def ensamblar_archivo(archivo_entrada, archivo_salida):
    """Ensambla un archivo .asm y genera salidas binaria y hex."""

    # Leer archivo de entrada
    with open(archivo_entrada, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    # Crear ensamblador y procesar
    ensamblador = Ensamblador()
    codigo_maquina = ensamblador.ensamblar(lineas)

    if codigo_maquina:
        # Escribir archivos de salida
        escribir_binario(codigo_maquina, archivo_salida)
        escribir_hexadecimal(codigo_maquina, archivo_salida)

        print(f"Ensamblado exitoso:")
        print(f"  - {archivo_salida}.bin ({len(codigo_maquina)} bytes)")
        print(f"  - {archivo_salida}.hex")

        # Mostrar tabla de símbolos
        if ensamblador.tabla_de_simbolos:
            print("Tabla de símbolos:")
            for simbolo, direccion in ensamblador.tabla_de_simbolos.items():
                print(f"  {simbolo}: 0x{direccion:08x}")
    else:
        print("Ensamblado fallido. Ver errores arriba.")

# Uso
ensamblar_archivo("mi_programa.asm", "mi_programa")
```

### Ejemplo: Validación de Sintaxis

```python
from core.ensamblador import Ensamblador

def validar_sintaxis(lineas_codigo):
    """Valida la sintaxis sin generar código máquina."""

    ensamblador = Ensamblador()

    # Solo ejecutar primera pasada
    ensamblador._primera_pasada(lineas_codigo)

    if ensamblador.manejador_errores.tiene_errores():
        print("Errores de sintaxis encontrados:")
        return False
    else:
        print("Sintaxis válida")
        return True

# Uso
codigo = [
    "main:",
    "    addi x1, x0, 10",
    "    invalid_instruction x2, x3"  # Error intencional
]

es_valido = validar_sintaxis(codigo)
```

### Ejemplo: Análisis de Instrucciones

```python
from isa import pseudo_instrucciones, riscv

def analizar_instruccion(mnemonico, operandos):
    """Analiza una instrucción y muestra información detallada."""

    print(f"Analizando: {mnemonico} {', '.join(operandos)}")

    # Verificar si es pseudo-instrucción
    if pseudo_instrucciones.es_pseudo(mnemonico):
        print("  Tipo: Pseudo-instrucción")
        expansiones = pseudo_instrucciones.expandir(mnemonico, operandos)
        print("  Expansión:")
        for i, (mnem, ops) in enumerate(expansiones, 1):
            print(f"    {i}. {mnem} {', '.join(ops)}")
    else:
        # Verificar si es instrucción base
        formato = riscv.MNEMONICO_A_FORMATO.get(mnemonico)
        if formato:
            print(f"  Tipo: Instrucción base (formato {formato})")
            print(f"  Opcode: 0x{riscv.OPCODE.get(formato, 0):02x}")
            if mnemonico in riscv.FUNC3:
                print(f"  FUNC3: 0b{riscv.FUNC3[mnemonico]:03b}")
        else:
            print("  Tipo: Instrucción desconocida")

# Uso
analizar_instruccion("li", ["x1", "1000"])
analizar_instruccion("add", ["x1", "x2", "x3"])
```

Esta API proporciona todas las herramientas necesarias para ensamblar código RISC-V, manejar errores, y extender la funcionalidad según las necesidades específicas.
