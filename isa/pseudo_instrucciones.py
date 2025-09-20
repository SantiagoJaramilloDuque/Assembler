"""
Módulo para la expansión de pseudo-instrucciones de RISC-V a instrucciones base.
"""

from typing import List, Tuple

# Conjunto de pseudo-instrucciones soportadas
PSEUDO_INSTRUCCIONES = {
    # Mover, negar, etc.
    'nop', 'li', 'mv', 'not', 'neg',
    'seqz', 'snez', 'sltz', 'sgtz',

    # Saltos condicionales contra cero
    'beqz', 'bnez', 'bltz', 'bgez', 'blez', 'bgtz',

    # Saltos condicionales entre registros
    'bgt', 'ble', 'bgtu', 'bleu',

    # Saltos incondicionales y llamadas
    'j', 'jal', 'jr', 'jalr', 'ret'
}


def es_pseudo(mnemonico: str) -> bool:
    """Verifica si un mnemónico corresponde a una pseudo-instrucción soportada."""
    return mnemonico in PSEUDO_INSTRUCCIONES


def expandir(mnemonico: str, operandos: List[str]) -> List[Tuple[str, List[str]]]:
    """
    Expande una pseudo-instrucción a una o más instrucciones base.
    Si no es pseudo-instrucción, la devuelve intacta.
    """
    # Si no es pseudo-instrucción, devolverla tal cual
    if mnemonico not in PSEUDO_INSTRUCCIONES:
        return [(mnemonico, operandos)]

    # ──────────────── Expansiones ────────────────

    # NOP → addi x0,x0,0
    if mnemonico == 'nop':
        return [('addi', ['x0', 'x0', '0'])]

    # mv rd, rs → addi rd, rs, 0
    if mnemonico == 'mv':
        return [('addi', [operandos[0], operandos[1], '0'])]

    # not rd, rs → xori rd, rs, -1
    if mnemonico == 'not':
        return [('xori', [operandos[0], operandos[1], '-1'])]

    # neg rd, rs → sub rd, x0, rs
    if mnemonico == 'neg':
        return [('sub', [operandos[0], 'x0', operandos[1]])]

    # Comparaciones con cero
    if mnemonico == 'seqz':
        return [('sltiu', [operandos[0], operandos[1], '1'])]
    if mnemonico == 'snez':
        return [('sltu', [operandos[0], 'x0', operandos[1]])]
    if mnemonico == 'sltz':
        return [('slt', [operandos[0], operandos[1], 'x0'])]
    if mnemonico == 'sgtz':
        return [('slt', [operandos[0], 'x0', operandos[1]])]

    # Saltos condicionales contra cero
    if mnemonico == 'beqz':
        return [('beq', [operandos[0], 'x0', operandos[1]])]
    if mnemonico == 'bnez':
        return [('bne', [operandos[0], 'x0', operandos[1]])]
    if mnemonico == 'bltz':
        return [('blt', [operandos[0], 'x0', operandos[1]])]
    if mnemonico == 'bgez':
        return [('bge', [operandos[0], 'x0', operandos[1]])]
    if mnemonico == 'blez':
        # blez rs, offset → bge x0, rs, offset
        return [('bge', ['x0', operandos[0], operandos[1]])]
    if mnemonico == 'bgtz':
        # bgtz rs, offset → blt x0, rs, offset
        return [('blt', ['x0', operandos[0], operandos[1]])]

    # Comparaciones entre registros
    if mnemonico == 'bgt':
        # bgt rs, rt, offset → blt rt, rs, offset
        return [('blt', [operandos[1], operandos[0], operandos[2]])]
    if mnemonico == 'ble':
        # ble rs, rt, offset → bge rt, rs, offset
        return [('bge', [operandos[1], operandos[0], operandos[2]])]
    if mnemonico == 'bgtu':
        # bgtu rs, rt, offset → bltu rt, rs, offset
        return [('bltu', [operandos[1], operandos[0], operandos[2]])]
    if mnemonico == 'bleu':
        # bleu rs, rt, offset → bgeu rt, rs, offset
        return [('bgeu', [operandos[1], operandos[0], operandos[2]])]

    # j offset → jal x0, offset
    if mnemonico == 'j':
        return [('jal', ['x0', operandos[0]])]

    # jal offset → jal ra, offset
    if mnemonico == 'jal':
        if len(operandos) == 1:
            return [('jal', ['ra', operandos[0]])]

    # jr rs → jalr x0, rs, 0
    if mnemonico == 'jr':
        return [('jalr', ['x0', operandos[0], '0'])]

    # jalr rs → jalr ra, rs, 0
    if mnemonico == 'jalr' and len(operandos) == 1:
        return [('jalr', ['ra', operandos[0], '0'])]

    # ret → jalr x0, ra, 0
    if mnemonico == 'ret':
        return [('jalr', ['x0', 'ra', '0'])]

    # li rd, imm → expandir inmediato en addi/lui+addi
    if mnemonico == 'li':
        rd, inmediato_str = operandos
        if not inmediato_str or inmediato_str.strip() == '':
            raise ValueError("La pseudo-instrucción 'li' requiere un inmediato o etiqueta")
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
            # Si es etiqueta, usar auipc + addi
            return [('auipc', [rd, f'%hi({inmediato_str})']),
                    ('addi', [rd, rd, f'%lo({inmediato_str})'])]

    # Si no se expandió nada (debería ser imposible si está en la lista)
    return [(mnemonico, operandos)]
