"""The mini-Scheme standard library."""

import math
import operator
import sys
from functools import reduce
from typing import Any, Callable

from printer import scheme_to_string
from scheme_types import (
    BuiltinProcedure,
    Closure,
    EMPTY,
    Pair,
    Symbol,
    is_proper_list,
    list_to_pairs,
    pairs_to_list,
)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _require_numbers(values: tuple[Any, ...]) -> None:
    if not all(_is_number(value) for value in values):
        raise TypeError("expected numbers")


def add(*values: Any) -> Any:
    _require_numbers(values)
    return sum(values)


def subtract(first: Any, *rest: Any) -> Any:
    _require_numbers((first, *rest))
    if not rest:
        return -first
    return first - sum(rest)


def multiply(*values: Any) -> Any:
    _require_numbers(values)
    return reduce(operator.mul, values, 1)


def divide(first: Any, *rest: Any) -> Any:
    _require_numbers((first, *rest))
    if not rest:
        return 1.0 / first
    result = first
    for value in rest:
        if isinstance(result, int) and isinstance(value, int):
            result = int(result / value)
        else:
            result = result / value
    return result


def quotient(left: Any, right: Any) -> int:
    _require_numbers((left, right))
    return int(left / right)


def modulo(left: Any, right: Any) -> Any:
    _require_numbers((left, right))
    return left % right


def chained(comparator: Callable[[Any, Any], bool], *values: Any) -> bool:
    return all(comparator(left, right) for left, right in zip(values, values[1:]))


def scheme_not(value: Any) -> bool:
    return value is False


def car(value: Any) -> Any:
    if not isinstance(value, Pair):
        raise TypeError("car expects a pair")
    return value.first


def cdr(value: Any) -> Any:
    if not isinstance(value, Pair):
        raise TypeError("cdr expects a pair")
    return value.rest


def length(value: Any) -> int:
    return len(pairs_to_list(value))


def append(*values: Any) -> Any:
    if not values:
        return EMPTY
    result = values[-1]
    if not is_proper_list(result):
        raise TypeError("append expects lists")
    for value in reversed(values[:-1]):
        items = pairs_to_list(value)
        result = list_to_pairs(items, result)
    return result


def eq(left: Any, right: Any) -> bool:
    if left is EMPTY or right is EMPTY:
        return left is right
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if _is_number(left) and _is_number(right):
        return left == right
    if isinstance(left, Symbol) or isinstance(right, Symbol):
        return type(left) is type(right) and left == right
    return left is right


def equal(left: Any, right: Any) -> bool:
    if isinstance(left, Pair) and isinstance(right, Pair):
        return equal(left.first, right.first) and equal(left.rest, right.rest)
    if left is EMPTY or right is EMPTY:
        return left is right
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if _is_number(left) and _is_number(right):
        return left == right
    return type(left) is type(right) and left == right


def display(value: Any) -> None:
    sys.stdout.write(scheme_to_string(value, display=True))
    return None


def newline() -> None:
    sys.stdout.write("\n")
    return None


def standard_bindings() -> dict[Symbol, BuiltinProcedure]:
    functions: dict[str, Callable[..., Any]] = {
        "+": add,
        "-": subtract,
        "*": multiply,
        "/": divide,
        "modulo": modulo,
        "quotient": quotient,
        "expt": pow,
        "abs": abs,
        "=": lambda *xs: chained(operator.eq, *xs),
        "<": lambda *xs: chained(operator.lt, *xs),
        ">": lambda *xs: chained(operator.gt, *xs),
        "<=": lambda *xs: chained(operator.le, *xs),
        ">=": lambda *xs: chained(operator.ge, *xs),
        "not": scheme_not,
        "cons": Pair,
        "car": car,
        "cdr": cdr,
        "list": lambda *xs: list_to_pairs(list(xs)),
        "length": length,
        "append": append,
        "null?": lambda value: value is EMPTY,
        "pair?": lambda value: isinstance(value, Pair),
        "list?": is_proper_list,
        "number?": _is_number,
        "boolean?": lambda value: isinstance(value, bool),
        "symbol?": lambda value: isinstance(value, Symbol),
        "string?": lambda value: isinstance(value, str) and not isinstance(value, Symbol),
        "procedure?": lambda value: isinstance(value, (BuiltinProcedure, Closure)),
        "zero?": lambda value: _is_number(value) and value == 0,
        "even?": lambda value: _is_number(value) and value % 2 == 0,
        "odd?": lambda value: _is_number(value) and value % 2 != 0,
        "eq?": eq,
        "equal?": equal,
        "display": display,
        "newline": newline,
    }
    return {
        Symbol(name): BuiltinProcedure(name, function)
        for name, function in functions.items()
    }
