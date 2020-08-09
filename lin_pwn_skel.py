#!/usr/bin/env python3.8

import os, sys
from pwn import *

context.update(arch="amd64", # arch="i386", arch="mips", arch="arm",
               endian="little", os="linux", log_level="debug",
               terminal=["tmux", "split-window", "-h", "-p 65"],)


LOCAL = True
TARGET_ELF = os.path.realpath("./changeme")
TARGET_LIBC = os.path.realpath("./libc.so")
elf = ELF(TARGET_ELF)
libc = ELF(TARGET_LIBC)


def gdb_load_symbols_cmd(sym_file, e, base):
    sec_str = []
    for s in e.sections:
        if not s.name or not s.header.sh_addr:
            continue
        sec_str.append('-s {} 0x{:x}'.format(s.name, base + s.header.sh_addr))
    text_addr = e.get_section_by_name('.text').header.sh_addr + base
    return 'add-symbol-file {} 0x{:x} {} \n'.format(sym_file, text_addr, ' '.join(sec_str))


def attach(r):
    if LOCAL:
        # dbg_file = "libc/usr/lib/debug/.build-id/ce/17e023542265fc11d9bc8f534bb4f070493d30.debug"
        bkps = [
            elf.symbols["main"],
        ]
        cmds = [
            # "heap-analysis-helper",
            # "format-string-helper",
            # gdb_load_symbols_cmd(dbg_file, libc, r.libs()[libc.path]),
            # "bp * $_base() + 0x1337",
        ]
        gdb.attach(r, '\n'.join(["break *{:#x}".format(x) for x in bkps] + cmds))
    return


def exploit(r):
    attach(r)
    # r.sendlineafter(b"> ", b"HelloPwn" )
    r.interactive()
    return


if __name__ == "__main__":
    if len(sys.argv)>=2:
        LOCAL = FALSE
        r = remote(sys.argv[1], int(sys.argv[2]))
    else:
        LOCAL = True
        r = process([TARGET_ELF, ]) #, env={"LD_PRELOAD": libc.path})
    exploit(r)
    sys.exit(0)
