from enum import Enum

from dataclasses import dataclass


class cexpr_type(Enum):
    LITERAL = 1
    UNARY_OP = 2
    BINARY_OP = 3
    NESTED = 4  # do we need this ?


@dataclass
class cexpr:
    expr_type: cexpr_type
    value: int | str | None = None
    children: list[cexpr] | None = None
