"""
Strategy Pattern implementations for different watch faces.
Each class encapsulates the specific drawing logic (trigonometry, colors, shapes)
for a unique luxury watch brand, keeping the main Canvas clean.
"""

import math
import tkinter as tk
from typing import Any, Dict


class BaseWatchFace:
    """Abstract base class for watch face rendering strategies."""
    
    def __init__(self, canvas: tk.Canvas, cx: float, cy: float, r: float):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.r = r

    def _angle_to_xy(self, angle_deg: float, radius: float) -> tuple[float, float]:
        rad = math.radians(angle_deg - 90)
        return self.cx + radius * math.cos(rad), self.cy + radius * math.sin(rad)

    def draw_straps(self, cfg: Dict[str, Any]) -> None:
        """Default generic strap drawing."""
        strap_type = cfg.get("strap_type", "leather")
        color = cfg.get("strap_color", "#333333")
        
        s_width = self.r * 1.15
        s_length = self.r * 1.5
        
        top_pts = [
            self.cx - s_width / 2, self.cy - self.r * 0.8,
            self.cx + s_width / 2, self.cy - self.r * 0.8,
            self.cx + s_width * 0.85 / 2, self.cy - self.r - s_length,
            self.cx - s_width * 0.85 / 2, self.cy - self.r - s_length
        ]
        
        bot_pts = [
            self.cx - s_width / 2, self.cy + self.r * 0.8,
            self.cx + s_width / 2, self.cy + self.r * 0.8,
            self.cx + s_width * 0.85 / 2, self.cy + self.r + s_length,
            self.cx - s_width * 0.85 / 2, self.cy + self.r + s_length
        ]
        
        self.canvas.create_polygon(top_pts, fill=color, outline="#111111", width=2)
        self.canvas.create_polygon(bot_pts, fill=color, outline="#111111", width=2)
        
        if strap_type == "leather":
            stitch_offset = 8
            top_stitch = [
                top_pts[0] + stitch_offset, top_pts[1] - stitch_offset,
                top_pts[2] - stitch_offset, top_pts[3] - stitch_offset,
                top_pts[4] - stitch_offset, top_pts[5] + stitch_offset,
                top_pts[6] + stitch_offset, top_pts[7] + stitch_offset
            ]
            bot_stitch = [
                bot_pts[0] + stitch_offset, bot_pts[1] + stitch_offset,
                bot_pts[2] - stitch_offset, bot_pts[3] + stitch_offset,
                bot_pts[4] - stitch_offset, bot_pts[5] - stitch_offset,
                bot_pts[6] + stitch_offset, bot_pts[7] - stitch_offset
            ]
            
            stitch_color = "#E0D8C8" if "Patek" in cfg.get("display_name", "") else "#555555"
            self.canvas.create_polygon(top_stitch, fill="", outline=stitch_color, dash=(4, 4), width=2)
            self.canvas.create_polygon(bot_stitch, fill="", outline=stitch_color, dash=(4, 4), width=2)

    def draw_case_and_dial(self, cfg: Dict[str, Any]) -> None:
        """Default circular dial."""
        self.canvas.create_oval(
            self.cx - self.r, self.cy - self.r,
            self.cx + self.r, self.cy + self.r,
            fill=cfg["dial_bg"],
            outline=cfg["dial_border"],
            width=8
        )

    def draw_markers(self, cfg: Dict[str, Any]) -> None:
        pass

    def draw_hands(self, state: Dict[str, Any], cfg: Dict[str, Any], frac_sec: float) -> None:
        pass

    def render(self, state: Dict[str, Any], cfg: Dict[str, Any], frac_sec: float) -> None:
        self.draw_straps(cfg)
        self.draw_case_and_dial(cfg)
        self.draw_markers(cfg)
        self.draw_hands(state, cfg, frac_sec)
        
        # Center Pinion
        r = 5
        self.canvas.create_oval(
            self.cx - r, self.cy - r,
            self.cx + r, self.cy + r,
            fill="#C0C0C0", outline="#333333", width=1
        )


