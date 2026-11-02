"""Compile an Odoo ``pbms_domain`` into SQLAlchemy or a DCI expression.

The domain is Odoo prefix notation, for example
``['&', ('gender', '=', 'FEMALE'), ('estimated_age', '>=', 18)]``.
A list of leaves with no operator is an implicit AND.
"""

import ast
from typing import Any, Optional

from sqlalchemy import and_, not_, or_

_MONGO = {
    "=": "$eq",
    "!=": "$ne",
    ">": "$gt",
    ">=": "$gte",
    "<": "$lt",
    "<=": "$lte",
    "like": "$contains",
    "ilike": "$contains",
    "in": "$in",
    "not in": "$nin",
}


class DomainError(ValueError):
    pass


def parse_domain(domain: Optional[str]) -> list:
    if domain is None or not str(domain).strip():
        return []
    try:
        value = ast.literal_eval(domain)
    except (SyntaxError, ValueError) as exc:
        raise DomainError(f"Invalid domain: {exc}") from exc
    if not isinstance(value, list):
        raise DomainError("Domain must be a list.")
    return value


def sqlalchemy_clause(domain: Optional[str], model, allowed: Optional[set[str]] = None):
    tokens = parse_domain(domain)
    if not tokens:
        return None
    return _polish(tokens, model, allowed, sql=True)


def dci_expression(
    domain: Optional[str],
    allowed: set[str],
    match_all_field: str,
) -> dict:
    tokens = parse_domain(domain)
    if not tokens:
        return {match_all_field: {"$ne": ""}}
    return _polish(tokens, model=None, allowed=allowed, sql=False)


def _polish(tokens: list, model, allowed: Optional[set[str]], sql: bool):
    stack: list[Any] = []
    for token in reversed(tokens):
        if token in ("&", "|"):
            if len(stack) < 2:
                raise DomainError(f"Operator '{token}' is missing operands.")
            left, right = stack.pop(), stack.pop()
            stack.append(_combine(token, left, right, sql))
        elif token == "!":
            if not stack:
                raise DomainError("Operator '!' is missing an operand.")
            child = stack.pop()
            stack.append(not_(child) if sql else _negate(child))
        elif isinstance(token, (list, tuple)) and len(token) == 3:
            stack.append(_leaf(token, model, allowed, sql))
        else:
            raise DomainError(f"Unsupported domain token: {token!r}")
    if not stack:
        return None
    if len(stack) == 1:
        return stack[0]
    combined = stack.pop()
    while stack:
        combined = _combine("&", combined, stack.pop(), sql)
    return combined


def _combine(operator: str, left, right, sql: bool):
    if sql:
        return and_(left, right) if operator == "&" else or_(left, right)
    key = "$and" if operator == "&" else "$or"
    return {key: [_as_expr(left), _as_expr(right)]}


_INVERSE = {
    "$eq": "$ne",
    "$ne": "$eq",
    "$gt": "$lte",
    "$gte": "$lt",
    "$lt": "$gte",
    "$lte": "$gt",
    "$in": "$nin",
    "$nin": "$in",
    "$contains": "$contains",
}


def _negate(node):
    if isinstance(node, dict) and "$and" in node:
        return {"$or": [_negate(item) for item in node["$and"]]}
    if isinstance(node, dict) and "$or" in node:
        return {"$and": [_negate(item) for item in node["$or"]]}
    if isinstance(node, dict) and len(node) == 1:
        field_name, operators = next(iter(node.items()))
        if isinstance(operators, dict) and len(operators) == 1:
            operator, value = next(iter(operators.items()))
            inverse = _INVERSE.get(operator)
            if inverse and inverse != operator:
                return {field_name: {inverse: value}}
    raise DomainError("This NOT domain cannot be expressed as a DCI query.")


def _as_expr(node):
    if isinstance(node, dict) and ("$and" in node or "$or" in node or "$not" in node):
        return node
    return node


def _leaf(token, model, allowed: Optional[set[str]], sql: bool):
    field_name, operator, value = token
    field_name = str(field_name)
    operator = str(operator).lower()
    if allowed is not None and field_name not in allowed:
        raise DomainError(
            f"Field '{field_name}' is not part of the DCI spec and cannot be used "
            "with the DCI connector."
        )
    if operator not in _MONGO:
        raise DomainError(f"Unsupported domain operator '{operator}'.")
    if sql:
        column = getattr(model, field_name, None)
        if column is None:
            raise DomainError(f"Unknown registry field '{field_name}'.")
        return _sql_op(column, operator, value)
    return {field_name: {_MONGO[operator]: value}}


def _sql_op(column, operator: str, value):
    if operator == "=":
        return column == value
    if operator == "!=":
        return column != value
    if operator == ">":
        return column > value
    if operator == ">=":
        return column >= value
    if operator == "<":
        return column < value
    if operator == "<=":
        return column <= value
    if operator == "like":
        return column.like(value)
    if operator == "ilike":
        return column.ilike(value)
    if operator == "in":
        return column.in_(value)
    if operator == "not in":
        return ~column.in_(value)
    raise DomainError(f"Unsupported domain operator '{operator}'.")
