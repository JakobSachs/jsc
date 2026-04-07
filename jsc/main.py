from . import DEBUG
from .parser import parse


import hashlib, sys, subprocess

from pathlib import Path


def compile(inp: str) -> str:
    ops, val = parse(inp)
    out = f"""
.globl main

main:
"""
    out += f"\tmovl    ${val}, %eax\n"

    for o in reversed(ops):
        match o:
            case "~":
                out += "\tnot %eax\n"
            case "-":
                out += "\tneg %eax\n"
            case "!":
                out += """\tcmpl $0, %eax
\tmovl $0, %eax
\tsete %al
"""

    out += "\tret\n"

    return out


def main():
    assert len(sys.argv) == 2
    inp = open(sys.argv[1], "r").read()
    outp = Path(sys.argv[1]).with_suffix("")

    asm_tmp = Path("/tmp") / Path(hashlib.md5(inp.encode("utf-8")).hexdigest() + ".s")
    with open(asm_tmp, "w+") as asm_out:
        asm_out.write(asm := compile(inp))

        if DEBUG:
            print(asm)

    # let gcc do the hard-part
    subprocess.run(["gcc", str(asm_tmp), "-o", outp])


if __name__ == "__main__":
    main()
