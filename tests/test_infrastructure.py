"""
Infrastructure Tests — Tick Node Phase 2 Validation.

Validates:
    • TimeCalculator returns an int for any valid zone pair.
    • Known zone differences are mathematically correct.
    • WATCH_BRANDS dictionary is well-formed.
    • TIME_ZONES / ALL_TIME_ZONES are consistent.

Run with:
    python -m pytest tests/test_infrastructure.py -v
    — or —
    python tests/test_infrastructure.py
"""

import sys
import os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from src.infrastructure.time_service import TimeCalculator
from src.infrastructure.static_data import (
    WATCH_BRANDS,
    TIME_ZONES,
    ALL_TIME_ZONES,
)


# ═══════════════════════════════════════════════════════════════════════════
# 1. TimeCalculator — return type
# ═══════════════════════════════════════════════════════════════════════════

def test_hour_difference_returns_int():
    """hour_difference() must always return a plain int."""
    calc = TimeCalculator()
    result = calc.hour_difference("Asia/Tokyo", origin="America/Bogota")
    assert isinstance(result, int), f"Expected int, got {type(result)}"


def test_hour_difference_same_zone_is_zero():
    """The difference between a zone and itself must be 0."""
    calc = TimeCalculator()
    assert calc.hour_difference("Europe/London", origin="Europe/London") == 0


# ═══════════════════════════════════════════════════════════════════════════
# 2. TimeCalculator — known pairs
# ═══════════════════════════════════════════════════════════════════════════

def test_bogota_to_tokyo():
    """
    Bogota is UTC-5, Tokyo is UTC+9.
    Difference = +9 − (−5) = +14 (always, neither observes DST).
    """
    calc = TimeCalculator()
    diff = calc.hour_difference("Asia/Tokyo", origin="America/Bogota")
    assert diff == 14, f"Expected +14, got {diff}"


def test_bogota_to_bogota():
    """Same city → 0."""
    calc = TimeCalculator()
    diff = calc.hour_difference("America/Bogota", origin="America/Bogota")
    assert diff == 0


def test_symmetry():
    """
    If A→B = +N, then B→A must be −N.
    Using fixed-offset zones (no DST) for determinism.
    """
    calc = TimeCalculator()
    forward = calc.hour_difference("Asia/Tokyo", origin="America/Bogota")
    backward = calc.hour_difference("America/Bogota", origin="Asia/Tokyo")
    assert forward == -backward, (
        f"Symmetry violated: forward={forward}, backward={backward}"
    )


def test_new_york_to_london_range():
    """
    NY (UTC-5 / UTC-4 DST) vs London (UTC+0 / UTC+1 BST).
    Difference is either +5 or +4 or +6 depending on DST overlap.
    We just verify it's in the plausible range.
    """
    calc = TimeCalculator()
    diff = calc.hour_difference("Europe/London", origin="America/New_York")
    assert 4 <= diff <= 6, f"NY→London difference {diff} out of plausible range"


# ═══════════════════════════════════════════════════════════════════════════
# 3. TimeCalculator — get_current_time
# ═══════════════════════════════════════════════════════════════════════════

def test_get_current_time_has_tzinfo():
    """Returned datetime must be timezone-aware."""
    calc = TimeCalculator()
    dt = calc.get_current_time("America/Bogota")
    assert dt.tzinfo is not None, "Datetime must be timezone-aware"


def test_get_current_time_default():
    """Calling without args should not raise."""
    calc = TimeCalculator()
    dt = calc.get_current_time()
    assert dt.tzinfo is not None


# ═══════════════════════════════════════════════════════════════════════════
# 4. Static Data — WATCH_BRANDS
# ═══════════════════════════════════════════════════════════════════════════

def test_watch_brands_has_minimum_entries():
    """At least 3 brands must be configured."""
    assert len(WATCH_BRANDS) >= 3, (
        f"Expected ≥3 brands, got {len(WATCH_BRANDS)}"
    )


def test_watch_brands_required_keys():
    """Every brand must have the full set of visual parameters."""
    required = {
        "display_name", "dial_bg", "dial_border",
        "marker_color", "marker_style",
        "hand_hours", "hand_minutes", "hand_seconds",
        "center_dot", "font_family", "accent",
    }
    for key, brand in WATCH_BRANDS.items():
        missing = required - set(brand.keys())
        assert not missing, (
            f"Brand '{key}' is missing keys: {missing}"
        )


def test_watch_brands_hand_structure():
    """Each hand config must have 'color' and 'width'."""
    for key, brand in WATCH_BRANDS.items():
        for hand in ("hand_hours", "hand_minutes", "hand_seconds"):
            h = brand[hand]
            assert "color" in h, f"{key}.{hand} missing 'color'"
            assert "width" in h, f"{key}.{hand} missing 'width'"


# ═══════════════════════════════════════════════════════════════════════════
# 5. Static Data — TIME_ZONES
# ═══════════════════════════════════════════════════════════════════════════

def test_time_zones_not_empty():
    """The grouped dictionary must have entries."""
    assert len(TIME_ZONES) > 0
    assert len(ALL_TIME_ZONES) > 0


def test_all_time_zones_matches_grouped():
    """ALL_TIME_ZONES must be the flat union of TIME_ZONES values."""
    flat = [tz for zones in TIME_ZONES.values() for tz in zones]
    assert ALL_TIME_ZONES == flat


def test_time_zones_are_valid_iana():
    """Every zone string must be loadable by zoneinfo."""
    from zoneinfo import ZoneInfo
    for tz_name in ALL_TIME_ZONES:
        try:
            ZoneInfo(tz_name)
        except Exception as e:
            assert False, f"Invalid zone '{tz_name}': {e}"


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
