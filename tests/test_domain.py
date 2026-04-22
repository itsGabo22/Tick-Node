"""
Silent Domain Tests — Tick Node Phase 1 Validation.

Every test uses assert exclusively; zero print() calls.
These tests mathematically prove that the circular doubly-linked lists
behave as infinite, null-free rings suitable for clock mechanics.

Run with:
    python -m pytest tests/test_domain.py -v
    — or —
    python tests/test_domain.py          (standalone, uses assert)
"""

import sys
import os

# ---------------------------------------------------------------------------
# Path setup so the test can find `src.domain` regardless of cwd
# ---------------------------------------------------------------------------
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from src.domain.entities import Node, CircularDoublyLinkedList


# ═══════════════════════════════════════════════════════════════════════════
# 1. NODE BASICS
# ═══════════════════════════════════════════════════════════════════════════

def test_node_creation():
    """A lone Node self-links and stores its data correctly."""
    n = Node(42)
    assert n.data == 42
    assert n.prev is n, "A lone node must point prev to itself"
    assert n.next is n, "A lone node must point next to itself"


def test_node_repr():
    """Node.__repr__ returns a readable string."""
    n = Node("hello")
    assert "hello" in repr(n)


# ═══════════════════════════════════════════════════════════════════════════
# 2. CONSTRUCTION INVARIANTS
# ═══════════════════════════════════════════════════════════════════════════

def test_empty_list_raises():
    """An empty iterable must raise ValueError — zero-size rings are forbidden."""
    try:
        CircularDoublyLinkedList([])
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_single_element_ring():
    """A single-element ring loops to itself in both directions."""
    ring = CircularDoublyLinkedList([7])
    assert len(ring) == 1
    assert ring.head.data == 7
    assert ring.head.next is ring.head
    assert ring.head.prev is ring.head
    assert ring.current is ring.head


def test_two_element_ring():
    """Two nodes form a bidirectional loop: A ↔ B ↔ A."""
    ring = CircularDoublyLinkedList([10, 20])
    a, b = ring.head, ring.head.next
    assert a.data == 10
    assert b.data == 20
    # Forward links
    assert a.next is b
    assert b.next is a
    # Backward links
    assert a.prev is b
    assert b.prev is a


def test_ring_closure_seconds():
    """Seconds ring (0-59): last node's next is the first, first's prev is last."""
    seconds = CircularDoublyLinkedList(list(range(0, 60)))
    assert len(seconds) == 60

    # Walk to the last node
    node = seconds.head
    for _ in range(59):
        node = node.next
    last = node

    assert last.data == 59
    assert last.next is seconds.head, "Last node must link back to head"
    assert seconds.head.prev is last, "Head's prev must be the last node"


def test_ring_closure_minutes():
    """Minutes ring (0-59): same closure guarantee as seconds."""
    minutes = CircularDoublyLinkedList(list(range(0, 60)))
    assert len(minutes) == 60
    assert minutes.head.data == 0

    node = minutes.head
    for _ in range(59):
        node = node.next
    assert node.data == 59
    assert node.next is minutes.head


def test_ring_closure_hours():
    """Hours ring (1-12): last node (12) links back to first node (1)."""
    hours = CircularDoublyLinkedList(list(range(1, 13)))
    assert len(hours) == 12
    assert hours.head.data == 1

    node = hours.head
    for _ in range(11):
        node = node.next
    assert node.data == 12
    assert node.next is hours.head
    assert hours.head.prev is node


# ═══════════════════════════════════════════════════════════════════════════
# 3. ZERO-NULL INVARIANT  (The Unbreakable Rule)
# ═══════════════════════════════════════════════════════════════════════════

def test_no_none_references_in_seconds():
    """Walk the entire seconds ring: EVERY node's prev and next must be a Node."""
    ring = CircularDoublyLinkedList(list(range(0, 60)))
    node = ring.head
    for _ in range(60):
        assert node is not None, "Node itself must not be None"
        assert isinstance(node.next, Node), f"next of {node.data} is None!"
        assert isinstance(node.prev, Node), f"prev of {node.data} is None!"
        node = node.next


