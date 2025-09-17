# -*- coding: utf-8 -*-
"""
nucleo_ensamblador.py

Contiene la clase principal `Ensamblador` que implementa la lógica de ensamblado
de dos pasadas, incluyendo el análisis de operandos, la resolución de símbolos
y la expansión de pseudo-instrucciones.
"""
import re
from typing import List, Dict, Tuple, Union

# Importa todas las definiciones de la arquitectura desde el módulo local.
from definiciones_riscv import *

class Ensamblador:
    """
    Clase que encapsula la lógica de un ensamblador de dos pasadas para RV32I.
    """
    def __init__(self):
        self.tabla_de_simbolos: Dict[str, int] = {}
        self.segmento_texto: bytearray = bytearray()
        self.direccion_actual: int = 0
        
        # Diccionario despachador para llamar a la función de ensamblado correcta.
        self.manejadores_formato = {
            'R': self._ensamblar_tipo_R,
            'I': self._ensamblar_tipo_I,
            'S': self._ensamblar_tipo_S,
            'B': self._ensamblar_tipo_B,
            'U': self._ensamblar_tipo_U,
            'J': self._ensamblar_tipo_J,
        }

    def primera_pasada(self, lineas_codigo: List[str]) -> None:
        """Construye la tabla de símbolos."""
        self.direccion_actual = 0
        for linea in lineas_codigo:
            linea = linea.split('#')[0].strip()
            if not linea:
                continue

            match = re.match(r'(\w+):', linea)
            if match:
                self.tabla_de_simbolos[match.group(1)] = self.direccion_actual
                linea = linea[len(match.group(0)):].strip()
            if not linea:
                continue

            partes = linea.split(maxsplit=1)
            mnemonico = partes[0].lower()
            if mnemonico.startswith('.'):
                continue

            operandos = [op.strip() for op in partes[1].split(',')] if len(partes) > 1 else []
            inst_expandidas = self._expandir_pseudo_instrucciones(mnemonico, operandos)
            self.direccion_actual += len(inst_expandidas) * 4

    def segunda_pasada(self, lineas_codigo: List[str]) -> bool:
        """Genera el código máquina."""
        self.direccion_actual = 0
        for num_linea, linea in enumerate(lineas_codigo, 1):
            linea_original = linea.strip()
            linea = linea.split('#')[0].strip()

            match = re.match(r'(\w+):', linea)
            if match:
                linea = linea[len(match.group(0)):].strip()
            if not linea or linea.startswith('.'):
                continue

            partes = linea.split(maxsplit=1)
            mnemonico = partes[0].lower()
            operandos = [op.strip() for op in partes[1].split(',')] if len(partes) > 1 else []

            try:
                inst_expandidas = self._expandir_pseudo_instrucciones(mnemonico, operandos)
                for mnem, ops in inst_expandidas:
                    # Si el mnemónico no existe en RV32I, lanza error
                    if mnem not in MNEMONICO_A_FORMATO:
                        raise ValueError(f"Instrucción no soportada en RV32I: {mnem}")
                    codigo_maquina = self.ensamblar_instruccion(mnem, ops, self.direccion_actual)
                    self.segmento_texto.extend(codigo_maquina)
                    self.direccion_actual += 4
            except (ValueError, IndexError) as e:
                print(f"Error en la línea {num_linea}: '{linea_original}'\n  -> {e}")
                return False
        return True

    def ensamblar_instruccion(self, mnemonico: str, operandos: List[str], pc_actual: int) -> bytes:
        """Despacha al método de ensamblado correcto según el formato."""
        formato = MNEMONICO_A_FORMATO.get(mnemonico)
        if not formato:
            raise ValueError(f"Mnemónico desconocido: '{mnemonico}'")
        manejador = self.manejadores_formato[formato]
        instruccion = manejador(mnemonico, operandos, pc_actual)
        return instruccion.to_bytes(4, byteorder='little')

    # --- Métodos de Ensamblado por Formato ---
    def _ensamblar_tipo_R(self, mnem: str, ops: List[str], pc: int) -> int:
        rd, rs1, rs2 = map(self._analizar_operando, ops)
        func7 = FUNC7.get(mnem, 0)
        func3 = FUNC3[mnem]
        opcode = OPCODE['R']
        return (func7 << 25) | (rs2 << 20) | (rs1 << 15) | (func3 << 12) | (rd << 7) | opcode

    def _ensamblar_tipo_I(self, mnem: str, ops: List[str], pc: int) -> int:
        # Instrucciones especiales
        if mnem in ["ecall", "ebreak", "fence"]:
            imm = 1 if mnem == "ebreak" else 0
            return (imm << 20) | (0 << 15) | (FUNC3[mnem] << 12) | (0 << 7) | OPCODE['SYSTEM']

        rd = self._analizar_operando(ops[0])
        match_carga = re.match(r'(.+)\((.+)\)', ops[1])
        if match_carga:
            inmediato_str, rs1_str = match_carga.groups()
            rs1 = self._analizar_operando(rs1_str)
            opcode = OPCODE['L'] if mnem in ["lb", "lh", "lw", "lbu", "lhu"] else OPCODE['jalr']
        else:
            rs1 = self._analizar_operando(ops[1])
            inmediato_str = ops[2]
            opcode = OPCODE['I']
        inmediato = self._resolver_simbolo(inmediato_str, pc)
        return ((inmediato & 0xFFF) << 20) | (rs1 << 15) | (FUNC3[mnem] << 12) | (rd << 7) | opcode

    def _ensamblar_tipo_S(self, mnem: str, ops: List[str], pc: int) -> int:
        rs2_str, operando_memoria = ops
        match = re.match(r'(.+)\((.+)\)', operando_memoria)
        if not match:
            raise ValueError(f"Formato de 'store' inválido: '{operando_memoria}'")
        inmediato_str, rs1_str = match.groups()
        rs1 = self._analizar_operando(rs1_str)
        rs2 = self._analizar_operando(rs2_str)
        inmediato = self._resolver_simbolo(inmediato_str, pc)
        imm11_5, imm4_0 = (inmediato >> 5) & 0x7F, inmediato & 0x1F
        return (imm11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (FUNC3[mnem] << 12) | (imm4_0 << 7) | OPCODE['S']

    def _ensamblar_tipo_B(self, mnem: str, ops: List[str], pc: int) -> int:
        rs1, rs2 = map(self._analizar_operando, ops[:2])
        inmediato = self._resolver_simbolo(ops[2], pc, es_relativo=True)
        imm12, imm10_5 = (inmediato >> 12) & 1, (inmediato >> 5) & 0x3F
        imm4_1, imm11 = (inmediato >> 1) & 0xF, (inmediato >> 11) & 1
        return (imm12 << 31) | (imm10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (FUNC3[mnem] << 12) | (imm4_1 << 8) | (imm11 << 7) | OPCODE['B']

    def _ensamblar_tipo_U(self, mnem: str, ops: List[str], pc: int) -> int:
        rd = self._analizar_operando(ops[0])
        inmediato = self._resolver_simbolo(ops[1], pc)
        opcode = OPCODE['auipc'] if mnem == 'auipc' else OPCODE['U']
        return (inmediato << 12) | (rd << 7) | opcode

    def _ensamblar_tipo_J(self, mnem: str, ops: List[str], pc: int) -> int:
        rd = self._analizar_operando(ops[0])
        inmediato = self._resolver_simbolo(ops[1], pc, es_relativo=True)
        imm20, imm10_1 = (inmediato >> 20) & 1, (inmediato >> 1) & 0x3FF
        imm11, imm19_12 = (inmediato >> 11) & 1, (inmediato >> 12) & 0xFF
        inmediato_reordenado = (imm20 << 20) | (imm19_12 << 12) | (imm11 << 11) | (imm10_1 << 1)
        return (inmediato_reordenado & 0xFFFFF) | (rd << 7) | OPCODE['J']

    # --- Métodos de Ayuda ---
    def _analizar_operando(self, operando: str) -> Union[int, str]:
        operando = operando.strip().lower()
        if operando in REGISTROS:
            return REGISTROS[operando]
        try:
            return int(operando, 0)
        except ValueError:
            return operando

    def _resolver_simbolo(self, simbolo: str, pc_actual: int, es_relativo: bool = False) -> int:
        match_hi = re.match(r'%hi\((\w+)\)', simbolo)
        match_lo = re.match(r'%lo\((\w+)\)', simbolo)
        etiqueta = simbolo
        if match_hi:
            etiqueta = match_hi.group(1)
        if match_lo:
            etiqueta = match_lo.group(1)

        if etiqueta in self.tabla_de_simbolos:
            direccion_etiqueta = self.tabla_de_simbolos[etiqueta]
            if es_relativo:
                return direccion_etiqueta - pc_actual
            if match_hi:
                return ((direccion_etiqueta - pc_actual) + 0x800) >> 12
            if match_lo:
                return (direccion_etiqueta - pc_actual) & 0xFFF
            return direccion_etiqueta
        else:
            try:
                return int(simbolo, 0)
            except ValueError:
                raise ValueError(f"Símbolo no definido: '{simbolo}'")

    def _expandir_pseudo_instrucciones(self, mnem: str, ops: List[str]) -> List[Tuple[str, List[str]]]:
        if mnem == 'nop':
            return [('addi', ['x0', 'x0', '0'])]
        if mnem == 'mv':
            return [('addi', [ops[0], ops[1], '0'])]
        if mnem == 'not':
            return [('xori', [ops[0], ops[1], '-1'])]
        if mnem == 'neg':
            return [('sub', [ops[0], 'x0', ops[1]])]
        if mnem == 'j':
            return [('jal', ['x0', ops[0]])]
        if mnem == 'jal' and len(ops) == 1:
            return [('jal', ['ra', ops[0]])]
        if mnem == 'ret':
            return [('jalr', ['x0', 'ra', '0'])]
        if mnem == 'call':
            etiqueta = ops[0]
            return [('auipc', ['ra', f'%hi({etiqueta})']), ('jalr', ['ra', f'%lo({etiqueta})(ra)'])]
        if mnem == 'li':
            rd, inmediato_str = ops
            try:
                inmediato = int(inmediato_str, 0)
                if -2048 <= inmediato < 2048:
                    return [('addi', [rd, 'x0', str(inmediato)])]
                alta, baja = (inmediato + 0x800) >> 12, inmediato & 0xFFF
                inst = [('lui', [rd, str(alta)])]
                if baja != 0:
                    inst.append(('addi', [rd, rd, str(baja)]))
                return inst
            except ValueError:
                return [('auipc', [rd, f'%hi({inmediato_str})']), ('addi', [rd, rd, f'%lo({inmediato_str})'])]
        mapa_saltos = {'beqz': 'beq', 'bnez': 'bne', 'bltz': 'blt', 'bgez': 'bge', 'blez': 'bge', 'bgtz': 'blt'}
        if mnem in mapa_saltos:
            rs1, etiqueta = ops
            rs2 = 'x0'
            if mnem in ['blez', 'bgtz']:
                rs1, rs2 = rs2, rs1
            return [(mapa_saltos[mnem], [rs1, rs2, etiqueta])]
        return [(mnem, ops)]
