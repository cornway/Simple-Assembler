/*Memory test program*/
            ji entry
            .section 0x10
sp_top:     .dword 0x40000100
mem_start:  .dword 0x00001000
mem_end:    .dword 0x00002000
dbg_addr:   .dword 0x80000020
            .allign 2
entry:      movw r5 sp_top
            ldmia sp r5 //sp
            ldmia r0 r5 //mem_start
            ldmia r1 r5 //mem_end
            movr r4 r1 //mem_start
            ldm r6 r5 //dbg_addr
            movw r2 0x12345678
            stm r6 r2 //dbg
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
            ldm r0 r0
            stm r0 r3
            halt