"""Runtime value types used by the mini-Scheme interpreter."""

from dataclasses import dataclass
from typing import Any, Callable


class Symbol(str):
    """A Scheme symbol, kept distinct from a Scheme string."""


class _EmptyList:
    def __repr__(self) -> str:
        return "EMPTY"


EMPTY = _EmptyList()


@dataclass(frozen=True)
class Pair:
    first: Any
    rest: Any


@dataclass(frozen=True)
class BuiltinProcedure:
    name: str
    function: Callable[..., Any]


@dataclass(frozen=True)
class Closure:
    parameters: tuple[Symbol, ...]
    body: tuple[Any, ...]
    environment: Any


def list_to_pairs(items: list[Any], tail: Any = EMPTY) -> Any:
    """Build a Pair chain from left to right."""
    result = tail
    for item in reversed(items):
        result = Pair(item, result)
    return result


def pairs_to_list(value: Any) -> list[Any]:
    """Convert a proper Scheme list to a Python list."""
    result: list[Any] = []
    while isinstance(value, Pair):
        result.append(value.first)
        value = value.rest
    if value is not EMPTY:
        raise TypeError("expected a proper list")
    return result


def is_proper_list(value: Any) -> bool:
    while isinstance(value, Pair):
        value = value.rest
    return value is EMPTY
