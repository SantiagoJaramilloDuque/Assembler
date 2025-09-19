# Arquitectura del Proyecto

Esta documentación describe la arquitectura interna del ensamblador RISC-V, explicando la responsabilidad de cada módulo y cómo interactúan entre sí.

## Visión General de la Arquitectura

El ensamblador sigue un diseño modular con separación clara de responsabilidades:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   assembler.py  │───▶│ core/           │───▶│ utils/          │
│   (Entry Point) │    │ (Logic Core)    │    │ (File Output)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ isa/            │
                       │ (ISA Definition)│
                       └─────────────────┘
```

## Módulos Principales

### 1. **assembler.py** - Punto de Entrada

**Responsabilidad**: Script principal que coordina todo el proceso de ensamblado.

```python
# Flujo principal
def main():
    1. Lee archivo .asm de entrada
    2. Instancia Ensamblador()
    3. Llama ensamblador.ensamblar(lineas)
    4. Escribe archivos de salida (.bin, .hex)
```

**Interacciones**:

- Lee archivo de entrada del sistema de archivos
- Usa `core.ensamblador.Ensamblador` para procesar
- Usa `utils.file_writer` para generar salidas

---

### 2. **core/ensamblador.py** - Núcleo del Ensamblador

**Responsabilidad**: Implementa la lógica principal del ensamblado de dos pasadas.

#### Clase `Ensamblador`

```python
class Ensamblador:
    def __init__(self):
        self.tabla_de_simbolos: Dict[str, int] = {}
        self.manejador_errores = ErrorHandler()
        self.segmento_texto: bytearray = bytearray()
        self.direccion_actual: int = 0
```

#### Flujo de Trabajo

```
ensamblar(lineas_codigo)
├── _primera_pasada(lineas_codigo)
│   ├── Analizar etiquetas
│   ├── Calcular direcciones
│   └── Construir tabla_de_simbolos
├── _segunda_pasada(lineas_codigo)
│   ├── Expandir pseudo-instrucciones
│   ├── Validar operandos
│   ├── Generar código máquina
│   └── Llenar segmento_texto
└── resumen_final()
```

#### Métodos por Tipo de Instrucción

- `_ensamblar_tipo_R()` - Instrucciones registro-registro
- `_ensamblar_tipo_I()` - Instrucciones con inmediato
- `_ensamblar_tipo_S()` - Instrucciones de almacenamiento
- `_ensamblar_tipo_B()` - Instrucciones de salto condicional
- `_ensamblar_tipo_U()` - Instrucciones de inmediato superior
- `_ensamblar_tipo_J()` - Instrucciones de salto

**Interacciones**:

- Usa `isa.riscv` para definiciones de la arquitectura
- Usa `isa.pseudo_instrucciones` para expansión
- Usa `core.error_handler` para reportar errores

---

### 3. **core/error_handler.py** - Manejo de Errores

**Responsabilidad**: Gestiona la recolección y visualización de errores.

#### Clase `ErrorHandler`

```python
class ErrorHandler:
    def reportar(self, num_linea, mensaje, linea_original=""):
        # Incrementa contador y muestra error formateado

    def tiene_errores(self) -> bool:
        # Indica si hay errores pendientes

    def resumen_final(self):
        # Muestra resumen final del proceso
```

#### Características

- **Formateo visual**: Usa Rich para paneles coloreados
- **Contexto completo**: Muestra línea problemática y número
- **Contador**: Mantiene registro de errores totales
- **No intrusivo**: No interrumpe el flujo, solo reporta

**Dependencias**:

- `rich.console` y `rich.panel` para formateo

---

### 4. **isa/riscv.py** - Definiciones RISC-V

**Responsabilidad**: Contiene todas las constantes y definiciones de la arquitectura RV32I.

#### Estructuras de Datos Principales

```python
# Mapeo de instrucciones a formatos
FORMATOS_INSTRUCCION: Dict[str, List[str]] = {
    'R': ["add", "sub", "sll", ...],
    'I': ["addi", "slli", ...],
    # ...
}

# Búsqueda rápida O(1)
MNEMONICO_A_FORMATO: Dict[str, str] = {...}

# Códigos de operación
OPCODE: Dict[str, int] = {
    'R': 0b0110011,
    'I': 0b0010011,
    # ...
}

# Códigos de función
FUNC3: Dict[str, int] = {...}
FUNC7: Dict[str, int] = {...}

