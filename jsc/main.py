from . import DEBUG
from .ast import cexpr, cexpr_type
from .parser import parse


import hashlib
import sys
import subprocess

from pathlib import Path


def _render_expr(inp: cexpr) -> str:

    match inp.expr_type:
        case cexpr_type.LITERAL:
            return f"\tmovl    ${inp.value}, %eax\n"
        case cexpr_type.UNARY_OP:
            out = _render_expr(inp.children[0])

            match inp.value:
                case "~":
                    out += "\tnot %eax\n"
                case "-":
                    out += "\tneg %eax\n"
                case "!":
                    out += """\tcmpl $0, %eax
    \tmovl $0, %eax
    \tsete %al
    """
                case _:
                    raise ValueError()
            return out
        case cexpr_type.BINARY_OP:
            out = _render_expr(inp.children[1])  # right val
            out += "\tpush %rax\n"
            out += _render_expr(inp.children[0])  # puts left value in eax

            out += "\tpop %rbx\n"  # puts right value in ebx

            match inp.value:
                case "+":
                    out += "\taddl %ebx, %eax\n"
                case "-":
                    out += "\tsubl %ebx, %eax\n"
                case "*":
                    out += "\timul %ebx, %eax\n"
                case "/":

                    out += "\tcdq\n"  # sign extend
                    out += "\tidivl %ebx\n"  # EBX = EAX / EBX
                    out += "\tmov %eax, %ebx\n"  # EBX = EAX / EBX
            return out
        case _:
            raise ValueError()


def compile(inp: str) -> str:
    out = """
.globl main

main:
"""
    out += _render_expr(parse(inp))
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