class SubmarinerFace(BaseWatchFace):
    """Rolex Submariner Strategy."""
    
    def draw_straps(self, cfg: Dict[str, Any]) -> None:
        # Custom steel bracelet links
        color = cfg.get("strap_color", "#C0C0C0")
        s_width = self.r * 1.1
        s_length = self.r * 1.5
        
        # Top links
        for i in range(8):
            frac1 = i / 8
            frac2 = (i + 1) / 8
            y1 = self.cy - self.r * 0.8 - frac1 * s_length
            y2 = self.cy - self.r * 0.8 - frac2 * s_length
            w1 = s_width * (1 - frac1 * 0.15)
            w2 = s_width * (1 - frac2 * 0.15)
            self.canvas.create_polygon(
                self.cx - w1/2, y1, self.cx + w1/2, y1,
                self.cx + w2/2, y2, self.cx - w2/2, y2,
                fill=color, outline="#888888", width=2
            )
            # Center link split
            self.canvas.create_line(self.cx - w1*0.2, y1, self.cx - w2*0.2, y2, fill="#888888", width=2)
            self.canvas.create_line(self.cx + w1*0.2, y1, self.cx + w2*0.2, y2, fill="#888888", width=2)

        # Bottom links
        for i in range(8):
            frac1 = i / 8
            frac2 = (i + 1) / 8
            y1 = self.cy + self.r * 0.8 + frac1 * s_length
            y2 = self.cy + self.r * 0.8 + frac2 * s_length
            w1 = s_width * (1 - frac1 * 0.15)
            w2 = s_width * (1 - frac2 * 0.15)
            self.canvas.create_polygon(
                self.cx - w1/2, y1, self.cx + w1/2, y1,
                self.cx + w2/2, y2, self.cx - w2/2, y2,
                fill=color, outline="#888888", width=2
            )
            # Center link split
            self.canvas.create_line(self.cx - w1*0.2, y1, self.cx - w2*0.2, y2, fill="#888888", width=2)
            self.canvas.create_line(self.cx + w1*0.2, y1, self.cx + w2*0.2, y2, fill="#888888", width=2)

    def draw_case_and_dial(self, cfg: Dict[str, Any]) -> None:
        self.canvas.create_oval(
            self.cx - self.r, self.cy - self.r,
            self.cx + self.r, self.cy + self.r,
            fill="#C0C0C0", outline="#888888", width=2
        )
        br = self.r * 0.96
        self.canvas.create_oval(
            self.cx - br, self.cy - br,
            self.cx + br, self.cy + br,
            fill=cfg["dial_border"], outline=""
        )
        for minute in range(60):
            angle = minute * 6
            if minute % 10 == 0 and minute != 0:
                x, y = self._angle_to_xy(angle, self.r * 0.88)
                self.canvas.create_text(x, y, text=str(minute), fill="#C0C0C0", font=("Helvetica", 14, "bold"))
            elif minute == 0:
                tx, ty = self._angle_to_xy(angle, self.r * 0.94)
                bx, by = self._angle_to_xy(angle, self.r * 0.82)
                rad = math.radians(angle - 90)
                pw = self.r * 0.05
                self.canvas.create_polygon(
                    tx - math.sin(rad)*pw, ty + math.cos(rad)*pw,
                    tx + math.sin(rad)*pw, ty - math.cos(rad)*pw,
                    bx, by, fill="#C0C0C0"
                )
                px, py = self._angle_to_xy(angle, self.r * 0.89)
                self.canvas.create_oval(px - 3, py - 3, px + 3, py + 3, fill="#FFFFFF")
            elif minute % 5 == 0:
                x1, y1 = self._angle_to_xy(angle, self.r * 0.85)
                x2, y2 = self._angle_to_xy(angle, self.r * 0.91)
                self.canvas.create_line(x1, y1, x2, y2, fill="#C0C0C0", width=3)
            elif minute < 15:
                x1, y1 = self._angle_to_xy(angle, self.r * 0.88)
                x2, y2 = self._angle_to_xy(angle, self.r * 0.91)
                self.canvas.create_line(x1, y1, x2, y2, fill="#C0C0C0", width=1)
        
        ir = self.r * 0.78
        self.canvas.create_oval(
            self.cx - ir, self.cy - ir,
            self.cx + ir, self.cy + ir,
            fill=cfg["dial_bg"], outline="#333333", width=2
        )
        
        self.canvas.create_text(self.cx, self.cy - self.r * 0.4, text="ROLEX", fill="#FFFFFF", font=("Helvetica", 16, "bold"))
        self.canvas.create_text(self.cx, self.cy - self.r * 0.32, text="OYSTER PERPETUAL", fill="#FFFFFF", font=("Helvetica", 8))
        self.canvas.create_text(self.cx, self.cy + self.r * 0.35, text="SUBMARINER", fill="#FFFFFF", font=("Helvetica", 10))
        self.canvas.create_text(self.cx, self.cy + self.r * 0.42, text="1000ft = 300m", fill="#FFFFFF", font=("Helvetica", 8))

    def draw_markers(self, cfg: Dict[str, Any]) -> None:
        for minute in range(60):
            if minute % 5 == 0: continue
            angle = minute * 6
            x1, y1 = self._angle_to_xy(angle, self.r * 0.75)
            x2, y2 = self._angle_to_xy(angle, self.r * 0.77)
            self.canvas.create_line(x1, y1, x2, y2, fill="#A0A0A0", width=2)

        for hour in range(1, 13):
            angle = hour * 30
            if hour == 12:
                tx, ty = self._angle_to_xy(angle, self.r * 0.74)
                bx, by = self._angle_to_xy(angle, self.r * 0.58)
                rad = math.radians(angle - 90)
                pw = self.r * 0.08
                self.canvas.create_polygon(
                    tx - math.sin(rad)*pw, ty + math.cos(rad)*pw,
                    tx + math.sin(rad)*pw, ty - math.cos(rad)*pw,
                    bx, by, fill="#FFFFFF", outline="#C0C0C0", width=2
                )
            elif hour in (3, 6, 9):
                x1, y1 = self._angle_to_xy(angle, self.r * 0.58)
                x2, y2 = self._angle_to_xy(angle, self.r * 0.74)
                rad = math.radians(angle - 90)
                pw = self.r * 0.03
                px, py = -math.sin(rad)*pw, math.cos(rad)*pw
                self.canvas.create_polygon(
                    x1+px, y1+py, x2+px, y2+py, x2-px, y2-py, x1-px, y1-py,
                    fill="#FFFFFF", outline="#C0C0C0", width=2
                )
            else:
                cx, cy = self._angle_to_xy(angle, self.r * 0.65)
                cr = self.r * 0.06
                self.canvas.create_oval(cx-cr, cy-cr, cx+cr, cy+cr, fill="#FFFFFF", outline="#C0C0C0", width=2)

    def draw_hands(self, state: Dict[str, Any], cfg: Dict[str, Any], frac_sec: float) -> None:
        s = state["seconds"] + frac_sec if state["direction"] == "Forward" else state["seconds"] - frac_sec
        m = state["minutes"] + s / 60
        h = (state["hours"] % 12) + m / 60

        # Mercedes Hour
        rad = math.radians(h * 30 - 90)
        length = self.r * 0.45
        width = 12
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        px, py = -sin_a * width/2, cos_a * width/2
        base_len = length * 0.65
        bx, by = self.cx + base_len * cos_a, self.cy + base_len * sin_a
        self.canvas.create_polygon(self.cx+px, self.cy+py, bx+px, by+py, bx-px, by-py, self.cx-px, self.cy-py, fill="#FFFFFF", outline="#C0C0C0", width=2)
        circle_r = width * 1.5
        self.canvas.create_oval(bx+length*0.1-circle_r, by+length*0.1-circle_r, bx+length*0.1+circle_r, by+length*0.1+circle_r, outline="#C0C0C0", width=2, fill="#FFFFFF")
        ccx, ccy = bx+length*0.1, by+length*0.1
        self.canvas.create_line(ccx, ccy, ccx+circle_r*cos_a, ccy+circle_r*sin_a, fill="#C0C0C0", width=2)
        self.canvas.create_line(ccx, ccy, ccx+circle_r*math.cos(rad+2.1), ccy+circle_r*math.sin(rad+2.1), fill="#C0C0C0", width=2)
        self.canvas.create_line(ccx, ccy, ccx+circle_r*math.cos(rad-2.1), ccy+circle_r*math.sin(rad-2.1), fill="#C0C0C0", width=2)
        tx, ty = self.cx + length * cos_a, self.cy + length * sin_a
        self.canvas.create_polygon(bx+length*0.2+px, by+length*0.2+py, tx, ty, bx+length*0.2-px, by+length*0.2-py, fill="#FFFFFF", outline="#C0C0C0", width=2)

        # Minute Sword
        rad = math.radians(m * 6 - 90)
        length = self.r * 0.65
        width = 8
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        px, py = -sin_a * width/2, cos_a * width/2
        mx, my = self.cx + length * 0.85 * cos_a, self.cy + length * 0.85 * sin_a
        dx, dy = length * cos_a, length * sin_a
        self.canvas.create_polygon(self.cx+px, self.cy+py, mx+px, my+py, self.cx+dx, self.cy+dy, mx-px, my-py, self.cx-px, self.cy-py, fill="#FFFFFF", outline="#C0C0C0", width=2)

        # Seconds
        sec_angle = s * 6
        sx, sy = self._angle_to_xy(sec_angle, self.r * 0.85)
        stx, sty = self._angle_to_xy(sec_angle + 180, self.r * 0.2)
        self.canvas.create_line(stx, sty, sx, sy, fill="#E8E8E8", width=2, capstyle=tk.ROUND)
        cwx, cwy = self._angle_to_xy(sec_angle + 180, self.r * 0.15)
        self.canvas.create_oval(cwx-4, cwy-4, cwx+4, cwy+4, fill="#E8E8E8", outline="")
        lx, ly = self._angle_to_xy(sec_angle, self.r * 0.5)
        self.canvas.create_oval(lx-5, ly-5, lx+5, ly+5, fill="#FFFFFF", outline="#C0C0C0", width=1.5)


