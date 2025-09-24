"""
Módulo para el manejo de directivas del ensamblador (.data, .text).
Proporciona funcionalidad para gestionar segmentos de memoria de texto y datos
trabajando únicamente con enteros.
"""
from typing import Dict, Optional
from enum import Enum

class TipoSegmento(Enum):
    """Enumeración de los tipos de segmento disponibles."""
    TEXT = ".text"
    DATA = ".data"

class ManejadorDirectivas:
    """
    Maneja el procesamiento de directivas del ensamblador.
    Gestiona cambios entre segmentos .text y .data y almacenamiento de enteros.
    """
    
    def __init__(self):
        """Inicializa el manejador de directivas."""
        # Direcciones base de cada segmento
        self.direcciones_base = {
            TipoSegmento.TEXT: 0x00000000,
            TipoSegmento.DATA: 0x10000000
        }
        
        # Direcciones actuales de cada segmento
        self.direcciones_actuales = {
            TipoSegmento.TEXT: 0x00000000,
            TipoSegmento.DATA: 0x10000000
        }
        
        # Segmento activo actualmente
        self.segmento_actual = TipoSegmento.TEXT
        
        # Contenido de cada segmento
        self.segmentos = {
            TipoSegmento.TEXT: bytearray(),
            TipoSegmento.DATA: bytearray()
        }
        
        # Tabla de símbolos por segmento
        self.simbolos_por_segmento: Dict[TipoSegmento, Dict[str, int]] = {
            TipoSegmento.TEXT: {},
            TipoSegmento.DATA: {}
        }

    def es_directiva(self, linea: str) -> bool:
        """
        Determina si una línea contiene una directiva.
        
        Args:
            linea: La línea de código a verificar.
            
        Returns:
            True si la línea contiene una directiva, False en caso contrario.
        """
        linea = linea.strip()
        return (linea.startswith('.text') or 
                linea.startswith('.data') or
                linea.startswith('.word') or
                linea.startswith('.half') or
                linea.startswith('.bin'))

    def procesar_directiva(self, linea: str, num_linea: int) -> Optional[str]:
        """
        Procesa una directiva y actualiza el estado del ensamblador.
        
        Args:
            linea: La línea que contiene la directiva.
            num_linea: Número de línea para reportes de error.
            
        Returns:
            None si la directiva se procesó correctamente, 
            un mensaje de error si hubo problemas.
        """
        linea = linea.strip()
        
        # Procesar directivas de segmento
        if linea.startswith('.text'):
            return self._cambiar_segmento(TipoSegmento.TEXT, linea)
        elif linea.startswith('.data'):
            return self._cambiar_segmento(TipoSegmento.DATA, linea)
        elif linea.startswith('.word'):
            # Solo permitir .word en segmento .data
            if self.segmento_actual != TipoSegmento.DATA:
                return "Directiva .word solo válida en segmento .data"
            return self._procesar_word(linea)
        elif linea.startswith('.half'):
            # Solo permitir .half en segmento .data
            if self.segmento_actual != TipoSegmento.DATA:
                return "Directiva .half solo válida en segmento .data"
            return self._procesar_half(linea)
        elif linea.startswith('.bin'):
            # Solo permitir .bin en segmento .data
            if self.segmento_actual != TipoSegmento.DATA:
                return "Directiva .bin solo válida en segmento .data"
            return self._procesar_bin(linea)
        
        return f"Directiva no reconocida: {linea}"

    def _cambiar_segmento(self, nuevo_segmento: TipoSegmento, linea: str) -> Optional[str]:
        """
        Cambia el segmento activo.
        
        Args:
            nuevo_segmento: El nuevo segmento al que cambiar.
            linea: La línea completa de la directiva.
            
        Returns:
            None si el cambio fue exitoso, mensaje de error en caso contrario.
        """
        partes = linea.split()
        
        # Verificar si se especifica una dirección base personalizada
        if len(partes) > 1:
            try:
                direccion_base = int(partes[1], 0)  # Permite hex (0x), octal (0o), binario (0b)
                self.direcciones_base[nuevo_segmento] = direccion_base
                self.direcciones_actuales[nuevo_segmento] = direccion_base
            except ValueError:
                return f"Dirección base inválida: '{partes[1]}'"
        
        self.segmento_actual = nuevo_segmento
        return None

    def _procesar_word(self, linea: str) -> Optional[str]:
        """
        Procesa directiva .word (32 bits enteros únicamente).
        
        Args:
            linea: La línea que contiene la directiva .word.
            
        Returns:
            None si se procesó correctamente, mensaje de error en caso contrario.
        """
        partes = linea.split(maxsplit=1)
        if len(partes) < 2:
            return "Directiva .word requiere al menos un valor"
        
        argumentos = partes[1]
        valores = [arg.strip() for arg in argumentos.split(',')]
        
        for valor in valores:
            try:
                # Solo aceptar enteros (sin decimales)
                if '.' in valor:
                    return f"Solo se permiten enteros en .word, encontrado: '{valor}'"
                
                num = int(valor, 0)  # Permite diferentes bases (hex, oct, bin)
                
                # Verificar rango de 32 bits con signo
                if not (-2147483648 <= num <= 2147483647):
                    return f"Valor fuera de rango para .word (32 bits): {valor}"
                
                # Convertir a bytes en little-endian
                bytes_valor = num.to_bytes(4, byteorder='little', signed=True)
                self.segmentos[TipoSegmento.DATA].extend(bytes_valor)
                self.direcciones_actuales[TipoSegmento.DATA] += 4
                
            except ValueError:
                return f"Valor inválido para .word: '{valor}'"
        
        return None

    def _procesar_half(self, linea: str) -> Optional[str]:
        """
        Procesa directiva .half (16 bits enteros únicamente).
        
        Args:
            linea: La línea que contiene la directiva .half.
            
        Returns:
            None si se procesó correctamente, mensaje de error en caso contrario.
        """
        partes = linea.split(maxsplit=1)
        if len(partes) < 2:
            return "Directiva .half requiere al menos un valor"
        
        argumentos = partes[1]
        valores = [arg.strip() for arg in argumentos.split(',')]
        
        for valor in valores:
            try:
                # Solo aceptar enteros (sin decimales)
                if '.' in valor:
                    return f"Solo se permiten enteros en .half, encontrado: '{valor}'"
                
                num = int(valor, 0)  # Permite diferentes bases (hex, oct, bin)
                
                # Verificar rango de 16 bits con signo
                if not (-32768 <= num <= 32767):
                    return f"Valor fuera de rango para .half (16 bits): {valor}"
                
                # Convertir a bytes en little-endian
                bytes_valor = num.to_bytes(2, byteorder='little', signed=True)
                self.segmentos[TipoSegmento.DATA].extend(bytes_valor)
                self.direcciones_actuales[TipoSegmento.DATA] += 2
                
            except ValueError:
                return f"Valor inválido para .half: '{valor}'"
        
        return None

    def _procesar_bin(self, linea: str) -> Optional[str]:
        """
        Procesa directiva .bin (datos binarios como cadenas de 0s y 1s).
        
        Args:
            linea: La línea que contiene la directiva .bin.
            
        Returns:
            None si se procesó correctamente, mensaje de error en caso contrario.
        """
        partes = linea.split(maxsplit=1)
        if len(partes) < 2:
            return "Directiva .bin requiere al menos un valor"
        
        argumentos = partes[1].strip()
        
        # Remover comillas si están presentes
        if (argumentos.startswith('"') and argumentos.endswith('"')) or \
           (argumentos.startswith("'") and argumentos.endswith("'")):
            argumentos = argumentos[1:-1]
        
        # Validar que solo contenga 0s y 1s
        if not all(c in '01' for c in argumentos):
            return "Directiva .bin solo acepta cadenas de 0s y 1s"
        
        # La cadena debe ser múltiplo de 8 bits
        if len(argumentos) % 8 != 0:
            return f"Directiva .bin requiere múltiplos de 8 bits, encontrado: {len(argumentos)} bits"
        
        # Procesar en grupos de 8 bits
        for i in range(0, len(argumentos), 8):
            byte_str = argumentos[i:i+8]
            try:
                # Convertir cadena binaria a byte
                byte_valor = int(byte_str, 2)
                self.segmentos[TipoSegmento.DATA].extend([byte_valor])
                self.direcciones_actuales[TipoSegmento.DATA] += 1
            except ValueError:
                return f"Error procesando byte binario: '{byte_str}'"
        
        return None

    def obtener_direccion_actual(self) -> int:
        """Obtiene la dirección actual del segmento activo."""
        return self.direcciones_actuales[self.segmento_actual]

    def incrementar_direccion(self, cantidad: int) -> None:
        """Incrementa la dirección actual del segmento activo."""
        self.direcciones_actuales[self.segmento_actual] += cantidad

    def agregar_simbolo(self, nombre: str, direccion: int) -> None:
        """Agrega un símbolo al segmento actual."""
        self.simbolos_por_segmento[self.segmento_actual][nombre] = direccion

    def obtener_simbolo(self, nombre: str) -> Optional[int]:
        """Busca un símbolo en todos los segmentos."""
        for simbolos in self.simbolos_por_segmento.values():
            if nombre in simbolos:
                return simbolos[nombre]
        return None

    def obtener_segmento_datos(self) -> bytearray:
        """Obtiene el contenido del segmento de datos."""
        return self.segmentos[TipoSegmento.DATA]

    def obtener_segmento_texto(self) -> bytearray:
        """Obtiene el contenido del segmento de texto."""
        return self.segmentos[TipoSegmento.TEXT]

    def esta_en_segmento_texto(self) -> bool:
        """Verifica si estamos actualmente en el segmento de texto."""
        return self.segmento_actual == TipoSegmento.TEXT

    def esta_en_segmento_datos(self) -> bool:
        """Verifica si estamos actualmente en el segmento de datos."""
        return self.segmento_actual == TipoSegmento.DATA

    def obtener_todos_los_simbolos(self) -> Dict[str, int]:
        """Obtiene todos los símbolos de todos los segmentos."""
        todos_simbolos = {}
        for simbolos in self.simbolos_por_segmento.values():
            todos_simbolos.update(simbolos)
        return todos_simbolos

    def resetear(self) -> None:
        """Resetea el estado del manejador de directivas."""
        self.direcciones_actuales = self.direcciones_base.copy()
        self.segmento_actual = TipoSegmento.TEXT
        for segmento in self.segmentos.values():
            segmento.clear()
        for simbolos in self.simbolos_por_segmento.values():
            simbolos.clear()