# isa/pseudo_instrucciones.py
# -*- coding: utf-8 -*-
"""
Módulo para la expansión de pseudo-instrucciones de RISC-V a instrucciones base.
"""
from typing import List, Tuple

# Conjunto de pseudo-instrucciones conocidas para una rápida verificación.
PSEUDO_INSTRUCCIONES = {
    'nop', 'mv', 'not', 'neg', 'j', 'ret', 'call', 'li', 'seqz', 'snez',
    'sltz', 'sgtz', 'jr', 'beqz', 'bnez', 'bltz', 'bgez', 'blez', 'bgtz'
}

def es_pseudo(mnemonico: str) -> bool:
    """Verifica si un mnemónico corresponde a una pseudo-instrucción conocida."""
    return mnemonico in PSEUDO_INSTRUCCIONES

def expandir(mnemonico: str, operandos: List[str]) -> List[Tuple[str, List[str]]]:
    """
    Expande una pseudo-instrucción a una o más instrucciones base.
    Si no es una pseudo-instrucción, la devuelve tal cual.
    """
    if mnemonico == 'nop':
        return [('addi', ['x0', 'x0', '0'])]
    if mnemonico == 'mv':
        return [('addi', [operandos[0], operandos[1], '0'])]
    if mnemonico == 'not':
        return [('xori', [operandos[0], operandos[1], '-1'])]
    if mnemonico == 'neg':
        return [('sub', [operandos[0], 'x0', operandos[1]])]
    if mnemonico == 'j':
        return [('jal', ['x0', operandos[0]])]
    # 'jal' con un solo operando es una pseudo-instrucción para `jal ra, destino`
    if mnemonico == 'jal' and len(operandos) == 1:
        return [('jal', ['ra', operandos[0]])]
    if mnemonico == 'ret':
        return [('jalr', ['x0', 'ra', '0'])]
    if mnemonico == 'call':
        etiqueta = operandos[0]
        return [('auipc', ['ra', f'%hi({etiqueta})']),
                ('jalr', ['ra', f'%lo({etiqueta})(ra)'])]

    # Comparaciones con cero
    if mnemonico == 'seqz':
        return [('sltiu', [operandos[0], operandos[1], '1'])]
    if mnemonico == 'snez':
        return [('sltu', [operandos[0], 'x0', operandos[1]])]
    if mnemonico == 'sltz':
        return [('slt', [operandos[0], operandos[1], 'x0'])]
    if mnemonico == 'sgtz':
        return [('slt', [operandos[0], 'x0', operandos[1]])]

    # Saltos indirectos
    if mnemonico == 'jr':
        return [('jalr', ['x0', operandos[0], '0'])]
    # 'jalr' con un solo operando es una pseudo-instrucción
    if mnemonico == 'jalr' and len(operandos) == 1:
        return [('jalr', ['ra', operandos[0], '0'])]

    # Carga de inmediatos (li)
    if mnemonico == 'li':
        rd, inmediato_str = operandos
        
        # Validar que el inmediato no esté vacío
        if not inmediato_str or inmediato_str.strip() == '':
            raise ValueError(f"La pseudo-instrucción 'li' requiere un valor inmediato o etiqueta válida")
        
        try:
            inmediato = int(inmediato_str, 0)
            if -2048 <= inmediato < 2048:
                return [('addi', [rd, 'x0', str(inmediato)])]

            alta = (inmediato + 0x800) >> 12
            baja = inmediato & 0xFFF
            instrucciones = [('lui', [rd, str(alta)])]
            if baja != 0:
                instrucciones.append(('addi', [rd, rd, str(baja)]))
            return instrucciones
        except ValueError:
            # Si no es un número válido, verificar que sea una etiqueta válida
            if not inmediato_str.strip() or not inmediato_str.replace('_', '').isalnum():
                raise ValueError(f"Valor inmediato o etiqueta inválida: '{inmediato_str}'")
            # El "inmediato" es en realidad una etiqueta válida
            return [('auipc', [rd, f'%hi({inmediato_str})']),
                    ('addi', [rd, rd, f'%lo({inmediato_str})'])]

    # Saltos condicionales contra cero
    mapa_saltos = {
        'beqz': 'beq', 'bnez': 'bne', 'bltz': 'blt', 'bgez': 'bge'
    }
    if mnemonico in mapa_saltos:
        rs1, etiqueta = operandos
        return [(mapa_saltos[mnemonico], [rs1, 'x0', etiqueta])]

    # Devuelve la instrucción original si no es una pseudo-instrucción
    return [(mnemonico, operandos)]