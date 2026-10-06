"""Tokenizer for the mini-Scheme source language."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    kind: str
    value: str


_ESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    index = 0

    while index < len(source):
        char = source[index]

        if char.isspace():
            index += 1
            continue

        if char == ";":
            while index < len(source) and source[index] != "\n":
                index += 1
            continue

        if char in "()'":
            tokens.append(Token(char, char))
            index += 1
            continue

        if char == '"':
            index += 1
            value: list[str] = []
            while index < len(source) and source[index] != '"':
                if source[index] == "\\":
                    index += 1
                    if index >= len(source):
                        raise SyntaxError("unfinished string escape")
                    escaped = source[index]
                    if escaped not in _ESCAPES:
                        raise SyntaxError(f"unsupported string escape: \\{escaped}")
                    value.append(_ESCAPES[escaped])
                else:
                    value.append(source[index])
                index += 1
            if index >= len(source):
                raise SyntaxError("unterminated string")
            index += 1
            tokens.append(Token("string", "".join(value)))
            continue

        start = index
        while (
            index < len(source)
            and not source[index].isspace()
            and source[index] not in "()';\""
        ):
            index += 1
        tokens.append(Token("atom", source[start:index]))

    return tokens
