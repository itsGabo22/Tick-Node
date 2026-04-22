"""
Use-Cases Tests — Tick Node Phase 3 Validation.

Validates the ClockManager's tick cascade, timezone shifting,
and backward time-machine logic.  All silent — assert only.

Run with:
    python -m pytest tests/test_use_cases.py -v
    — or —
    python tests/test_use_cases.py
"""

import sys
import os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from src.domain.entities import CircularDoublyLinkedList
from src.use_cases.strategies import (
    ForwardStrategy,
    BackwardStrategy,
    TimeFlowStrategy,
)
from src.use_cases.clock_manager import ClockManager


# ═══════════════════════════════════════════════════════════════════════════
# Helpers — Build a ClockManager at a KNOWN time (no real-clock dependency)
# ═══════════════════════════════════════════════════════════════════════════

def _make_clock(h: int, m: int, s: int, strategy=None) -> ClockManager:
    """
    Create a ClockManager and forcibly set it to h:m:s.

    This bypasses _sync_to_system_time so tests are deterministic.
    """
    clock = ClockManager.__new__(ClockManager)
    clock.hours = CircularDoublyLinkedList(list(range(1, 13)))
    clock.minutes = CircularDoublyLinkedList(list(range(0, 60)))
    clock.seconds = CircularDoublyLinkedList(list(range(0, 60)))
    clock.strategy = strategy or ForwardStrategy()
    clock.hours.set_current(h)
    clock.minutes.set_current(m)
    clock.seconds.set_current(s)
    return clock


# ═══════════════════════════════════════════════════════════════════════════
# 1. STRATEGY PATTERN
# ═══════════════════════════════════════════════════════════════════════════

def test_forward_strategy_steps_forward():
    """ForwardStrategy moves the cursor to .next."""
    ring = CircularDoublyLinkedList(list(range(0, 60)))
    ring.set_current(10)
    fs = ForwardStrategy()
    fs.step(ring)
    assert ring.current.data == 11


def test_backward_strategy_steps_backward():
    """BackwardStrategy moves the cursor to .prev."""
    ring = CircularDoublyLinkedList(list(range(0, 60)))
    ring.set_current(10)
    bs = BackwardStrategy()
    bs.step(ring)
    assert ring.current.data == 9


def test_strategies_are_abstract():
    """TimeFlowStrategy cannot be instantiated directly."""
    try:
        TimeFlowStrategy()
        assert False, "Should have raised TypeError"
    except TypeError:
        pass


def test_direction_names():
    """Each strategy reports its human-readable direction."""
    assert ForwardStrategy().direction_name() == "Forward"
    assert BackwardStrategy().direction_name() == "Backward"


# ═══════════════════════════════════════════════════════════════════════════
# 2. CLOCK MANAGER — INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

def test_clock_initialises_with_real_time():
    """
    ClockManager() should not raise and should produce a valid state
    with hours in [1..12], minutes in [0..59], seconds in [0..59].
    """
    clock = ClockManager()
    state = clock.get_state()
    assert 1 <= state["hours"] <= 12
    assert 0 <= state["minutes"] <= 59
    assert 0 <= state["seconds"] <= 59
    assert state["direction"] == "Forward"


def test_clock_state_returns_dict():
    """get_state() returns a dict with the expected keys."""
    clock = _make_clock(3, 15, 45)
    state = clock.get_state()
    assert state == {
        "hours": 3,
        "minutes": 15,
        "seconds": 45,
        "direction": "Forward",
    }


# ═══════════════════════════════════════════════════════════════════════════
# 3. TICK — FORWARD CASCADE
# ═══════════════════════════════════════════════════════════════════════════

def test_single_tick_increments_second():
    """One tick moves seconds from 0 to 1."""
    clock = _make_clock(12, 0, 0)
    clock.tick()
    assert clock.seconds.current.data == 1
    assert clock.minutes.current.data == 0
    assert clock.hours.current.data == 12


def test_60_ticks_increment_minute():
    """60 ticks = 1 full second cycle → minutes go from 0 to 1."""
    clock = _make_clock(12, 0, 0)
    for _ in range(60):
        clock.tick()
    state = clock.get_state()
    assert state["seconds"] == 0, "Seconds should wrap back to 0"
    assert state["minutes"] == 1, "Minutes should have advanced to 1"
    assert state["hours"] == 12, "Hours should not change"


def test_3600_ticks_increment_hour():
    """3600 ticks = 60 minutes → hours go from 12 to 1."""
    clock = _make_clock(12, 0, 0)
    for _ in range(3600):
        clock.tick()
    state = clock.get_state()
    assert state["seconds"] == 0
    assert state["minutes"] == 0
    assert state["hours"] == 1, "12 + 1 hour on a 12-ring = 1"


def test_multiple_minute_cascade():
    """120 ticks = 2 minutes."""
    clock = _make_clock(6, 30, 0)
    for _ in range(120):
        clock.tick()
    state = clock.get_state()
    assert state["seconds"] == 0
    assert state["minutes"] == 32
    assert state["hours"] == 6


def test_tick_at_boundary_11_59_59():
    """From 11:59:59 forward → 12:00:00."""
    clock = _make_clock(11, 59, 59)
    clock.tick()
    state = clock.get_state()
    assert state == {
        "hours": 12,
        "minutes": 0,
        "seconds": 0,
        "direction": "Forward",
    }


def test_tick_at_boundary_12_59_59():
    """From 12:59:59 forward → 1:00:00 (full cycle)."""
    clock = _make_clock(12, 59, 59)
    clock.tick()
    state = clock.get_state()
    assert state == {
        "hours": 1,
        "minutes": 0,
        "seconds": 0,
        "direction": "Forward",
    }


