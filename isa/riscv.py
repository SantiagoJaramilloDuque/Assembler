"""
Contiene las definiciones estáticas de la arquitectura RISC-V (RV32I),
incluyendo formatos de instrucción, opcodes, códigos de función y nombres de registros.
"""
from typing import List, Dict

# Mapeo de mnemónicos a su formato de instrucción (solo RV32I)
FORMATOS_INSTRUCCION: Dict[str, List[str]] = {
    'R': ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "sra", "or", "and"],
    'I': ["addi", "slli", "slti", "sltiu", "xori", "srli", "srai", "ori", "andi",
        "jalr", "lb", "lh", "lw", "lbu", "lhu",
        "ecall", "ebreak"],
    'S': ["sb", "sh", "sw"],
    'B': ["beq", "bne", "blt", "bge", "bltu", "bgeu"],
    'U': ["lui", "auipc"],
    'J': ["jal"]
}

# Diccionario invertido para buscar el formato de un mnemónico de forma eficiente (O(1)).
MNEMONICO_A_FORMATO: Dict[str, str] = {
    mnem: fmt for fmt, lista_mnem in FORMATOS_INSTRUCCION.items() for mnem in lista_mnem
}

# Códigos de operación (opcodes) para cada formato.
OPCODE: Dict[str, int] = {
    'R': 0b0110011,
    'I': 0b0010011,  # Para operaciones con inmediato
    'L': 0b0000011,  # Para cargas (load)
    'S': 0b0100011,  # Para almacenamientos (store)
    'B': 0b1100011,  # Para saltos condicionales (branch)
    'J': 0b1101111,  # Para jal
    'U': 0b0110111,  # Para lui
    'auipc': 0b0010111,
    'jalr': 0b1100111,
    'SYSTEM': 0b1110011
}

# Códigos de función de 3 bits (func3)
FUNC3: Dict[str, int] = {
    "add": 0b000, "sub": 0b000, "sll": 0b001, "slt": 0b010, "sltu": 0b011, "xor": 0b100,
    "srl": 0b101, "sra": 0b101, "or": 0b110, "and": 0b111,
    "addi": 0b000, "slli": 0b001, "slti": 0b010, "sltiu": 0b011, "xori": 0b100,
    "srli": 0b101, "srai": 0b101, "ori": 0b110, "andi": 0b111,
    "lb": 0b000, "lh": 0b001, "lw": 0b010, "lbu": 0b100, "lhu": 0b101,
    "sb": 0b000, "sh": 0b001, "sw": 0b010,
    "beq": 0b000, "bne": 0b001, "blt": 0b100, "bge": 0b101,
    "bltu": 0b110, "bgeu": 0b111,
    "jalr": 0b000, "ecall": 0b000, "ebreak": 0b000
}

# Códigos de función de 7 bits (func7). Solo los que no son cero.
FUNC7: Dict[str, int] = {
    "sub": 0b0100000,
    "sra": 0b0100000,
    "srai": 0b0100000
}

# Mapeo de nombres de registros (ABI) a sus números.
REGISTROS: Dict[str, int] = {f'x{i}': i for i in range(32)}
REGISTROS.update({
    'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4, 't0': 5, 't1': 6, 't2': 7,
    's0': 8, 'fp': 8, 's1': 9, 'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14,
    'a5': 15, 'a6': 16, 'a7': 17, 's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22,
    's7': 23, 's8': 24, 's9': 25, 's10': 26, 's11': 27, 't3': 28, 't4': 29,
    't5': 30, 't6': 31
})