# -*- coding: utf-8 -*-
"""
ensamblador.py

Punto de entrada principal para el ensamblador RISC-V.
Este script maneja la lectura del archivo de entrada, la escritura de los
archivos de salida y orquesta el proceso de ensamblado utilizando la clase Ensamblador.
"""
from nucleo_ensamblador import Ensamblador

def principal() -> None:
    """
    Función principal que orquesta el proceso de ensamblado.
    """
    archivo_entrada = "program.asm"
    archivo_salida_hex = "program.hex"
    archivo_salida_bin = "program.bin"

    print(f"Iniciando ensamblaje de '{archivo_entrada}'...")

    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            lineas_codigo = f.readlines()
    except FileNotFoundError:
        print(f"Error: El archivo de entrada '{archivo_entrada}' no fue encontrado.")
        return

    # 1. Crear una instancia del ensamblador.
    ensamblador = Ensamblador()
    
    # 2. Realizar la primera pasada.
    print("Realizando primera pasada (construcción de tabla de símbolos)...")
    ensamblador.primera_pasada(lineas_codigo)
    
    # 3. Realizar la segunda pasada.
    print("Realizando segunda pasada (generación de código máquina)...")
    if not ensamblador.segunda_pasada(lineas_codigo):
        print("\nEl ensamblaje falló debido a errores.")
        return
        
    # 4. Escribir los resultados en los archivos de salida.
    try:
        with open(archivo_salida_hex, 'w') as f_hex, open(archivo_salida_bin, 'w') as f_bin:
            for i in range(0, len(ensamblador.segmento_texto), 4):
                palabra_bytes = ensamblador.segmento_texto[i:i+4]
                palabra_entero = int.from_bytes(palabra_bytes, byteorder='little')
                
                f_hex.write(f"{palabra_entero:08X}\n")
                f_bin.write(f"{palabra_entero:032b}\n")
        
        print(f"\n¡Ensamblaje completado exitosamente!")
        print(f"Salida generada en '{archivo_salida_hex}' y '{archivo_salida_bin}'.\n")

    except IOError as e:
        print(f"Error al escribir los archivos de salida: {e}")

if __name__ == "__main__":
    principal()