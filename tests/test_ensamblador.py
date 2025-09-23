"""
Tests unitarios para la clase Ensamblador.
"""
import unittest
from unittest.mock import patch
import sys
import os

# Añadir el directorio padre al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.ensamblador import Ensamblador


class TestEnsamblador(unittest.TestCase):
    """Tests para la clase Ensamblador."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        # Patch para evitar imprimir en consola durante tests
        self.console_patcher = patch('core.error_handler.Console')
        self.console_patcher.start()
        self.ensamblador = Ensamblador()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        self.console_patcher.stop()
    
    def test_inicializacion(self):
        """Test de inicialización correcta del Ensamblador."""
        self.assertEqual(self.ensamblador.tabla_de_simbolos, {})
        self.assertEqual(len(self.ensamblador.segmento_texto), 0)
        self.assertEqual(self.ensamblador.direccion_actual, 0)
        self.assertEqual(self.ensamblador.segmento_actual, ".text")
    
    def test_ensamblar_programa_simple_exitoso(self):
        """Test de ensamblado exitoso de un programa simple."""
        codigo = [
            "add x1, x2, x3",
            "addi x4, x5, 100"
        ]
        resultado = self.ensamblador.ensamblar(codigo)
        
        # Debe retornar un bytearray con código máquina
        self.assertIsInstance(resultado, bytearray)
        self.assertGreater(len(resultado), 0)
        # Cada instrucción son 4 bytes
        self.assertEqual(len(resultado), 8)
    
    def test_ensamblar_con_etiquetas(self):
        """Test de ensamblado con etiquetas."""
        codigo = [
            "main:",
            "    add x1, x2, x3",
            "    beq x1, x0, main"
        ]
        resultado = self.ensamblador.ensamblar(codigo)
        
        # Debe procesar correctamente las etiquetas
        self.assertIn("main", self.ensamblador.tabla_de_simbolos)
        self.assertEqual(self.ensamblador.tabla_de_simbolos["main"], 0)
        self.assertIsInstance(resultado, bytearray)
    
    def test_ensamblar_con_pseudo_instrucciones(self):
        """Test de ensamblado con pseudo-instrucciones."""
        codigo = [
            "nop",
            "mv x1, x2",
            "li x3, 1000"
        ]
        resultado = self.ensamblador.ensamblar(codigo)
        
        self.assertIsInstance(resultado, bytearray)
        self.assertGreater(len(resultado), 0)
    
    def test_ensamblar_instruccion_invalida(self):
        """Test que una instrucción inválida genera error."""
        codigo = ["instruccion_inexistente x1, x2"]
        resultado = self.ensamblador.ensamblar(codigo)
        
        # Debe retornar None por errores
        self.assertIsNone(resultado)
        self.assertTrue(self.ensamblador.manejador_errores.tiene_errores())
    
    def test_ensamblar_operandos_invalidos(self):
        """Test que operandos inválidos generan error."""
        codigo = ["add x1, x2"]  # Faltan operandos
        resultado = self.ensamblador.ensamblar(codigo)
        
        self.assertIsNone(resultado)
        self.assertTrue(self.ensamblador.manejador_errores.tiene_errores())
    
    def test_ensamblar_registro_invalido(self):
        """Test que un registro inválido genera error."""
        codigo = ["add x99, x2, x3"]  # x99 no existe
        resultado = self.ensamblador.ensamblar(codigo)
        
        self.assertIsNone(resultado)
        self.assertTrue(self.ensamblador.manejador_errores.tiene_errores())
    
    def test_validar_operandos_correctos(self):
        """Test de validación correcta de operandos."""
        # No debe lanzar excepción
        try:
            self.ensamblador._validar_operandos('add', ['x1', 'x2', 'x3'])
            self.ensamblador._validar_operandos('addi', ['x1', 'x2', '100'])
        except ValueError:
            self.fail("La validación de operandos correctos no debería fallar")
    
    def test_analizar_registro_valido(self):
        """Test de análisis correcto de registros válidos."""
        self.assertEqual(self.ensamblador._analizar_registro('x0'), 0)
        self.assertEqual(self.ensamblador._analizar_registro('x31'), 31)
        self.assertEqual(self.ensamblador._analizar_registro('zero'), 0)
        self.assertEqual(self.ensamblador._analizar_registro('ra'), 1)


if __name__ == '__main__':
    unittest.main()