def test_no_none_references_in_hours():
    """Walk the entire hours ring: EVERY node's prev and next must be a Node."""
    ring = CircularDoublyLinkedList(list(range(1, 13)))
    node = ring.head
    for _ in range(12):
        assert node is not None
        assert isinstance(node.next, Node)
        assert isinstance(node.prev, Node)
        node = node.next


# ═══════════════════════════════════════════════════════════════════════════
# 4. TRAVERSAL — FORWARD (infinite loop proof)
# ═══════════════════════════════════════════════════════════════════════════

def test_advance_forward_100_times_seconds():
    """
    Starting at 0, advancing 100 times on a 60-element ring must land
    on 100 % 60 = 40.  This proves the ring loops correctly.
    """
    ring = CircularDoublyLinkedList(list(range(0, 60)))
    for _ in range(100):
        ring.advance_forward()
    assert ring.current.data == 100 % 60  # 40


def test_advance_forward_100_times_hours():
    """
    Hours ring [1..12].  Starting at 1, advance 100 times.
    Expected: (0 + 100) % 12 = 4 → value at index 4 is 5.
    """
    ring = CircularDoublyLinkedList(list(range(1, 13)))
    for _ in range(100):
        ring.advance_forward()
    expected_index = 100 % 12  # 4
    assert ring.current.data == expected_index + 1  # 5


def test_advance_forward_exact_cycle():
    """Advancing exactly `size` times returns to the start."""
    ring = CircularDoublyLinkedList(list(range(0, 60)))
    start = ring.current.data
    for _ in range(60):
        ring.advance_forward()
    assert ring.current.data == start


def test_advance_forward_multiple_cycles():
    """Advancing 5 full cycles (300 steps) returns to the start."""
    ring = CircularDoublyLinkedList(list(range(0, 60)))
    start = ring.current.data
    for _ in range(300):
        ring.advance_forward()
    assert ring.current.data == start


# ═══════════════════════════════════════════════════════════════════════════
# 5. TRAVERSAL — BACKWARD (bidirectional proof)
# ═══════════════════════════════════════════════════════════════════════════

def test_advance_backward_100_times_seconds():
    """
    Starting at 0, going backward 100 steps on a 60-ring:
    (0 − 100) mod 60 = (−100) mod 60 = 20.
    """
    ring = CircularDoublyLinkedList(list(range(0, 60)))
    for _ in range(100):
        ring.advance_backward()
    assert ring.current.data == (-100) % 60  # 20


def test_advance_backward_100_times_hours():
    """
    Hours [1..12].  Start at 1 (index 0), go back 100 steps.
    index = (0 − 100) mod 12 = 8 → value = 9.
    """
    ring = CircularDoublyLinkedList(list(range(1, 13)))
    for _ in range(100):
        ring.advance_backward()
    expected_index = (-100) % 12  # 8
    assert ring.current.data == expected_index + 1  # 9


def test_advance_backward_exact_cycle():
    """Going backward exactly `size` steps returns to start."""
    ring = CircularDoublyLinkedList(list(range(0, 60)))
    start = ring.current.data
    for _ in range(60):
        ring.advance_backward()
    assert ring.current.data == start


def test_forward_then_backward_cancel():
    """N steps forward + N steps backward = original position."""
    ring = CircularDoublyLinkedList(list(range(0, 60)))
    start = ring.current.data
    for _ in range(37):
        ring.advance_forward()
    for _ in range(37):
        ring.advance_backward()
    assert ring.current.data == start


# ═══════════════════════════════════════════════════════════════════════════
# 6. SEARCH & CURSOR
# ═══════════════════════════════════════════════════════════════════════════

def test_find_existing_value():
    """find() locates a value that exists in the ring."""
    ring = CircularDoublyLinkedList(list(range(1, 13)))
    node = ring.find(7)
    assert node.data == 7


def test_find_missing_value_raises():
    """find() raises KeyError for a value not in the ring."""
    ring = CircularDoublyLinkedList(list(range(1, 13)))
    try:
        ring.find(99)
        assert False, "Should have raised KeyError"
    except KeyError:
        pass


