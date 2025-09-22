"""
Contiene la clase principal `Ensamblador` que implementa la lógica de ensamblado
de dos pasadas.
"""
import re
from typing import List, Dict, Optional, Union

from .error_handler import ErrorHandler
from .directivas import ManejadorDirectivas
from isa import riscv, pseudo_instrucciones

class Ensamblador:
    """
    Implementa un ensamblador de dos pasadas para la arquitectura RV32I.
    """
    def __init__(self):
        self.tabla_de_simbolos: Dict[str, int] = {}
        self.manejador_errores = ErrorHandler()
        self.manejador_directivas = ManejadorDirectivas()
        self.segmento_texto: bytearray = bytearray()
        self.direccion_actual: int = 0
        self.segmento_actual: str = ".text"

    def ensamblar(self, lineas_codigo: List[str]) -> Optional[Dict[str, bytearray]]:
        """
        Orquesta el proceso completo de ensamblado.
        
        Args:
            lineas_codigo: Una lista de strings, donde cada string es una línea de código.
        
        Returns:
            Un diccionario con los segmentos de código máquina si el ensamblado es exitoso,
            o None si ocurren errores. Las claves son 'text' y 'data'.
        """
        self._primera_pasada(lineas_codigo)
        if not self.manejador_errores.tiene_errores():
            self._segunda_pasada(lineas_codigo)
        
        self.manejador_errores.resumen_final()
        
        if not self.manejador_errores.tiene_errores():
            return {
                'text': self.manejador_directivas.obtener_segmento_texto(),
                'data': self.manejador_directivas.obtener_segmento_datos()
            }
        return None

    def _primera_pasada(self, lineas_codigo: List[str]) -> None:
        """Construye la tabla de símbolos recorriendo el código."""
        print("Realizando primera pasada (construcción de tabla de símbolos)...")
        self.manejador_directivas.resetear()

        for num_linea, linea_original in enumerate(lineas_codigo, 1):
            linea = linea_original.split('#')[0].strip()
            if not linea:
                continue

            # Verificar si es una directiva
            if self.manejador_directivas.es_directiva(linea):
                error = self.manejador_directivas.procesar_directiva(linea, num_linea)
                if error:
                    self.manejador_errores.reportar(num_linea, error, linea_original)
                continue

            # Procesar etiquetas
            match_etiqueta = re.match(r'(\w+):', linea)
            if match_etiqueta:
                simbolo = match_etiqueta.group(1)
                direccion_actual = self.manejador_directivas.obtener_direccion_actual()
                
                if simbolo in self.tabla_de_simbolos:
                    self.manejador_errores.reportar(num_linea, 
                        f"Símbolo '{simbolo}' ya está definido", linea_original)
                else:
                    self.tabla_de_simbolos[simbolo] = direccion_actual
                    self.manejador_directivas.agregar_simbolo(simbolo, direccion_actual)
                
                linea = linea[len(match_etiqueta.group(0)):].strip()

            # Solo procesar instrucciones en el segmento de texto
            if not linea or not self.manejador_directivas.esta_en_segmento_texto():
                continue

            # Validar sintaxis general de la línea
            error_sintaxis = self._validar_sintaxis_general(linea, num_linea)
            if error_sintaxis:
                self.manejador_errores.reportar(num_linea, error_sintaxis, linea_original)
                continue

            partes = linea.split(maxsplit=1)
            mnemonico = partes[0].lower()
            operandos = [op.strip() for op in partes[1].split(',')] if len(partes) > 1 else []
            
            try:
                inst_expandidas = pseudo_instrucciones.expandir(mnemonico, operandos)
                self.manejador_directivas.incrementar_direccion(len(inst_expandidas) * 4)
            except ValueError as e:
                self.manejador_errores.reportar(num_linea, str(e), linea_original)

    def _segunda_pasada(self, lineas_codigo: List[str]) -> None:
        """Genera el código máquina usando la tabla de símbolos."""
        print("Realizando segunda pasada (generación de código máquina)...")
        self.manejador_directivas.resetear()
        
        # Integrar todos los símbolos encontrados en la primera pasada
        self.tabla_de_simbolos.update(self.manejador_directivas.obtener_todos_los_simbolos())

        for num_linea, linea_original in enumerate(lineas_codigo, 1):
            linea = linea_original.split('#')[0].strip()
            if not linea:
                continue

            # Procesar directivas
            if self.manejador_directivas.es_directiva(linea):
                error = self.manejador_directivas.procesar_directiva(linea, num_linea)
                if error:
                    self.manejador_errores.reportar(num_linea, error, linea_original)
                continue

            # Procesar etiquetas
            match_etiqueta = re.match(r'(\w+):', linea)
            if match_etiqueta:
                linea = linea[len(match_etiqueta.group(0)):].strip()

            # Solo procesar instrucciones en el segmento de texto
            if not linea or not self.manejador_directivas.esta_en_segmento_texto():
                continue

            # Validar sintaxis general de la línea
            error_sintaxis = self._validar_sintaxis_general(linea, num_linea)
            if error_sintaxis:
                self.manejador_errores.reportar(num_linea, error_sintaxis, linea_original)
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
                    direccion_actual = self.manejador_directivas.obtener_direccion_actual()
                    codigo_maquina = self._ensamblar_instruccion(mnem, ops, direccion_actual)
                    self.manejador_directivas.obtener_segmento_texto().extend(codigo_maquina)
                    self.manejador_directivas.incrementar_direccion(4)

            except ValueError as e:
                self.manejador_errores.reportar(num_linea, str(e), linea_original)

    def _validar_sintaxis_general(self, linea: str, num_linea: int) -> Optional[str]:
        """
        Valida la sintaxis general de una línea de assembly.
        
        Args:
            linea: La línea de código assembly sin comentarios ni espacios iniciales/finales.
            num_linea: Número de línea para contexto de errores.
            
        Returns:
            None si la sintaxis es válida, mensaje de error si hay problemas.
        """
        # 1. Verificar caracteres válidos (letras, números, espacios, comas, paréntesis, guiones, %, puntos, @)
        caracteres_validos = re.compile(r'^[a-zA-Z0-9\s,()._\-+%:x@]+$')
        if not caracteres_validos.match(linea):
            caracteres_invalidos = ''.join(set(c for c in linea if not re.match(r'[a-zA-Z0-9\s,()._\-+%:x@]', c)))
            return f"Caracteres inválidos en la línea: '{caracteres_invalidos}'"
        
        # 2. Verificar que no haya espacios excesivos o múltiples comas consecutivas
        if '  ' in linea:  # Múltiples espacios consecutivos
            return "Múltiples espacios consecutivos no están permitidos"
        
        if ',,' in linea:  # Múltiples comas consecutivas
            return "Múltiples comas consecutivas no están permitidas"
        
        # 3. Validar formato básico de instrucción
        partes = linea.split(maxsplit=1)
        if not partes:
            return None  # Línea vacía, ya manejada antes
        
        mnemonico = partes[0].lower()
        
        # 4. Verificar que el mnemónico solo contenga caracteres alfanuméricos
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', mnemonico):
            return f"Mnemónico inválido: '{mnemonico}' - debe comenzar con letra y contener solo letras y números"
        
        # 5. Si hay operandos, validar su formato básico
        if len(partes) > 1:
            operandos_str = partes[1]
            
            # Verificar que no termine o empiece con coma
            if operandos_str.startswith(',') or operandos_str.endswith(','):
                return "Los operandos no pueden empezar o terminar con coma"
            
            # Verificar que los paréntesis estén balanceados
            if operandos_str.count('(') != operandos_str.count(')'):
                return "Paréntesis no balanceados en los operandos"
            
            # Validar cada operando individualmente
            operandos = [op.strip() for op in operandos_str.split(',')]
            for i, operando in enumerate(operandos):
                if not operando:  # Operando vacío
                    return f"Operando {i+1} está vacío"
                
                error_operando = self._validar_sintaxis_operando(operando)
                if error_operando:
                    return f"Operando {i+1} '{operando}': {error_operando}"
        
        return None

    def _validar_sintaxis_operando(self, operando: str) -> Optional[str]:
        """
        Valida la sintaxis de un operando individual.
        
        Args:
            operando: El operando a validar (ya sin espacios iniciales/finales).
            
        Returns:
            None si es válido, mensaje de error si hay problemas.
        """
        if not operando:
            return "Operando vacío"
        
        # 1. Funciones %hi y %lo (verificar primero antes que otros patrones)
        if re.match(r'^%hi\([a-zA-Z_][a-zA-Z0-9_]*\)$', operando) or \
           re.match(r'^%lo\([a-zA-Z_][a-zA-Z0-9_]*\)$', operando):
            return None
        
        # 2. Registro simple (x0-x31, nombres como sp, ra, etc.)
        if re.match(r'^x\d+$', operando.lower()):
            try:
                num_reg = int(operando[1:])
                if num_reg > 31:
                    return f"número de registro fuera de rango (0-31)"
            except ValueError:
                return "formato de registro inválido"
            return None
        
        if operando.lower() in riscv.REGISTROS:
            return None
        
        # 3. Inmediato decimal, hexadecimal, octal o binario
        if re.match(r'^-?\d+$', operando) or \
           re.match(r'^-?0x[0-9a-fA-F]+$', operando) or \
           re.match(r'^-?0o[0-7]+$', operando) or \
           re.match(r'^-?0b[01]+$', operando):
            return None
        
        # 4. Acceso a memoria: inmediato(registro) o etiqueta(registro)
        memoria_match = re.match(r'^(.+)\((.+)\)$', operando)
        if memoria_match:
            offset, registro = memoria_match.groups()
            
            # Validar el registro dentro de los paréntesis
            error_reg = self._validar_sintaxis_operando(registro)
            if error_reg and registro.lower() not in riscv.REGISTROS:
                return f"registro en paréntesis inválido: {error_reg}"
            
            # Validar el offset (puede ser inmediato o etiqueta)
            if not (re.match(r'^-?\d+$', offset) or 
                   re.match(r'^-?0x[0-9a-fA-F]+$', offset) or
                   re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', offset)):
                return "offset debe ser un número o una etiqueta válida"
            
            return None
        
        # 5. Etiqueta simple
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', operando):
            return None
        
        # Si llegamos aquí, el operando no coincide con ningún patrón válido
        return "formato no reconocido"

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
