"""Conversion of Scheme values to their required textual form."""

from typing import Any

from scheme_types import BuiltinProcedure, Closure, EMPTY, Pair, Symbol


def _escape_string(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )


def scheme_to_string(value: Any, display: bool = False) -> str:
    if value is True:
        return "#t"
    if value is False:
        return "#f"
    if value is EMPTY:
        return "()"
    if isinstance(value, Symbol):
        return str(value)
    if isinstance(value, str):
        return value if display else f'"{_escape_string(value)}"'
    if isinstance(value, Pair):
        parts: list[str] = []
        cursor: Any = value
        while isinstance(cursor, Pair):
            parts.append(scheme_to_string(cursor.first))
            cursor = cursor.rest
        if cursor is EMPTY:
            return "(" + " ".join(parts) + ")"
        return "(" + " ".join(parts) + " . " + scheme_to_string(cursor) + ")"
    if isinstance(value, (BuiltinProcedure, Closure)):
        return "#<procedure>"
    return str(value)
