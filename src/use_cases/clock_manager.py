"""
Clock Manager — The Orchestrator (Use-Case Layer) for Tick Node.

This class wires together three CircularDoublyLinkedLists (hours,
minutes, seconds) and drives them with a pluggable TimeFlowStrategy.

Responsibilities:
    1. Initialize the three rings and sync them to the real system clock.
    2. Execute tick() — advance seconds and cascade into minutes/hours
       using an implicit Observer pattern.
    3. Shift the hour pointer for world-clock jumps (shift_time_zone).
    4. Swap the time-flow direction at runtime (toggle_time_machine).
    5. Expose a clean get_state() dict for the future UI layer.

Design Contracts:
    • ZERO print() calls.
    • ZERO Streamlit / UI dependencies.
    • Returns data; never renders it.
"""

from __future__ import annotations

from typing import Any, Dict

from src.domain.entities import CircularDoublyLinkedList
from src.use_cases.strategies import (
    BackwardStrategy,
    ForwardStrategy,
    TimeFlowStrategy,
)
from src.infrastructure.time_service import TimeCalculator


class ClockManager:
    """
    Orchestrates the three circular lists that represent a 12-hour clock.

    Attributes:
        hours   : CircularDoublyLinkedList[1..12]
        minutes : CircularDoublyLinkedList[0..59]
        seconds : CircularDoublyLinkedList[0..59]
        strategy: The active TimeFlowStrategy (Forward by default).
    """

    # ------------------------------------------------------------------ #
    #  Construction & Synchronisation
    # ------------------------------------------------------------------ #

    def __init__(
        self,
        zone_name: str | None = None,
        strategy: TimeFlowStrategy | None = None,
    ) -> None:
        """
        Build the three rings and point them to the current time.

        Args:
            zone_name: IANA zone for initial sync (None = local).
            strategy:  Initial time-flow direction (default Forward).
        """
        # Build the rings
        self.hours = CircularDoublyLinkedList(list(range(1, 13)))
        self.minutes = CircularDoublyLinkedList(list(range(0, 60)))
        self.seconds = CircularDoublyLinkedList(list(range(0, 60)))

        # Strategy (default: forward / normal clock)
        self.strategy: TimeFlowStrategy = strategy or ForwardStrategy()

        # Sync to real time
        self._sync_to_system_time(zone_name)

    def _sync_to_system_time(self, zone_name: str | None = None) -> None:
        """
        Read the system clock and move the cursors to match.

        Uses TimeCalculator from the infrastructure layer to obtain
        a timezone-aware datetime, then extracts h/m/s components.
        """
        calc = TimeCalculator()
        now = calc.get_current_time(zone_name)

        # Convert 24h → 12h format (0/12 → 12, 13→1, etc.)
        hour_12 = now.hour % 12
        if hour_12 == 0:
            hour_12 = 12

        self.hours.set_current(hour_12)
        self.minutes.set_current(now.minute)
        self.seconds.set_current(now.second)

    # ------------------------------------------------------------------ #
    #  The Tick — Heart beat of the clock
    # ------------------------------------------------------------------ #

    def tick(self) -> Dict[str, int]:
        """
        Advance the clock by one second in the active direction.

        Cascade logic (implicit Observer pattern):
            • Seconds overflow (59→0 forward, 0→59 backward)
              triggers a minute step.
            • Minutes overflow triggers an hour step.

        Returns:
            The new state dict {hours, minutes, seconds}.
        """
        old_second = self.seconds.current.data
        self.strategy.step(self.seconds)
        new_second = self.seconds.current.data

        # Detect second overflow → cascade to minutes
        second_overflowed = self._detect_overflow(
            old_second, new_second, cycle_size=60
        )

        if second_overflowed:
            old_minute = self.minutes.current.data
            self.strategy.step(self.minutes)
            new_minute = self.minutes.current.data

            # Detect minute overflow → cascade to hours
            minute_overflowed = self._detect_overflow(
                old_minute, new_minute, cycle_size=60
            )

            if minute_overflowed:
                self.strategy.step(self.hours)

        return self.get_state()

    @staticmethod
    def _detect_overflow(old: int, new: int, cycle_size: int) -> bool:
        """
        Determine if a step caused a wrap-around in a ring.

        Forward overflow:  old == cycle_size - 1  and  new == 0
            (e.g. 59 → 0 for seconds/minutes)
        Backward overflow: old == 0  and  new == cycle_size - 1
            (e.g. 0 → 59 for seconds/minutes)

        For the hours ring (size 12), the values are 1-12, so the
        caller should never hit this path directly — hours cascade
        is driven by minute overflow.
        """
        forward_wrap = (old == cycle_size - 1) and (new == 0)
        backward_wrap = (old == 0) and (new == cycle_size - 1)
        return forward_wrap or backward_wrap

    # ------------------------------------------------------------------ #
    #  World Clock — Timezone shifting
    # ------------------------------------------------------------------ #

    def shift_time_zone(self, hours_diff: int) -> Dict[str, int]:
        """
        Shift ONLY the hour hand by *hours_diff* positions.

        Positive → advance_forward (destination is ahead).
        Negative → advance_backward (destination is behind).
        Minutes and seconds remain untouched.

        This leverages the bidirectional nature of the circular list
        to its fullest: a simple for-loop of .next or .prev calls.

        Args:
            hours_diff: Integer offset from TimeCalculator.hour_difference().

        Returns:
            The new state dict.
        """
        if hours_diff > 0:
            for _ in range(hours_diff):
                self.hours.advance_forward()
        elif hours_diff < 0:
            for _ in range(abs(hours_diff)):
                self.hours.advance_backward()
        # hours_diff == 0 → no movement needed

        return self.get_state()

    # ------------------------------------------------------------------ #
    #  State Export (for the UI layer)
    # ------------------------------------------------------------------ #

    def get_state(self) -> Dict[str, Any]:
        """
        Return a clean snapshot of the clock's current position.

        The UI layer reads this dict to calculate hand angles.
        """
        return {
            "hours": self.hours.current.data,
            "minutes": self.minutes.current.data,
            "seconds": self.seconds.current.data,
            "direction": self.strategy.direction_name(),
        }

    # ------------------------------------------------------------------ #
    #  Time Machine — Strategy swap
    # ------------------------------------------------------------------ #

    def toggle_time_machine(self) -> str:
        """
        Swap between ForwardStrategy and BackwardStrategy.

        Returns:
            The name of the NEW active strategy.
        """
        if isinstance(self.strategy, ForwardStrategy):
            self.strategy = BackwardStrategy()
        else:
            self.strategy = ForwardStrategy()
        return self.strategy.direction_name()

    def set_strategy(self, strategy: TimeFlowStrategy) -> None:
        """Explicitly inject a strategy (useful for testing)."""
        self.strategy = strategy
