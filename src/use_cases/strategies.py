"""
Time Flow Strategies — Strategy Pattern (GoF) for Tick Node.

Defines the abstraction and concrete strategies that control the
direction of time traversal across the circular doubly-linked lists.

    • ForwardStrategy  → advances nodes via .advance_forward()   (normal clock)
    • BackwardStrategy → advances nodes via .advance_backward()  (time machine)

The ClockManager holds a reference to the active strategy and delegates
every tick() call through it, making the direction swappable at runtime
without touching the clock logic.

Design Contracts:
    • Strategies are stateless — they receive a list and act on it.
    • ZERO print() calls.
    • ZERO Streamlit / UI dependencies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.entities import CircularDoublyLinkedList, Node


class TimeFlowStrategy(ABC):
    """
    Abstract base for time-direction strategies.

    Every concrete strategy must implement ``step()``, which moves
    the cursor of a CircularDoublyLinkedList exactly one position
    in the strategy's direction and returns the new current node.
    """

    @abstractmethod
    def step(self, ring: CircularDoublyLinkedList) -> Node:
        """Advance the ring's cursor one position and return the new node."""
        ...

    @abstractmethod
    def direction_name(self) -> str:
        """Human-readable label for the UI (e.g. 'Forward', 'Backward')."""
        ...


class ForwardStrategy(TimeFlowStrategy):
    """Normal clock flow — time moves forward (.next)."""

    def step(self, ring: CircularDoublyLinkedList) -> Node:
        return ring.advance_forward()

    def direction_name(self) -> str:
        return "Forward"


class BackwardStrategy(TimeFlowStrategy):
    """Time-machine mode — time moves backward (.prev)."""

    def step(self, ring: CircularDoublyLinkedList) -> Node:
        return ring.advance_backward()

    def direction_name(self) -> str:
        return "Backward"
