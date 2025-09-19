# core/ensamblador.py
# -*- coding: utf-8 -*-
"""
Contiene la clase principal `Ensamblador` que implementa la lógica de ensamblado
de dos pasadas.
"""
import re
from typing import List, Dict, Optional, Union

from .error_handler import ErrorHandler
from isa import riscv, pseudo_instrucciones

class Ensamblador:
    """
    Implementa un ensamblador de dos pasadas para la arquitectura RV32I.
    """
    def __init__(self):
        self.tabla_de_simbolos: Dict[str, int] = {}
        self.manejador_errores = ErrorHandler()
        self.segmento_texto: bytearray = bytearray()
        self.direccion_actual: int = 0
        self.segmento_actual: str = ".text"

    def ensamblar(self, lineas_codigo: List[str]) -> Optional[bytearray]:
        """
        Orquesta el proceso completo de ensamblado.
        
        Args:
            lineas_codigo: Una lista de strings, donde cada string es una línea de código.
        
        Returns:
            Un bytearray con el código máquina si el ensamblado es exitoso,
            o None si ocurren errores.
        """
        self._primera_pasada(lineas_codigo)
        if not self.manejador_errores.tiene_errores():
            self._segunda_pasada(lineas_codigo)
        
        self.manejador_errores.resumen_final()
        
        return self.segmento_texto if not self.manejador_errores.tiene_errores() else None

    def _primera_pasada(self, lineas_codigo: List[str]) -> None:
        """Construye la tabla de símbolos recorriendo el código."""
        print("Realizando primera pasada (construcción de tabla de símbolos)...")
        self.direccion_actual = 0
        self.segmento_actual = ".text"

        for num_linea, linea_original in enumerate(lineas_codigo, 1):
            linea = linea_original.split('#')[0].strip()
            if not linea:
                continue

            if linea.startswith('.text'):
                self.segmento_actual = ".text"
                self.direccion_actual = 0
                continue
            elif linea.startswith('.data'):
                # Este ensamblador no maneja datos, pero reconoce la directiva.
                self.segmento_actual = ".data"
                self.direccion_actual = 0x10000000 
                continue

            match_etiqueta = re.match(r'(\w+):', linea)
            if match_etiqueta:
                simbolo = match_etiqueta.group(1)
                if simbolo in self.tabla_de_simbolos:
                    # Error: Símbolo redefinido (no implementado en primera pasada para simplicidad)
                    pass
                self.tabla_de_simbolos[simbolo] = self.direccion_actual
                linea = linea[len(match_etiqueta.group(0)):].strip()

            if not linea or self.segmento_actual != ".text":
                continue

            partes = linea.split(maxsplit=1)
            mnemonico = partes[0].lower()
            operandos = [op.strip() for op in partes[1].split(',')] if len(partes) > 1 else []
            
            try:
                inst_expandidas = pseudo_instrucciones.expandir(mnemonico, operandos)
                self.direccion_actual += len(inst_expandidas) * 4
            except ValueError as e:
                self.manejador_errores.reportar(num_linea, str(e), linea_original)

    def _segunda_pasada(self, lineas_codigo: List[str]) -> None:
        """Genera el código máquina usando la tabla de símbolos."""
        print("Realizando segunda pasada (generación de código máquina)...")
        self.direccion_actual = 0
        self.segmento_actual = ".text"

        for num_linea, linea_original in enumerate(lineas_codigo, 1):
            linea = linea_original.split('#')[0].strip()
            if not linea:
                continue

            if linea.startswith('.'):
                self.segmento_actual = ".text" if linea.startswith('.text') else ".data"
                self.direccion_actual = 0 if self.segmento_actual == ".text" else 0x10000000
                continue

            match_etiqueta = re.match(r'(\w+):', linea)
            if match_etiqueta:
                linea = linea[len(match_etiqueta.group(0)):].strip()

            if not linea or self.segmento_actual != ".text":
                continue

            partes = linea.split(maxsplit=1)
            mnemonico = partes[0].lower()
            operandos = [op.strip() for op in partes[1].split(',')] if len(partes) > 1 else []

            try:
                if mnemonico not in riscv.MNEMONICO_A_FORMATO and not pseudo_instrucciones.es_pseudo(mnemonico):
                    raise ValueError(f"Instrucción no soportada: '{mnemonico}'")

                inst_expandidas = pseudo_instrucciones.expandir(mnemonico, operandos)

                for mnem, ops in inst_expandidas:
                    self._validar_operandos(mnem, ops) # Validación mejorada
                    codigo_maquina = self._ensamblar_instruccion(mnem, ops, self.direccion_actual)
                    self.segmento_texto.extend(codigo_maquina)
                    self.direccion_actual += 4

            except ValueError as e:
                self.manejador_errores.reportar(num_linea, str(e), linea_original)

    def _validar_operandos(self, mnem: str, ops: List[str]) -> None:
        """Validación más robusta del número y tipo de operandos."""
        # Excepción para ecall y ebreak: no tienen operandos
        if mnem in ['ecall', 'ebreak']:
            if len(ops) != 0:
                raise ValueError(f"'{mnem}' no espera operandos, pero se dieron {len(ops)}")
            return  # No validar nada más

        formato = riscv.MNEMONICO_A_FORMATO.get(mnem)
        if not formato:
            raise ValueError(f"Mnemónico desconocido en la validación: '{mnem}'")

        # Validar número de operandos
        num_ops_esperado = {'R': 3, 'I': 3, 'S': 2, 'B': 3, 'U': 2, 'J': 2}
        if formato in ['I'] and mnem in ['lw', 'lb', 'lh', 'lbu', 'lhu']:
            num_ops_esperado['I'] = 2

        if formato in num_ops_esperado and len(ops) != num_ops_esperado[formato]:
            raise ValueError(f"'{mnem}' espera {num_ops_esperado[formato]} operandos, pero se dieron {len(ops)}")

        # Validar que los registros existan
        for op in ops:
            if op in riscv.REGISTROS:
                continue
            # Ignorar inmediatos, etiquetas o accesos a memoria como `8(sp)`
            if re.fullmatch(r'-?\d+', op) or op in self.tabla_de_simbolos or re.fullmatch(r'.*\(.*\)', op):
                continue
            if not op.lower() in riscv.REGISTROS and not '%' in op: # Ignorar %hi/%lo
                if re.fullmatch(r'x\d{1,2}|[a-z]+\d?', op.lower()):
                    raise ValueError(f"Registro no válido: '{op}'")


    def _ensamblar_instruccion(self, mnem: str, ops: List[str], pc_actual: int) -> bytes:
        """Despacha al método de ensamblado correcto según el formato."""
        formato = riscv.MNEMONICO_A_FORMATO[mnem]
        ensamblador_fn = getattr(self, f'_ensamblar_tipo_{formato}')
        instruccion = ensamblador_fn(mnem, ops, pc_actual)
        return instruccion.to_bytes(4, byteorder='little')

    # --- MÉTODOS DE ENSAMBLADO POR FORMATO ---
    def _ensamblar_tipo_R(self, mnem: str, ops: List[str], pc: int) -> int:
        rd, rs1, rs2 = map(self._analizar_registro, ops)
        func7 = riscv.FUNC7.get(mnem, 0)
        return (func7 << 25) | (rs2 << 20) | (rs1 << 15) | (riscv.FUNC3[mnem] << 12) | (rd << 7) | riscv.OPCODE['R']

    def _ensamblar_tipo_I(self, mnem: str, ops: List[str], pc: int) -> int:
        if mnem in ["ecall", "ebreak"]:
            imm = 1 if mnem == "ebreak" else 0
            return (imm << 20) | (0 << 15) | (riscv.FUNC3[mnem] << 12) | (0 << 7) | riscv.OPCODE['SYSTEM']

        rd = self._analizar_registro(ops[0])

        # ¿es un acceso de carga rd, imm(rs1) ?
        match_carga = re.match(r'(.+)\((.+)\)', ops[1])
        if match_carga:  # Formato lw, lb, etc. rd, imm(rs1)
            inmediato_str, rs1_str = match_carga.groups()
            rs1 = self._analizar_registro(rs1_str)
            opcode = riscv.OPCODE['L']
            inmediato = self._resolver_simbolo_o_inmediato(inmediato_str, pc)
            # Inmediato para loads es signed 12-bit
            if not -2048 <= inmediato <= 2047:
                raise ValueError(f"Inmediato '{inmediato}' fuera de rango para load (-2048 a 2047)")
            return ((inmediato & 0xFFF) << 20) | (rs1 << 15) | (riscv.FUNC3[mnem] << 12) | (rd << 7) | opcode

        # Formato rd, rs1, imm  (addi, xori, slti, jalr, shifts immediatos, ...)
        rs1 = self._analizar_registro(ops[1])
        inmediato_str = ops[2]
        opcode = riscv.OPCODE['I']
        if mnem == "jalr":
            opcode = riscv.OPCODE['jalr']

        # Si es shift inmediato (slli, srli, srai) -> shamt (0..31) y func7 en bits 31:25
        if mnem in ("slli", "srli", "srai"):
            shamt = self._resolver_simbolo_o_inmediato(inmediato_str, pc)
            if not 0 <= shamt <= 31:
                raise ValueError(f"Shamt '{shamt}' fuera de rango para '{mnem}' (0..31)")
            func7 = riscv.FUNC7.get(mnem, 0)  # srai -> 0x20, srli/slli -> 0x00
            # Encodificar: func7[31:25] | shamt[24:20] | rs1[19:15] | func3[14:12] | rd[11:7] | opcode[6:0]
            return (func7 << 25) | ((shamt & 0x1F) << 20) | (rs1 << 15) | (riscv.FUNC3[mnem] << 12) | (rd << 7) | opcode

        # resto de I-type normales (addi, xori, andi, slti, sltiu, etc.)
        inmediato = self._resolver_simbolo_o_inmediato(inmediato_str, pc)
        if not -2048 <= inmediato <= 2047:
            raise ValueError(f"Inmediato '{inmediato}' fuera de rango para instrucción tipo I (-2048 a 2047)")

        return ((inmediato & 0xFFF) << 20) | (rs1 << 15) | (riscv.FUNC3[mnem] << 12) | (rd << 7) | opcode


    def _ensamblar_tipo_S(self, mnem: str, ops: List[str], pc: int) -> int:
        rs2_str, operando_memoria = ops
        match = re.match(r'(.+)\((.+)\)', operando_memoria)
        if not match:
            raise ValueError(f"Formato de 'store' inválido: '{operando_memoria}'")
        
        inmediato_str, rs1_str = match.groups()
        rs1 = self._analizar_registro(rs1_str)
        rs2 = self._analizar_registro(rs2_str)
        inmediato = self._resolver_simbolo_o_inmediato(inmediato_str, pc)
        
        imm11_5 = (inmediato >> 5) & 0x7F
        imm4_0 = inmediato & 0x1F
        return (imm11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (riscv.FUNC3[mnem] << 12) | (imm4_0 << 7) | riscv.OPCODE['S']

    def _ensamblar_tipo_B(self, mnem: str, ops: List[str], pc: int) -> int:
        rs1, rs2 = map(self._analizar_registro, ops[:2])
        inmediato = self._resolver_simbolo_o_inmediato(ops[2], pc, es_relativo=True)
        if not -4096 <= inmediato <= 4094 or inmediato % 2 != 0:
            raise ValueError(f"Salto fuera de rango o no alineado para '{mnem}': {inmediato}")
        
        imm12 = (inmediato >> 12) & 1
        imm10_5 = (inmediato >> 5) & 0x3F
        imm4_1 = (inmediato >> 1) & 0xF
        imm11 = (inmediato >> 11) & 1
        return (imm12 << 31) | (imm10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (riscv.FUNC3[mnem] << 12) | (imm4_1 << 8) | (imm11 << 7) | riscv.OPCODE['B']

    def _ensamblar_tipo_U(self, mnem: str, ops: List[str], pc: int) -> int:
        rd = self._analizar_registro(ops[0])
        inmediato = self._resolver_simbolo_o_inmediato(ops[1], pc)
        opcode = riscv.OPCODE['auipc'] if mnem == 'auipc' else riscv.OPCODE['U']
        # El inmediato de 20 bits debe ir en los bits 31-12
        return ((inmediato & 0xFFFFF) << 12) | (rd << 7) | opcode


    def _ensamblar_tipo_J(self, mnem: str, ops: List[str], pc: int) -> int:
        rd = self._analizar_registro(ops[0])
        inmediato = self._resolver_simbolo_o_inmediato(ops[1], pc, es_relativo=True)
        
        imm20 = (inmediato >> 20) & 1
        imm10_1 = (inmediato >> 1) & 0x3FF
        imm11 = (inmediato >> 11) & 1
        imm19_12 = (inmediato >> 12) & 0xFF
        
        return (imm20 << 31) | (imm19_12 << 12) | (imm11 << 20) | (imm10_1 << 21) | (rd << 7) | riscv.OPCODE['J']

    # --- MÉTODOS DE AYUDA ---
    def _analizar_registro(self, operando: str) -> int:
        """Convierte un nombre de registro a su número."""
        operando = operando.strip().lower()
        if operando not in riscv.REGISTROS:
            raise ValueError(f"El registro '{operando}' no es válido.")
        return riscv.REGISTROS[operando]

    def _resolver_simbolo_o_inmediato(self, simbolo: str, pc_actual: int, es_relativo: bool = False) -> int:
        """Resuelve un operando que puede ser un símbolo, un inmediato, o una función hi/lo.
           Si es_relativo=True, devuelve (valor - pc_actual) cuando el operando es un literal
           o cuando es una etiqueta conocida (ya lo hacías para etiquetas).
        """
        simbolo = simbolo.strip()

        # Manejo de %hi(simbolo) y %lo(simbolo)
        match_hi = re.match(r'%hi\((\w+)\)', simbolo)
        match_lo = re.match(r'%lo\((\w+)\)', simbolo)

        etiqueta = simbolo
        if match_hi: etiqueta = match_hi.group(1)
        if match_lo: etiqueta = match_lo.group(1)

        # Caso: etiqueta conocida en tabla de símbolos
        if etiqueta in self.tabla_de_simbolos:
            direccion_etiqueta = self.tabla_de_simbolos[etiqueta]
            desplazamiento = direccion_etiqueta - pc_actual if es_relativo else direccion_etiqueta

            if match_hi:
                return (desplazamiento + 0x800) >> 12
            if match_lo:
                return desplazamiento & 0xFFF
            return desplazamiento

        # No es etiqueta conocida: intentar interpretar como número literal
        try:
            valor_literal = int(simbolo, 0)  # permite 0x.., 0o.., 0b.. y decimales
            if es_relativo:
                # Si piden relativo, devolvemos valor_literal - pc_actual
                return valor_literal - pc_actual
            else:
                return valor_literal
        except ValueError:
            # No es literal ni etiqueta conocida -> error
            raise ValueError(f"Símbolo no definido: '{simbolo}'")