# Registros (numéricos + ABI)
REGISTROS: Dict[str, int] = {
    'x0': 0, 'x1': 1, ...,
    'zero': 0, 'ra': 1, ...
}
```

#### Características

- **Datos estáticos**: Solo constantes, sin lógica
- **Búsqueda eficiente**: Diccionarios para O(1) lookup
- **Completo RV32I**: Todas las instrucciones base
- **ABI estándar**: Nombres de registros según especificación

---

### 5. **isa/pseudo_instrucciones.py** - Pseudo-instrucciones

**Responsabilidad**: Expande pseudo-instrucciones a instrucciones base.

#### Funciones Principales

```python
def es_pseudo(mnemonico: str) -> bool:
    # Verifica si es pseudo-instrucción

def expandir(mnemonico: str, operandos: List[str]) -> List[Tuple[str, List[str]]]:
    # Expande a una o más instrucciones base
```

#### Pseudo-instrucciones Soportadas

```python
PSEUDO_INSTRUCCIONES = {
    'nop', 'mv', 'not', 'neg', 'j', 'ret', 'call', 'li',
    'seqz', 'snez', 'sltz', 'sgtz', 'jr', 'beqz', 'bnez',
    'bltz', 'bgez', 'blez', 'bgtz'
}
```

#### Ejemplos de Expansión

- `nop` → `[('addi', ['x0', 'x0', '0'])]`
- `li rd, imm` → `[('lui', [...]), ('addi', [...])]` (para inmediatos grandes)
- `call label` → `[('auipc', [...]), ('jalr', [...])]`

---

### 6. **utils/file_writer.py** - Escritura de Archivos

**Responsabilidad**: Genera archivos de salida en diferentes formatos.

#### Funciones

```python
def escribir_binario(codigo_maquina: bytearray, archivo: str):
    # Escribe archivo .bin

def escribir_hexadecimal(codigo_maquina: bytearray, archivo: str):
    # Escribe archivo .hex formateado
```

---

### 7. **tests/** - Suite de Tests

**Responsabilidad**: Verificación automática de funcionalidad.

#### Estructura de Tests

```
tests/
├── test_ensamblador.py         # Tests del núcleo
├── test_error_handler.py       # Tests de manejo de errores
├── test_pseudo_instrucciones.py # Tests de expansión
├── test_riscv.py              # Tests de definiciones ISA
└── run_all_tests.py           # Ejecutor de todos los tests
```

## Flujo de Datos

### 1. Entrada

```
archivo.asm → assembler.py → List[str] (líneas)
```

### 2. Primera Pasada

```
List[str] → Ensamblador._primera_pasada() → tabla_de_simbolos
```

### 3. Segunda Pasada

```
List[str] + tabla_de_simbolos → _segunda_pasada() → bytearray (código máquina)
```

### 4. Salida

```
bytearray → file_writer → {archivo.bin, archivo.hex}
```

## Patrones de Diseño Utilizados

### 1. **Strategy Pattern** (Métodos de Ensamblado)

Cada tipo de instrucción tiene su propio método de ensamblado:

```python
formato = riscv.MNEMONICO_A_FORMATO[mnem]
ensamblador_fn = getattr(self, f'_ensamblar_tipo_{formato}')
```

### 2. **Template Method** (Proceso de Ensamblado)

El flujo general está definido en `ensamblar()`, con pasos específicos en métodos separados.

### 3. **Facade Pattern** (assembler.py)

Proporciona una interfaz simple para un sistema complejo.

### 4. **Singleton-like** (Definiciones ISA)

Los módulos `isa/` actúan como singletons de datos.

## Extensibilidad

### Agregar Nueva Instrucción

1. **isa/riscv.py**: Agregar a `FORMATOS_INSTRUCCION`, `FUNC3`, etc.
2. **core/ensamblador.py**: Implementar lógica específica si es necesario
3. **tests/**: Agregar tests de verificación

### Agregar Nueva Pseudo-instrucción

1. **isa/pseudo_instrucciones.py**:
   - Agregar a `PSEUDO_INSTRUCCIONES`
   - Implementar expansión en `expandir()`
2. **tests/test_pseudo_instrucciones.py**: Agregar tests

### Nuevo Formato de Salida

1. **utils/file_writer.py**: Agregar nueva función
2. **assembler.py**: Llamar nueva función
3. **tests/**: Verificar funcionalidad

## Métricas del Proyecto

- **Líneas de código**: ~800 líneas
- **Módulos**: 7 principales
- **Tests**: 60+ casos de prueba
- **Cobertura**: ~95% del código principal
- **Instrucciones soportadas**: 37 base + 19 pseudo
- **Formatos de instrucción**: 6 tipos (R, I, S, B, U, J)

Esta arquitectura modular permite fácil mantenimiento, testing independiente de componentes, y extensibilidad para futuras características.
