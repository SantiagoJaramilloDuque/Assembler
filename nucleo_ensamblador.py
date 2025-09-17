# -*- coding: utf-8 -*-
"""
nucleo_ensamblador.py

Contiene la clase principal `Ensamblador` que implementa la lógica de ensamblado
de dos pasadas, incluyendo el análisis de operandos, la resolución de símbolos
y la expansión de pseudo-instrucciones.
"""
import re
from typing import List, Dict, Tuple, Union
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Importa todas las definiciones de la arquitectura desde el módulo local.
from definiciones_riscv import *


console = Console()

class Ensamblador:
    def __init__(self):
        self.tabla_de_simbolos: Dict[str, int] = {}
        self.segmento_texto: bytearray = bytearray()
        self.direccion_actual: int = 0
        self.segmento_actual: str = ".text"  # Por defecto empieza en .text
        
        self.manejadores_formato = {
            'R': self._ensamblar_tipo_R,
            'I': self._ensamblar_tipo_I,
            'S': self._ensamblar_tipo_S,
            'B': self._ensamblar_tipo_B,
            'U': self._ensamblar_tipo_U,
            'J': self._ensamblar_tipo_J,
        }

    def primera_pasada(self, lineas_codigo: List[str]) -> None:
        """Construye la tabla de símbolos recorriendo el código."""
        self.direccion_actual = 0
        self.segmento_actual = ".text"
        for linea in lineas_codigo:
            linea = linea.split('#')[0].strip()
            if not linea:
                continue

            # Manejo de directivas
            if linea.startswith('.'):
                if linea.startswith('.text'):
                    self.segmento_actual = ".text"
                    self.direccion_actual = 0x00000000
                elif linea.startswith('.data'):
                    self.segmento_actual = ".data"
                    self.direccion_actual = 0x10000000  # inicio del segmento de datos
                continue

            # Manejo de etiquetas
            match = re.match(r'(\w+):', linea)
            if match:
                self.tabla_de_simbolos[match.group(1)] = self.direccion_actual
                linea = linea[len(match.group(0)):].strip()
            if not linea:
                continue

            # Solo contamos instrucciones en .text
            if self.segmento_actual == ".text":
                partes = linea.split(maxsplit=1)
                mnemonico = partes[0].lower()
                operandos = [op.strip() for op in partes[1].split(',')] if len(partes) > 1 else []
                inst_expandidas = self._expandir_pseudo_instrucciones(mnemonico, operandos)
                self.direccion_actual += len(inst_expandidas) * 4

    def segunda_pasada(self, lineas_codigo: List[str]) -> bool:
        """Genera el código máquina usando la tabla de símbolos con validación robusta."""
        self.direccion_actual = 0
        self.segmento_actual = ".text"
        errores = 0

        for num_linea, linea in enumerate(lineas_codigo, 1):
            linea_original = linea.strip()
            linea = linea.split('#')[0].strip()
            if not linea:
                continue

            if linea.startswith('.'):
                if linea.startswith('.text'):
                    self.segmento_actual = ".text"
                    self.direccion_actual = 0x00000000
                elif linea.startswith('.data'):
                    self.segmento_actual = ".data"
                    self.direccion_actual = 0x10000000
                continue

            match = re.match(r'(\w+):', linea)
            if match:
                linea = linea[len(match.group(0)):].strip()
            if not linea:
                continue

            if self.segmento_actual != ".text":
                continue

            partes = linea.split(maxsplit=1)
            mnemonico = partes[0].lower()
            operandos = [op.strip() for op in partes[1].split(',')] if len(partes) > 1 else []

            try:
                # 1. Validar que el mnemónico exista o sea pseudoinstrucción
                if mnemonico not in MNEMONICO_A_FORMATO and not self._es_pseudo(mnemonico):
                    raise ValueError(f"Instrucción no soportada: '{mnemonico}'")

                inst_expandidas = self._expandir_pseudo_instrucciones(mnemonico, operandos)

                for mnem, ops in inst_expandidas:
                    self._validar_operandos(mnem, ops, num_linea, linea_original)  # <--- validación aquí
                    codigo_maquina = self.ensamblar_instruccion(mnem, ops, self.direccion_actual)
                    self.segmento_texto.extend(codigo_maquina)
                    self.direccion_actual += 4

            except ValueError as e:
                errores += 1
                texto_error = Text(f"Error en la línea {num_linea}: {e}", style="bold red")
                console.print(Panel(texto_error, title=f"[red]Línea {num_linea}[/red]"))
                console.print(f"[yellow]{linea_original}[/yellow]")

        return errores == 0

    def _es_pseudo(self, mnem: str) -> bool:
        """Devuelve True si es una pseudoinstrucción conocida."""
        pseudos = ['nop', 'mv', 'not', 'neg', 'j', 'jal', 'ret', 'call',
                   'seqz', 'snez', 'sltz', 'sgtz', 'jr', 'li']
        return mnem in pseudos

    def _validar_operandos(self, mnem: str, ops: List[str], num_linea: int, linea_original: str):
        """Valida número y tipo de operandos e inmediatos en rango."""
        # Número de operandos esperado
        esperado = {
            "addi": 3, "xori": 3, "ori": 3, "andi": 3, "slli": 3, "srli": 3, "srai": 3,
            "slti": 3, "sltiu": 3, "lw": 2, "sw": 2, "beq": 3, "bne": 3, "jal": 2,
            "jalr": 3, "ecall": 0, "ebreak": 0
        }
        if mnem in esperado and len(ops) != esperado[mnem]:
            raise ValueError(f"'{mnem}' espera {esperado[mnem]} operandos, se dieron {len(ops)}.")
        

        # Validar inmediatos (ejemplo para addi)
        if mnem == "addi":
            try:
                inmediato = int(ops[2], 0)
                if not -2048 <= inmediato <= 2047:
                    raise ValueError(f"Immediate fuera de rango para '{mnem}' (-2048..2047): {ops[2]}")
            except ValueError:
                raise ValueError(f"El inmediato '{ops[2]}' no es un número válido.")

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

        # --- ya existentes ---
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
            return [('auipc', ['ra', f'%hi({etiqueta})']),
                    ('jalr', ['ra', f'%lo({etiqueta})(ra)'])]

        # --- nuevas ---
        if mnem == 'seqz':
            return [('sltiu', [ops[0], ops[1], '1'])]
        if mnem == 'snez':
            return [('sltu', [ops[0], 'x0', ops[1]])]
        if mnem == 'sltz':
            return [('slt', [ops[0], ops[1], 'x0'])]
        if mnem == 'sgtz':
            return [('slt', [ops[0], 'x0', ops[1]])]
        if mnem == 'jr':
            return [('jalr', ['x0', ops[0], '0'])]
        if mnem == 'jalr' and len(ops) == 1:
            return [('jalr', ['ra', ops[0], '0'])]

        # li ya estaba en tu código
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
                return [('auipc', [rd, f'%hi({inmediato_str})']),
                        ('addi', [rd, rd, f'%lo({inmediato_str})'])]

        # Saltos condicionales ya mapeados
        mapa_saltos = {
            'beqz': 'beq', 'bnez': 'bne',
            'bltz': 'blt', 'bgez': 'bge',
            'blez': 'bge', 'bgtz': 'blt'
        }
        if mnem in mapa_saltos:
            rs1, etiqueta = ops
            rs2 = 'x0'
            if mnem in ['blez', 'bgtz']:
                rs1, rs2 = rs2, rs1
            return [(mapa_saltos[mnem], [rs1, rs2, etiqueta])]

        return [(mnem, ops)]

