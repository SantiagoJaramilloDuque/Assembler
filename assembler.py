"""
Punto de entrada principal para el ensamblador RISC-V.
Este modulo maneja la lectura del archivo de entrada, la escritura de los
archivos de salida y orquesta el proceso de ensamblado.
"""
from core.ensamblador import Ensamblador
from utils.file_writer import escribir_archivos_salida
import os
import sys

def principal() -> None:
    """
    Función principal que orquesta todo el proceso de ensamblado.
    """
    archivo_entrada = sys.argv[1]

    print(f"Iniciando ensamblaje de '{archivo_entrada}'...")

    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            lineas_codigo = f.readlines()
    except FileNotFoundError:
        print(f"Error: El archivo de entrada '{archivo_entrada}' no fue encontrado.")
        return

    # 1. Crear una instancia del ensamblador.
    ensamblador = Ensamblador()
    
    # 2. Ejecutar el proceso de ensamblado.
    codigo_maquina = ensamblador.ensamblar(lineas_codigo)
    
    # 3. Si el ensamblado fue exitoso, escribir los archivos de salida.
    if codigo_maquina:
        escribir_archivos_salida(codigo_maquina)

if __name__ == "__main__":
    principal()