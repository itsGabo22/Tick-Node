"""
Time Service — Local Timezone Calculator for Tick Node.

Computes the integer hour-difference between two IANA time zones
using only the Python standard library (datetime + zoneinfo).

Design Contracts:
    • ZERO external API calls — everything is calculated locally.
    • Returns a plain int (positive = destination is ahead,
      negative = destination is behind).
    • The clock domain will use this int to call .next (positive)
      or .prev (negative) on the hours circular list.
"""

from datetime import datetime
from zoneinfo import ZoneInfo


class TimeCalculator:
    """
    Stateless service that calculates hour offsets between time zones.

    The comparison always uses the *current* UTC offsets, which means
    it implicitly accounts for DST (daylight saving time) on both sides.

    Usage:
        calc = TimeCalculator()
        diff = calc.hour_difference("Asia/Tokyo")        # e.g. +14
        diff = calc.hour_difference("America/Los_Angeles") # e.g. -2

        # Or with an explicit origin:
        diff = calc.hour_difference("Europe/London",
                                    origin="America/Bogota")
    """

    @staticmethod
    def _current_utc_offset_hours(zone_name: str) -> float:
        """
        Return the *current* UTC offset for a zone as fractional hours.

        Example:
            "Asia/Kolkata" → 5.5
            "America/Bogota" → -5.0
        """
        tz = ZoneInfo(zone_name)
        now = datetime.now(tz)
        offset = now.utcoffset()
        # offset is a timedelta — convert to hours
        return offset.total_seconds() / 3600

    @staticmethod
    def get_local_zone_name() -> str:
        """
        Best-effort detection of the system's local IANA zone name.

        Falls back to 'America/Bogota' if detection fails.
        """
        try:
            # Python 3.12+ exposes this directly:
            # from zoneinfo import ZoneInfo
            # But we can infer from the system clock:
            import time

            local_name = time.tzname[0]
            # On Windows, tzname gives abbreviations like 'COT'.
            # We cannot reliably map abbreviations → IANA, so we
            # use a pragmatic approach: try the system timezone first.
            try:
                from datetime import timezone

                local_tz = datetime.now().astimezone().tzinfo
                # Some Python builds give us the key directly
                if hasattr(local_tz, "key"):
                    return local_tz.key
            except Exception:
                pass

            return "America/Bogota"  # Safe default for this project
        except Exception:
            return "America/Bogota"

    def hour_difference(
        self,
        destination: str,
        origin: str | None = None,
    ) -> int:
        """
        Calculate the integer hour difference: destination − origin.

        Args:
            destination: IANA zone name (e.g. "Asia/Tokyo").
            origin:      IANA zone name for the reference point.
                         If None, uses the system's local zone.

        Returns:
            Positive int if destination is *ahead* of origin,
            negative int if destination is *behind*.

        The result is rounded to the nearest integer to keep
        the clock domain (which operates in whole hours) simple.

        Examples (origin = "America/Bogota", UTC-5):
            destination = "Asia/Tokyo"        →  +14
            destination = "Europe/London"      →  +5  (or +6 during BST)
            destination = "America/Los_Angeles" →  -2  (or -3 outside PDT)
        """
        if origin is None:
            origin = self.get_local_zone_name()

        origin_offset = self._current_utc_offset_hours(origin)
        dest_offset = self._current_utc_offset_hours(destination)

        return round(dest_offset - origin_offset)

    def get_current_time(self, zone_name: str | None = None) -> datetime:
        """
        Return the current datetime in the given zone.

        If zone_name is None, returns local time.
        Useful for initializing the clock hands to the correct position.
        """
        if zone_name is None:
            zone_name = self.get_local_zone_name()
        return datetime.now(ZoneInfo(zone_name))
