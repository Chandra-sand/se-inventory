"""
Simple inventory module with safe I/O, validation, and PEP 8 compliance.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# In-memory stock storage
stock_data: Dict[str, int] = {}


def _validate_item(item: str) -> None:
    """Validate item name is a non-empty string."""
    if not isinstance(item, str) or not item.strip():
        raise ValueError("item must be a non-empty string")


def _validate_qty_to_add(qty: int) -> None:
    """Validate quantity for add_item is a non-negative integer."""
    if not isinstance(qty, int):
        raise TypeError("qty must be an integer")
    if qty < 0:
        raise ValueError("qty must be non-negative")


def _validate_qty_to_remove(qty: int) -> None:
    """Validate quantity for remove_item is a positive integer."""
    if not isinstance(qty, int) or qty <= 0:
        raise ValueError("qty must be a positive integer")


def add_item(item: str = "default", qty: int = 0, logs: List[str] | None = None) -> None:
    """
    Add qty units of item to inventory.
    Uses a non-mutable default for logs to avoid shared state.
    """
    if logs is None:
        logs = []
    _validate_item(item)
    _validate_qty_to_add(qty)
    stock_data[item] = stock_data.get(item, 0) + qty
    logs.append(f"{datetime.now()}: Added {qty} of {item}")


def remove_item(item: str, qty: int) -> None:
    """
    Remove qty units of item.
    If resulting quantity <= 0 or item is absent, item is removed.
    """
    _validate_item(item)
    _validate_qty_to_remove(qty)
    current = stock_data.get(item)
    if current is None:
        # Nothing to remove; no exception masking
        return
    remaining = current - qty
    if remaining > 0:
        stock_data[item] = remaining
    else:
        del stock_data[item]


def get_qty(item: str) -> int:
    """
    Return quantity for item; returns 0 if item not present.
    """
    _validate_item(item)
    return stock_data.get(item, 0)


def load_data(file: str = "inventory.json") -> None:
    """
    Load inventory from JSON file with encoding and schema validation.
    """
    path = Path(file)
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not all(
        isinstance(k, str) and isinstance(v, int) for k, v in data.items()
    ):
        raise ValueError("inventory file schema invalid")
    stock_data.clear()
    stock_data.update(data)


def save_data(file: str = "inventory.json") -> None:
    """
    Save inventory to JSON file atomically with UTF-8 encoding.
    """
    path = Path(file)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(stock_data, f, ensure_ascii=False, separators=(",", ":"))
    tmp.replace(path)


def print_data() -> None:
    """Print a human-readable report of all items."""
    print("Items Report")
    for name, qty in stock_data.items():
        print(f"{name} -> {qty}")


def check_low_items(threshold: int = 5) -> List[str]:
    """
    Return list of item names whose quantities are below threshold.
    """
    if not isinstance(threshold, int) or threshold < 0:
        raise ValueError("threshold must be a non-negative integer")
    result: List[str] = []
    for name, qty in stock_data.items():
        if qty < threshold:
            result.append(name)
    return result


def demo() -> None:
    """Demonstrate inventory operations."""
    add_item("apple", 10)
    try:
        add_item("banana", 2)
    except ValueError:
        pass
    try:
        add_item(123, 10)  # type: ignore[arg-type]
    except ValueError:
        pass
    remove_item("apple", 3)
    remove_item("orange", 1)
    print("Apple stock:", get_qty("apple"))
    print("Low items:", check_low_items())
    save_data()
    load_data()
    print_data()


if __name__ == "__main__":
    demo()
