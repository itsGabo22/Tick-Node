"""
Tick Node — Analog Clock Desktop Application.

Phase 6: CustomTkinter High-Performance Desktop App.
Combines the backend Circular Doubly Linked Lists with a smooth
60FPS trigonometry-based Canvas renderer.
"""

import time
import customtkinter as ctk

from src.use_cases.clock_manager import ClockManager
from src.use_cases.history import HistoryStack
from src.infrastructure.static_data import WATCH_BRANDS, ALL_TIME_ZONES
from src.infrastructure.time_service import TimeCalculator
from src.ui.clock_canvas import HighResClockCanvas
from src.ui.control_panel import ControlPanel


# ═══════════════════════════════════════════════════════════════════════════
# Application Setup
# ═══════════════════════════════════════════════════════════════════════════

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TickNodeApp(ctk.CTk):
    """
    Main application window wrapping backend and UI components.
    Runs a 60FPS render loop alongside a 1Hz logical tick loop.
    """

    def __init__(self) -> None:
        super().__init__()
        
        self.title("Tick Node — Reloj Analógico")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Grid layout: 1 row, 2 columns (Sidebar, Canvas)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # ── Backend Initialization ──
        self.clock = ClockManager()
        self.history = HistoryStack()
        self.calc = TimeCalculator()
        
        # ── State Tracking ──
        self.current_zone = self.calc.get_local_zone_name()
        if self.current_zone not in ALL_TIME_ZONES:
            self.current_zone = ALL_TIME_ZONES[0]
            
        self.brand_map = {v["display_name"]: k for k, v in WATCH_BRANDS.items()}
        self.current_brand_key = list(WATCH_BRANDS.keys())[0]
        
        # Timing variables for smooth sweep
        self.last_tick_time = time.time()
        
        # ── UI Setup ──
        self._setup_ui()
        
        # ── Start Engines ──
        self.auto_tick()
        self.update_display()

    def _setup_ui(self) -> None:
        """Instantiate sidebar and main canvas."""
        # Sidebar
        brands_display = list(self.brand_map.keys())
        self.control_panel = ControlPanel(
            self,
            brands=brands_display,
            zones=ALL_TIME_ZONES,
            on_brand_change=self.handle_brand_change,
            on_zone_change=self.handle_zone_change,
            on_undo=self.handle_undo,
            on_time_machine_toggle=self.handle_time_machine,
            width=250
        )
        self.control_panel.grid(row=0, column=0, sticky="nsew")
        
        # Set initial visual states
        self.control_panel.set_active_brand(WATCH_BRANDS[self.current_brand_key]["display_name"])
        self.control_panel.set_active_zone(self.current_zone)
        
        # Main Canvas Area
        self.canvas_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.canvas_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # The CTk Dark mode background is roughly #242424
        self.clock_canvas = HighResClockCanvas(
            self.canvas_frame, 
            width=500, height=500, 
            bg="#242424"
        )
        self.clock_canvas.place(relx=0.5, rely=0.5, anchor="center")

    # ═══════════════════════════════════════════════════════════════════════════
    # Callbacks
    # ═══════════════════════════════════════════════════════════════════════════

    def handle_brand_change(self, display_name: str) -> None:
        self.current_brand_key = self.brand_map[display_name]

    def handle_zone_change(self, zone: str) -> None:
        if zone == self.current_zone:
            return
            
        diff = self.calc.hour_difference(destination=zone, origin=self.current_zone)
        self.history.push({
            "from": self.current_zone,
            "to": zone,
            "diff": diff
        })
        self.clock.shift_time_zone(diff)
        self.current_zone = zone

    def handle_undo(self) -> None:
        if not self.history.is_empty():
            record = self.history.pop()
            self.clock.shift_time_zone(-record["diff"])
            self.current_zone = record["from"]
            self.control_panel.set_active_zone(self.current_zone)

    def handle_time_machine(self) -> None:
        self.clock.toggle_time_machine()

    # ═══════════════════════════════════════════════════════════════════════════
    # Game Loops
    # ═══════════════════════════════════════════════════════════════════════════

    def auto_tick(self) -> None:
        """1 Hz logical tick for the backend lists."""
        self.clock.tick()
        self.last_tick_time = time.time()
        self.after(1000, self.auto_tick)

    def update_display(self) -> None:
        """60 FPS render loop for smooth sweeping."""
        state = self.clock.get_state()
        brand_config = WATCH_BRANDS[self.current_brand_key]
        
        # Calculate fractional second progress (0.0 to 1.0)
        elapsed = time.time() - self.last_tick_time
        fractional_second = min(1.0, elapsed)
        
        self.clock_canvas.render_clock(state, brand_config, fractional_second)
        
        # ~60 FPS (1000ms / 60 ≈ 16ms)
        self.after(16, self.update_display)


if __name__ == "__main__":
    app = TickNodeApp()
    app.mainloop()
