"""Uniform printing of backend API result dicts."""
from typing import Any


def print_result(result: dict[str, Any]) -> int:
    """Print messages from a backend api dict and return shell exit code."""
    for msg in result.get("messages", []) or []:
        print(msg)
    return 0 if result.get("success", False) else 1
