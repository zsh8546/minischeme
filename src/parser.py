"""Recursive-descent parser for mini-Scheme expressions."""

import re
from typing import Any

from scheme_types import Symbol
from tokenizer import Token


_INTEGER = re.compile(r"[+-]?\d+\Z")
_FLOAT = re.compile(r"[+-]?(?:\d+\.\d*|\.\d+)\Z")


def _parse_atom(token: Token) -> Any:
    if token.kind == "string":
        return token.value
    text = token.value
    if text == "#t":
        return True
    if text == "#f":
        return False
    if _INTEGER.fullmatch(text):
        return int(text)
    if _FLOAT.fullmatch(text):
        return float(text)
    return Symbol(text)


def parse(tokens: list[Token]) -> list[Any]:
    """Parse all top-level expressions in *tokens*."""
    position = 0

    def expression() -> Any:
        nonlocal position
        if position >= len(tokens):
            raise SyntaxError("unexpected end of input")

        token = tokens[position]
        position += 1

        if token.kind == "(":
            result: list[Any] = []
            while position < len(tokens) and tokens[position].kind != ")":
                result.append(expression())
            if position >= len(tokens):
                raise SyntaxError("missing closing parenthesis")
            position += 1
            return result
        if token.kind == ")":
            raise SyntaxError("unexpected closing parenthesis")
        if token.kind == "'":
            return [Symbol("quote"), expression()]
        return _parse_atom(token)

    result: list[Any] = []
    while position < len(tokens):
        result.append(expression())
    return result
