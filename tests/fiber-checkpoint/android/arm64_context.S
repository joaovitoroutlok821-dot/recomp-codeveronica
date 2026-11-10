// Minimal AArch64 cooperative context switch for Android NDK prototype.
// Context layout is defined in fiber_android_arm64.cpp.
.text
.align  2
.global rex_fiber_swap
.type rex_fiber_swap, %function
rex_fiber_swap:
    // Save callee-saved integer registers and the continuation address.
    stp     x19, x20, [x0, #0]
    stp     x21, x22, [x0, #16]
    stp     x23, x24, [x0, #32]
    stp     x25, x26, [x0, #48]
    stp     x27, x28, [x0, #64]
    stp     x29, x30, [x0, #80]
    mov     x9, sp
    str     x9, [x0, #96]

    // AAPCS64 requires preservation of the low 64 bits of v8-v15.
    stp     d8,  d9,  [x0, #104]
    stp     d10, d11, [x0, #120]
    stp     d12, d13, [x0, #136]
    stp     d14, d15, [x0, #152]

    // Restore target context. x0/x1 are caller-saved and intentionally not
    // part of a suspended C++ call's preserved state.
    ldp     d8,  d9,  [x1, #104]
    ldp     d10, d11, [x1, #120]
    ldp     d12, d13, [x1, #136]
    ldp     d14, d15, [x1, #152]
    ldp     x19, x20, [x1, #0]
    ldp     x21, x22, [x1, #16]
    ldp     x23, x24, [x1, #32]
    ldp     x25, x26, [x1, #48]
    ldp     x27, x28, [x1, #64]
    ldp     x29, x30, [x1, #80]
    ldr     x9, [x1, #96]
    mov     sp, x9
    ret
.size rex_fiber_swap, .-rex_fiber_swap

.align 2
.global rex_fiber_register_probe
.type rex_fiber_register_probe, %function
// int rex_fiber_register_probe(Fiber* target)
// Loads sentinels into AAPCS64 callee-saved x19-x29 and d8-d15,
// yields to target, then verifies that the suspended context restored them.
rex_fiber_register_probe:
    sub     sp, sp, #176
    stp     x19, x20, [sp, #0]
    stp     x21, x22, [sp, #16]
    stp     x23, x24, [sp, #32]
    stp     x25, x26, [sp, #48]
    stp     x27, x28, [sp, #64]
    stp     x29, x30, [sp, #80]
    stp     d8, d9, [sp, #96]
    stp     d10, d11, [sp, #112]
    stp     d12, d13, [sp, #128]
    stp     d14, d15, [sp, #144]
    str     x0, [sp, #160]

    movz    x19, #0x1919
    movz    x20, #0x2020
    movz    x21, #0x2121
    movz    x22, #0x2222
    movz    x23, #0x2323
    movz    x24, #0x2424
    movz    x25, #0x2525
    movz    x26, #0x2626
    movz    x27, #0x2727
    movz    x28, #0x2828
    movz    x29, #0x2929
    movz    x10, #0xD808
    fmov    d8, x10
    movz    x10, #0xD909
    fmov    d9, x10
    movz    x10, #0xDA0A
    fmov    d10, x10
    movz    x10, #0xDB0B
    fmov    d11, x10
    movz    x10, #0xDC0C
    fmov    d12, x10
    movz    x10, #0xDD0D
    fmov    d13, x10
    movz    x10, #0xDE0E
    fmov    d14, x10
    movz    x10, #0xDF0F
    fmov    d15, x10

    ldr     x0, [sp, #160]
    bl      rex_fiber_switch

    // Verify integer callee-saved registers.
    movz    x10, #0x1919
    cmp     x19, x10
    b.ne    .Lfiber_reg_fail
    movz    x10, #0x2020
    cmp     x20, x10
    b.ne    .Lfiber_reg_fail
    movz    x10, #0x2121
    cmp     x21, x10
    b.ne    .Lfiber_reg_fail
    movz    x10, #0x2222
    cmp     x22, x10
    b.ne    .Lfiber_reg_fail
    movz    x10, #0x2323
    cmp     x23, x10
    b.ne    .Lfiber_reg_fail
    movz    x10, #0x2424
    cmp     x24, x10
    b.ne    .Lfiber_reg_fail
    movz    x10, #0x2525
    cmp     x25, x10
    b.ne    .Lfiber_reg_fail
    movz    x10, #0x2626
    cmp     x26, x10
    b.ne    .Lfiber_reg_fail
    movz    x10, #0x2727
    cmp     x27, x10
    b.ne    .Lfiber_reg_fail
    movz    x10, #0x2828
    cmp     x28, x10
    b.ne    .Lfiber_reg_fail
    movz    x10, #0x2929
    cmp     x29, x10
    b.ne    .Lfiber_reg_fail

    // Verify the low 64 bits of v8-v15 (AAPCS64 d8-d15).
    fmov    x11, d8
    movz    x10, #0xD808
    cmp     x11, x10
    b.ne    .Lfiber_reg_fail
    fmov    x11, d9
    movz    x10, #0xD909
    cmp     x11, x10
    b.ne    .Lfiber_reg_fail
    fmov    x11, d10
    movz    x10, #0xDA0A
    cmp     x11, x10
    b.ne    .Lfiber_reg_fail
    fmov    x11, d11
    movz    x10, #0xDB0B
    cmp     x11, x10
    b.ne    .Lfiber_reg_fail
    fmov    x11, d12
    movz    x10, #0xDC0C
    cmp     x11, x10
    b.ne    .Lfiber_reg_fail
    fmov    x11, d13
    movz    x10, #0xDD0D
    cmp     x11, x10
    b.ne    .Lfiber_reg_fail
    fmov    x11, d14
    movz    x10, #0xDE0E
    cmp     x11, x10
    b.ne    .Lfiber_reg_fail
    fmov    x11, d15
    movz    x10, #0xDF0F
    cmp     x11, x10
    b.ne    .Lfiber_reg_fail

    mov     x0, #0
    b       .Lfiber_reg_restore
.Lfiber_reg_fail:
    mov     x0, #1
.Lfiber_reg_restore:
    ldp     x19, x20, [sp, #0]
    ldp     x21, x22, [sp, #16]
    ldp     x23, x24, [sp, #32]
    ldp     x25, x26, [sp, #48]
    ldp     x27, x28, [sp, #64]
    ldp     x29, x30, [sp, #80]
    ldp     d8, d9, [sp, #96]
    ldp     d10, d11, [sp, #112]
    ldp     d12, d13, [sp, #128]
    ldp     d14, d15, [sp, #144]
    add     sp, sp, #176
    ret
.size rex_fiber_register_probe, .-rex_fiber_register_probe
