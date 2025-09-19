# --- PRUEBA SOLO U-TYPE ---
# Formato: rd, imm20 (cargado en bits 31..12)

    # LUI: Carga valores "puros" en la parte alta
    lui x1, 0x00010    # x1 = 0x00010 << 12 = 0x00010000
    lui x2, 0xABCDE    # x2 = 0xABCDE << 12 (valor alto arbitrario)
    lui x3, 0xFFFFF    # Máximo inmediato de 20 bits (sign-extend)

    # AUIPC: Suma PC + imm20<<12
    auipc x4, 0x00001  # x4 = PC + 0x1000
    auipc x5, 0x12345  # x5 = PC + 0x12345000
    auipc x6, 0xFFFFF  # Prueba con máximo valor para sign-extension