class CalatravaFace(BaseWatchFace):
    """Patek Philippe Calatrava Strategy."""
    def draw_straps(self, cfg: Dict[str, Any]) -> None:
        super().draw_straps(cfg) # Basic leather with stitching

    def draw_case_and_dial(self, cfg: Dict[str, Any]) -> None:
        self.canvas.create_oval(
            self.cx - self.r, self.cy - self.r,
            self.cx + self.r, self.cy + self.r,
            fill=cfg["dial_bg"], outline="#E0E0E0", width=8
        )
        # Inner track ring
        ir = self.r * 0.95
        self.canvas.create_oval(
            self.cx - ir, self.cy - ir,
            self.cx + ir, self.cy + ir,
            outline="#333333", width=1
        )
        self.canvas.create_text(self.cx, self.cy - self.r * 0.35, text="PATEK PHILIPPE", fill="#111111", font=("Garamond", 16, "bold"))
        self.canvas.create_text(self.cx, self.cy - self.r * 0.25, text="GENEVE", fill="#111111", font=("Garamond", 10))

        # Small seconds subdial
        sr = self.r * 0.25
        scy = self.cy + self.r * 0.4
        self.canvas.create_oval(self.cx - sr, scy - sr, self.cx + sr, scy + sr, outline="#333333", width=1)
        for i in range(12):
            rad = math.radians(i * 30 - 90)
            x1, y1 = self.cx + sr * 0.8 * math.cos(rad), scy + sr * 0.8 * math.sin(rad)
            x2, y2 = self.cx + sr * 0.95 * math.cos(rad), scy + sr * 0.95 * math.sin(rad)
            self.canvas.create_line(x1, y1, x2, y2, fill="#111111", width=1)

    def draw_markers(self, cfg: Dict[str, Any]) -> None:
        for hour in range(1, 13):
            angle = hour * 30
            x1, y1 = self._angle_to_xy(angle, self.r * 0.75)
            x2, y2 = self._angle_to_xy(angle, self.r * 0.9)
            rad = math.radians(angle - 90)
            pw = self.r * 0.02
            px, py = -math.sin(rad)*pw, math.cos(rad)*pw
            self.canvas.create_polygon(
                x1+px, y1+py, x2, y2, x1-px, y1-py,
                fill="#2C2C2C", outline="#111111"
            )
            # Dot minute markers
            for m in range(4):
                mx, my = self._angle_to_xy(angle + (m+1)*6, self.r * 0.92)
                self.canvas.create_oval(mx-1, my-1, mx+1, my+1, fill="#111111", outline="")

    def draw_hands(self, state: Dict[str, Any], cfg: Dict[str, Any], frac_sec: float) -> None:
        s = state["seconds"] + frac_sec if state["direction"] == "Forward" else state["seconds"] - frac_sec
        m = state["minutes"] + s / 60
        h = (state["hours"] % 12) + m / 60

        def draw_sword(angle, length, width):
            rad = math.radians(angle - 90)
            cos_a, sin_a = math.cos(rad), math.sin(rad)
            px, py = -sin_a * width/2, cos_a * width/2
            mx, my = self.cx + length * 0.8 * cos_a, self.cy + length * 0.8 * sin_a
            dx, dy = length * cos_a, length * sin_a
            self.canvas.create_polygon(
                self.cx+px*0.5, self.cy+py*0.5, mx+px*1.5, my+py*1.5,
                self.cx+dx, self.cy+dy, mx-px*1.5, my-py*1.5, self.cx-px*0.5, self.cy-py*0.5,
                fill="#1A1A1A", outline="#000000"
            )

        draw_sword(h * 30, self.r * 0.55, 10)
        draw_sword(m * 6, self.r * 0.85, 6)
        
        # Sub-seconds hand
        sr = self.r * 0.25
        scy = self.cy + self.r * 0.4
        rad = math.radians(s * 6 - 90)
        sx, sy = self.cx + sr * 0.9 * math.cos(rad), scy + sr * 0.9 * math.sin(rad)
        self.canvas.create_line(self.cx, scy, sx, sy, fill="#1A1A1A", width=2)
        self.canvas.create_oval(self.cx-3, scy-3, self.cx+3, scy+3, fill="#1A1A1A")


