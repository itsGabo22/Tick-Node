"""
Tick Node — Analog Clock Desktop Application.

Phase 6: CustomTkinter High-Performance Desktop App.
Combines the backend Circular Doubly Linked Lists with a smooth
60FPS trigonometry-based Canvas renderer.
"""

import time
import customtkinter as ctk
from datetime import timedelta

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
        # Tracker for 24-hour AM/PM since ClockManager is purely 12-hour analog
        self.virtual_datetime = self.calc.get_current_time(self.current_zone)

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
            on_theme_change=self.handle_theme_change,
            width=250
        )
        self.control_panel.grid(row=0, column=0, sticky="nsew")
        
        # Set initial visual states
        self.control_panel.set_active_brand(WATCH_BRANDS[self.current_brand_key]["display_name"])
        self.control_panel.set_active_zone(self.current_zone)
        
        # Main Canvas Area
        self.canvas_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.canvas_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Center the canvas and labels
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(4, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # Brand Label
        self.lbl_brand_display = ctk.CTkLabel(
            self.canvas_frame, text="", font=ctk.CTkFont(size=28, weight="bold")
        )
        self.lbl_brand_display.grid(row=1, column=0, pady=(0, 20))

        # The CTk Dark mode background is roughly #242424
        self.clock_canvas = HighResClockCanvas(
            self.canvas_frame, 
            width=500, height=500, 
            bg="#242424"
        )
        self.clock_canvas.grid(row=2, column=0)

        # Digital Time Label
        self.lbl_digital_time = ctk.CTkLabel(
            self.canvas_frame, text="", font=ctk.CTkFont(family="Courier", size=36, weight="bold")
        )
        self.lbl_digital_time.grid(row=3, column=0, pady=(20, 0))

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
        self.virtual_datetime += timedelta(hours=diff)

    def handle_undo(self) -> None:
        # Full Reset to real time as if restarting the program
        self.clock = ClockManager()
        
        # Clear history stack
        while not self.history.is_empty():
            self.history.pop()
            
        # Reset Time Zone to local
        self.current_zone = self.calc.get_local_zone_name()
        if self.current_zone not in ALL_TIME_ZONES:
            self.current_zone = ALL_TIME_ZONES[0]
        self.control_panel.set_active_zone(self.current_zone)
        
        # Reset virtual datetime
        self.virtual_datetime = self.calc.get_current_time(self.current_zone)
        
        # Turn off time machine UI
        self.control_panel.switch_time_machine.deselect()

    def handle_time_machine(self) -> None:
        self.clock.toggle_time_machine()

    def handle_theme_change(self, mode: str) -> None:
        if mode == "Claro":
            ctk.set_appearance_mode("light")
            self.clock_canvas.configure(bg="#EBEBEB")
        else:
            ctk.set_appearance_mode("dark")
            self.clock_canvas.configure(bg="#242424")

    # ═══════════════════════════════════════════════════════════════════════════
    # Game Loops
    # ═══════════════════════════════════════════════════════════════════════════

    def auto_tick(self) -> None:
        """1 Hz logical tick for the backend lists."""
        self.clock.tick()
        
        # Update virtual datetime to track AM/PM accurately
        state = self.clock.get_state()
        if state["direction"] == "Forward":
            self.virtual_datetime += timedelta(seconds=1)
        else:
            self.virtual_datetime -= timedelta(seconds=1)
            
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
        
        # Update extra UI labels to accompany the clock
        self.lbl_brand_display.configure(
            text=brand_config["display_name"],
            text_color=("gray10", "gray90")
        )
        
        am_pm = self.virtual_datetime.strftime("%p")
        time_str = f"{state['hours']:02d}:{state['minutes']:02d}:{state['seconds']:02d} {am_pm}"
        if state["direction"] == "Backward":
            time_str += " ⏪"
        self.lbl_digital_time.configure(
            text=time_str,
            text_color=("gray10", "gray90")
        )
        
        # ~60 FPS (1000ms / 60 ≈ 16ms)
        self.after(16, self.update_display)


if __name__ == "__main__":
    app = TickNodeApp()
    app.mainloop()
