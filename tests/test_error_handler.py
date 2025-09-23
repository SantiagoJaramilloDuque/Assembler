"""
Tests unitarios para la clase ErrorHandler.
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Añadir el directorio padre al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.error_handler import ErrorHandler


class TestErrorHandler(unittest.TestCase):
    """Tests para la clase ErrorHandler."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        # Usar patch para evitar imprimir en la consola durante los tests
        self.console_patcher = patch('core.error_handler.Console')
        self.mock_console = self.console_patcher.start()
        self.error_handler = ErrorHandler()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        self.console_patcher.stop()
    
    def test_inicializacion(self):
        """Test de inicialización correcta del ErrorHandler."""
        self.assertEqual(self.error_handler._error_count, 0)
        self.assertFalse(self.error_handler.tiene_errores())
    
    def test_reportar_error_incrementa_contador(self):
        """Test que reportar un error incrementa el contador."""
        self.error_handler.reportar(1, "Error de prueba", "código de prueba")
        self.assertEqual(self.error_handler._error_count, 1)
        self.assertTrue(self.error_handler.tiene_errores())
    
    def test_reportar_multiples_errores(self):
        """Test que reportar múltiples errores incrementa el contador correctamente."""
        self.error_handler.reportar(1, "Error 1", "línea 1")
        self.error_handler.reportar(2, "Error 2", "línea 2")
        self.error_handler.reportar(3, "Error 3", "línea 3")
        
        self.assertEqual(self.error_handler._error_count, 3)
        self.assertTrue(self.error_handler.tiene_errores())
    
    def test_reportar_sin_linea_original(self):
        """Test que reportar un error sin línea original funciona."""
        self.error_handler.reportar(5, "Error sin línea")
        self.assertEqual(self.error_handler._error_count, 1)
        self.assertTrue(self.error_handler.tiene_errores())
    
    def test_resumen_final_sin_errores(self):
        """Test que el resumen final sin errores funciona correctamente."""
        self.error_handler.resumen_final()
        # Verificar que se llamó print en la consola mock
        self.mock_console.return_value.print.assert_called()
    
    def test_resumen_final_con_errores(self):
        """Test que el resumen final con errores funciona correctamente."""
        self.error_handler.reportar(1, "Error de prueba")
        self.error_handler.resumen_final()
        # Verificar que se llamó print en la consola mock
        self.mock_console.return_value.print.assert_called()


if __name__ == '__main__':
    unittest.main()