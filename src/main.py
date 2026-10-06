"""Command-line entry point for the mini-Scheme interpreter."""

import sys
from pathlib import Path

from environment import Environment
from evaluator import evaluate
from parser import parse
from primitives import standard_bindings
from printer import scheme_to_string
from tokenizer import tokenize


def create_global_environment() -> Environment:
    environment = Environment()
    for name, procedure in standard_bindings().items():
        environment.define(name, procedure)
    return environment


def run_source(source: str, environment: Environment) -> None:
    for expression in parse(tokenize(source)):
        result = evaluate(expression, environment)
        if result is not None:
            print(scheme_to_string(result))


def main() -> None:
    environment = create_global_environment()
    if len(sys.argv) == 1:
        run_source(sys.stdin.read(), environment)
        return
    for filename in sys.argv[1:]:
        run_source(Path(filename).read_text(encoding="utf-8"), environment)


if __name__ == "__main__":
    main()
