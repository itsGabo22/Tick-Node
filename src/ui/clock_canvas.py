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

from src.ui.watch_faces import (
    BaseWatchFace,
    SubmarinerFace,
    CalatravaFace,
    RoyalOakFace,
    SpeedmasterFace,
    TankFace
)

class HighResClockCanvas(tk.Canvas):
    """
    Advanced Canvas renderer for the analog clock.
    Delegates drawing to brand-specific strategy classes to support
    varying case shapes (round, rectangular, octagonal) and complex aesthetics.
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
        
        # Initialize all rendering strategies
        self.strategies = {
            "SubmarinerFace": SubmarinerFace(self, self.cx, self.cy, self.r),
            "CalatravaFace": CalatravaFace(self, self.cx, self.cy, self.r),
            "RoyalOakFace": RoyalOakFace(self, self.cx, self.cy, self.r),
            "SpeedmasterFace": SpeedmasterFace(self, self.cx, self.cy, self.r),
            "TankFace": TankFace(self, self.cx, self.cy, self.r),
        }

    def _update_dimensions(self) -> None:
        w = int(self.winfo_width())
        h = int(self.winfo_height())
        if w <= 1 or h <= 1:
            w, h = self.width, self.height
            
        if getattr(self, '_last_size', None) != (w, h):
            self.cx = w / 2
            self.cy = h / 2
            # Prevent excessive zoom: cap the max radius
            self.r = min(w, h) / 2 * 0.6
            if self.r > 210: self.r = 210
            if self.r < 100: self.r = 100
            
            self.strategies = {
                "SubmarinerFace": SubmarinerFace(self, self.cx, self.cy, self.r),
                "CalatravaFace": CalatravaFace(self, self.cx, self.cy, self.r),
                "RoyalOakFace": RoyalOakFace(self, self.cx, self.cy, self.r),
                "SpeedmasterFace": SpeedmasterFace(self, self.cx, self.cy, self.r),
                "TankFace": TankFace(self, self.cx, self.cy, self.r),
            }
            self._last_size = (w, h)
            self.current_w = w
            self.current_h = h

    def _draw_gradient(self, colors: list, w: int, h: int) -> None:
        """Draws a vertical gradient from top to bottom."""
        steps = 30
        h_step = h / steps
        segments = max(1, len(colors) - 1)
        for i in range(steps):
            progress = i / max(1, steps - 1)
            seg = int(progress * segments)
            if seg >= segments: seg = segments - 1
            
            local_p = (progress - (seg / segments)) * segments
            c1, c2 = colors[seg], colors[seg+1]
            r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
            r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
            
            r = int(r1 + (r2 - r1) * local_p)
            g = int(g1 + (g2 - g1) * local_p)
            b = int(b1 + (b2 - b1) * local_p)
            
            self.create_rectangle(0, i*h_step, w, (i+1)*h_step+2, fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

    def _draw_sky(self, virtual_hour: int) -> str:
        w, h = self.current_w, self.current_h
        if 0 <= virtual_hour <= 5:
            bg_color = "#0B1021"
            text_color = "#FFFFFF"
            self.create_rectangle(0, 0, w, h, fill=bg_color, outline="")
            # Draw moon
            self.create_oval(w*0.8, h*0.1, w*0.8+60, h*0.1+60, fill="#FFF8E7", outline="")
            self.create_oval(w*0.8-10, h*0.1-10, w*0.8+50, h*0.1+50, fill=bg_color, outline="")
            # Draw stars
            import random
            random.seed(virtual_hour)
            for _ in range(100):
                x, y = random.randint(0, w), random.randint(0, h)
                self.create_oval(x, y, x+2, y+2, fill="#FFFFFF", outline="")
        elif 6 <= virtual_hour <= 11:
            text_color = "#111111"
            # Morning Gradient: Soft blue to peach sunrise
            self._draw_gradient(["#4FA8F6", "#87CEEB", "#FFDAB9", "#FFF0F5"], w, h)
            # Draw morning sun (rising)
            self.create_oval(w*0.7, h*0.4, w*0.7+120, h*0.4+120, fill="#FFD700", outline="")
            self.create_oval(w*0.7+10, h*0.4+10, w*0.7+110, h*0.4+110, fill="#FFE4B5", outline="")
            # Background Mountains
            self.create_polygon(0, h, w*0.35, h*0.65, w*0.6, h, fill="#A3C6D3", outline="")
            self.create_polygon(w*0.4, h, w*0.8, h*0.55, w, h, fill="#8EB3C7", outline="")
            # Foreground Mountains
            self.create_polygon(-w*0.1, h, w*0.2, h*0.75, w*0.5, h, fill="#799EB2", outline="")
            self.create_polygon(w*0.3, h, w*0.65, h*0.7, w+w*0.1, h, fill="#648A9C", outline="")
        elif 12 <= virtual_hour <= 16:
            text_color = "#111111"
            # Bright Afternoon Gradient: Deep blue to light blue
            self._draw_gradient(["#1E90FF", "#4DA6FF", "#87CEFA", "#B0E0E6"], w, h)
            # Draw high sun
            self.create_oval(w*0.5-50, h*0.1-20, w*0.5+50, h*0.1+80, fill="#FFF6A5", outline="")
            self.create_oval(w*0.5-40, h*0.1-10, w*0.5+40, h*0.1+70, fill="#FFFACD", outline="")
            # Fluffy Clouds
            self.create_oval(w*0.7, h*0.25, w*0.7+120, h*0.25+50, fill="#FFFFFF", outline="")
            self.create_oval(w*0.7+40, h*0.25-20, w*0.7+100, h*0.25+30, fill="#FFFFFF", outline="")
            self.create_oval(w*0.2, h*0.4, w*0.2+100, h*0.4+40, fill="#FFFFFF", outline="")
            self.create_oval(w*0.2+30, h*0.4-15, w*0.2+80, h*0.4+20, fill="#FFFFFF", outline="")
            # Green Rolling Hills
            self.create_polygon(0, h, w*0.4, h*0.75, w*0.7, h, fill="#556B2F", outline="")
            self.create_polygon(w*0.3, h, w*0.8, h*0.7, w, h, fill="#6B8E23", outline="")
            self.create_polygon(-w*0.1, h, w*0.2, h*0.85, w*0.5, h, fill="#8FBC8F", outline="")
            self.create_polygon(w*0.4, h, w*0.7, h*0.8, w+w*0.1, h, fill="#9ACD32", outline="")
        elif 17 <= virtual_hour <= 19:
            text_color = "#FFFFFF"
            # Sunset Gradient: Deep purple to crimson to gold
            self._draw_gradient(["#2B1B54", "#8B008B", "#FF4500", "#FFD700"], w, h)
            # Draw setting sun
            self.create_oval(w*0.4, h*0.6, w*0.4+140, h*0.6+140, fill="#FF6347", outline="")
            self.create_oval(w*0.4+20, h*0.6+20, w*0.4+120, h*0.6+120, fill="#FF8C00", outline="")
            # Background Mountains Silhouette
            self.create_polygon(0, h, w*0.25, h*0.6, w*0.55, h, fill="#3A1C4A", outline="")
            self.create_polygon(w*0.35, h, w*0.75, h*0.5, w, h, fill="#2C123B", outline="")
            # Foreground Mountains Silhouette
            self.create_polygon(-w*0.1, h, w*0.15, h*0.8, w*0.4, h, fill="#1A0824", outline="")
            self.create_polygon(w*0.2, h, w*0.6, h*0.75, w+w*0.1, h, fill="#0F0314", outline="")
        else: # 20-23
            bg_color = "#1A1A1D"
            text_color = "#FFFFFF"
            self.create_rectangle(0, 0, w, h, fill=bg_color, outline="")
            # Draw moon
            self.create_oval(w*0.8, h*0.1, w*0.8+60, h*0.1+60, fill="#FFF8E7", outline="")
            # Draw stars
            import random
            random.seed(virtual_hour)
            for _ in range(100):
                x, y = random.randint(0, w), random.randint(0, h)
                self.create_oval(x, y, x+2, y+2, fill="#FFFFFF", outline="")
                
        return text_color

    def render_clock(
        self, 
        state: Dict[str, Any], 
        brand_config: Dict[str, Any],
        fractional_second: float = 0.0,
        virtual_hour: int = 12,
        time_str: str = "",
        travel_str: str = ""
    ) -> None:
        """
        Main drawing routine for the clock frame.
        fractional_second allows for 60fps smooth sweeping between discrete seconds.
        """
        self._update_dimensions()
        self.delete("all")
        
        # Draw background sky and get contrast text color
        text_color = self._draw_sky(virtual_hour)
        
        # Look up the strategy from the static configuration
        strategy_name = brand_config.get("face_strategy")
        strategy = self.strategies.get(strategy_name)
        
        if strategy:
            strategy.render(state, brand_config, fractional_second)
        else:
            # Fallback for undefined strategies
            fallback = BaseWatchFace(self, self.cx, self.cy, self.r)
            fallback.render(state, brand_config, fractional_second)

        # Draw UI Text Natively with Drop Shadows for readability
        def draw_shadow_text(x, y, txt, font, anchor):
            shadow_color = "#000000" if text_color == "#FFFFFF" else "#FFFFFF"
            self.create_text(x+2, y+2, text=txt, fill=shadow_color, font=font, anchor=anchor)
            self.create_text(x, y, text=txt, fill=text_color, font=font, anchor=anchor)

        draw_shadow_text(self.cx, 50, brand_config["display_name"], 
                         ("Helvetica", 28, "bold"), "n")
                         
        draw_shadow_text(self.cx, self.current_h - 90, time_str, 
                         ("Courier", 36, "bold"), "s")
                         
        draw_shadow_text(self.cx, self.current_h - 40, travel_str, 
                         ("Helvetica", 18, "bold"), "s")
