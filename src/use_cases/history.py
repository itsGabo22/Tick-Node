"""
History Stack — Classic LIFO Data Structure for Tick Node.

Stores timezone jump records so the user can "Undo" travel.
Each entry is a dict with the zone name and the hour difference
that was applied, enabling exact reversal.

Design Contracts:
    • Pure Python — no external dependencies.
    • ZERO print() calls.
"""

from __future__ import annotations

from typing import Any, List


class HistoryStack:
    """
    A classic Stack (LIFO — Last In, First Out) backed by a Python list.

    Used by the UI to record every timezone shift so it can be undone
    in reverse order via the "Deshacer Viaje" button.

    Each pushed item is expected to be a dict like:
        {"zone": "Asia/Tokyo", "diff": 14}
    but the stack itself is type-agnostic.
    """

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: List[Any] = []

    # ------------------------------------------------------------------ #
    #  Core Operations
    # ------------------------------------------------------------------ #

    def push(self, item: Any) -> None:
        """Push an item onto the top of the stack. O(1) amortized."""
        self._items.append(item)

    def pop(self) -> Any:
        """
        Remove and return the top item. O(1).

        Raises:
            IndexError: If the stack is empty.
        """
        if self.is_empty():
            raise IndexError("Cannot pop from an empty HistoryStack.")
        return self._items.pop()

    def peek(self) -> Any:
        """
        Return the top item WITHOUT removing it.

        Raises:
            IndexError: If the stack is empty.
        """
        if self.is_empty():
            raise IndexError("Cannot peek at an empty HistoryStack.")
        return self._items[-1]

    # ------------------------------------------------------------------ #
    #  Introspection
    # ------------------------------------------------------------------ #

    def is_empty(self) -> bool:
        """True if the stack has no items."""
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)

    def to_list(self) -> List[Any]:
        """Return a shallow copy of the internal list (bottom → top)."""
        return list(self._items)

    def __repr__(self) -> str:
        return f"HistoryStack({self._items!r})"