# ═══════════════════════════════════════════════════════════════════════════
# 4. TICK — BACKWARD CASCADE (Time Machine)
# ═══════════════════════════════════════════════════════════════════════════

def test_backward_single_tick():
    """Backward tick from :01 → :00."""
    clock = _make_clock(6, 30, 1, strategy=BackwardStrategy())
    clock.tick()
    assert clock.seconds.current.data == 0
    assert clock.minutes.current.data == 30


def test_backward_cascade_1_00_00():
    """
    From 1:00:00 backward → 12:59:59.
    The full reverse cascade must fire.
    """
    clock = _make_clock(1, 0, 0, strategy=BackwardStrategy())
    clock.tick()
    state = clock.get_state()
    assert state["seconds"] == 59
    assert state["minutes"] == 59
    assert state["hours"] == 12


def test_backward_60_ticks_decrement_minute():
    """60 backward ticks from :30:00 → :29:00."""
    clock = _make_clock(6, 30, 0, strategy=BackwardStrategy())
    for _ in range(60):
        clock.tick()
    state = clock.get_state()
    assert state["seconds"] == 0
    assert state["minutes"] == 29
    assert state["hours"] == 6


def test_backward_3600_ticks_decrement_hour():
    """3600 backward ticks from 6:00:00 → 5:00:00."""
    clock = _make_clock(6, 0, 0, strategy=BackwardStrategy())
    for _ in range(3600):
        clock.tick()
    state = clock.get_state()
    assert state["seconds"] == 0
    assert state["minutes"] == 0
    assert state["hours"] == 5


# ═══════════════════════════════════════════════════════════════════════════
# 5. TIMEZONE SHIFTING
# ═══════════════════════════════════════════════════════════════════════════

def test_shift_positive_14():
    """Bogotá → Tokyo (+14h). Only hours change."""
    clock = _make_clock(3, 15, 45)
    clock.shift_time_zone(14)
    state = clock.get_state()
    # 3 + 14 = 17 → 17 on a 12-ring = 5  (3→4→...→12→1→2→3→4→5)
    assert state["hours"] == 5
    assert state["minutes"] == 15, "Minutes must not change"
    assert state["seconds"] == 45, "Seconds must not change"


def test_shift_negative_2():
    """Shift -2 hours."""
    clock = _make_clock(3, 15, 45)
    clock.shift_time_zone(-2)
    state = clock.get_state()
    assert state["hours"] == 1  # 3 - 2 = 1
    assert state["minutes"] == 15
    assert state["seconds"] == 45


def test_shift_zero():
    """Shift 0 → nothing changes."""
    clock = _make_clock(7, 30, 20)
    clock.shift_time_zone(0)
    state = clock.get_state()
    assert state["hours"] == 7
    assert state["minutes"] == 30
    assert state["seconds"] == 20


def test_shift_wraps_around():
    """Shift that crosses 12→1 boundary."""
    clock = _make_clock(11, 0, 0)
    clock.shift_time_zone(3)
    assert clock.hours.current.data == 2  # 11 + 3 = 14 → wraps to 2


def test_shift_negative_wraps_around():
    """Shift that crosses 1→12 boundary backward."""
    clock = _make_clock(2, 0, 0)
    clock.shift_time_zone(-5)
    assert clock.hours.current.data == 9  # 2 - 5 = -3 → wraps to 9


# ═══════════════════════════════════════════════════════════════════════════
# 6. TOGGLE TIME MACHINE
# ═══════════════════════════════════════════════════════════════════════════

def test_toggle_switches_to_backward():
    """Default is Forward → toggle → Backward."""
    clock = _make_clock(6, 0, 0)
    result = clock.toggle_time_machine()
    assert result == "Backward"
    assert isinstance(clock.strategy, BackwardStrategy)


def test_toggle_switches_back_to_forward():
    """Backward → toggle → Forward."""
    clock = _make_clock(6, 0, 0, strategy=BackwardStrategy())
    result = clock.toggle_time_machine()
    assert result == "Forward"
    assert isinstance(clock.strategy, ForwardStrategy)


def test_double_toggle_returns_to_original():
    """Toggle twice returns to the original strategy."""
    clock = _make_clock(6, 0, 0)
    clock.toggle_time_machine()
    clock.toggle_time_machine()
    assert isinstance(clock.strategy, ForwardStrategy)


def test_toggle_affects_tick_direction():
    """After toggling, tick should go backward."""
    clock = _make_clock(6, 30, 10)
    clock.toggle_time_machine()
    clock.tick()
    assert clock.seconds.current.data == 9  # 10 - 1 = 9


# ═══════════════════════════════════════════════════════════════════════════
# 7. STRESS — FULL DAY CYCLE
# ═══════════════════════════════════════════════════════════════════════════

def test_full_12_hour_cycle_returns_to_start():
    """43200 ticks (12 hours) forward = back to the same time."""
    clock = _make_clock(3, 15, 45)
    for _ in range(43200):
        clock.tick()
    state = clock.get_state()
    assert state["hours"] == 3
    assert state["minutes"] == 15
    assert state["seconds"] == 45


# ═══════════════════════════════════════════════════════════════════════════
# RUNNER
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
            sys.stderr.write(f"FAIL  {fn.__name__}: {e}\n")
        except Exception as e:
            failed += 1
            sys.stderr.write(f"ERROR {fn.__name__}: {e}\n")

    sys.stderr.write(
        f"\n{'='*50}\n"
        f"Results: {passed} passed, {failed} failed, "
        f"{passed + failed} total\n"
        f"{'='*50}\n"
    )

    sys.exit(1 if failed else 0)
