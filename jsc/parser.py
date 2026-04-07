from . import DEBUG

from lark import Lark

PARSER = Lark(
    r"""
    main: "int" "main" "(" ")" "{" stmt "}" 

    stmt: ID expr ";"
        
    expr: NUMBER | SINGLETON_OP expr

    SINGLETON_OP: "!" | "-" | "~"

    %import common.INT -> NUMBER
    %import common.WS
    %import common.CNAME -> ID

    %ignore WS
""",
    start="main",
)


def parse(inp: str):

    root = PARSER.parse(inp)

    if DEBUG:
        print("root prettyprint\n" + 60 * "=")
        print(root.pretty())

    ret_stmt = root.children[0]

    assert ret_stmt.children[0] == "return"
    expr = ret_stmt.children[1]
    ops = []
    while len(expr.children) == 2:
        ops.append(expr.children[0].value)
        expr = expr.children[1]
    return ops, int(expr.children[-1])
