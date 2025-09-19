# Guía de Testing

Esta documentación explica cómo ejecutar y agregar tests unitarios al ensamblador RISC-V, así como las mejores prácticas para el testing del proyecto.

## Tabla de Contenidos

- [Ejecutar Tests](#ejecutar-tests)
- [Estructura de Tests](#estructura-de-tests)
- [Escribir Nuevos Tests](#escribir-nuevos-tests)
- [Mejores Prácticas](#mejores-prácticas)
- [Cobertura de Tests](#cobertura-de-tests)
- [Debugging de Tests](#debugging-de-tests)
- [Integración Continua](#integración-continua)

## Ejecutar Tests

### Métodos de Ejecución

#### Opción 1: Script Dedicado (Recomendado)

```bash
cd Assembler
python tests/run_all_tests.py
```

#### Opción 2: Módulo unittest

```bash
# Todos los tests
python -m unittest discover tests -v

# Tests específicos por archivo
python -m unittest tests.test_ensamblador -v
python -m unittest tests.test_error_handler -v
python -m unittest tests.test_pseudo_instrucciones -v
python -m unittest tests.test_riscv -v

# Test específico por método
python -m unittest tests.test_ensamblador.TestEnsamblador.test_ensamblar_programa_simple_exitoso -v
```

#### Opción 3: Ejecutar archivo individual

```bash
python tests/test_ensamblador.py
python tests/test_error_handler.py
# etc...
```

### Salida Esperada

**Ejecución exitosa:**

```
test_ensamblar_con_etiquetas (tests.test_ensamblador.TestEnsamblador.test_ensamblar_con_etiquetas) ... ok
test_ensamblar_con_pseudo_instrucciones (tests.test_ensamblador.TestEnsamblador.test_ensamblar_con_pseudo_instrucciones) ... ok
test_ensamblar_instruccion_invalida (tests.test_ensamblador.TestEnsamblador.test_ensamblar_instruccion_invalida) ... ok
test_ensamblar_programa_simple_exitoso (tests.test_ensamblador.TestEnsamblador.test_ensamblar_programa_simple_exitoso) ... ok
...

----------------------------------------------------------------------
Ran 64 tests in 0.123s

OK
```

**Con errores:**

```
FAIL: test_total_registros (tests.test_riscv.TestRiscv.test_total_registros)
Test que verifica el número total de entradas en REGISTROS.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "tests\test_riscv.py", line 165, in test_total_registros
    self.assertEqual(len(riscv.REGISTROS), total_esperado)
AssertionError: 65 != 63

----------------------------------------------------------------------
Ran 64 tests in 0.098s

FAILED (failures=1)
```

## Estructura de Tests

### Organización de Archivos

```
tests/
├── __init__.py                    # Inicialización del paquete
├── run_all_tests.py              # Script ejecutor principal
├── test_ensamblador.py           # Tests del núcleo del ensamblador
├── test_error_handler.py         # Tests del manejo de errores
├── test_pseudo_instrucciones.py  # Tests de pseudo-instrucciones
└── test_riscv.py                 # Tests de definiciones ISA
```

### Patrón de Nombres

- **Archivos**: `test_<modulo>.py`
- **Clases**: `Test<ClaseATestear>`
- **Métodos**: `test_<funcionalidad_especifica>`

### Estructura Típica de un Test

```python
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Setup del path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modulo_a_testear import ClaseATestear

class TestClaseATestear(unittest.TestCase):
    """Tests para ClaseATestear."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.instancia = ClaseATestear()

    def tearDown(self):
        """Limpieza después de cada test."""
        pass

    def test_funcionalidad_basica(self):
        """Test de funcionalidad básica."""
        resultado = self.instancia.metodo()
        self.assertEqual(resultado, valor_esperado)

    def test_manejo_de_errores(self):
        """Test que verifica manejo correcto de errores."""
        with self.assertRaises(ValueError):
            self.instancia.metodo_que_debe_fallar()

if __name__ == '__main__':
    unittest.main()
```

## Escribir Nuevos Tests

### Ejemplo: Test para Nueva Pseudo-instrucción

Supongamos que queremos agregar la pseudo-instrucción `la` (load address):

#### 1. Primero, implementar la funcionalidad

**En `isa/pseudo_instrucciones.py`:**

```python
# Agregar 'la' al conjunto
PSEUDO_INSTRUCCIONES = {
    'nop', 'mv', 'not', 'neg', 'j', 'ret', 'call', 'li', 'la',  # <- Agregar 'la'
    'seqz', 'snez', 'sltz', 'sgtz', 'jr', 'beqz', 'bnez',
    'bltz', 'bgez', 'blez', 'bgtz'
}

# Agregar expansión en la función expandir()
def expandir(mnemonico: str, operandos: List[str]) -> List[Tuple[str, List[str]]]:
    # ... código existente ...

    # Agregar este bloque
    if mnemonico == 'la':
        rd, simbolo = operandos
        return [('auipc', [rd, f'%hi({simbolo})']),
                ('addi', [rd, rd, f'%lo({simbolo})'])]

    # ... resto del código ...
```

#### 2. Escribir tests para la nueva funcionalidad

**En `tests/test_pseudo_instrucciones.py`:**

```python
def test_es_pseudo_la(self):
    """Test que verifica que 'la' es reconocida como pseudo-instrucción."""
    self.assertTrue(pseudo_instrucciones.es_pseudo('la'))

def test_expandir_la(self):
    """Test expansión de la (load address)."""
    resultado = pseudo_instrucciones.expandir('la', ['x1', 'variable'])
    esperado = [('auipc', ['x1', '%hi(variable)']),
               ('addi', ['x1', 'x1', '%lo(variable)'])]
    self.assertEqual(resultado, esperado)
```

#### 3. Ejecutar los tests

```bash
python -m unittest tests.test_pseudo_instrucciones.TestPseudoInstrucciones.test_expandir_la -v
```

### Ejemplo: Test para Validación de Errores

**En `tests/test_ensamblador.py`:**

```python
def test_error_inmediato_fuera_de_rango(self):
    """Test que inmediatos fuera de rango generan error."""
    codigo = ["addi x1, x2, 5000"]  # Fuera del rango [-2048, 2047]
    resultado = self.ensamblador.ensamblar(codigo)

    self.assertIsNone(resultado)
    self.assertTrue(self.ensamblador.manejador_errores.tiene_errores())

def test_error_etiqueta_no_definida(self):
    """Test que etiquetas no definidas generan error."""
    codigo = ["j etiqueta_inexistente"]
    resultado = self.ensamblador.ensamblar(codigo)

    self.assertIsNone(resultado)
    self.assertTrue(self.ensamblador.manejador_errores.tiene_errores())
```

### Ejemplo: Test con Datos Parametrizados

```python
def test_expansion_saltos_condicionales_cero(self):
    """Test expansión de múltiples saltos condicionales con cero."""
    casos = [
        ('beqz', ['x1', 'etiqueta'], [('beq', ['x1', 'x0', 'etiqueta'])]),
        ('bnez', ['x2', 'loop'], [('bne', ['x2', 'x0', 'loop'])]),
        ('bltz', ['x3', 'negative'], [('blt', ['x3', 'x0', 'negative'])]),
        ('bgez', ['x4', 'positive'], [('bge', ['x4', 'x0', 'positive'])])
    ]

    for mnemonico, operandos, esperado in casos:
        with self.subTest(mnemonico=mnemonico):
            resultado = pseudo_instrucciones.expandir(mnemonico, operandos)
            self.assertEqual(resultado, esperado)
```

## 📏 Mejores Prácticas

### 1. Principios FIRST

- **Fast**: Tests rápidos (< 1 segundo cada uno)
- **Independent**: Tests independientes entre sí
- **Repeatable**: Mismos resultados en cualquier entorno
- **Self-Validating**: Resultado claro (pass/fail)
- **Timely**: Escritos junto con el código

### 2. Nomenclatura Descriptiva

```python
# ❌ Mal
def test_1(self):
    pass

# ✅ Bien
def test_ensamblar_instruccion_add_registros_validos(self):
    pass

# ✅ Muy bien
def test_ensamblar_add_con_registros_validos_genera_codigo_correcto(self):
    pass
```

### 3. Estructura AAA (Arrange-Act-Assert)

```python
def test_suma_dos_numeros(self):
    # Arrange (Preparar)
    ensamblador = Ensamblador()
    codigo = ["add x1, x2, x3"]

    # Act (Actuar)
    resultado = ensamblador.ensamblar(codigo)

    # Assert (Verificar)
    self.assertIsNotNone(resultado)
    self.assertEqual(len(resultado), 4)  # Una instrucción = 4 bytes
```

### 4. Un Concepto por Test

```python
# ❌ Test que verifica múltiples cosas
def test_ensamblador_completo(self):
    # Testa inicialización Y ensamblado Y errores...
    pass

# ✅ Tests separados por concepto
def test_inicializacion_correcta(self):
    # Solo testa inicialización
    pass

def test_ensamblar_instruccion_valida(self):
    # Solo testa ensamblado exitoso
    pass

def test_deteccion_error_instruccion_invalida(self):
    # Solo testa detección de errores
    pass
```

### 5. Uso de Mocks para Aislamiento

```python
class TestErrorHandler(unittest.TestCase):
    def setUp(self):
        # Mock Rich Console para evitar output durante tests
        self.console_patcher = patch('core.error_handler.Console')
        self.mock_console = self.console_patcher.start()
        self.error_handler = ErrorHandler()

    def tearDown(self):
        self.console_patcher.stop()
```

### 6. Tests de Casos Límite

```python
def test_inmediato_en_limites_validos(self):
    """Test inmediatos en los límites exactos."""
    casos_limites = [
        ("addi x1, x2, -2048", True),   # Límite inferior
        ("addi x1, x2, 2047", True),    # Límite superior
        ("addi x1, x2, -2049", False),  # Fuera del límite inferior
        ("addi x1, x2, 2048", False)    # Fuera del límite superior
    ]

    for codigo, debe_funcionar in casos_limites:
        with self.subTest(codigo=codigo):
            resultado = self.ensamblador.ensamblar([codigo])
            if debe_funcionar:
                self.assertIsNotNone(resultado)
            else:
                self.assertIsNone(resultado)
```

## Cobertura de Tests

### Verificar Cobertura

#### Instalar coverage.py

```bash
pip install coverage
```

#### Ejecutar con cobertura

```bash
# Ejecutar tests con cobertura
coverage run -m unittest discover tests

# Generar reporte en terminal
coverage report

# Generar reporte HTML
coverage html
```

#### Reporte de ejemplo

```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
core/__init__.py                      0      0   100%
core/ensamblador.py                 156     12    92%
core/error_handler.py                25      2    92%
isa/__init__.py                       0      0   100%
isa/pseudo_instrucciones.py          78      8    90%
isa/riscv.py                         15      0   100%
utils/__init__.py                     0      0   100%
utils/file_writer.py                 18      2    89%
-----------------------------------------------------
TOTAL                               292     24    92%
```

### Objetivos de Cobertura

- **Mínimo aceptable**: 80%
- **Objetivo**: 90%
- **Ideal**: 95%+ (sin perseguir 100% ciegamente)

## 🐛 Debugging de Tests

### Ejecutar un solo test con debug

```python
# Agregar breakpoint en el test
def test_problema_especifico(self):
    import pdb; pdb.set_trace()  # Breakpoint
    resultado = self.funcion_problematica()
    self.assertEqual(resultado, esperado)
```

### Ver output durante tests

```python
def test_con_debug_info(self):
    resultado = self.funcion()
    print(f"Debug: resultado = {resultado}")  # Se verá con -s
    self.assertEqual(resultado, esperado)
```

```bash
# Ejecutar con output visible
python -m unittest tests.test_modulo.TestClase.test_con_debug_info -s
```

### Logging en tests

```python
import logging

class TestConLogging(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def test_con_logs(self):
        self.logger.debug("Iniciando test")
        # ... código del test ...
        self.logger.debug("Test completado")
```

## Integración Continua

### GitHub Actions (Ejemplo)

**Archivo: `.github/workflows/tests.yml`**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.7, 3.8, 3.9, 3.10, 3.11]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v3
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install rich coverage

      - name: Run tests
        run: |
          python tests/run_all_tests.py

      - name: Run tests with coverage
        run: |
          coverage run -m unittest discover tests
          coverage report
          coverage xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Pre-commit Hook

**Archivo: `.git/hooks/pre-commit`**

```bash
#!/bin/bash
# Ejecutar tests antes de commit

echo "Ejecutando tests..."
python tests/run_all_tests.py

if [ $? -ne 0 ]; then
    echo "❌ Tests fallaron. Commit cancelado."
    exit 1
fi

echo "✅ Todos los tests pasaron."
exit 0
```

```bash
# Hacer ejecutable
chmod +x .git/hooks/pre-commit
```

## Métricas de Calidad

### Ejecutar análisis completo

**Script: `quality_check.py`**

```python
#!/usr/bin/env python3
import subprocess
import sys

def run_command(cmd, description):
    """Ejecuta comando y reporta resultado."""
    print(f"\n{'='*50}")
    print(f"Ejecutando: {description}")
    print(f"{'='*50}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Ejecuta verificaciones de calidad completas."""

    checks = [
        ("python tests/run_all_tests.py", "Ejecutando tests unitarios"),
        ("coverage run -m unittest discover tests", "Calculando cobertura"),
        ("coverage report", "Reporte de cobertura"),
    ]

    results = []
    for cmd, desc in checks:
        success = run_command(cmd, desc)
        results.append((desc, success))

    # Reporte final
    print(f"\n{'='*50}")
    print("RESUMEN DE CALIDAD")
    print(f"{'='*50}")

    for desc, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {desc}")

    failed = sum(1 for _, success in results if not success)

    if failed == 0:
        print(f"\n🎉 Todos los checks pasaron!")
        sys.exit(0)
    else:
        print(f"\nAtención: {failed} checks fallaron")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Esta guía proporciona todo lo necesario para ejecutar, escribir y mantener tests de alta calidad en el proyecto del ensamblador RISC-V.
