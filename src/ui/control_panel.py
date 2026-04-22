"""
Control Panel — The Modern Sidebar for Tick Node.

A sleek customtkinter frame housing all the interactive controls.
"""

import customtkinter as ctk
from typing import Callable, List, Any


class ControlPanel(ctk.CTkFrame):
    """
    Sidebar frame containing configuration dropdowns and buttons.
    Uses customtkinter for a modern, rounded aesthetic.
    """

    def __init__(
        self,
        master: Any,
        brands: List[str],
        zones: List[str],
        on_brand_change: Callable[[str], None],
        on_zone_change: Callable[[str], None],
        on_undo: Callable[[], None],
        on_time_machine_toggle: Callable[[], None],
        on_theme_change: Callable[[str], None],
        **kwargs: Any
    ) -> None:
        super().__init__(master, corner_radius=0, **kwargs)

        self.grid_rowconfigure(10, weight=1)  # Spacer to push bottom items down

        # ── Title ──
        self.lbl_title = ctk.CTkLabel(
            self, text="Panel de Control", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.lbl_title.grid(row=0, column=0, padx=20, pady=(30, 20), sticky="w")

        # ── Brand Selector ──
        self.lbl_brand = ctk.CTkLabel(
            self, text="Marca de Lujo", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_brand.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.help_brand = ctk.CTkLabel(self, text="Cambia el estilo visual (Factory).", font=ctk.CTkFont(size=11), text_color="gray")
        self.help_brand.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")

        self.opt_brand = ctk.CTkOptionMenu(
            self,
            values=brands,
            command=on_brand_change,
            dynamic_resizing=False
        )
        self.opt_brand.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        # ── Timezone Selector ──
        self.lbl_zone = ctk.CTkLabel(
            self, text="Zona Horaria", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_zone.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        self.help_zone = ctk.CTkLabel(self, text="Viaja por el mundo. Guarda en Pila.", font=ctk.CTkFont(size=11), text_color="gray")
        self.help_zone.grid(row=5, column=0, padx=20, pady=(0, 5), sticky="w")

        self.opt_zone = ctk.CTkOptionMenu(
            self,
            values=zones,
            command=on_zone_change,
            dynamic_resizing=False
        )
        self.opt_zone.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")

        # ── Undo Button ──
        self.btn_undo = ctk.CTkButton(
            self,
            text="⏪ Deshacer Viaje",
            command=on_undo,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE")
        )
        self.btn_undo.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.help_undo = ctk.CTkLabel(self, text="Extrae de la Pila y vuelve a tiempo real.", font=ctk.CTkFont(size=11), text_color="gray")
        self.help_undo.grid(row=8, column=0, padx=20, pady=(0, 20), sticky="w")

        # ── Time Machine Switch ──
        self.switch_time_machine = ctk.CTkSwitch(
            self,
            text="Máquina del Tiempo",
            command=on_time_machine_toggle,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.switch_time_machine.grid(row=9, column=0, padx=20, pady=(10, 0), sticky="w")
        self.help_time = ctk.CTkLabel(self, text="Invierte las listas (Strategy).", font=ctk.CTkFont(size=11), text_color="gray")
        self.help_time.grid(row=10, column=0, padx=20, pady=(0, 20), sticky="w")
        
        self.grid_rowconfigure(11, weight=1)  # Spacer

        # ── Theme Toggle ──
        self.seg_theme = ctk.CTkSegmentedButton(
            self, values=["Oscuro", "Claro"],
            command=on_theme_change
        )
        self.seg_theme.set("Oscuro")
        self.seg_theme.grid(row=12, column=0, padx=20, pady=(10, 20), sticky="ew")

    def set_active_brand(self, brand: str) -> None:
        """Update the option menu visually."""
        self.opt_brand.set(brand)

    def set_active_zone(self, zone: str) -> None:
        """Update the option menu visually."""
        self.opt_zone.set(zone)
