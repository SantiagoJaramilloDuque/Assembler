# ML_Translator

Well, this is a translator that converts from LOW LEVEL LANGUAGE RISC-V INSTRUCTIONS to HEXADECIMAL MACHINE LANGUAGE 

the branch "fully_functional_translator" is the most updated branch

HOW DOES IT WORK?

in the file "InputSampleLLL.txt" you write the RISC-V instructions line by line, then you execute the main code and volià, 
the hexadecimal instructions will appear in the file "OutputSampleHex"

HOW YOU SHOULD WRITE THE LOW LEVEL LANGUAGE INSTRUCTIONS

you follow the RISC-V standard but every element of the sentence must be separated by a comma (,)

EXAMPLE, if you want to write:
addi sp, sp, -20

you write: addi,sp,sp,-20

OTHER EXAMPLES:
sw x8, 0(sp) -> sw,x8,0,sp

jalr x0, 0(ra) -> jalr,x0,0,ra

jal -7 -> jal,x1,-7 //I know that 'x1' in this case is implicit but you must be explicit for this code to work properly

THE JUMPS

in branch instrutions you simply enter the cuantity of jumps required for going from line A to line B

that's to say, if you have:

0x...4024     for0:       bge, x18, x9, endfor0
                .
                .
                .
               
0x...4068     endfor0:    ...

if you subtract the hexadecimal numbers 4068 - 4024 = you get 44, you convert that to decimal base and it's 68, you divide it by 4 and it's 17

so, 17 is the number that you must write in the instruction:  bge, x18, x9, 17

why?

well, for a processor addressed by Byte, one instruction is in actually saved in 4 lines of memory, but in the real life you only have to count the
lines between instructions

same applies for negative jumps (backwards jumps) if you got -68 in base decimal, you write -17 in the B-Type instruction

I GUARANTEE YOU THAT THIS PROGRAM WORKS 100% PERFECTLY FOR ANY R,T,S,B,J TYPE INSTRUCTION ACCORDING TO RISC-V ARCHITECTURE OF 32-bits intructions

the only 2 insturctions for which I don't gurantee quality are 'lui' and 'auipc' I never used them and I don't know them deeply, I assumed the Imm 
for U type do jumps the same way as 'jal' does, so the logic is the same specified above.


I hope this is useful for you.

