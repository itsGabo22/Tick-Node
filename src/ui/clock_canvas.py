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
        
        # Look up the strategy from the static configuration
        strategy_name = brand_config.get("face_strategy")
        strategy = self.strategies.get(strategy_name)
        
        if strategy:
            strategy.render(state, brand_config, fractional_second)
        else:
            # Fallback for undefined strategies
            fallback = BaseWatchFace(self, self.cx, self.cy, self.r)
            fallback.render(state, brand_config, fractional_second)
