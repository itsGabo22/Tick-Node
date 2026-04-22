"""
High-Fidelity Render Engine — Clock Canvas for Tick Node.

Builds a real-time Tkinter Canvas analog clock face.
Uses trigonometry to compute fractional angles for a hyper-realistic
'Smooth Sweep' animation. Hands are drawn with detailed polygons
matching luxury styles (Mercedes, Sword, Baton).

Design Contracts:
    • Pure Python standard library (tkinter, math).
    • Reads state and brand_config but modifies neither.
"""

import math
import tkinter as tk
from typing import Any, Dict


class HighResClockCanvas(tk.Canvas):
    """
    Advanced Canvas renderer for the analog clock.
    """

    def __init__(self, master: Any, width: int = 500, height: int = 500, **kwargs: Any) -> None:
        super().__init__(
            master, 
            width=width, 
            height=height, 
            highlightthickness=0, 
            **kwargs
        )
        self.width = width
        self.height = height
        self.cx = width / 2
        self.cy = height / 2
        self.r = min(width, height) / 2 * 0.9

    def render_clock(
        self, 
        state: Dict[str, Any], 
        brand_config: Dict[str, Any],
        fractional_second: float = 0.0
    ) -> None:
        """
        Main drawing routine for the clock frame.
        fractional_second allows for 60fps smooth sweeping between discrete seconds.
        """
        self.delete("all")
        
        # 1. Dial Background and Bezel
        self.create_oval(
            self.cx - self.r, self.cy - self.r,
            self.cx + self.r, self.cy + self.r,
            fill=brand_config["dial_bg"],
            outline=brand_config["dial_border"],
            width=8
        )

        # 2. Ticks & Markers
        self._draw_markers(brand_config)

        # 3. Hands (with Smooth Sweep)
        self._draw_hands(state, brand_config, fractional_second)

        # 4. Center Pinion
        self._draw_center_pinion(brand_config)

    def _angle_to_xy(self, angle_deg: float, radius: float) -> tuple[float, float]:
        """Convert clock angle (0=12) to canvas coordinates."""
        # -90 to shift 0 to the top.
        rad = math.radians(angle_deg - 90)
        return self.cx + radius * math.cos(rad), self.cy + radius * math.sin(rad)

    def _draw_markers(self, cfg: Dict[str, Any]) -> None:
        """Draw hour numerals and minute ticks."""
        style = cfg.get("marker_style", "baton")
        color = cfg["marker_color"]

        roman_map = {
            1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
            7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"
        }

        # Minute ticks
        for minute in range(60):
            if minute % 5 == 0:
                continue
            angle = minute * 6
            x1, y1 = self._angle_to_xy(angle, self.r * 0.90)
            x2, y2 = self._angle_to_xy(angle, self.r * 0.95)
            self.create_line(x1, y1, x2, y2, fill=color, width=1)

        # Hour markers
        font_family = "Helvetica" if "sans-serif" in cfg.get("font_family", "") else "Times"
        
        for hour in range(1, 13):
            angle = hour * 30
            
            if style == "roman":
                x, y = self._angle_to_xy(angle, self.r * 0.75)
                self.create_text(
                    x, y, text=roman_map[hour], 
                    fill=color, font=(font_family, 18, "bold")
                )
            elif style == "arabic":
                x, y = self._angle_to_xy(angle, self.r * 0.75)
                self.create_text(
                    x, y, text=str(hour), 
                    fill=color, font=(font_family, 20, "bold")
                )
            else: # baton
                x1, y1 = self._angle_to_xy(angle, self.r * 0.85)
                x2, y2 = self._angle_to_xy(angle, self.r * 0.95)
                self.create_line(x1, y1, x2, y2, fill=color, width=4)

    def _draw_hands(self, state: Dict[str, Any], cfg: Dict[str, Any], frac_sec: float) -> None:
        """Draw hands with trigonometry and luxury shapes."""
        h = state["hours"]
        m = state["minutes"]
        s = state["seconds"]

        # Smooth Sweep Angles
        # If running backward, we might reverse the sweep visually, but the math 
        # is just adding fractional progress.
        if state["direction"] == "Backward":
            total_s = s - frac_sec
        else:
            total_s = s + frac_sec

        sec_angle = total_s * 6
        min_angle = m * 6 + (total_s / 60) * 6
        hour_angle = (h % 12) * 30 + (m / 60) * 30 + (total_s / 3600) * 30

        # Hour Hand
        self._draw_polygon_hand(
            angle=hour_angle, 
            length=self.r * 0.55, 
            width=cfg["hand_hours"]["width"] * 2, 
            color=cfg["hand_hours"]["color"],
            style=cfg.get("display_name", "")
        )

        # Minute Hand
        self._draw_polygon_hand(
            angle=min_angle, 
            length=self.r * 0.75, 
            width=cfg["hand_minutes"]["width"] * 2, 
            color=cfg["hand_minutes"]["color"],
            style="Sword" if "Patek" in cfg.get("display_name", "") else "Baton"
        )

        # Second Hand
        sx, sy = self._angle_to_xy(sec_angle, self.r * 0.85)
        stx, sty = self._angle_to_xy(sec_angle + 180, self.r * 0.2)
        self.create_line(
            stx, sty, sx, sy, 
            fill=cfg["hand_seconds"]["color"], 
            width=cfg["hand_seconds"]["width"] + 1,
            capstyle=tk.ROUND
        )
        
        # Second hand counter-weight
        cwx, cwy = self._angle_to_xy(sec_angle + 180, self.r * 0.15)
        self.create_oval(
            cwx - 4, cwy - 4, cwx + 4, cwy + 4,
            fill=cfg["hand_seconds"]["color"], outline=""
        )

    def _draw_polygon_hand(self, angle: float, length: float, width: float, color: str, style: str) -> None:
        """Draw a complex hand shape (Mercedes, Sword, Baton)."""
        rad = math.radians(angle - 90)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # Base vector
        dx = length * cos_a
        dy = length * sin_a
        
        # Perpendicular vector for width
        px = -sin_a * width / 2
        py = cos_a * width / 2
        
        if "Rolex" in style:
            # Mercedes Style (Circle near the tip)
            base_len = length * 0.65
            bx = self.cx + base_len * cos_a
            by = self.cy + base_len * sin_a
            
            # Stem
            self.create_polygon(
                self.cx + px, self.cy + py,
                bx + px, by + py,
                bx - px, by - py,
                self.cx - px, self.cy - py,
                fill=color, outline=""
            )
            
            # Mercedes Circle
            circle_r = width * 1.5
            self.create_oval(
                bx + dx*0.1 - circle_r, by + dy*0.1 - circle_r,
                bx + dx*0.1 + circle_r, by + dy*0.1 + circle_r,
                outline=color, width=2, fill=self.cget("bg")
            )
            
            # Tip
            tx = self.cx + length * cos_a
            ty = self.cy + length * sin_a
            self.create_polygon(
                bx + dx*0.2 + px, by + dy*0.2 + py,
                tx, ty,
                bx + dx*0.2 - px, by + dy*0.2 - py,
                fill=color, outline=""
            )
            
        elif "Patek" in style or style == "Sword":
            # Sword Style (Diamond)
            mid_len = length * 0.8
            mx = self.cx + mid_len * cos_a
            my = self.cy + mid_len * sin_a
            
            self.create_polygon(
                self.cx + px*0.5, self.cy + py*0.5,
                mx + px*1.5, my + py*1.5,
                self.cx + dx, self.cy + dy,
                mx - px*1.5, my - py*1.5,
                self.cx - px*0.5, self.cy - py*0.5,
                fill=color, outline=color
            )
            
        else:
            # Baton Style (Straight Line with tapered end)
            self.create_polygon(
                self.cx + px, self.cy + py,
                self.cx + dx - px, self.cy + dy - py,
                self.cx + dx + px, self.cy + dy + py,
                self.cx - px, self.cy - py,
                fill=color, outline=""
            )

    def _draw_center_pinion(self, cfg: Dict[str, Any]) -> None:
        """Draw the central connecting pinion."""
        r = 6
        self.create_oval(
            self.cx - r, self.cy - r,
            self.cx + r, self.cy + r,
            fill=cfg.get("center_dot", "#FFFFFF"),
            outline="#000000",
            width=1
        )
