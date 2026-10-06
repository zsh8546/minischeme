"""Lexical environments for Scheme variable lookup."""

from typing import Any, Iterable

from scheme_types import Symbol


class Environment:
    def __init__(self, parent: "Environment | None" = None):
        self.parent = parent
        self.bindings: dict[Symbol, Any] = {}

    def define(self, name: Symbol, value: Any) -> None:
        self.bindings[name] = value

    def lookup(self, name: Symbol) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        raise NameError(f"undefined symbol: {name}")

    def child(self, names: Iterable[Symbol], values: Iterable[Any]) -> "Environment":
        names = tuple(names)
        values = tuple(values)
        if len(names) != len(values):
            raise TypeError("wrong number of arguments")
        result = Environment(self)
        for name, value in zip(names, values):
            result.define(name, value)
        return result
