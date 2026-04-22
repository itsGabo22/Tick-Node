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
        "dial_bg": "#181818",
        "dial_border": "#000000",
        "strap_type": "metal",
        "strap_color": "#C0C0C0",
        "face_strategy": "SubmarinerFace",
    },

    "patek_philippe": {
        "display_name": "Patek Philippe Calatrava",
        "dial_bg": "#E9C2A6", # Salmon dial
        "dial_border": "#E0E0E0",
        "strap_type": "leather",
        "strap_color": "#4A3018", # Dark brown leather
        "face_strategy": "CalatravaFace",
    },

    "audemars_piguet": {
        "display_name": "Audemars Piguet Royal Oak",
        "dial_bg": "#E8E9EB", # White/Silver Tapisserie
        "dial_border": "#B0B0B0",
        "strap_type": "metal",
        "strap_color": "#B0B0B0",
        "face_strategy": "RoyalOakFace",
    },

    "omega": {
        "display_name": "Omega Speedmaster",
        "dial_bg": "#151515", # Matte Black
        "dial_border": "#000000", # Black tachymeter insert
        "strap_type": "metal",
        "strap_color": "#B8B8B8",
        "face_strategy": "SpeedmasterFace",
    },

    "cartier": {
        "display_name": "Cartier Tank",
        "dial_bg": "#F9F9F4", # Silver opaline
        "dial_border": "#D8D8D8", # Steel/White Gold
        "strap_type": "leather",
        "strap_color": "#151515", # Black leather
        "face_strategy": "TankFace",
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
