
label:      nop
            mov r0 0xbabe
label3:     mov r1 0xbeef
label2:     nop
            addi32 r0 1
            nop
            nop
            jnz label2
            ji label