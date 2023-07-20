from nicegui_test.procs.lisp_math import parse, math_eval
import pytest


@pytest.mark.parametrize(
    ["raw", "parsed"],
    [
        ("(* 1 2)", ["*", 1, 2]),
        ("(+ 1 (- 5.0 2.0))", ["+", 1, ["-", 5.0, 2.0]]),
        ("1", 1),
        ("1 2 3", 1),
    ],
)
def test_correct_parse(raw, parsed):
    assert parse(raw) == parsed


@pytest.mark.parametrize(
    ["raw", "expected_text"],
    [
        ("", "value cannot be empty"),
        (")", "unexpected )"),
    ],
)
def test_incorrect_parse(raw, expected_text):
    with pytest.raises(ValueError) as ex:
        parse(raw)
    assert str(ex.value) == expected_text


@pytest.mark.parametrize(
    ["raw", "expected"],
    [
        ("1", 1),
        ("1 2", 1),
        ("(+ 1 2)", 3),
        ("(+ 1 (+ 2 3))", 6),
        ("(+ (/ 4 2) (* 3 6))", 20),
    ],
)
def test_math_eval(raw, expected):
    assert math_eval(raw) == expected
