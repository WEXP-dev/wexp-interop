"""Exact JSON-number parsing and deterministic UTF-8 serialization."""

from __future__ import annotations

import json
import math
from decimal import Decimal, DecimalException
from typing import Any


def parse_decimal(value: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except DecimalException as exc:
        raise ValueError(f"unsupported JSON number: {value}") from exc
    if not parsed.is_finite():
        raise ValueError(f"non-finite JSON number: {value}")
    return parsed


def validate_json_limits(
    value: Any,
    *,
    max_depth: int = 128,
    max_nodes: int = 100_000,
) -> None:
    """Reject JSON values that would make recursive comparison/encoding unsafe."""
    stack: list[tuple[Any, int]] = [(value, 0)]
    nodes = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > max_nodes:
            raise ValueError(f"JSON value exceeds {max_nodes} nodes")
        if depth > max_depth:
            raise ValueError(f"JSON value exceeds depth {max_depth}")
        if isinstance(current, dict):
            stack.extend((member, depth + 1) for member in current.values())
        elif isinstance(current, list):
            stack.extend((member, depth + 1) for member in current)


def _encode(value: Any, level: int, sort_keys: bool) -> str:
    indentation = "  "
    prefix = indentation * level
    child_prefix = indentation * (level + 1)
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("non-finite Decimal is not JSON")
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float is not JSON")
        return json.dumps(value, allow_nan=False)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=True)
    if isinstance(value, list):
        if not value:
            return "[]"
        members = [child_prefix + _encode(member, level + 1, sort_keys) for member in value]
        return "[\n" + ",\n".join(members) + "\n" + prefix + "]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        if any(not isinstance(key, str) for key in value):
            raise TypeError("JSON object keys must be strings")
        keys = sorted(value) if sort_keys else value.keys()
        members = [
            child_prefix
            + json.dumps(key, ensure_ascii=True)
            + ": "
            + _encode(value[key], level + 1, sort_keys)
            for key in keys
        ]
        return "{\n" + ",\n".join(members) + "\n" + prefix + "}"
    raise TypeError(f"unsupported JSON value: {type(value).__name__}")


def canonical_json_bytes(value: Any, *, sort_keys: bool = True) -> bytes:
    return (_encode(value, 0, sort_keys) + "\n").encode("utf-8")
