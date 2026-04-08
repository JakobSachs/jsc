from jsc.ast import cexpr, cexpr_type
from jsc.parser import _parse_expr, PARSER

from lark import Tree

import pytest
from hypothesis import given, strategies as st

st_u32 = st.integers(min_value=0, max_value=2**32)


@given(st_u32)
def test_parse_expr_literal(n):
    inp: Tree = PARSER.parse(str(n), start="expr")

    res = _parse_expr(inp)

    assert isinstance(res, cexpr)
    assert res.expr_type == cexpr_type.LITERAL
    assert res.value == n


@given(st_u32)
@pytest.mark.parametrize("op", ["-", "~", "!"])
def test_parse_expr_unary(op, n):
    inp = PARSER.parse(op + str(n), start="expr")

    res = _parse_expr(inp)

    assert isinstance(res, cexpr)
    assert res.expr_type == cexpr_type.UNARY_OP
    assert isinstance(res.value, str)
    assert res.value == op
    assert (res.children is not None) and len(res.children) == 1

    val = res.children[0]
    assert val.expr_type == cexpr_type.LITERAL
    assert val.value == n


@given(st_u32, st_u32)
@pytest.mark.parametrize("op", ["+", "-", "*", "/"])
def test_parse_expr_binary(op, a, b):
    inp = PARSER.parse(str(a) + op + str(b), start="expr")

    res = _parse_expr(inp)

    assert isinstance(res, cexpr)
    assert res.expr_type == cexpr_type.BINARY_OP
    assert res.value == op
    assert (res.children is not None) and len(res.children) == 2

    val_a = res.children[0]
    val_b = res.children[1]

    assert val_a.expr_type == cexpr_type.LITERAL
    assert isinstance(val_a.value, int)
    assert val_a.value == a

    assert val_b.expr_type == cexpr_type.LITERAL
    assert isinstance(val_b.value, int)
    assert val_b.value == b
