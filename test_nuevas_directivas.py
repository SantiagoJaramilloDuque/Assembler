"""
Test para verificar el funcionamiento de las nuevas directivas .half y .bin
"""
import sys
import os

# Agregar el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.directivas import ManejadorDirectivas, TipoSegmento

def test_directiva_half():
    """Prueba la directiva .half"""
    print("🧪 Probando directiva .half...")
    
    manejador = ManejadorDirectivas()
    
    # Cambiar a segmento .data
    error = manejador.procesar_directiva(".data", 1)
    assert error is None, f"Error cambiando a .data: {error}"
    
    # Probar valores válidos
    error = manejador.procesar_directiva(".half 100, -200, 0x7FFF", 2)
    assert error is None, f"Error procesando .half válido: {error}"
    
    # Verificar que se agregaron 6 bytes (3 valores * 2 bytes)
    datos = manejador.obtener_segmento_datos()
    assert len(datos) == 6, f"Esperado 6 bytes, obtenido {len(datos)}"
    
    # Verificar valores en little-endian
    # 100 = 0x0064 -> [0x64, 0x00]
    assert datos[0] == 0x64 and datos[1] == 0x00, f"Error en primer valor: {datos[0:2]}"
    
    # -200 = 0xFF38 -> [0x38, 0xFF]
    assert datos[2] == 0x38 and datos[3] == 0xFF, f"Error en segundo valor: {datos[2:4]}"
    
    # 0x7FFF -> [0xFF, 0x7F]
    assert datos[4] == 0xFF and datos[5] == 0x7F, f"Error en tercer valor: {datos[4:6]}"
    
    print("✅ Directiva .half funciona correctamente")

def test_directiva_half_errores():
    """Prueba errores en directiva .half"""
    print("🧪 Probando errores en directiva .half...")
    
    manejador = ManejadorDirectivas()
    manejador.procesar_directiva(".data", 1)
    
    # Valor fuera de rango
    error = manejador.procesar_directiva(".half 50000", 2)
    assert error is not None, "Debería fallar con valor fuera de rango"
    assert "fuera de rango" in error.lower()
    
    # Valor decimal
    error = manejador.procesar_directiva(".half 3.14", 3)
    assert error is not None, "Debería fallar con valor decimal"
    assert "enteros" in error.lower()
    
    # En segmento .text
    manejador.procesar_directiva(".text", 4)
    error = manejador.procesar_directiva(".half 100", 5)
    assert error is not None, "Debería fallar en segmento .text"
    assert ".data" in error
    
    print("✅ Errores en .half detectados correctamente")

def test_directiva_bin():
    """Prueba la directiva .bin"""
    print("🧪 Probando directiva .bin...")
    
    manejador = ManejadorDirectivas()
    manejador.procesar_directiva(".data", 1)
    
    # Probar patrón binario válido
    error = manejador.procesar_directiva('.bin "10101010"', 2)
    assert error is None, f"Error procesando .bin válido: {error}"
    
    # Verificar que se agregó 1 byte
    datos = manejador.obtener_segmento_datos()
    assert len(datos) == 1, f"Esperado 1 byte, obtenido {len(datos)}"
    assert datos[0] == 0xAA, f"Esperado 0xAA, obtenido 0x{datos[0]:02X}"
    
    # Probar patrón de 16 bits
    error = manejador.procesar_directiva('.bin "1111000011110000"', 3)
    assert error is None, f"Error procesando .bin de 16 bits: {error}"
    
    # Verificar que se agregaron 2 bytes más
    datos = manejador.obtener_segmento_datos()
    assert len(datos) == 3, f"Esperado 3 bytes, obtenido {len(datos)}"
    assert datos[1] == 0xF0, f"Esperado 0xF0, obtenido 0x{datos[1]:02X}"
    assert datos[2] == 0x0F, f"Esperado 0x0F, obtenido 0x{datos[2]:02X}"
    
    print("✅ Directiva .bin funciona correctamente")

def test_directiva_bin_errores():
    """Prueba errores en directiva .bin"""
    print("🧪 Probando errores en directiva .bin...")
    
    manejador = ManejadorDirectivas()
    manejador.procesar_directiva(".data", 1)
    
    # Caracteres inválidos
    error = manejador.procesar_directiva('.bin "1010102"', 2)
    assert error is not None, "Debería fallar con caracteres inválidos"
    assert "0s y 1s" in error
    
    # No múltiplo de 8
    error = manejador.procesar_directiva('.bin "101"', 3)
    assert error is not None, "Debería fallar si no es múltiplo de 8"
    assert "múltiplos de 8" in error
    
    # Sin comillas también debería funcionar
    error = manejador.procesar_directiva('.bin 11110000', 4)
    assert error is None, f"Debería funcionar sin comillas: {error}"
    
    print("✅ Errores en .bin detectados correctamente")

def test_programa_completo():
    """Prueba con el programa de ejemplo"""
    print("🧪 Probando programa completo...")
    
    # Leer el archivo de prueba
    with open('test_nuevas_directivas.asm', 'r') as f:
        lineas = f.readlines()
    
    manejador = ManejadorDirectivas()
    
    # Procesar solo las líneas con directivas
    for i, linea in enumerate(lineas, 1):
        linea = linea.strip()
        if not linea or linea.startswith('#'):
            continue
            
        if manejador.es_directiva(linea):
            error = manejador.procesar_directiva(linea, i)
            if error:
                print(f"❌ Error en línea {i}: {error}")
                return False
    
    # Verificar que se generaron datos
    datos = manejador.obtener_segmento_datos()
    print(f"📊 Segmento .data generado: {len(datos)} bytes")
    
    # Mostrar contenido en hexadecimal
    for i in range(0, len(datos), 16):
        chunk = datos[i:i+16]
        hex_str = ' '.join(f'{b:02X}' for b in chunk)
        print(f"   {i:04X}: {hex_str}")
    
    print("✅ Programa completo procesado exitosamente")
    return True

if __name__ == "__main__":
    print("🚀 Iniciando tests para nuevas directivas .half y .bin")
    print("=" * 60)
    
    try:
        test_directiva_half()
        test_directiva_half_errores()
        test_directiva_bin()
        test_directiva_bin_errores()
        test_programa_completo()
        
        print("=" * 60)
        print("🎉 ¡Todos los tests pasaron exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        sys.exit(1)