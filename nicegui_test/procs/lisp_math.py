"""
Simplified version of https://norvig.com/lispy.html
"""
from typing import Union
import math
import operator as op

Symbol = str
Number = Union[int, float]
Atom = Union[Symbol, Number]
List = list
Exp = Union[Atom, List]

Env = {
    "+": op.add,
    "-": op.sub,
    "*": op.mul,
    "/": op.truediv,
    "abs": abs,
    "pow": math.pow,
    "exp": math.exp,
}


def tokenize(chars: str) -> list[str]:
    """
    Converts a string to a list of tokens.
    """
    return chars.strip().replace("(", " ( ").replace(")", " ) ").split()


def read_from_tokens(tokens: list[str]) -> Exp:
    if len(tokens) == 0:
        raise ValueError("value cannot be empty")
    token = tokens.pop(0)
    if token == "(":
        L = []
        while tokens[0] != ")":
            L.append(read_from_tokens(tokens))
        tokens.pop(0)
        return L
    elif token == ")":
        raise ValueError("unexpected )")
    else:
        return to_atom(token)


def to_atom(token: str) -> Atom:
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


def parse(program: str) -> Exp:
    return read_from_tokens(tokenize(program))


def _do_eval(exp: Exp) -> Union[int, float]:
    if isinstance(exp, (int, float)):
        return exp
    elif isinstance(exp, Symbol):
        return Env[exp]
    else:
        proc = _do_eval(exp[0])
        args = [_do_eval(arg) for arg in exp[1:]]
        return proc(*args)


def math_eval(exp: Union[str, Exp]) -> Union[int, float]:
    if isinstance(exp, str):
        exp = parse(exp)
    return _do_eval(exp)
