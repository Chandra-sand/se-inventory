from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Iterable

# Configure logging once, in module scope or under if __name__ == "__main__"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

# Use lower_snake_case names
stock_data: Dict[str, int] = {}


def _validate_item_qty(item: str, qty: int) -> None:
    if not isinstance(item, str) or not item.strip():
        raise ValueError("item must be a non-empty string")
    if not isinstance(qty, int):
        raise TypeError("qty must be an integer")
    # disallow negative adds; allow zero
    if qty < 0:
        raise ValueError("qty must be non-negative")


def add_item(item: str = "default", qty: int = 0, logs: List[str] | None = None) -> None:
    # Avoid mutable default for logs
    if logs is None:
        logs = []
    _validate_item_qty(item, qty)
    stock_data[item] = stock_data.get(item, 0) + qty
    logs.append(f"{datetime.now()}: Added {qty} of {item}")


def remove_item(item: str, qty: int) -> None:
    if not isinstance(item, str) or not item.strip():
        raise ValueError("item must be a non-empty string")
    if not isinstance(qty, int) or qty <= 0:
        raise ValueError("qty must be a positive integer")
    # Handle missing keys explicitly; no bare except
    if item not in stock_data:
        logging.warning("Attempted to remove from missing item: %s", item)
        return
    new_qty = stock_data[item] - qty
    if new_qty > 0:
        stock_data[item] = new_qty
    else:
        # If removal zeroes or goes below zero, delete
        del stock_data[item]


def get_qty(item: str) -> int:
    if not isinstance(item, str) or not item.strip():
        raise ValueError("item must be a non-empty string")
    # Return 0 for missing items rather than KeyError for robustness
    return stock_data.get(item, 0)


def load_data(file: str = "inventory.json") -> None:
    # Use context manager; validate JSON; handle specific exceptions
    path = Path(file)
    if not path.exists():
        logging.info("Inventory file not found: %s (starting empty)", file)
        return
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or not all(
            isinstance(k, str) and isinstance(v, int) for k, v in data.items()
        ):
            raise ValueError("inventory file schema invalid")
        # Update in place; avoid rebinding global unless necessary
        stock_data.clear()
        stock_data.update(data)
    except (json.JSONDecodeError, ValueError) as err:
        logging.error("Failed to load inventory: %s", err)
        # start with empty data on failure
        stock_data.clear()


def save_data(file: str = "inventory.json") -> None:
    path = Path(file)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(stock_data, f, ensure_ascii=False, separators=(",", ":"))
        tmp.replace(path)
    except OSError as err:
        logging.error("Failed to save inventory: %s", err)


def print_data() -> None:
    print("Items Report")
    for name, qty in stock_data.items():
        print(f"{name} -> {qty}")


def check_low_items(threshold: int = 5) -> List[str]:
    if not isinstance(threshold, int) or threshold < 0:
        raise ValueError("threshold must be a non-negative integer")
    result: List[str] = []
    for name, qty in stock_data.items():
        if qty < threshold:
            result.append(name)
    return result


def demo() -> None:
    # Safe demo sequence showing validations
    add_item("apple", 10)
    # Negative add is rejected by validation
    try:
        add_item("banana", -2)
    except ValueError:
        logging.info("Rejected negative quantity for banana")

    # Bad types rejected
    for bad in [(123, "ten"), ("orange", "1")]:
        try:
            add_item(bad[0], bad[1])  # type: ignore[arg-type]
        except (TypeError, ValueError):
            logging.info("Rejected invalid add: %r", bad)

    remove_item("apple", 3)
    remove_item("orange", 1)  # warns, not fatal

    print("Apple stock:", get_qty("apple"))
    print("Low items:", check_low_items())

    save_data()
    load_data()
    print_data()


if __name__ == "__main__":
    demo()