def test_set_current():
    """set_current() moves the cursor to the specified value."""
    ring = CircularDoublyLinkedList(list(range(0, 60)))
    ring.set_current(45)
    assert ring.current.data == 45
    # Advancing forward from 45 should land on 46
    ring.advance_forward()
    assert ring.current.data == 46


def test_set_current_then_traverse():
    """After set_current(30), advance 35 steps → land on (30+35)%60 = 5."""
    ring = CircularDoublyLinkedList(list(range(0, 60)))
    ring.set_current(30)
    for _ in range(35):
        ring.advance_forward()
    assert ring.current.data == (30 + 35) % 60  # 5


# ═══════════════════════════════════════════════════════════════════════════
# 7. DATA EXTRACTION (to_list, __iter__, __len__)
# ═══════════════════════════════════════════════════════════════════════════

def test_to_list_seconds():
    """to_list() returns all 60 values in order."""
    expected = list(range(0, 60))
    ring = CircularDoublyLinkedList(expected)
    assert ring.to_list() == expected


def test_to_list_hours():
    """to_list() returns 1..12 in order."""
    expected = list(range(1, 13))
    ring = CircularDoublyLinkedList(expected)
    assert ring.to_list() == expected


def test_iter_protocol():
    """The ring supports for-in iteration and list() conversion."""
    expected = list(range(0, 60))
    ring = CircularDoublyLinkedList(expected)
    assert list(ring) == expected


def test_len():
    """__len__ returns the correct size."""
    assert len(CircularDoublyLinkedList(list(range(0, 60)))) == 60
    assert len(CircularDoublyLinkedList(list(range(1, 13)))) == 12
    assert len(CircularDoublyLinkedList([1])) == 1


def test_repr_contains_key_info():
    """__repr__ includes at least the current value and size."""
    ring = CircularDoublyLinkedList(list(range(1, 13)))
    r = repr(ring)
    assert "size=12" in r
    assert "current=1" in r


# ═══════════════════════════════════════════════════════════════════════════
# 8. STRESS TEST — BIDIRECTIONAL 10_000 STEPS
# ═══════════════════════════════════════════════════════════════════════════

def test_stress_forward_10000():
    """10,000 forward steps: always lands on the mathematically correct node."""
    ring = CircularDoublyLinkedList(list(range(0, 60)))
    steps = 10_000
    for _ in range(steps):
        ring.advance_forward()
    assert ring.current.data == steps % 60  # 10000 % 60 = 40


def test_stress_backward_10000():
    """10,000 backward steps: mathematically correct."""
    ring = CircularDoublyLinkedList(list(range(0, 60)))
    steps = 10_000
    for _ in range(steps):
        ring.advance_backward()
    assert ring.current.data == (-steps) % 60  # (-10000) % 60 = 20


def test_stress_mixed_directions():
    """7,777 forward then 3,333 backward on hours ring."""
    ring = CircularDoublyLinkedList(list(range(1, 13)))
    for _ in range(7_777):
        ring.advance_forward()
    for _ in range(3_333):
        ring.advance_backward()
    net = 7_777 - 3_333  # 4444
    expected_index = net % 12  # 4444 % 12 = 4
    assert ring.current.data == expected_index + 1  # 5


# ═══════════════════════════════════════════════════════════════════════════
# RUNNER — allows `python tests/test_domain.py`
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import inspect

    current_module = sys.modules[__name__]
    test_functions = [
        obj
        for name, obj in inspect.getmembers(current_module, inspect.isfunction)
        if name.startswith("test_")
    ]

    passed = 0
    failed = 0

    for fn in test_functions:
        try:
            fn()
            passed += 1
        except AssertionError as e:
            failed += 1
            # Minimal output: only report failures
            sys.stderr.write(f"FAIL  {fn.__name__}: {e}\n")
        except Exception as e:
            failed += 1
            sys.stderr.write(f"ERROR {fn.__name__}: {e}\n")

    # Final summary — single line, not scattered prints
    sys.stderr.write(
        f"\n{'='*50}\n"
        f"Results: {passed} passed, {failed} failed, "
        f"{passed + failed} total\n"
        f"{'='*50}\n"
    )

    sys.exit(1 if failed else 0)