class RoyalOakFace(BaseWatchFace):
    """Audemars Piguet Royal Oak Strategy."""
    def draw_case_and_dial(self, cfg: Dict[str, Any]) -> None:
        # Octagonal Bezel
        pts = []
        for i in range(8):
            angle = i * 45 + 22.5
            rad = math.radians(angle)
            pts.extend([self.cx + self.r * 1.05 * math.cos(rad), self.cy + self.r * 1.05 * math.sin(rad)])
        
        self.canvas.create_polygon(pts, fill="#C0C0C0", outline="#888888", width=4)
        
        # 8 Hexagonal Screws
        for i in range(8):
            angle = i * 45 + 22.5
            sx, sy = self.cx + self.r * 0.95 * math.cos(math.radians(angle)), self.cy + self.r * 0.95 * math.sin(math.radians(angle))
            self.canvas.create_oval(sx-5, sy-5, sx+5, sy+5, fill="#D0D0D0", outline="#555555")
            self.canvas.create_line(sx-3, sy-3, sx+3, sy+3, fill="#555555", width=2)

        # Dial Background
        ir = self.r * 0.85
        self.canvas.create_oval(self.cx - ir, self.cy - ir, self.cx + ir, self.cy + ir, fill=cfg["dial_bg"])
        
        # Tapisserie Pattern (Grid)
        step = int(self.r * 0.08)
        for i in range(-int(ir), int(ir), step):
            # Horizontal lines
            h_len = math.sqrt(max(0, ir**2 - i**2))
            self.canvas.create_line(self.cx - h_len, self.cy + i, self.cx + h_len, self.cy + i, fill="#C0C0C0", width=1)
            # Vertical lines
            v_len = math.sqrt(max(0, ir**2 - i**2))
            self.canvas.create_line(self.cx + i, self.cy - v_len, self.cx + i, self.cy + v_len, fill="#C0C0C0", width=1)

        def draw_subdial(x_off, y_off):
            scx, scy = self.cx + x_off, self.cy + y_off
            sr = self.r * 0.22
            self.canvas.create_oval(scx - sr, scy - sr, scx + sr, scy + sr, fill="#1D3557", outline="#888888", width=2)
            for i in range(12):
                sx, sy = scx + sr * 0.7 * math.cos(math.radians(i * 30)), scy + sr * 0.7 * math.sin(math.radians(i * 30))
                self.canvas.create_line(scx + sr * 0.9 * math.cos(math.radians(i * 30)), scy + sr * 0.9 * math.sin(math.radians(i * 30)), sx, sy, fill="#FFFFFF", width=1)
            self.canvas.create_line(scx, scy, scx, scy - sr * 0.8, fill="#FFFFFF", width=2)
            
        draw_subdial(-self.r * 0.35, 0)
        draw_subdial(self.r * 0.35, 0)
        draw_subdial(0, self.r * 0.35)

        self.canvas.create_text(self.cx, self.cy - self.r * 0.45, text="AUDEMARS PIGUET", fill="#111111", font=("Helvetica", 10, "bold"))
        self.canvas.create_text(self.cx, self.cy - self.r * 0.35, text="AUTOMATIC", fill="#111111", font=("Helvetica", 6))

    def draw_markers(self, cfg: Dict[str, Any]) -> None:
        for hour in range(1, 13):
            angle = hour * 30
            x1, y1 = self._angle_to_xy(angle, self.r * 0.65)
            x2, y2 = self._angle_to_xy(angle, self.r * 0.8)
            rad = math.radians(angle - 90)
            pw = self.r * 0.03
            px, py = -math.sin(rad)*pw, math.cos(rad)*pw
            
            if hour == 12:
                self.canvas.create_polygon(x1+px*1.5, y1+py*1.5, x2+px*1.5, y2+py*1.5, x2+px*0.5, y2+py*0.5, x1+px*0.5, y1+py*0.5, fill="#FFFFFF", outline="#888888")
                self.canvas.create_polygon(x1-px*0.5, y1-py*0.5, x2-px*0.5, y2-py*0.5, x2-px*1.5, y2-py*1.5, x1-px*1.5, y1-py*1.5, fill="#FFFFFF", outline="#888888")
            else:
                self.canvas.create_polygon(x1+px, y1+py, x2+px, y2+py, x2-px, y2-py, x1-px, y1-py, fill="#FFFFFF", outline="#888888")

    def draw_hands(self, state: Dict[str, Any], cfg: Dict[str, Any], frac_sec: float) -> None:
        s = state["seconds"] + frac_sec if state["direction"] == "Forward" else state["seconds"] - frac_sec
        m = state["minutes"] + s / 60
        h = (state["hours"] % 12) + m / 60

        def draw_baton_hand(angle, length, width):
            rad = math.radians(angle - 90)
            cos_a, sin_a = math.cos(rad), math.sin(rad)
            px, py = -sin_a * width/2, cos_a * width/2
            dx, dy = length * cos_a, length * sin_a
            self.canvas.create_polygon(
                self.cx+px, self.cy+py, self.cx+dx+px, self.cy+dy+py,
                self.cx+dx-px, self.cy+dy-py, self.cx-px, self.cy-py,
                fill="#FFFFFF", outline="#888888", width=2
            )

        draw_baton_hand(h * 30, self.r * 0.5, 12)
        draw_baton_hand(m * 6, self.r * 0.75, 8)
        
        sx, sy = self._angle_to_xy(s * 6, self.r * 0.8)
        stx, sty = self._angle_to_xy(s * 6 + 180, self.r * 0.2)
        self.canvas.create_line(stx, sty, sx, sy, fill="#FFFFFF", width=2)


