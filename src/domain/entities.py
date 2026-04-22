"""
Domain Entities — The Pure Heart of Tick Node.

This module contains the foundational data structures that power the clock:
  • Node: A single element in the circular chain.
  • CircularDoublyLinkedList: A closed, null-free ring of nodes.

Design Contracts:
  1. ZERO None references — once built, every node.prev and node.next
     point to a real Node. The ring is infinite by construction.
  2. ZERO print() calls — data extraction happens exclusively through
     to_list(), __iter__(), and __len__().
  3. Single Responsibility Principle (SRP) — these classes know nothing
     about clocks, UIs, or time zones.  They are pure data structures.
"""

from __future__ import annotations

from typing import Any, Generator, List


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------
class Node:
    """
    A single node in a circular doubly-linked list.

    Attributes:
        data:  The value stored in this node.
        prev:  Reference to the previous node in the ring.
        next:  Reference to the next node in the ring.

    Invariant (post-construction by CircularDoublyLinkedList):
        self.prev is not None  and  self.next is not None
    """

    __slots__ = ("data", "prev", "next")

    def __init__(self, data: Any) -> None:
        self.data: Any = data
        # Temporarily point to self so this node is *already* a valid
        # single-element ring.  The list builder will rewire these.
        self.prev: Node = self
        self.next: Node = self

    def __repr__(self) -> str:
        return f"Node({self.data!r})"


# ---------------------------------------------------------------------------
# CircularDoublyLinkedList
# ---------------------------------------------------------------------------
class CircularDoublyLinkedList:
    """
    A closed, doubly-linked circular list built from an iterable of values.

    The list is constructed *fully wired* at init time:
      • The last node's `next` points to the first node.
      • The first node's `prev` points to the last node.
      • No sentinel / dummy nodes exist — every node carries real data.

    A movable cursor called `current` allows O(1) traversal in both
    directions via advance_forward() and advance_backward().

    Complexity:
        Construction : O(n)
        Advance      : O(1)
        find()       : O(n)
        to_list()    : O(n)

    Raises:
        ValueError: If constructed with an empty iterable (a ring of size
                    zero is meaningless for the clock domain).
    """

    __slots__ = ("_head", "_size", "current")

    # ------------------------------------------------------------------ #
    #  Construction
    # ------------------------------------------------------------------ #
    def __init__(self, values: List[Any]) -> None:
        if not values:
            raise ValueError(
                "CircularDoublyLinkedList requires at least one value. "
                "An empty ring violates the zero-null invariant."
            )

        # Build the first node — it self-links via Node.__init__
        first = Node(values[0])
        tail = first
        self._size: int = 1

        # Chain remaining nodes
        for value in values[1:]:
            new_node = Node(value)
            new_node.prev = tail
            tail.next = new_node
            tail = new_node
            self._size += 1

        # Close the ring: last ↔ first
        tail.next = first
        first.prev = tail

        self._head: Node = first
        self.current: Node = first

    # ------------------------------------------------------------------ #
    #  Traversal — O(1)
    # ------------------------------------------------------------------ #
    def advance_forward(self) -> Node:
        """Move the cursor one step forward and return the NEW current node."""
        self.current = self.current.next
        return self.current

    def advance_backward(self) -> Node:
        """Move the cursor one step backward and return the NEW current node."""
        self.current = self.current.prev
        return self.current

    # ------------------------------------------------------------------ #
    #  Search — O(n)
    # ------------------------------------------------------------------ #
    def find(self, target: Any) -> Node:
        """
        Walk the ring starting from head until a node with
        ``node.data == target`` is found.

        Returns:
            The matching Node.

        Raises:
            KeyError: If the target is not present in the ring.
        """
        node = self._head
        for _ in range(self._size):
            if node.data == target:
                return node
            node = node.next
        raise KeyError(
            f"Value {target!r} not found in the circular list."
        )

    def set_current(self, target: Any) -> Node:
        """
        Move the cursor to the node whose data equals *target*.

        Returns:
            The node that is now current.

        Raises:
            KeyError: Propagated from find() if *target* is absent.
        """
        self.current = self.find(target)
        return self.current

    # ------------------------------------------------------------------ #
    #  Data extraction (no print!)
    # ------------------------------------------------------------------ #
    def to_list(self) -> List[Any]:
        """Return a plain Python list of all values, starting from head."""
        result: List[Any] = []
        node = self._head
        for _ in range(self._size):
            result.append(node.data)
            node = node.next
        return result

    def __iter__(self) -> Generator[Any, None, None]:
        """
        Yield every value in the ring exactly once, starting from head.

        This generator is *finite* (yields ``_size`` items) so it is
        safe for ``list()``, ``for`` loops, and comprehensions.
        """
        node = self._head
        for _ in range(self._size):
            yield node.data
            node = node.next

    # ------------------------------------------------------------------ #
    #  Introspection
    # ------------------------------------------------------------------ #
    def __len__(self) -> int:
        return self._size

    @property
    def head(self) -> Node:
        """The first node in the ring (read-only)."""
        return self._head

    def __repr__(self) -> str:
        values = self.to_list()
        # Show at most 12 values to keep the repr manageable
        if len(values) > 12:
            display = ", ".join(str(v) for v in values[:12]) + ", …"
        else:
            display = ", ".join(str(v) for v in values)
        return (
            f"CircularDoublyLinkedList([{display}], "
            f"size={self._size}, "
            f"current={self.current.data!r})"
        )
