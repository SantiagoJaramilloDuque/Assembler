"""
Tests unitarios para el módulo de directivas simplificado.
Prueba el manejo de .text, .data y .word únicamente con enteros.
"""
import unittest
import sys
import os

# Agregar el directorio padre al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.directivas import ManejadorDirectivas, TipoSegmento

class TestDirectivas(unittest.TestCase):
    """Tests para el manejador de directivas simplificado."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.manejador = ManejadorDirectivas()
    
    def test_inicializacion(self):
        """Test de inicialización del manejador."""
        self.assertEqual(self.manejador.segmento_actual, TipoSegmento.TEXT)
        self.assertEqual(self.manejador.obtener_direccion_actual(), 0x00000000)
        self.assertTrue(self.manejador.esta_en_segmento_texto())
        self.assertFalse(self.manejador.esta_en_segmento_datos())
    
    def test_reconocimiento_directivas(self):
        """Test de reconocimiento de directivas válidas."""
        self.assertTrue(self.manejador.es_directiva(".text"))
        self.assertTrue(self.manejador.es_directiva(".data"))
        self.assertTrue(self.manejador.es_directiva(".word 10"))
        self.assertFalse(self.manejador.es_directiva("add x1, x2, x3"))
        self.assertFalse(self.manejador.es_directiva("main:"))
    
    def test_cambio_segmento_text(self):
        """Test de cambio al segmento .text."""
        error = self.manejador.procesar_directiva(".text", 1)
        self.assertIsNone(error)
        self.assertEqual(self.manejador.segmento_actual, TipoSegmento.TEXT)
        self.assertTrue(self.manejador.esta_en_segmento_texto())
    
    def test_cambio_segmento_data(self):
        """Test de cambio al segmento .data."""
        error = self.manejador.procesar_directiva(".data", 1)
        self.assertIsNone(error)
        self.assertEqual(self.manejador.segmento_actual, TipoSegmento.DATA)
        self.assertTrue(self.manejador.esta_en_segmento_datos())
        self.assertEqual(self.manejador.obtener_direccion_actual(), 0x10000000)
    
    def test_directiva_word_valida(self):
        """Test de procesamiento de .word con valores válidos."""
        # Cambiar a segmento .data primero
        self.manejador.procesar_directiva(".data", 1)
        
        # Probar con un entero positivo
        error = self.manejador.procesar_directiva(".word 42", 2)
        self.assertIsNone(error)
        
        # Verificar que se agregó al segmento de datos
        datos = self.manejador.obtener_segmento_datos()
        self.assertEqual(len(datos), 4)  # 4 bytes para un word
        
        # Verificar el valor (little-endian)
        valor = int.from_bytes(datos[0:4], byteorder='little', signed=True)
        self.assertEqual(valor, 42)
    
    def test_directiva_word_multiple_valores(self):
        """Test de .word con múltiples valores."""
        self.manejador.procesar_directiva(".data", 1)
        
        error = self.manejador.procesar_directiva(".word 10, 20, -5", 2)
        self.assertIsNone(error)
        
        datos = self.manejador.obtener_segmento_datos()
        self.assertEqual(len(datos), 12)  # 3 words = 12 bytes
        
        # Verificar los valores
        valor1 = int.from_bytes(datos[0:4], byteorder='little', signed=True)
        valor2 = int.from_bytes(datos[4:8], byteorder='little', signed=True)
        valor3 = int.from_bytes(datos[8:12], byteorder='little', signed=True)
        
        self.assertEqual(valor1, 10)
        self.assertEqual(valor2, 20)
        self.assertEqual(valor3, -5)
    
    def test_directiva_word_hexadecimal(self):
        """Test de .word con valores hexadecimales."""
        self.manejador.procesar_directiva(".data", 1)
        
        error = self.manejador.procesar_directiva(".word 0xFF, 0x100", 2)
        self.assertIsNone(error)
        
        datos = self.manejador.obtener_segmento_datos()
        valor1 = int.from_bytes(datos[0:4], byteorder='little', signed=True)
        valor2 = int.from_bytes(datos[4:8], byteorder='little', signed=True)
        
        self.assertEqual(valor1, 255)
        self.assertEqual(valor2, 256)
    
    def test_directiva_word_fuera_de_segmento_data(self):
        """Test de error al usar .word fuera del segmento .data."""
        # Por defecto estamos en .text
        error = self.manejador.procesar_directiva(".word 10", 1)
        self.assertIsNotNone(error)
        self.assertIn("solo válida en segmento .data", error)
    
    def test_directiva_word_valor_decimal_rechazado(self):
        """Test de rechazo de valores decimales en .word."""
        self.manejador.procesar_directiva(".data", 1)
        
        error = self.manejador.procesar_directiva(".word 3.14", 2)
        self.assertIsNotNone(error)
        self.assertIn("Solo se permiten enteros", error)
    
    def test_directiva_word_valor_fuera_de_rango(self):
        """Test de error con valores fuera del rango de 32 bits."""
        self.manejador.procesar_directiva(".data", 1)
        
        # Valor demasiado grande
        error = self.manejador.procesar_directiva(".word 2147483648", 2)
        self.assertIsNotNone(error)
        self.assertIn("fuera de rango", error)
        
        # Valor demasiado pequeño
        error = self.manejador.procesar_directiva(".word -2147483649", 3)
        self.assertIsNotNone(error)
        self.assertIn("fuera de rango", error)

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()