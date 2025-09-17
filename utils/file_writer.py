# utils/file_writer.py
# -*- coding: utf-8 -*-
"""
Utilidad para escribir el código máquina en archivos de salida con formato
hexadecimal y binario.
"""
def escribir_archivos_salida(nombre_base: str, segmento_texto: bytearray) -> None:
    """
    Escribe el contenido del segmento de texto en archivos .hex y .bin.
    
    Args:
        nombre_base: El nombre base para los archivos de salida (ej. "program").
        segmento_texto: El bytearray que contiene el código máquina.
    """
    archivo_salida_hex = f"{nombre_base}.hex"
    archivo_salida_bin = f"{nombre_base}.bin"

    print(f"Generando salida en '{archivo_salida_hex}' y '{archivo_salida_bin}'...")

    try:
        with open(archivo_salida_hex, 'w') as f_hex, open(archivo_salida_bin, 'w') as f_bin:
            # Procesar el bytearray en trozos de 4 bytes (una palabra de 32 bits)
            for i in range(0, len(segmento_texto), 4):
                palabra_bytes = segmento_texto[i:i+4]
                # Convertir los 4 bytes a un entero (usando little-endian, estándar en RISC-V)
                palabra_entero = int.from_bytes(palabra_bytes, byteorder='little')
                
                # Escribir en formato hexadecimal de 8 dígitos (32 bits)
                f_hex.write(f"{palabra_entero:08X}\n")
                # Escribir en formato binario de 32 dígitos
                f_bin.write(f"{palabra_entero:032b}\n")
    except IOError as e:
        print(f"Error al escribir los archivos de salida: {e}")