"""
Tests unitarios para validación de sintaxis general del ensamblador.
"""
import unittest
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ensamblador import Ensamblador

class TestValidacionSintaxis(unittest.TestCase):
    """Tests para la validación de sintaxis general."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.ensamblador = Ensamblador()
    
    def test_caracteres_invalidos(self):
        """Test para detectar caracteres inválidos."""
        linea = "add $x1, x2, x3"  # Carácter $ no válido
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNotNone(error)
        self.assertIn("Caracteres inválidos", error)
    
    def test_espacios_multiples(self):
        """Test para detectar espacios múltiples."""
        linea = "add  x1, x2, x3"  # Doble espacio
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNotNone(error)
        self.assertIn("Múltiples espacios consecutivos", error)
    
    def test_comas_multiples(self):
        """Test para detectar comas múltiples."""
        linea = "add x1,, x2, x3"  # Doble coma
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNotNone(error)
        self.assertIn("Múltiples comas consecutivas", error)
    
    def test_mnemonico_invalido(self):
        """Test para detectar mnemónicos inválidos."""
        linea = "123add x1, x2, x3"  # Mnemónico que empieza con número
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNotNone(error)
        self.assertIn("Mnemónico inválido", error)
    
    def test_operandos_coma_inicial(self):
        """Test para detectar coma al inicio de operandos."""
        linea = "add ,x1, x2, x3"  # Coma al inicio
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNotNone(error)
        self.assertIn("no pueden empezar o terminar con coma", error)
    
    def test_operandos_coma_final(self):
        """Test para detectar coma al final de operandos."""
        linea = "add x1, x2, x3,"  # Coma al final
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNotNone(error)
        self.assertIn("no pueden empezar o terminar con coma", error)
    
    def test_parentesis_no_balanceados(self):
        """Test para detectar paréntesis no balanceados."""
        linea = "lw x1, 4(sp"  # Falta paréntesis de cierre
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNotNone(error)
        self.assertIn("Paréntesis no balanceados", error)
    
    def test_operando_vacio(self):
        """Test para detectar operandos vacíos."""
        linea = "add x1, , x3"  # Operando vacío en el medio
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNotNone(error)
        self.assertIn("está vacío", error)
    
    def test_registro_fuera_de_rango(self):
        """Test para detectar registros fuera de rango."""
        linea = "add x32, x1, x2"  # x32 no existe (máximo es x31)
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNotNone(error)
        self.assertIn("fuera de rango", error)
    
    def test_registro_formato_invalido(self):
        """Test para detectar formato de registro inválido."""
        linea = "add x1@invalid, x1, x2"  # registro con carácter inválido
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNotNone(error)
        self.assertIn("formato no reconocido", error)
    
    def test_sintaxis_valida_instruccion_simple(self):
        """Test para instrucción simple válida."""
        linea = "add x1, x2, x3"
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNone(error)
    
    def test_sintaxis_valida_load_store(self):
        """Test para instrucciones de load/store válidas."""
        linea = "lw x1, 4(sp)"
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNone(error)
    
    def test_sintaxis_valida_inmediatos(self):
        """Test para inmediatos en diferentes formatos."""
        lineas_validas = [
            "addi x1, x2, 100",        # Decimal
            "addi x1, x2, -50",        # Decimal negativo
            "addi x1, x2, 0x1000",     # Hexadecimal
            "addi x1, x2, -0xFF",      # Hexadecimal negativo
            "addi x1, x2, 0b1010",     # Binario
            "addi x1, x2, 0o777"       # Octal
        ]
        
        for linea in lineas_validas:
            with self.subTest(linea=linea):
                error = self.ensamblador._validar_sintaxis_general(linea, 1)
                self.assertIsNone(error)
    
    def test_sintaxis_valida_hi_lo(self):
        """Test para funciones %hi y %lo válidas."""
        lineas_validas = [
            "lui x1, %hi(etiqueta)",
            "addi x1, x1, %lo(etiqueta)"
        ]
        
        for linea in lineas_validas:
            with self.subTest(linea=linea):
                error = self.ensamblador._validar_sintaxis_general(linea, 1)
                self.assertIsNone(error)
    
    def test_sintaxis_valida_registros_nombre(self):
        """Test para registros con nombres estándar."""
        linea = "add sp, ra, zero"
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNone(error)
    
    def test_acceso_memoria_registro_invalido(self):
        """Test para registro inválido en acceso a memoria."""
        linea = "lw x1, 4(x32)"  # x32 no existe
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNotNone(error)
        self.assertIn("fuera de rango", error)
    
    def test_acceso_memoria_offset_invalido(self):
        """Test para offset inválido en acceso a memoria."""
        linea = "lw x1, abc#def(sp)"  # offset con carácter # inválido
        error = self.ensamblador._validar_sintaxis_general(linea, 1)
        self.assertIsNotNone(error)
        self.assertIn("Caracteres inválidos", error)
    
    def test_instruccion_sin_operandos_valida(self):
        """Test para instrucciones sin operandos válidas."""
        lineas_validas = ["nop", "ret", "ecall", "ebreak"]
        
        for linea in lineas_validas:
            with self.subTest(linea=linea):
                error = self.ensamblador._validar_sintaxis_general(linea, 1)
                self.assertIsNone(error)

if __name__ == '__main__':
    unittest.main()