class SpeedmasterFace(BaseWatchFace):
    """Omega Speedmaster Strategy."""
    def draw_case_and_dial(self, cfg: Dict[str, Any]) -> None:
        self.canvas.create_oval(
            self.cx - self.r, self.cy - self.r,
            self.cx + self.r, self.cy + self.r,
            fill="#000000", outline="#C0C0C0", width=4
        )
        
        for text, angle in [("60", 0), ("65", 30), ("70", 60), ("80", 120), ("100", 180), ("140", 240), ("240", 300)]:
            x, y = self._angle_to_xy(angle, self.r * 0.95)
            self.canvas.create_text(x, y, text=text, fill="#FFFFFF", font=("Arial", 8, "bold"))
            
        ir = self.r * 0.88
        self.canvas.create_oval(self.cx - ir, self.cy - ir, self.cx + ir, self.cy + ir, fill=cfg["dial_bg"])
        
        self.canvas.create_text(self.cx, self.cy - self.r * 0.45, text="Ω", fill="#FFFFFF", font=("Helvetica", 18))
        self.canvas.create_text(self.cx, self.cy - self.r * 0.35, text="OMEGA", fill="#FFFFFF", font=("Arial", 12, "bold"))
        self.canvas.create_text(self.cx, self.cy - self.r * 0.27, text="Speedmaster", fill="#FFFFFF", font=("Garamond", 12, "italic"))
        self.canvas.create_text(self.cx, self.cy - self.r * 0.20, text="PROFESSIONAL", fill="#FFFFFF", font=("Arial", 8))

        def draw_subdial(x_off, y_off):
            scx, scy = self.cx + x_off, self.cy + y_off
            sr = self.r * 0.22
            self.canvas.create_oval(scx - sr, scy - sr, scx + sr, scy + sr, fill="#151515", outline="#444444")
            for i in range(12):
                sx, sy = scx + sr * 0.8 * math.cos(math.radians(i * 30)), scy + sr * 0.8 * math.sin(math.radians(i * 30))
                self.canvas.create_line(scx + sr * 0.95 * math.cos(math.radians(i * 30)), scy + sr * 0.95 * math.sin(math.radians(i * 30)), sx, sy, fill="#FFFFFF")
            self.canvas.create_line(scx, scy, scx, scy - sr * 0.8, fill="#FFFFFF", width=2)
            
        draw_subdial(-self.r * 0.35, 0)
        draw_subdial(self.r * 0.35, 0)
        draw_subdial(0, self.r * 0.35)

    def draw_markers(self, cfg: Dict[str, Any]) -> None:
        for minute in range(60):
            angle = minute * 6
            length = 0.82 if minute % 5 == 0 else 0.85
            x1, y1 = self._angle_to_xy(angle, self.r * length)
            x2, y2 = self._angle_to_xy(angle, self.r * 0.88)
            self.canvas.create_line(x1, y1, x2, y2, fill="#FFFFFF", width=3 if minute % 5 == 0 else 1)
            
            # Speedmaster 1/5th second ticks
            if minute % 5 != 0:
                for frac in range(1, 5):
                    fa = angle + frac * 1.2
                    fx1, fy1 = self._angle_to_xy(fa, self.r * 0.86)
                    fx2, fy2 = self._angle_to_xy(fa, self.r * 0.88)
                    self.canvas.create_line(fx1, fy1, fx2, fy2, fill="#FFFFFF", width=1)

    def draw_hands(self, state: Dict[str, Any], cfg: Dict[str, Any], frac_sec: float) -> None:
        s = state["seconds"] + frac_sec if state["direction"] == "Forward" else state["seconds"] - frac_sec
        m = state["minutes"] + s / 60
        h = (state["hours"] % 12) + m / 60

        def draw_pencil(angle, length, width):
            rad = math.radians(angle - 90)
            cos_a, sin_a = math.cos(rad), math.sin(rad)
            px, py = -sin_a * width/2, cos_a * width/2
            dx, dy = length * cos_a, length * sin_a
            tip_x, tip_y = self.cx + length * 1.1 * cos_a, self.cy + length * 1.1 * sin_a
            self.canvas.create_polygon(
                self.cx+px, self.cy+py, self.cx+dx+px, self.cy+dy+py, tip_x, tip_y,
                self.cx+dx-px, self.cy+dy-py, self.cx-px, self.cy-py,
                fill="#FFFFFF", outline="#D0D0D0", width=2
            )

        draw_pencil(h * 30, self.r * 0.5, 8)
        draw_pencil(m * 6, self.r * 0.8, 6)
        
        sx, sy = self._angle_to_xy(s * 6, self.r * 0.88)
        stx, sty = self._angle_to_xy(s * 6, self.r * 0.7)
        self.canvas.create_line(self.cx, self.cy, sx, sy, fill="#FFFFFF", width=2)
        
        rad = math.radians(s * 6 - 90)
        pw = 5
        self.canvas.create_polygon(
            stx - math.sin(rad)*pw, sty + math.cos(rad)*pw,
            sx, sy,
            stx + math.sin(rad)*pw, sty - math.cos(rad)*pw,
            fill="#FFFFFF"
        )


