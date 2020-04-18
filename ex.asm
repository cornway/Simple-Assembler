            ji label2
label0:     .word 0xffff
            .word 0xaaaa
            .asciz "hello_world."
            .allign 32
label:      stm r0 r1
            nop
            mov r0 0xbabe
label3:     mov r1 0xbeef
label2:     nop
            addi32 r0 1
            nop
            nop
            jnz label2
            ji label