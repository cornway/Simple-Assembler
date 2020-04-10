
label:      nop
            mov r0 0xbabe
            mov r1 0xbeef
label2:     nop
            addi32 r0 1
            nop
            nop
            jnz label2