class TankFace(BaseWatchFace):
    """Cartier Tank Strategy (Rectangular)."""
    
    def __init__(self, canvas: tk.Canvas, cx: float, cy: float, r: float):
        super().__init__(canvas, cx, cy, r)
        self.rect_w = r * 0.55
        self.rect_h = r * 0.85

    def draw_straps(self, cfg: Dict[str, Any]) -> None:
        color = cfg.get("strap_color", "#1A1A1A")
        y_case = self.rect_h * 1.15
        s_len = self.r * 0.8  # Reduced so it looks like a strap, not a column
        
        self.canvas.create_rectangle(
            self.cx - self.rect_w * 0.85, self.cy - y_case - s_len, 
            self.cx + self.rect_w * 0.85, self.cy - y_case, 
            fill=color, outline="#111111", width=2
        )
        self.canvas.create_rectangle(
            self.cx - self.rect_w * 0.85, self.cy + y_case, 
            self.cx + self.rect_w * 0.85, self.cy + y_case + s_len, 
            fill=color, outline="#111111", width=2
        )
        
    def draw_case_and_dial(self, cfg: Dict[str, Any]) -> None:
        self.canvas.create_rectangle(
            self.cx - self.rect_w * 1.2, self.cy - self.rect_h * 1.2,
            self.cx + self.rect_w * 1.2, self.cy + self.rect_h * 1.2,
            fill="#E0E0E0", outline="#A0A0A0", width=4
        )
        
        self.canvas.create_rectangle(self.cx - self.rect_w * 1.2, self.cy - self.rect_h * 1.2, self.cx - self.rect_w, self.cy + self.rect_h * 1.2, fill="#D0D0D0", outline="")
        self.canvas.create_rectangle(self.cx + self.rect_w, self.cy - self.rect_h * 1.2, self.cx + self.rect_w * 1.2, self.cy + self.rect_h * 1.2, fill="#D0D0D0", outline="")
        
        self.canvas.create_rectangle(self.cx + self.rect_w * 1.2, self.cy - 8, self.cx + self.rect_w * 1.3, self.cy + 8, fill="#C0C0C0", outline="#A0A0A0")
        self.canvas.create_oval(self.cx + self.rect_w * 1.3 - 3, self.cy - 6, self.cx + self.rect_w * 1.3 + 5, self.cy + 6, fill="#00008B", outline="")
        
        self.canvas.create_rectangle(
            self.cx - self.rect_w, self.cy - self.rect_h,
            self.cx + self.rect_w, self.cy + self.rect_h,
            fill=cfg["dial_bg"], outline="#111111"
        )
        
        ir_w, ir_h = self.rect_w * 0.6, self.rect_h * 0.6
        self.canvas.create_rectangle(self.cx - ir_w, self.cy - ir_h, self.cx + ir_w, self.cy + ir_h, outline="#111111", width=3)
        self.canvas.create_rectangle(self.cx - ir_w + 5, self.cy - ir_h + 5, self.cx + ir_w - 5, self.cy + ir_h - 5, outline="#111111", width=1)
        
        for i in range(0, 60, 5):
            angle = i * 6
            # Distribute ticks along the rectangular chemin de fer
            pass # Keep it clean and elegant
        
        self.canvas.create_text(self.cx, self.cy - self.rect_h * 0.4, text="CARTIER", fill="#111111", font=("Garamond", 14, "bold"))
        self.canvas.create_text(self.cx, self.cy + self.rect_h * 0.9, text="SWISS MADE", fill="#111111", font=("Helvetica", 6))

    def draw_markers(self, cfg: Dict[str, Any]) -> None:
        roman_map = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"}
        for hour in range(1, 13):
            angle = hour * 30
            rad = math.radians(angle - 90)
            x = self.cx + self.rect_w * 0.85 * math.cos(rad)
            y = self.cy + self.rect_h * 0.85 * math.sin(rad)
            y = self.cy + (y - self.cy) * 1.05
            
            rot = -angle
            if 3 < hour < 9:
                rot += 180
            self.canvas.create_text(x, y, text=roman_map[hour], fill="#111111", font=("Garamond", 18, "bold"), angle=rot)

    def draw_hands(self, state: Dict[str, Any], cfg: Dict[str, Any], frac_sec: float) -> None:
        s = state["seconds"] + frac_sec if state["direction"] == "Forward" else state["seconds"] - frac_sec
        m = state["minutes"] + s / 60
        h = (state["hours"] % 12) + m / 60

        def draw_blued_sword(angle, length, width):
            rad = math.radians(angle - 90)
            cos_a, sin_a = math.cos(rad), math.sin(rad)
            px, py = -sin_a * width/2, cos_a * width/2
            mx, my = self.cx + length * 0.8 * cos_a, self.cy + length * 0.8 * sin_a
            dx, dy = length * cos_a, length * sin_a
            self.canvas.create_polygon(
                self.cx+px*0.5, self.cy+py*0.5, mx+px*1.5, my+py*1.5,
                self.cx+dx, self.cy+dy, mx-px*1.5, my-py*1.5, self.cx-px*0.5, self.cy-py*0.5,
                fill="#00008B", outline="#000044"
            )

        draw_blued_sword(h * 30, self.rect_w * 0.65, 8)
        draw_blued_sword(m * 6, self.rect_h * 0.75, 6)
        
        # Second hand (thin blue needle)
        rad_s = math.radians(s * 6 - 90)
        sx = self.cx + self.rect_h * 0.85 * math.cos(rad_s)
        sy = self.cy + self.rect_h * 0.85 * math.sin(rad_s)
        self.canvas.create_line(self.cx, self.cy, sx, sy, fill="#00008B", width=2)
        # Counterbalance
        bx = self.cx - self.rect_h * 0.15 * math.cos(rad_s)
        by = self.cy - self.rect_h * 0.15 * math.sin(rad_s)
        self.canvas.create_line(self.cx, self.cy, bx, by, fill="#00008B", width=2)
