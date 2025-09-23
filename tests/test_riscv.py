"""
Tests unitarios para el módulo riscv.
"""
import unittest
import sys
import os

# Añadir el directorio padre al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from isa import riscv


class TestRiscv(unittest.TestCase):
    """Tests para el módulo riscv."""
    
    def test_formatos_instruccion_completitud(self):
        """Test que verifica que todos los formatos están definidos."""
        formatos_esperados = ['R', 'I', 'S', 'B', 'U', 'J']
        for formato in formatos_esperados:
            with self.subTest(formato=formato):
                self.assertIn(formato, riscv.FORMATOS_INSTRUCCION)
                self.assertIsInstance(riscv.FORMATOS_INSTRUCCION[formato], list)
                self.assertGreater(len(riscv.FORMATOS_INSTRUCCION[formato]), 0)
    
    def test_mnemonico_a_formato_consistencia(self):
        """Test que verifica la consistencia entre FORMATOS_INSTRUCCION y MNEMONICO_A_FORMATO."""
        # Todos los mnemónicos en FORMATOS_INSTRUCCION deben estar en MNEMONICO_A_FORMATO
        for formato, mnemónicos in riscv.FORMATOS_INSTRUCCION.items():
            for mnem in mnemónicos:
                with self.subTest(mnemonico=mnem):
                    self.assertIn(mnem, riscv.MNEMONICO_A_FORMATO)
                    self.assertEqual(riscv.MNEMONICO_A_FORMATO[mnem], formato)
    
    def test_mnemonico_a_formato_no_duplicados(self):
        """Test que verifica que no hay mnemónicos duplicados en diferentes formatos."""
        todos_mnemonicos = []
        for lista_mnem in riscv.FORMATOS_INSTRUCCION.values():
            todos_mnemonicos.extend(lista_mnem)
        
        # No debe haber duplicados
        self.assertEqual(len(todos_mnemonicos), len(set(todos_mnemonicos)))
    
    def test_opcodes_definidos(self):
        """Test que verifica que todos los opcodes necesarios están definidos."""
        opcodes_esperados = ['R', 'I', 'L', 'S', 'B', 'J', 'U', 'auipc', 'jalr', 'SYSTEM']
        for opcode in opcodes_esperados:
            with self.subTest(opcode=opcode):
                self.assertIn(opcode, riscv.OPCODE)
                self.assertIsInstance(riscv.OPCODE[opcode], int)
                # Los opcodes deben estar en el rango válido de 7 bits
                self.assertGreaterEqual(riscv.OPCODE[opcode], 0)
                self.assertLessEqual(riscv.OPCODE[opcode], 0b1111111)
    
    def test_func3_para_instrucciones_tipo_r(self):
        """Test que verifica que todas las instrucciones tipo R tienen func3 definido."""
        instrucciones_r = riscv.FORMATOS_INSTRUCCION['R']
        for instr in instrucciones_r:
            with self.subTest(instruccion=instr):
                self.assertIn(instr, riscv.FUNC3)
                self.assertIsInstance(riscv.FUNC3[instr], int)
                # func3 debe ser de 3 bits
                self.assertGreaterEqual(riscv.FUNC3[instr], 0)
                self.assertLessEqual(riscv.FUNC3[instr], 0b111)
    
    def test_func3_para_instrucciones_tipo_i(self):
        """Test que verifica que todas las instrucciones tipo I tienen func3 definido."""
        instrucciones_i = riscv.FORMATOS_INSTRUCCION['I']
        for instr in instrucciones_i:
            with self.subTest(instruccion=instr):
                self.assertIn(instr, riscv.FUNC3)
                self.assertIsInstance(riscv.FUNC3[instr], int)
                # func3 debe ser de 3 bits
                self.assertGreaterEqual(riscv.FUNC3[instr], 0)
                self.assertLessEqual(riscv.FUNC3[instr], 0b111)
    
    def test_func7_solo_para_instrucciones_necesarias(self):
        """Test que verifica que func7 está definido solo para las instrucciones que lo necesitan."""
        # Solo sub y sra necesitan func7 diferente de 0
        instrucciones_con_func7 = ['sub', 'sra']
        for instr in instrucciones_con_func7:
            with self.subTest(instruccion=instr):
                self.assertIn(instr, riscv.FUNC7)
                self.assertIsInstance(riscv.FUNC7[instr], int)
                # func7 debe ser de 7 bits
                self.assertGreaterEqual(riscv.FUNC7[instr], 0)
                self.assertLessEqual(riscv.FUNC7[instr], 0b1111111)
    
    def test_registros_numericos(self):
        """Test que verifica que todos los registros x0-x31 están definidos."""
        for i in range(32):
            reg_name = f'x{i}'
            with self.subTest(registro=reg_name):
                self.assertIn(reg_name, riscv.REGISTROS)
                self.assertEqual(riscv.REGISTROS[reg_name], i)
    
    def test_registros_abi(self):
        """Test que verifica que los registros ABI están correctamente mapeados."""
        registros_abi_esperados = {
            'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
            't0': 5, 't1': 6, 't2': 7, 's0': 8, 'fp': 8, 's1': 9,
            'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14,
            'a5': 15, 'a6': 16, 'a7': 17, 's2': 18, 's3': 19,
            's4': 20, 's5': 21, 's6': 22, 's7': 23, 's8': 24,
            's9': 25, 's10': 26, 's11': 27, 't3': 28, 't4': 29,
            't5': 30, 't6': 31
        }
        
        for reg_abi, numero in registros_abi_esperados.items():
            with self.subTest(registro=reg_abi):
                self.assertIn(reg_abi, riscv.REGISTROS)
                self.assertEqual(riscv.REGISTROS[reg_abi], numero)
    
    def test_registros_duales(self):
        """Test que verifica que s0 y fp apuntan al mismo registro."""
        self.assertEqual(riscv.REGISTROS['s0'], riscv.REGISTROS['fp'])
        self.assertEqual(riscv.REGISTROS['s0'], 8)
    
    def test_total_registros(self):
        """Test que verifica el número total de entradas en REGISTROS."""
        # 32 registros x0-x31 + 33 nombres ABI (s0 y fp son entradas separadas aunque apunten al mismo registro)
        total_esperado = 32 + 33
        self.assertEqual(len(riscv.REGISTROS), total_esperado)
    
    def test_instrucciones_carga_en_formato_i(self):
        """Test que verifica que las instrucciones de carga están en formato I."""
        instrucciones_carga = ['lb', 'lh', 'lw', 'lbu', 'lhu']
        for instr in instrucciones_carga:
            with self.subTest(instruccion=instr):
                self.assertIn(instr, riscv.FORMATOS_INSTRUCCION['I'])
                self.assertEqual(riscv.MNEMONICO_A_FORMATO[instr], 'I')
    
    def test_instrucciones_almacenamiento_en_formato_s(self):
        """Test que verifica que las instrucciones de almacenamiento están en formato S."""
        instrucciones_store = ['sb', 'sh', 'sw']
        for instr in instrucciones_store:
            with self.subTest(instruccion=instr):
                self.assertIn(instr, riscv.FORMATOS_INSTRUCCION['S'])
                self.assertEqual(riscv.MNEMONICO_A_FORMATO[instr], 'S')
    
    def test_instrucciones_salto_en_formato_b(self):
        """Test que verifica que las instrucciones de salto están en formato B."""
        instrucciones_branch = ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']
        for instr in instrucciones_branch:
            with self.subTest(instruccion=instr):
                self.assertIn(instr, riscv.FORMATOS_INSTRUCCION['B'])
                self.assertEqual(riscv.MNEMONICO_A_FORMATO[instr], 'B')


if __name__ == '__main__':
    unittest.main()