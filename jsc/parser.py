from . import DEBUG
from .ast import cexpr, cexpr_type

from lark import Lark, Tree, Token

PARSER = Lark(
    r"""
    main: "int" "main" "(" ")" "{" stmt "}"

    stmt: ID expr ";"

    ?expr: sum

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> literal
        | UNARY_OP atom     -> unary_op_expr
        | "(" sum ")"

    UNARY_OP: "!" | "-" | "~"

    %import common.INT -> NUMBER
    %import common.WS
    %import common.CNAME -> ID

    %ignore WS
""",
    parser="lalr",
    start=["main", "expr"],
)


OPS_MAP = {
    "add": "+",
    "sub": "-",
    "div": "/",
    "mul": "*",
}


def _parse_expr(inp: Tree | Token) -> cexpr:
    if isinstance(inp, Token):
        return cexpr(expr_type=cexpr_type.LITERAL, value=int(inp))

    match inp.data:
        case "literal":
            return cexpr(expr_type=cexpr_type.LITERAL, value=int(inp.children[0]))

        case "unary_op_expr":
            op = str(inp.children[0])
            inner = _parse_expr(inp.children[1])
            return cexpr(expr_type=cexpr_type.UNARY_OP, value=op, children=[inner])

        case "add" | "sub" | "div" | "mul":
            assert len(inp.children) == 2
            return cexpr(
                expr_type=cexpr_type.BINARY_OP,
                value=OPS_MAP[inp.data],
                children=[_parse_expr(inp.children[0]), _parse_expr(inp.children[1])],
            )

        case v:
            raise ValueError(str(v) + " is unknown\n\t" + str(inp))


def parse(inp: str):

    root = PARSER.parse(inp, start="main")

    if DEBUG:
        print("root prettyprint\n" + 60 * "=")
        print(root.pretty())

    ret_stmt = root.children[0]
    assert ret_stmt.children[0] == "return"
    return _parse_expr(ret_stmt.children[1])
