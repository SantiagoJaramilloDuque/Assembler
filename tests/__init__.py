"""
Paquete de tests unitarios para el ensamblador RISC-V.

Este paquete contiene tests para todos los módulos principales:
- test_error_handler: Tests para el manejo de errores
- test_ensamblador: Tests para la funcionalidad principal del ensamblador
- test_pseudo_instrucciones: Tests para la expansión de pseudo-instrucciones
- test_riscv: Tests para las definiciones de la arquitectura RISC-V

Para ejecutar todos los tests:
    python -m unittest discover tests

Para ejecutar un archivo específico de tests:
    python -m unittest tests.test_error_handler
"""