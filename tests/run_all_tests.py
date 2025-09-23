"""
Script para ejecutar todos los tests unitarios del proyecto.
"""
import unittest
import sys
import os

# Añadir el directorio padre al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

if __name__ == '__main__':
    # Descubrir y ejecutar todos los tests en la carpeta tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Ejecutar los tests con verbosidad
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Salir con código de error si hay fallas
    sys.exit(0 if result.wasSuccessful() else 1)