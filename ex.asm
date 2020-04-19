/*Memory test program*/
mem_start:  .dword 0x00001000
mem_end:    .dword 0x00002000
sp_top:     .dword 0x40000100
dbg_addr:   .dword 0x800000A0
            .asciiz "hello world! ****"
            .allign 2
            movw r5 sp_top
            ldm sp r5
            movw r5 mem_start
            ldm r0 r5
            movw r5 mem_end
            movr r4 r5
            ldm r1 r5
            movw r2 0x12345678
write_loop: stmdb r1 r2
            cmp r0 r1
            jneq write_loop
            movw r3 0
            movr r1 r4
read_loop:  ldmia r6 r0
            cmp r6 r2
            jeq match
            inc r3 1
match:      cmp r0 r1
            jneq read_loop
            movw r0 dbg_addr
            stm r0 r3
            halt