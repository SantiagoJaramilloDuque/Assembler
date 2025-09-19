# Instrucciones RISC-V Soportadas

Esta documentación detalla todas las instrucciones y pseudo-instrucciones soportadas por el ensamblador, incluyendo su formato, codificación y ejemplos de uso.

## Tabla de Contenidos

- [Instrucciones Base RV32I](#instrucciones-base-rv32i)
- [Pseudo-instrucciones](#pseudo-instrucciones)
- [Formatos de Instrucción](#formatos-de-instrucción)
- [Registros](#registros)
- [Ejemplos de Codificación](#ejemplos-de-codificación)

## Instrucciones Base RV32I

### Instrucciones Tipo R (Registro-Registro)

| Instrucción         | Operación                | Formato | Descripción                       |
| ------------------- | ------------------------ | ------- | --------------------------------- |
| `add rd, rs1, rs2`  | rd = rs1 + rs2           | R       | Suma                              |
| `sub rd, rs1, rs2`  | rd = rs1 - rs2           | R       | Resta                             |
| `sll rd, rs1, rs2`  | rd = rs1 << rs2          | R       | Desplazamiento lógico izquierda   |
| `slt rd, rs1, rs2`  | rd = (rs1 < rs2) ? 1 : 0 | R       | Menor que (con signo)             |
| `sltu rd, rs1, rs2` | rd = (rs1 < rs2) ? 1 : 0 | R       | Menor que (sin signo)             |
| `xor rd, rs1, rs2`  | rd = rs1 ^ rs2           | R       | XOR lógico                        |
| `srl rd, rs1, rs2`  | rd = rs1 >> rs2          | R       | Desplazamiento lógico derecha     |
| `sra rd, rs1, rs2`  | rd = rs1 >> rs2          | R       | Desplazamiento aritmético derecha |
| `or rd, rs1, rs2`   | rd = rs1 \| rs2          | R       | OR lógico                         |
| `and rd, rs1, rs2`  | rd = rs1 & rs2           | R       | AND lógico                        |

**Ejemplo**:

```assembly
add x1, x2, x3    # x1 = x2 + x3
sub x4, x5, x6    # x4 = x5 - x6
```

### Instrucciones Tipo I (Inmediato)

#### Operaciones Aritméticas con Inmediato

| Instrucción          | Operación                | Rango Inmediato | Descripción                     |
| -------------------- | ------------------------ | --------------- | ------------------------------- |
| `addi rd, rs1, imm`  | rd = rs1 + imm           | -2048 a 2047    | Suma con inmediato              |
| `slti rd, rs1, imm`  | rd = (rs1 < imm) ? 1 : 0 | -2048 a 2047    | Menor que inmediato (con signo) |
| `sltiu rd, rs1, imm` | rd = (rs1 < imm) ? 1 : 0 | -2048 a 2047    | Menor que inmediato (sin signo) |
| `xori rd, rs1, imm`  | rd = rs1 ^ imm           | -2048 a 2047    | XOR con inmediato               |
| `ori rd, rs1, imm`   | rd = rs1 \| imm          | -2048 a 2047    | OR con inmediato                |
| `andi rd, rs1, imm`  | rd = rs1 & imm           | -2048 a 2047    | AND con inmediato               |

#### Desplazamientos con Inmediato

| Instrucción         | Operación       | Rango Inmediato | Descripción                       |
| ------------------- | --------------- | --------------- | --------------------------------- |
| `slli rd, rs1, imm` | rd = rs1 << imm | 0 a 31          | Desplazamiento lógico izquierda   |
| `srli rd, rs1, imm` | rd = rs1 >> imm | 0 a 31          | Desplazamiento lógico derecha     |
| `srai rd, rs1, imm` | rd = rs1 >> imm | 0 a 31          | Desplazamiento aritmético derecha |

#### Instrucciones de Carga

| Instrucción        | Operación                 | Descripción                 |
| ------------------ | ------------------------- | --------------------------- |
| `lb rd, imm(rs1)`  | rd = MEM[rs1 + imm][7:0]  | Cargar byte (con signo)     |
| `lh rd, imm(rs1)`  | rd = MEM[rs1 + imm][15:0] | Cargar halfword (con signo) |
| `lw rd, imm(rs1)`  | rd = MEM[rs1 + imm][31:0] | Cargar word                 |
| `lbu rd, imm(rs1)` | rd = MEM[rs1 + imm][7:0]  | Cargar byte (sin signo)     |
| `lhu rd, imm(rs1)` | rd = MEM[rs1 + imm][15:0] | Cargar halfword (sin signo) |

**Ejemplo**:

```assembly
addi x1, x2, 100     # x1 = x2 + 100
lw x3, 8(sp)         # x3 = memoria[sp + 8]
slli x4, x5, 2       # x4 = x5 << 2 (multiplicar por 4)
```

#### Instrucciones de Salto y Sistema

| Instrucción         | Operación                 | Descripción                      |
| ------------------- | ------------------------- | -------------------------------- |
| `jalr rd, rs1, imm` | rd = PC+4; PC = rs1 + imm | Salto y enlace mediante registro |
| `ecall`             | -                         | Llamada al sistema               |
| `ebreak`            | -                         | Punto de interrupción            |
| `fence`             | -                         | Sincronización de memoria        |

### Instrucciones Tipo S (Almacenamiento)

| Instrucción        | Operación                  | Descripción        |
| ------------------ | -------------------------- | ------------------ |
| `sb rs2, imm(rs1)` | MEM[rs1 + imm][7:0] = rs2  | Almacenar byte     |
| `sh rs2, imm(rs1)` | MEM[rs1 + imm][15:0] = rs2 | Almacenar halfword |
| `sw rs2, imm(rs1)` | MEM[rs1 + imm][31:0] = rs2 | Almacenar word     |

**Ejemplo**:

```assembly
sw x1, 12(sp)        # memoria[sp + 12] = x1
sb x2, 0(x3)         # memoria[x3] = x2 (solo byte inferior)
```

### Instrucciones Tipo B (Salto Condicional)

| Instrucción          | Condición              | Descripción                            |
| -------------------- | ---------------------- | -------------------------------------- |
| `beq rs1, rs2, imm`  | rs1 == rs2             | Salto si igual                         |
| `bne rs1, rs2, imm`  | rs1 != rs2             | Salto si no igual                      |
| `blt rs1, rs2, imm`  | rs1 < rs2 (con signo)  | Salto si menor que                     |
| `bge rs1, rs2, imm`  | rs1 >= rs2 (con signo) | Salto si mayor o igual que             |
| `bltu rs1, rs2, imm` | rs1 < rs2 (sin signo)  | Salto si menor que (sin signo)         |
| `bgeu rs1, rs2, imm` | rs1 >= rs2 (sin signo) | Salto si mayor o igual que (sin signo) |

**Rango de salto**: -4096 a +4094 bytes (múltiplos de 2)

**Ejemplo**:

```assembly
beq x1, x2, loop     # Saltar a 'loop' si x1 == x2
blt x3, x4, end      # Saltar a 'end' si x3 < x4
```

### Instrucciones Tipo U (Inmediato Superior)

| Instrucción     | Operación             | Descripción                   |
| --------------- | --------------------- | ----------------------------- |
| `lui rd, imm`   | rd = imm << 12        | Cargar inmediato superior     |
| `auipc rd, imm` | rd = PC + (imm << 12) | Sumar inmediato superior a PC |

**Rango de inmediato**: 20 bits (0 a 1048575)

**Ejemplo**:

```assembly
lui x1, 0x12345      # x1 = 0x12345000
auipc x2, 0x1000     # x2 = PC + 0x1000000
```

### Instrucciones Tipo J (Salto)

| Instrucción   | Operación                  | Descripción    |
| ------------- | -------------------------- | -------------- |
| `jal rd, imm` | rd = PC + 4; PC = PC + imm | Salto y enlace |

**Rango de salto**: -1048576 a +1048574 bytes (múltiplos de 2)

**Ejemplo**:

```assembly
jal ra, function     # Llamar función, retorno en ra
jal x0, label        # Salto incondicional (no guardar retorno)
```

## Pseudo-instrucciones

Las pseudo-instrucciones son instrucciones de conveniencia que se expanden automáticamente a una o más instrucciones base.

### Operaciones Básicas

| Pseudo-instrucción | Expansión         | Descripción         |
| ------------------ | ----------------- | ------------------- |
| `nop`              | `addi x0, x0, 0`  | No operación        |
| `mv rd, rs`        | `addi rd, rs, 0`  | Mover registro      |
| `not rd, rs`       | `xori rd, rs, -1` | Complemento lógico  |
| `neg rd, rs`       | `sub rd, x0, rs`  | Negación aritmética |

### Carga de Inmediatos

| Pseudo-instrucción | Expansión                                        | Descripción             |
| ------------------ | ------------------------------------------------ | ----------------------- |
| `li rd, imm`       | `addi rd, x0, imm` (si -2048 ≤ imm < 2048)       | Cargar inmediato        |
| `li rd, imm`       | `lui rd, hi` + `addi rd, rd, lo` (si imm grande) | Cargar inmediato grande |

**Ejemplo**:

```assembly
li x1, 100           # x1 = 100 (se convierte a: addi x1, x0, 100)
li x2, 0x12345678    # Inmediato grande (se convierte a: lui + addi)
```

### Saltos y Llamadas

| Pseudo-instrucción | Expansión                                            | Descripción                   |
| ------------------ | ---------------------------------------------------- | ----------------------------- |
| `j offset`         | `jal x0, offset`                                     | Salto incondicional           |
| `jal offset`       | `jal ra, offset`                                     | Salto y enlace (ra implícito) |
| `jr rs`            | `jalr x0, rs, 0`                                     | Salto a registro              |
| `jalr rs`          | `jalr ra, rs, 0`                                     | Salto y enlace a registro     |
| `ret`              | `jalr x0, ra, 0`                                     | Retorno de función            |
| `call offset`      | `auipc ra, %hi(offset)` + `jalr ra, %lo(offset)(ra)` | Llamada lejana                |

### Comparaciones con Cero

| Pseudo-instrucción | Expansión         | Descripción            |
| ------------------ | ----------------- | ---------------------- |
| `seqz rd, rs`      | `sltiu rd, rs, 1` | Set si igual a cero    |
| `snez rd, rs`      | `sltu rd, x0, rs` | Set si no igual a cero |
| `sltz rd, rs`      | `slt rd, rs, x0`  | Set si menor que cero  |
| `sgtz rd, rs`      | `slt rd, x0, rs`  | Set si mayor que cero  |

### Saltos Condicionales con Cero

| Pseudo-instrucción | Expansión            | Descripción                   |
| ------------------ | -------------------- | ----------------------------- |
| `beqz rs, offset`  | `beq rs, x0, offset` | Salto si igual a cero         |
| `bnez rs, offset`  | `bne rs, x0, offset` | Salto si no igual a cero      |
| `bltz rs, offset`  | `blt rs, x0, offset` | Salto si menor que cero       |
| `bgez rs, offset`  | `bge rs, x0, offset` | Salto si mayor o igual a cero |

**Ejemplo**:

```assembly
beqz x1, zero_case   # Saltar si x1 == 0
bnez x2, non_zero    # Saltar si x2 != 0
```

## Formatos de Instrucción

### Formato R (Registro)

```
31    25 24  20 19  15 14  12 11   7 6     0
[func7 ] [rs2 ] [rs1 ] [f3 ] [ rd ] [opcode]
```

### Formato I (Inmediato)

```
31          20 19  15 14  12 11   7 6     0
[   imm[11:0] ] [rs1 ] [f3 ] [ rd ] [opcode]
```

### Formato S (Almacenamiento)

```
31    25 24  20 19  15 14  12 11       7 6     0
[imm[11:5]] [rs2 ] [rs1 ] [f3 ] [imm[4:0]] [opcode]
```

### Formato B (Salto Condicional)

```
31 30    25 24  20 19  15 14  12 11    8 7 6     0
[i][imm[10:5]] [rs2 ] [rs1 ] [f3 ] [imm[4:1]][i] [opcode]
```

### Formato U (Inmediato Superior)

```
31                    12 11   7 6     0
[       imm[31:12]      ] [ rd ] [opcode]
```

### Formato J (Salto)

```
31 30      21 20 19        12 11   7 6     0
[i][imm[10:1]][i] [imm[19:12]] [ rd ] [opcode]
```

## Registros

### Registros Numéricos

- `x0` - `x31`: Registros de propósito general (x0 siempre es 0)

### Registros ABI (Application Binary Interface)

| Registro | ABI    | Descripción                   | Guardado por |
| -------- | ------ | ----------------------------- | ------------ |
| x0       | zero   | Constante cero                | -            |
| x1       | ra     | Dirección de retorno          | Llamador     |
| x2       | sp     | Puntero de pila               | Llamado      |
| x3       | gp     | Puntero global                | -            |
| x4       | tp     | Puntero de hilo               | -            |
| x5-x7    | t0-t2  | Temporales                    | Llamador     |
| x8       | s0/fp  | Marco de pila / Guardado      | Llamado      |
| x9       | s1     | Guardado                      | Llamado      |
| x10-x11  | a0-a1  | Argumentos/valores de retorno | Llamador     |
| x12-x17  | a2-a7  | Argumentos                    | Llamador     |
| x18-x27  | s2-s11 | Guardados                     | Llamado      |
| x28-x31  | t3-t6  | Temporales                    | Llamador     |

## Ejemplos de Codificación

### Ejemplo 1: Instrucción ADD

```assembly
add x1, x2, x3
```

**Codificación**:

- Formato: R
- func7 = 0000000, rs2 = 3, rs1 = 2, func3 = 000, rd = 1, opcode = 0110011
- Binario: `00000000001100010000000010110011`
- Hexadecimal: `003100B3`

### Ejemplo 2: Instrucción ADDI

```assembly
addi x1, x2, 100
```

**Codificación**:

- Formato: I
- imm = 100 (000001100100), rs1 = 2, func3 = 000, rd = 1, opcode = 0010011
- Binario: `00000001100100010000000010010011`
- Hexadecimal: `06410093`

### Ejemplo 3: Pseudo-instrucción LI

```assembly
li x1, 0x12345678
```

**Expansión**:

```assembly
lui x1, 0x12346      # Parte alta + 1 (por redondeo)
addi x1, x1, 0x678   # Parte baja
```

## Limitaciones y Restricciones

### Rangos de Inmediatos

- **Tipo I**: -2048 a 2047 (12 bits con signo)
- **Tipo S/B**: -2048 a 2047 (12 bits con signo, divididos)
- **Tipo U**: 0 a 1048575 (20 bits sin signo)
- **Tipo J**: -1048576 a 1048574 (21 bits con signo)

### Alineación

- **Instrucciones**: Deben estar alineadas a 4 bytes
- **Halfwords**: Deben estar alineadas a 2 bytes
- **Words**: Deben estar alineadas a 4 bytes

### Registro x0

- Siempre lee como 0
- Las escrituras se descartan
- Útil para descartar resultados o como fuente de 0

Esta documentación cubre todas las instrucciones soportadas por el ensamblador. Para ejemplos prácticos de uso, consulta la documentación de ejemplos.
