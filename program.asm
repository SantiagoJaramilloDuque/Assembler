    .text
    .globl main
    
main:
    # ---- Pseudoinstrucciones ----
    nop                 # addi x0, x0, 0
    li x5, 1234         # carga inmediato (expande a lui+addi si es grande)
    mv x6, x5           # mueve (addi x6, x5, 0)
    not x7, x5          # bitwise not
    neg x8, x5          # aritmético neg

    # ---- Instrucciones tipo R ----
    add x9, x5, x6
    sub x10, x6, x5
    and x11, x6, x7
    or  x12, x7, x8
    xor x13, x5, x7
    sll x14, x5, x6
    srl x15, x6, x5
    sra x16, x7, x5
    slt x17, x5, x6
    sltu x18, x6, x5

    # ---- Instrucciones tipo I ----
    addi x19, x0, 42
    andi x20, x19, 15
    ori  x21, x19, 7
    xori x22, x19, 3
    slli x23, x19, 1
    srli x24, x19, 2
    srai x25, x19, 3

    # ---- Cargas (tipo I load) ----
    lw x27, 0(x26)
    lh x28, 2(x26)
    lb x29, 4(x26)
    lhu x30, 2(x26)
    lbu x31, 4(x26)

    # ---- Guardados (tipo S) ----
    sw x27, 8(x26)
    sh x28, 12(x26)
    sb x29, 16(x26)

    # ---- Instrucciones tipo B ----
    beq x5, x6, etiqueta
    bne x5, x6, etiqueta
    blt x5, x6, etiqueta
    bge x5, x6, etiqueta
    bltu x5, x6, etiqueta
    bgeu x5, x6, etiqueta

    # ---- Instrucciones tipo U ----
    lui x1, 0x12345
    auipc x2, 0x10

    # ---- Saltos (tipo J e I) ----
    jal x1, etiqueta
    jalr x0, 0(x1)       # salto indirecto
    j etiqueta          # pseudo: jal x0, etiqueta
    call etiqueta       # pseudo: jal ra, etiqueta
    ret                 # pseudo: jalr x0, ra, 0

etiqueta:
    addi x3, x0, 99

    # ---- Finalizar ----
    li a7, 93           # código de syscall exit en Linux
    ecall               # salir
