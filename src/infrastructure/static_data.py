"""
Static Data — In-Memory Datastore for Tick Node.

Pure Python configuration dictionaries. No Streamlit, no external APIs.
This module acts as the "read-only database" of the infrastructure layer.

Contents:
    • WATCH_BRANDS : Visual configuration for luxury watch faces.
    • TIME_ZONES   : Curated list of representative world time zones.
"""

from typing import Any, Dict, List


# ═══════════════════════════════════════════════════════════════════════════
# WATCH BRANDS — Visual configuration for the analog clock renderer
# ═══════════════════════════════════════════════════════════════════════════
#
# Each brand entry contains every parameter needed by the future
# WatchFaceFactory (Phase 4) to render a Plotly analog clock face.
#
# Keys:
#   display_name  : Human-readable brand name (shown in UI).
#   dial_bg       : Background color of the clock dial.
#   dial_border   : Outer ring / bezel color.
#   marker_color  : Color of the hour markers on the dial.
#   marker_style  : "roman" | "baton" | "arabic" — type of hour markers.
#   hand_hours    : dict with color + width for the hour hand.
#   hand_minutes  : dict with color + width for the minute hand.
#   hand_seconds  : dict with color + width for the second hand.
#   center_dot    : Color of the center pivot point.
#   font_family   : Typography hint for text elements.
#   accent        : Brand signature accent color (logo, sub-dials, etc.).
# ═══════════════════════════════════════════════════════════════════════════

WATCH_BRANDS: Dict[str, Dict[str, Any]] = {

    "rolex": {
        "display_name": "Rolex Submariner",
        "dial_bg": "#0B1A2E",
        "dial_border": "#C4A34D",
        "marker_color": "#C4A34D",
        "marker_style": "baton",
        "strap_type": "metal",
        "strap_color": "#B0C4DE",
        "hand_hours": {"color": "#C4A34D", "width": 6},
        "hand_minutes": {"color": "#C4A34D", "width": 4},
        "hand_seconds": {"color": "#E8372A", "width": 1.5},
        "center_dot": "#C4A34D",
        "font_family": "Georgia, serif",
        "accent": "#006039",
    },

    "patek_philippe": {
        "display_name": "Patek Philippe Calatrava",
        "dial_bg": "#FAF6F0",
        "dial_border": "#8B7355",
        "marker_color": "#2C2C2C",
        "marker_style": "roman",
        "strap_type": "leather",
        "strap_color": "#3E2723",
        "hand_hours": {"color": "#1A1A2E", "width": 5},
        "hand_minutes": {"color": "#1A1A2E", "width": 3},
        "hand_seconds": {"color": "#6B4C30", "width": 1},
        "center_dot": "#1A1A2E",
        "font_family": "'Playfair Display', serif",
        "accent": "#8B7355",
    },

    "audemars_piguet": {
        "display_name": "Audemars Piguet Royal Oak",
        "dial_bg": "#1B2838",
        "dial_border": "#A0A0A0",
        "marker_color": "#FFFFFF",
        "marker_style": "baton",
        "strap_type": "metal",
        "strap_color": "#A9A9A9",
        "hand_hours": {"color": "#FFFFFF", "width": 6},
        "hand_minutes": {"color": "#FFFFFF", "width": 4},
        "hand_seconds": {"color": "#E8372A", "width": 1.5},
        "center_dot": "#FFFFFF",
        "font_family": "'Helvetica Neue', sans-serif",
        "accent": "#4A90D9",
    },

    "omega": {
        "display_name": "Omega Speedmaster",
        "dial_bg": "#1C1C1C",
        "dial_border": "#D4D4D4",
        "marker_color": "#F5F5DC",
        "marker_style": "arabic",
        "strap_type": "metal",
        "strap_color": "#C0C0C0",
        "hand_hours": {"color": "#F5F5DC", "width": 5},
        "hand_minutes": {"color": "#F5F5DC", "width": 3},
        "hand_seconds": {"color": "#FF6B35", "width": 1.5},
        "center_dot": "#D4D4D4",
        "font_family": "'Roboto', sans-serif",
        "accent": "#FF6B35",
    },

    "cartier": {
        "display_name": "Cartier Tank",
        "dial_bg": "#FFFFF0",
        "dial_border": "#B8860B",
        "marker_color": "#1A1A2E",
        "marker_style": "roman",
        "strap_type": "leather",
        "strap_color": "#1A1A1A",
        "hand_hours": {"color": "#00008B", "width": 4},
        "hand_minutes": {"color": "#00008B", "width": 2.5},
        "hand_seconds": {"color": "#B8860B", "width": 1},
        "center_dot": "#00008B",
        "font_family": "'Garamond', serif",
        "accent": "#B8860B",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# TIME ZONES — Curated list of representative world zones
# ═══════════════════════════════════════════════════════════════════════════
#
# Format: zoneinfo-compatible IANA identifiers.
# Grouped by continent for readability; the UI can display them
# however it prefers (dropdown, grouped selectbox, etc.).
# ═══════════════════════════════════════════════════════════════════════════

TIME_ZONES: Dict[str, List[str]] = {
    "América": [
        "America/New_York",
        "America/Chicago",
        "America/Denver",
        "America/Los_Angeles",
        "America/Bogota",
        "America/Mexico_City",
        "America/Sao_Paulo",
        "America/Argentina/Buenos_Aires",
        "America/Toronto",
    ],
    "Europa": [
        "Europe/London",
        "Europe/Paris",
        "Europe/Berlin",
        "Europe/Madrid",
        "Europe/Rome",
        "Europe/Moscow",
    ],
    "Asia": [
        "Asia/Tokyo",
        "Asia/Shanghai",
        "Asia/Dubai",
        "Asia/Kolkata",
        "Asia/Seoul",
        "Asia/Singapore",
    ],
    "Oceanía": [
        "Australia/Sydney",
        "Pacific/Auckland",
    ],
    "África": [
        "Africa/Cairo",
        "Africa/Lagos",
        "Africa/Johannesburg",
    ],
}

# Flat list for quick iteration / validation
ALL_TIME_ZONES: List[str] = [
    tz for zones in TIME_ZONES.values() for tz in zones
]
