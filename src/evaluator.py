"""Evaluation rules for mini-Scheme."""

from typing import Any

from environment import Environment
from scheme_types import BuiltinProcedure, Closure, EMPTY, Pair, Symbol, list_to_pairs


def is_truthy(value: Any) -> bool:
    return value is not False


def quote_value(expression: Any) -> Any:
    if isinstance(expression, list):
        return list_to_pairs([quote_value(item) for item in expression])
    return expression


def evaluate_sequence(expressions: list[Any] | tuple[Any, ...], environment: Environment) -> Any:
    result = None
    for expression in expressions:
        result = evaluate(expression, environment)
    return result


def apply_procedure(procedure: Any, arguments: list[Any]) -> Any:
    if isinstance(procedure, BuiltinProcedure):
        return procedure.function(*arguments)
    if isinstance(procedure, Closure):
        local = procedure.environment.child(procedure.parameters, arguments)
        return evaluate_sequence(procedure.body, local)
    raise TypeError("attempted to call a non-procedure")


def _require_symbol(value: Any) -> Symbol:
    if not isinstance(value, Symbol):
        raise SyntaxError("expected a symbol")
    return value


def _parameters(expression: Any) -> tuple[Symbol, ...]:
    if not isinstance(expression, list):
        raise SyntaxError("parameter list must be a list")
    return tuple(_require_symbol(item) for item in expression)


def evaluate(expression: Any, environment: Environment) -> Any:
    if isinstance(expression, Symbol):
        return environment.lookup(expression)
    if not isinstance(expression, list):
        return expression
    if not expression:
        raise SyntaxError("an empty expression cannot be called")

    operator = expression[0]
    operands = expression[1:]

    if operator == Symbol("quote"):
        if len(operands) != 1:
            raise SyntaxError("quote expects one argument")
        return quote_value(operands[0])

    if operator == Symbol("if"):
        if len(operands) not in (2, 3):
            raise SyntaxError("if expects two or three arguments")
        if is_truthy(evaluate(operands[0], environment)):
            return evaluate(operands[1], environment)
        return evaluate(operands[2], environment) if len(operands) == 3 else None

    if operator == Symbol("cond"):
        for clause in operands:
            if not isinstance(clause, list) or not clause:
                raise SyntaxError("invalid cond clause")
            test_expression = clause[0]
            is_else = test_expression == Symbol("else")
            test_value = True if is_else else evaluate(test_expression, environment)
            if is_else or is_truthy(test_value):
                if len(clause) == 1:
                    return test_value
                return evaluate_sequence(clause[1:], environment)
        return None

    if operator == Symbol("and"):
        result: Any = True
        for operand in operands:
            result = evaluate(operand, environment)
            if result is False:
                return False
        return result

    if operator == Symbol("or"):
        for operand in operands:
            result = evaluate(operand, environment)
            if result is not False:
                return result
        return False

    if operator == Symbol("define"):
        if len(operands) < 2:
            raise SyntaxError("invalid define")
        target = operands[0]
        if isinstance(target, list):
            if not target:
                raise SyntaxError("missing function name")
            name = _require_symbol(target[0])
            closure = Closure(_parameters(target[1:]), tuple(operands[1:]), environment)
            environment.define(name, closure)
        else:
            if len(operands) != 2:
                raise SyntaxError("variable define expects one value")
            name = _require_symbol(target)
            environment.define(name, evaluate(operands[1], environment))
        return name

    if operator == Symbol("lambda"):
        if len(operands) < 2:
            raise SyntaxError("lambda needs parameters and a body")
        return Closure(_parameters(operands[0]), tuple(operands[1:]), environment)

    if operator == Symbol("let"):
        if len(operands) < 2 or not isinstance(operands[0], list):
            raise SyntaxError("invalid let")
        names: list[Symbol] = []
        values: list[Any] = []
        for binding in operands[0]:
            if not isinstance(binding, list) or len(binding) != 2:
                raise SyntaxError("invalid let binding")
            names.append(_require_symbol(binding[0]))
            values.append(evaluate(binding[1], environment))
        return evaluate_sequence(operands[1:], environment.child(names, values))

    if operator == Symbol("begin"):
        return evaluate_sequence(operands, environment)

    procedure = evaluate(operator, environment)
    arguments = [evaluate(operand, environment) for operand in operands]
    return apply_procedure(procedure, arguments)
