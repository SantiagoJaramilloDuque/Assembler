"""
Utilidad para escribir el código máquina en archivos de salida con formato
hexadecimal y binario.
"""
import sys
import os
from typing import Dict

def escribir_archivos_salida(segmentos: Dict[str, bytearray]) -> None:
    """
    Escribe el contenido de los segmentos en archivos .hex y .bin.
    
    Args:
        segmentos: Diccionario con los segmentos de código ('text' y 'data').
    """
    # Obtener el nombre base del archivo de entrada
    archivo_entrada = sys.argv[1]
    nombre_base = os.path.splitext(archivo_entrada)[0]
    
    # Escribir segmento de texto
    if segmentos['text']:
        archivo_texto_hex = f"{nombre_base}.hex"
        archivo_texto_bin = f"{nombre_base}.bin"
        print(f"Generando segmento de texto en '{archivo_texto_hex}' y '{archivo_texto_bin}'...")
        
        try:
            _escribir_segmento(segmentos['text'], archivo_texto_hex, archivo_texto_bin)
        except IOError as e:
            print(f"Error al escribir archivos de texto: {e}")
    
    # Escribir segmento de datos si existe
    if segmentos['data']:
        archivo_datos_hex = f"{nombre_base}_data.hex"
        archivo_datos_bin = f"{nombre_base}_data.bin"
        print(f"Generando segmento de datos en '{archivo_datos_hex}' y '{archivo_datos_bin}'...")
        
        try:
            _escribir_segmento(segmentos['data'], archivo_datos_hex, archivo_datos_bin)
        except IOError as e:
            print(f"Error al escribir archivos de datos: {e}")

def _escribir_segmento(segmento: bytearray, archivo_hex: str, archivo_bin: str) -> None:
    """
    Escribe un segmento específico en archivos hexadecimal y binario.
    
    Args:
        segmento: El bytearray que contiene el código o datos.
        archivo_hex: Nombre del archivo hexadecimal.
        archivo_bin: Nombre del archivo binario.
    """
    with open(archivo_hex, 'w') as f_hex, open(archivo_bin, 'w') as f_bin:
        # Procesar el bytearray en trozos de 4 bytes (una palabra de 32 bits)
        for i in range(0, len(segmento), 4):
            palabra_bytes = segmento[i:i+4]
            
            # Rellenar con ceros si no hay suficientes bytes
            while len(palabra_bytes) < 4:
                palabra_bytes.append(0)
            
            # Convertir los 4 bytes a un entero (usando little-endian, estándar en RISC-V)
            palabra_entero = int.from_bytes(palabra_bytes, byteorder='little')
            
            # Escribir en formato hexadecimal de 8 dígitos (32 bits)
            f_hex.write(f"{palabra_entero:08X}\n")
            # Escribir en formato binario de 32 dígitos
            f_bin.write(f"{palabra_entero:032b}\n")