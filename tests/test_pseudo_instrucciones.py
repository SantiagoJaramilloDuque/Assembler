"""
Tests unitarios para el módulo pseudo_instrucciones.
"""
import unittest
import sys
import os

# Añadir el directorio padre al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from isa import pseudo_instrucciones


class TestPseudoInstrucciones(unittest.TestCase):
    """Tests para el módulo pseudo_instrucciones."""
    
    def test_es_pseudo_instrucciones_conocidas(self):
        """Test que identifica correctamente las pseudo-instrucciones conocidas."""
        # Pseudo-instrucciones que deben ser reconocidas
        pseudo_conocidas = ['nop', 'mv', 'not', 'neg', 'j', 'ret', 'call', 'li', 
                           'seqz', 'snez', 'sltz', 'sgtz', 'jr', 'beqz', 'bnez', 
                           'bltz', 'bgez', 'blez', 'bgtz']
        
        for pseudo in pseudo_conocidas:
            with self.subTest(pseudo=pseudo):
                self.assertTrue(pseudo_instrucciones.es_pseudo(pseudo))
    
    def test_es_pseudo_instrucciones_no_conocidas(self):
        """Test que no identifica como pseudo-instrucciones las instrucciones base."""
        instrucciones_base = ['add', 'sub', 'and', 'or', 'xor', 'addi', 'lw', 'sw', 'beq', 'jal']
        
        for inst in instrucciones_base:
            with self.subTest(instruccion=inst):
                self.assertFalse(pseudo_instrucciones.es_pseudo(inst))
    
    def test_expandir_nop(self):
        """Test expansión de nop."""
        resultado = pseudo_instrucciones.expandir('nop', [])
        esperado = [('addi', ['x0', 'x0', '0'])]
        self.assertEqual(resultado, esperado)
    
    def test_expandir_mv(self):
        """Test expansión de mv."""
        resultado = pseudo_instrucciones.expandir('mv', ['x1', 'x2'])
        esperado = [('addi', ['x1', 'x2', '0'])]
        self.assertEqual(resultado, esperado)
    
    def test_expandir_not(self):
        """Test expansión de not."""
        resultado = pseudo_instrucciones.expandir('not', ['x1', 'x2'])
        esperado = [('xori', ['x1', 'x2', '-1'])]
        self.assertEqual(resultado, esperado)
    
    def test_expandir_neg(self):
        """Test expansión de neg."""
        resultado = pseudo_instrucciones.expandir('neg', ['x1', 'x2'])
        esperado = [('sub', ['x1', 'x0', 'x2'])]
        self.assertEqual(resultado, esperado)
    
    def test_expandir_j(self):
        """Test expansión de j."""
        resultado = pseudo_instrucciones.expandir('j', ['etiqueta'])
        esperado = [('jal', ['x0', 'etiqueta'])]
        self.assertEqual(resultado, esperado)
    
    def test_expandir_jal_un_operando(self):
        """Test expansión de jal con un operando."""
        resultado = pseudo_instrucciones.expandir('jal', ['etiqueta'])
        esperado = [('jal', ['ra', 'etiqueta'])]
        self.assertEqual(resultado, esperado)
    
    def test_expandir_ret(self):
        """Test expansión de ret."""
        resultado = pseudo_instrucciones.expandir('ret', [])
        esperado = [('jalr', ['x0', 'ra', '0'])]
        self.assertEqual(resultado, esperado)
    
    def test_expandir_call(self):
        """Test expansión de call."""
        resultado = pseudo_instrucciones.expandir('call', ['funcion'])
        esperado = [('auipc', ['ra', '%hi(funcion)']),
                   ('jalr', ['ra', '%lo(funcion)(ra)'])]
        self.assertEqual(resultado, esperado)
    
    def test_expandir_comparaciones_cero(self):
        """Test expansión de comparaciones con cero."""
        casos = [
            ('seqz', ['x1', 'x2'], [('sltiu', ['x1', 'x2', '1'])]),
            ('snez', ['x1', 'x2'], [('sltu', ['x1', 'x0', 'x2'])]),
            ('sltz', ['x1', 'x2'], [('slt', ['x1', 'x2', 'x0'])]),
            ('sgtz', ['x1', 'x2'], [('slt', ['x1', 'x0', 'x2'])])
        ]
        
        for mnemonico, operandos, esperado in casos:
            with self.subTest(mnemonico=mnemonico):
                resultado = pseudo_instrucciones.expandir(mnemonico, operandos)
                self.assertEqual(resultado, esperado)
    
    def test_expandir_jr(self):
        """Test expansión de jr."""
        resultado = pseudo_instrucciones.expandir('jr', ['x1'])
        esperado = [('jalr', ['x0', 'x1', '0'])]
        self.assertEqual(resultado, esperado)
    
    def test_expandir_jalr_un_operando(self):
        """Test expansión de jalr con un operando."""
        resultado = pseudo_instrucciones.expandir('jalr', ['x1'])
        esperado = [('jalr', ['ra', 'x1', '0'])]
        self.assertEqual(resultado, esperado)
    
    def test_expandir_li_pequeno(self):
        """Test expansión de li con inmediato pequeño."""
        resultado = pseudo_instrucciones.expandir('li', ['x1', '100'])
        esperado = [('addi', ['x1', 'x0', '100'])]
        self.assertEqual(resultado, esperado)
    
    def test_expandir_li_grande(self):
        """Test expansión de li con inmediato grande."""
        resultado = pseudo_instrucciones.expandir('li', ['x1', '0x12345678'])
        # Debe usar lui + addi
        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0][0], 'lui')
        self.assertEqual(resultado[1][0], 'addi')
    
    def test_expandir_li_etiqueta(self):
        """Test expansión de li con etiqueta."""
        resultado = pseudo_instrucciones.expandir('li', ['x1', 'etiqueta'])
        esperado = [('auipc', ['x1', '%hi(etiqueta)']),
                   ('addi', ['x1', 'x1', '%lo(etiqueta)'])]
        self.assertEqual(resultado, esperado)
    
    def test_expandir_saltos_condicionales_cero(self):
        """Test expansión de saltos condicionales con cero."""
        casos = [
            ('beqz', ['x1', 'etiqueta'], [('beq', ['x1', 'x0', 'etiqueta'])]),
            ('bnez', ['x1', 'etiqueta'], [('bne', ['x1', 'x0', 'etiqueta'])]),
            ('bltz', ['x1', 'etiqueta'], [('blt', ['x1', 'x0', 'etiqueta'])]),
            ('bgez', ['x1', 'etiqueta'], [('bge', ['x1', 'x0', 'etiqueta'])])
        ]
        
        for mnemonico, operandos, esperado in casos:
            with self.subTest(mnemonico=mnemonico):
                resultado = pseudo_instrucciones.expandir(mnemonico, operandos)
                self.assertEqual(resultado, esperado)
    
    def test_expandir_instruccion_no_pseudo(self):
        """Test que las instrucciones no pseudo se devuelven sin cambios."""
        resultado = pseudo_instrucciones.expandir('add', ['x1', 'x2', 'x3'])
        esperado = [('add', ['x1', 'x2', 'x3'])]
        self.assertEqual(resultado, esperado)


if __name__ == '__main__':
    unittest.main()