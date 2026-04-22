"""
Watch Face Factory — Factory Pattern (GoF) for Tick Node.

Builds a fully styled Plotly go.Figure representing an analog clock.
The factory receives the current clock state and a brand configuration
dict (from static_data.py) and returns a ready-to-render figure.

Design Contracts:
    • ZERO Streamlit imports — this is a pure Plotly builder.
    • ZERO print() calls.
    • Returns a go.Figure; the UI layer decides how to display it.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

import plotly.graph_objects as go


# ═══════════════════════════════════════════════════════════════════════════
# Angle helpers (clock convention: 12 o'clock = 0°, clockwise positive)
# ═══════════════════════════════════════════════════════════════════════════

def _clock_angle_to_xy(
    degrees: float, length: float, cx: float = 0, cy: float = 0
) -> Tuple[float, float]:
    """
    Convert a clock-convention angle (0° at 12, CW) to (x, y).

    Math convention: 0° at 3 o'clock, CCW.
    Conversion: math_angle = 90° − clock_angle.
    """
    rad = math.radians(90 - degrees)
    return cx + length * math.cos(rad), cy + length * math.sin(rad)


# ═══════════════════════════════════════════════════════════════════════════
# Roman numeral map (for marker_style == "roman")
# ═══════════════════════════════════════════════════════════════════════════

_ROMAN = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
    7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII",
}


# ═══════════════════════════════════════════════════════════════════════════
# WatchFaceFactory
# ═══════════════════════════════════════════════════════════════════════════

class WatchFaceFactory:
    """
    Factory that produces Plotly figures of analog clock faces.

    Usage:
        fig = WatchFaceFactory.create_watch_face(
            state={"hours": 10, "minutes": 10, "seconds": 30, "direction": "Forward"},
            brand_config=WATCH_BRANDS["rolex"],
        )
    """

    # Layout constants
    _DIAL_RADIUS = 1.0
    _MARKER_RADIUS = 0.85
    _TEXT_RADIUS = 0.72
    _HAND_HOUR_LEN = 0.50
    _HAND_MIN_LEN = 0.70
    _HAND_SEC_LEN = 0.80
    _TICK_INNER = 0.88
    _TICK_OUTER = 0.95
    _MINOR_INNER = 0.91
    _MINOR_OUTER = 0.95

    @classmethod
    def create_watch_face(
        cls,
        state: Dict[str, Any],
        brand_config: Dict[str, Any],
    ) -> go.Figure:
        """
        Build and return a complete analog clock figure.

        Args:
            state:        Dict with keys hours, minutes, seconds, direction.
            brand_config: Dict from WATCH_BRANDS (colors, widths, style…).

        Returns:
            A plotly.graph_objects.Figure ready for st.plotly_chart().
        """
        h = state["hours"]
        m = state["minutes"]
        s = state["seconds"]

        fig = go.Figure()

        # 1. Draw the dial background
        cls._draw_dial(fig, brand_config)

        # 2. Draw hour markers / numerals
        cls._draw_markers(fig, brand_config)

        # 3. Draw minute tick marks
        cls._draw_minute_ticks(fig, brand_config)

        # 4. Draw the three hands
        cls._draw_hands(fig, h, m, s, brand_config)

        # 5. Draw the center dot
        cls._draw_center(fig, brand_config)

        # 6. Layout — clean, no axes, no grid
        cls._apply_layout(fig, brand_config, state)

        return fig

    # ------------------------------------------------------------------ #
    #  Dial
    # ------------------------------------------------------------------ #

    @classmethod
    def _draw_dial(cls, fig: go.Figure, cfg: Dict) -> None:
        """Draw the outer circle and filled background."""
        # Outer bezel ring
        theta = [i for i in range(361)]
        x_ring = [cls._DIAL_RADIUS * math.cos(math.radians(t)) for t in theta]
        y_ring = [cls._DIAL_RADIUS * math.sin(math.radians(t)) for t in theta]

        # Filled background
        fig.add_trace(go.Scatter(
            x=x_ring, y=y_ring,
            fill="toself",
            fillcolor=cfg["dial_bg"],
            line=dict(color=cfg["dial_border"], width=4),
            hoverinfo="skip",
            showlegend=False,
        ))

    # ------------------------------------------------------------------ #
    #  Hour markers
    # ------------------------------------------------------------------ #

    @classmethod
    def _draw_markers(cls, fig: go.Figure, cfg: Dict) -> None:
        """Draw 12 hour indicators (batons, roman numerals, or arabic)."""
        style = cfg.get("marker_style", "baton")

        for hour in range(1, 13):
            angle_deg = hour * 30  # 360° / 12

            if style == "roman":
                tx, ty = _clock_angle_to_xy(angle_deg, cls._TEXT_RADIUS)
                fig.add_annotation(
                    x=tx, y=ty,
                    text=f"<b>{_ROMAN[hour]}</b>",
                    showarrow=False,
                    font=dict(
                        size=13,
                        color=cfg["marker_color"],
                        family=cfg.get("font_family", "serif"),
                    ),
                    xanchor="center", yanchor="middle",
                )
            elif style == "arabic":
                tx, ty = _clock_angle_to_xy(angle_deg, cls._TEXT_RADIUS)
                fig.add_annotation(
                    x=tx, y=ty,
                    text=f"<b>{hour}</b>",
                    showarrow=False,
                    font=dict(
                        size=14,
                        color=cfg["marker_color"],
                        family=cfg.get("font_family", "sans-serif"),
                    ),
                    xanchor="center", yanchor="middle",
                )
            else:  # baton (default)
                ix, iy = _clock_angle_to_xy(angle_deg, cls._TICK_INNER - 0.03)
                ox, oy = _clock_angle_to_xy(angle_deg, cls._TICK_OUTER)
                fig.add_shape(
                    type="line",
                    x0=ix, y0=iy, x1=ox, y1=oy,
                    line=dict(color=cfg["marker_color"], width=3),
                )

    # ------------------------------------------------------------------ #
    #  Minute tick marks
    # ------------------------------------------------------------------ #

    @classmethod
    def _draw_minute_ticks(cls, fig: go.Figure, cfg: Dict) -> None:
        """Draw 60 small tick marks around the dial."""
        for minute in range(60):
            if minute % 5 == 0:
                continue  # Skip positions covered by hour markers
            angle_deg = minute * 6
            ix, iy = _clock_angle_to_xy(angle_deg, cls._MINOR_INNER)
            ox, oy = _clock_angle_to_xy(angle_deg, cls._MINOR_OUTER)
            fig.add_shape(
                type="line",
                x0=ix, y0=iy, x1=ox, y1=oy,
                line=dict(color=cfg["marker_color"], width=1),
            )

    # ------------------------------------------------------------------ #
    #  Hands
    # ------------------------------------------------------------------ #

    @classmethod
    def _draw_hands(
        cls,
        fig: go.Figure,
        h: int, m: int, s: int,
        cfg: Dict,
    ) -> None:
        """Draw the hour, minute, and second hands."""
        # Angles (clock convention)
        sec_angle = s * 6                          # 360 / 60
        min_angle = m * 6 + s * 0.1                # smooth sweep
        hour_angle = (h % 12) * 30 + m * 0.5      # smooth sweep

        # Hour hand
        hx, hy = _clock_angle_to_xy(hour_angle, cls._HAND_HOUR_LEN)
        h_tail_x, h_tail_y = _clock_angle_to_xy(hour_angle + 180, 0.06)
        fig.add_shape(
            type="line",
            x0=h_tail_x, y0=h_tail_y, x1=hx, y1=hy,
            line=dict(
                color=cfg["hand_hours"]["color"],
                width=cfg["hand_hours"]["width"],
            ),
        )

        # Minute hand
        mx, my = _clock_angle_to_xy(min_angle, cls._HAND_MIN_LEN)
        m_tail_x, m_tail_y = _clock_angle_to_xy(min_angle + 180, 0.08)
        fig.add_shape(
            type="line",
            x0=m_tail_x, y0=m_tail_y, x1=mx, y1=my,
            line=dict(
                color=cfg["hand_minutes"]["color"],
                width=cfg["hand_minutes"]["width"],
            ),
        )

        # Second hand
        sx, sy = _clock_angle_to_xy(sec_angle, cls._HAND_SEC_LEN)
        s_tail_x, s_tail_y = _clock_angle_to_xy(sec_angle + 180, 0.15)
        fig.add_shape(
            type="line",
            x0=s_tail_x, y0=s_tail_y, x1=sx, y1=sy,
            line=dict(
                color=cfg["hand_seconds"]["color"],
                width=cfg["hand_seconds"]["width"],
            ),
        )

    # ------------------------------------------------------------------ #
    #  Center pivot dot
    # ------------------------------------------------------------------ #

    @classmethod
    def _draw_center(cls, fig: go.Figure, cfg: Dict) -> None:
        """Draw a small filled circle at the center pivot."""
        fig.add_trace(go.Scatter(
            x=[0], y=[0],
            mode="markers",
            marker=dict(
                size=10,
                color=cfg["center_dot"],
                line=dict(width=1, color=cfg["dial_border"]),
            ),
            hoverinfo="skip",
            showlegend=False,
        ))

    # ------------------------------------------------------------------ #
    #  Layout
    # ------------------------------------------------------------------ #

    @classmethod
    def _apply_layout(
        cls,
        fig: go.Figure,
        cfg: Dict,
        state: Dict[str, Any],
    ) -> None:
        """Configure axes, background, and title."""
        direction_icon = "⏩" if state.get("direction") == "Forward" else "⏪"
        time_str = (
            f"{state['hours']:02d}:{state['minutes']:02d}"
            f":{state['seconds']:02d}"
        )

        fig.update_layout(
            title=dict(
                text=(
                    f"<b>{cfg['display_name']}</b><br>"
                    f"<span style='font-size:14px;color:{cfg['accent']}'>"
                    f"{time_str}  {direction_icon}</span>"
                ),
                x=0.5,
                xanchor="center",
                font=dict(
                    size=18,
                    color=cfg["marker_color"],
                    family=cfg.get("font_family", "sans-serif"),
                ),
            ),
            xaxis=dict(
                visible=False,
                range=[-1.3, 1.3],
                scaleanchor="y",
                scaleratio=1,
            ),
            yaxis=dict(
                visible=False,
                range=[-1.3, 1.3],
            ),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            width=500,
            height=540,
            margin=dict(l=20, r=20, t=80, b=20),
            showlegend=False,
        )
