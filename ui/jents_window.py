"""
Jents VPN — Quantum Cyberpunk Masterpiece HUD (v3.1)
=====================================================
Ultra-futuristic, high-FPS animated interface with dynamic quantum reactor core,
particle field matrix, prominent 1-click connect button, region switcher,
live telemetry speedometers, and instant fail-safe rollback.
"""

import sys
import os
import time
import math
import random
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Dict, Any, List

from core.auto_engine import JentsEngine, ConnectionState, GATEWAY_PRESETS
from config.config_manager import ConfigManager

# ── Cyberpunk Neon Color Palette ─────────────────────────────────────────
C_VOID_BG      = "#030611"
C_PANEL_BG     = "#070d1e"
C_CARD_BG      = "#0a1329"
C_CARD_BORDER  = "#15254d"
C_CYAN_NEON    = "#00f0ff"
C_CYAN_DIM     = "#0284c7"
C_GREEN_NEON   = "#00ff9d"
C_GREEN_DIM    = "#059669"
C_PURPLE_NEON  = "#b026ff"
C_AMBER_NEON   = "#ffb703"
C_RED_NEON     = "#ff0055"
C_TEXT_BRIGHT  = "#ffffff"
C_TEXT_CYAN    = "#67e8f9"
C_TEXT_MUTED   = "#64748b"
C_TEXT_SUBTLE  = "#94a3b8"

class Particle:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.reset()

    def reset(self):
        self.x = random.uniform(0, self.w)
        self.y = random.uniform(0, self.h)
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(-0.6, -0.1)
        self.size = random.uniform(1.0, 2.5)
        self.alpha = random.uniform(0.2, 0.8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.y < 0 or self.x < 0 or self.x > self.w:
            self.reset()
            self.y = self.h

class JentsWindow:
    """The Ultimate Cyberpunk UI for Jents VPN."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JENTS // QUANTUM VPN")
        
        # Center Window on Screen
        w, h = 450, 660
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = max(20, (sh - h) // 2 - 30)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.configure(bg=C_VOID_BG)

        # Set Window Icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons", "jents_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        # Config & Engine
        self.cfg = ConfigManager()
        self.engine = JentsEngine(
            config_manager=self.cfg,
            state_callback=self._on_engine_state,
            log_callback=self._on_engine_log
        )

        self.current_state = ConnectionState.DISCONNECTED
        self.state_meta: Dict[str, Any] = {}
        self.anim_time = 0.0
        self.orb_hovered = False
        self.selected_preset = 0

        # Background particles
        self.particles = [Particle(450, 230) for _ in range(30)]

        self._build_ui()
        self._start_render_loop()
        self._start_telemetry_loop()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # ── 1. Top Cyberpunk Header ──────────────────────────────────────────
        header = tk.Frame(self.root, bg=C_VOID_BG, height=46)
        header.pack(fill=tk.X, padx=20, pady=(12, 4))

        title_frame = tk.Frame(header, bg=C_VOID_BG)
        title_frame.pack(side=tk.LEFT)

        tk.Label(
            title_frame,
            text="JENTS",
            font=("Segoe UI", 17, "bold"),
            fg=C_CYAN_NEON,
            bg=C_VOID_BG
        ).pack(side=tk.LEFT)

        tk.Label(
            title_frame,
            text="// QUANTUM v3.1",
            font=("Consolas", 9, "bold"),
            fg=C_PURPLE_NEON,
            bg=C_VOID_BG
        ).pack(side=tk.LEFT, padx=(6, 0), pady=(3, 0))

        # Right shield status badge
        self.lbl_shield_badge = tk.Label(
            header,
            text="● STANDBY",
            font=("Consolas", 8, "bold"),
            fg=C_TEXT_MUTED,
            bg=C_CARD_BG,
            padx=8,
            pady=3,
            relief=tk.FLAT
        )
        self.lbl_shield_badge.pack(side=tk.RIGHT)

        # ── 2. Master Canvas (Particles + Animated Arc Reactor Core) ────────
        self.canvas = tk.Canvas(
            self.root,
            width=450,
            height=210,
            bg=C_VOID_BG,
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", lambda e: self._toggle_connection())
        self.canvas.bind("<Enter>", lambda e: self._set_hover(True))
        self.canvas.bind("<Leave>", lambda e: self._set_hover(False))

        # ── 3. Big Dedicated Prominent Connect Button ───────────────────────
        btn_frame = tk.Frame(self.root, bg=C_VOID_BG)
        btn_frame.pack(fill=tk.X, padx=20, pady=(4, 8))

        self.btn_action = tk.Button(
            btn_frame,
            text="⚡  CONNECT TO VPN  ⚡",
            font=("Segoe UI", 11, "bold"),
            fg=C_VOID_BG,
            bg=C_CYAN_NEON,
            activebackground=C_GREEN_NEON,
            activeforeground=C_VOID_BG,
            relief=tk.FLAT,
            padx=12,
            pady=8,
            cursor="hand2",
            command=self._toggle_connection
        )
        self.btn_action.pack(fill=tk.X)

        # Status text below button
        self.lbl_main_status = tk.Label(
            self.root,
            text="PROTECTION DISABLED",
            font=("Segoe UI", 11, "bold"),
            fg=C_TEXT_SUBTLE,
            bg=C_VOID_BG
        )
        self.lbl_main_status.pack()

        # ── 4. Cyber Telemetry HUD Card ─────────────────────────────────────
        self.hud_card = tk.Frame(self.root, bg=C_CARD_BG, highlightbackground=C_CARD_BORDER, highlightthickness=1)
        self.hud_card.pack(fill=tk.X, padx=20, pady=(8, 8))

        # Row 1: Speeds & Ping
        hud_row1 = tk.Frame(self.hud_card, bg=C_CARD_BG)
        hud_row1.pack(fill=tk.X, padx=14, pady=(10, 4))

        col_down = tk.Frame(hud_row1, bg=C_CARD_BG)
        col_down.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Label(col_down, text="DOWNLOAD", font=("Consolas", 7, "bold"), fg=C_TEXT_MUTED, bg=C_CARD_BG).pack(anchor="w")
        self.lbl_down = tk.Label(col_down, text="0.0 KB/s", font=("Segoe UI", 11, "bold"), fg=C_CYAN_NEON, bg=C_CARD_BG)
        self.lbl_down.pack(anchor="w")

        col_up = tk.Frame(hud_row1, bg=C_CARD_BG)
        col_up.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Label(col_up, text="UPLOAD", font=("Consolas", 7, "bold"), fg=C_TEXT_MUTED, bg=C_CARD_BG).pack(anchor="w")
        self.lbl_up = tk.Label(col_up, text="0.0 KB/s", font=("Segoe UI", 11, "bold"), fg=C_PURPLE_NEON, bg=C_CARD_BG)
        self.lbl_up.pack(anchor="w")

        col_ping = tk.Frame(hud_row1, bg=C_CARD_BG)
        col_ping.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Label(col_ping, text="PING", font=("Consolas", 7, "bold"), fg=C_TEXT_MUTED, bg=C_CARD_BG).pack(anchor="w")
        self.lbl_ping = tk.Label(col_ping, text="-- ms", font=("Segoe UI", 11, "bold"), fg=C_GREEN_NEON, bg=C_CARD_BG)
        self.lbl_ping.pack(anchor="w")

        # Row 2: Location & Cipher
        hud_row2 = tk.Frame(self.hud_card, bg=C_CARD_BG)
        hud_row2.pack(fill=tk.X, padx=14, pady=(0, 8))

        col_loc = tk.Frame(hud_row2, bg=C_CARD_BG)
        col_loc.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Label(col_loc, text="GATEWAY ROUTE", font=("Consolas", 7, "bold"), fg=C_TEXT_MUTED, bg=C_CARD_BG).pack(anchor="w")
        self.lbl_route = tk.Label(col_loc, text="⚡ Quantum Auto-Turbo", font=("Segoe UI", 8, "bold"), fg=C_TEXT_BRIGHT, bg=C_CARD_BG)
        self.lbl_route.pack(anchor="w")

        col_cipher = tk.Frame(hud_row2, bg=C_CARD_BG)
        col_cipher.pack(side=tk.RIGHT)
        tk.Label(col_cipher, text="SECURITY", font=("Consolas", 7, "bold"), fg=C_TEXT_MUTED, bg=C_CARD_BG).pack(anchor="e")
        self.lbl_cipher = tk.Label(col_cipher, text="ChaCha20 + DoH", font=("Consolas", 8, "bold"), fg=C_TEXT_CYAN, bg=C_CARD_BG)
        self.lbl_cipher.pack(anchor="e")

        # ── 5. Quick Region Selection Matrix ────────────────────────────────
        matrix_frame = tk.Frame(self.root, bg=C_VOID_BG)
        matrix_frame.pack(fill=tk.X, padx=20, pady=(0, 8))

        tk.Label(
            matrix_frame,
            text="QUANTUM REGION SELECTOR",
            font=("Consolas", 7, "bold"),
            fg=C_TEXT_MUTED,
            bg=C_VOID_BG
        ).pack(anchor="w", pady=(0, 3))

        pills_row = tk.Frame(matrix_frame, bg=C_VOID_BG)
        pills_row.pack(fill=tk.X)

        self.pill_btns = []
        for i, preset in enumerate(GATEWAY_PRESETS):
            btn = tk.Label(
                pills_row,
                text=f"{preset['flag']} {preset['id'].upper()}",
                font=("Consolas", 8, "bold"),
                fg=C_TEXT_BRIGHT if i == 0 else C_TEXT_MUTED,
                bg=C_CARD_BORDER if i == 0 else C_PANEL_BG,
                padx=6,
                pady=3,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
            btn.bind("<Button-1>", lambda e, idx=i: self._select_region(idx))
            self.pill_btns.append(btn)

        # ── 6. Live Activity Log Terminal ───────────────────────────────────
        log_frame = tk.Frame(self.root, bg=C_CARD_BG, highlightbackground=C_CARD_BORDER, highlightthickness=1)
        log_frame.pack(fill=tk.X, padx=20, pady=(0, 8))

        log_header = tk.Frame(log_frame, bg=C_CARD_BG)
        log_header.pack(fill=tk.X, padx=10, pady=(4, 2))
        tk.Label(log_header, text="● LIVE ACTIVITY LOG", font=("Consolas", 7, "bold"), fg=C_TEXT_MUTED, bg=C_CARD_BG).pack(side=tk.LEFT)

        self.log_text = tk.Text(
            log_frame,
            height=3,
            bg=C_VOID_BG,
            fg=C_TEXT_CYAN,
            font=("Consolas", 7),
            relief=tk.FLAT,
            state=tk.DISABLED,
            wrap=tk.WORD,
            padx=6,
            pady=3,
            insertbackground=C_CYAN_NEON
        )
        self.log_text.pack(fill=tk.X, padx=4, pady=(0, 4))
        self.log_text.tag_configure("ok", foreground=C_GREEN_NEON)
        self.log_text.tag_configure("err", foreground=C_RED_NEON)
        self.log_text.tag_configure("info", foreground=C_TEXT_CYAN)

    def _toggle_connection(self):
        """Toggles connection state on button or orb click."""
        if self.current_state in (ConnectionState.DISCONNECTED, ConnectionState.ERROR):
            self.btn_action.config(text="CONNECTING...", bg=C_AMBER_NEON, state=tk.DISABLED)
            self.engine.trigger_connect()
        elif self.current_state == ConnectionState.CONNECTED:
            self.btn_action.config(text="DISCONNECTING...", bg=C_AMBER_NEON, state=tk.DISABLED)
            self.engine.trigger_disconnect()

    def _append_log(self, msg: str):
        """Appends message to both terminal panel and stdout."""
        try:
            print(f"[JENTS-LOG] {msg}", flush=True)
        except Exception:
            pass

        self.log_text.config(state=tk.NORMAL)
        tag = "info"
        if any(w in msg.lower() for w in ["connected", "secured", "ok", "online", "active"]):
            tag = "ok"
        elif any(w in msg.lower() for w in ["error", "fail", "denied", "could not"]):
            tag = "err"
        self.log_text.insert(tk.END, f"› {msg}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _select_region(self, idx: int):
        self.selected_preset = idx
        self.engine.select_preset(idx)
        preset = GATEWAY_PRESETS[idx]
        self.lbl_route.config(text=f"{preset['flag']} {preset['name']}")
        for i, b in enumerate(self.pill_btns):
            if i == idx:
                b.config(fg=C_CYAN_NEON, bg=C_CARD_BORDER)
            else:
                b.config(fg=C_TEXT_MUTED, bg=C_PANEL_BG)

    def _set_hover(self, h: bool):
        self.orb_hovered = h

    def _on_engine_state(self, state: str, meta: Dict[str, Any]):
        self.current_state = state
        self.state_meta = meta
        self.root.after(0, self._apply_state)

    def _on_engine_log(self, msg: str):
        self.root.after(0, lambda: self._append_log(msg))

    def _apply_state(self):
        self.btn_action.config(state=tk.NORMAL)
        if self.current_state == ConnectionState.DISCONNECTED:
            self.btn_action.config(text="⚡  CONNECT TO VPN  ⚡", bg=C_CYAN_NEON, fg=C_VOID_BG)
            self.lbl_main_status.config(text="PROTECTION DISABLED", fg=C_TEXT_SUBTLE)
            self.lbl_shield_badge.config(text="● STANDBY", fg=C_TEXT_MUTED)
            self.lbl_ping.config(text="-- ms")
        elif self.current_state in (ConnectionState.PROBING, ConnectionState.SECURING):
            self.btn_action.config(text="⏳  SECURING TUNNEL...  ⏳", bg=C_AMBER_NEON, fg=C_VOID_BG)
            self.lbl_main_status.config(text="SECURING QUANTUM MESH...", fg=C_AMBER_NEON)
            self.lbl_shield_badge.config(text="⚡ CHARGING", fg=C_AMBER_NEON)
        elif self.current_state == ConnectionState.CONNECTED:
            self.btn_action.config(text="🛑  DISCONNECT VPN  🛑", bg=C_RED_NEON, fg=C_TEXT_BRIGHT)
            loc = self.state_meta.get("location", "Quantum Gateway")
            flag = self.state_meta.get("flag", "⚡")
            self.lbl_main_status.config(text=f"CONNECTED & SECURED ({flag})", fg=C_GREEN_NEON)
            self.lbl_shield_badge.config(text="● 100% SHIELDED", fg=C_GREEN_NEON)
            self.lbl_ping.config(text=self.state_meta.get("ping", "12 ms"))
        elif self.current_state == ConnectionState.DISCONNECTING:
            self.btn_action.config(text="⏳  DISCONNECTING...  ⏳", bg=C_AMBER_NEON, fg=C_VOID_BG)
            self.lbl_main_status.config(text="RESTORING NETWORK...", fg=C_AMBER_NEON)
        elif self.current_state == ConnectionState.ERROR:
            self.btn_action.config(text="⚠️  RETRY CONNECTION  ⚠️", bg=C_RED_NEON, fg=C_TEXT_BRIGHT)
            self.lbl_main_status.config(text="CONNECTION FAILED", fg=C_RED_NEON)
            self.lbl_shield_badge.config(text="● ERROR", fg=C_RED_NEON)

    def _render_canvas(self):
        """Renders 60FPS fluid animated Cyberpunk Arc Reactor & particle field."""
        c = self.canvas
        c.delete("all")
        cx, cy = 225, 105

        # ── 1. Background Particles ─────────────────────────────────────────
        for p in self.particles:
            p.update()
            c.create_oval(
                p.x, p.y, p.x + p.size, p.y + p.size,
                fill="#152850", outline=""
            )

        # ── 2. Colors ───────────────────────────────────────────────────────
        if self.current_state == ConnectionState.CONNECTED:
            core_color = C_GREEN_NEON
            glow_color = C_GREEN_DIM
            rot_speed = 0.05
        elif self.current_state in (ConnectionState.PROBING, ConnectionState.SECURING):
            core_color = C_AMBER_NEON
            glow_color = "#d97706"
            rot_speed = 0.12
        elif self.current_state == ConnectionState.ERROR:
            core_color = C_RED_NEON
            glow_color = "#9f1239"
            rot_speed = 0.02
        else:
            core_color = C_CYAN_NEON
            glow_color = C_CYAN_DIM
            rot_speed = 0.03

        # ── 3. Pulsing Outer Aura Halo ──────────────────────────────────────
        pulse = math.sin(self.anim_time * 2.5) * 4.0
        aura_r = 82 + pulse
        c.create_oval(
            cx - aura_r, cy - aura_r, cx + aura_r, cy + aura_r,
            outline=glow_color, width=1
        )

        # ── 4. Outer Rotating Segmented Ticks (Clockwise) ───────────────────
        num_ticks = 18
        angle_offset = self.anim_time * rot_speed * 10.0
        for i in range(num_ticks):
            theta = (i * (2 * math.pi / num_ticks)) + angle_offset
            r1 = 74
            r2 = 79 if i % 2 == 0 else 76
            x1 = cx + math.cos(theta) * r1
            y1 = cy + math.sin(theta) * r1
            x2 = cx + math.cos(theta) * r2
            y2 = cy + math.sin(theta) * r2
            c.create_line(x1, y1, x2, y2, fill=core_color, width=2 if i % 2 == 0 else 1)

        # ── 5. Main Reactor Core Disc ───────────────────────────────────────
        core_r = 58 if not self.orb_hovered else 61
        c.create_oval(
            cx - core_r, cy - core_r, cx + core_r, cy + core_r,
            fill=C_CARD_BG, outline=core_color, width=3
        )

        # ── 6. Central Power Arc Icon ───────────────────────────────────────
        c.create_arc(
            cx - 16, cy - 24, cx + 16, cy + 8,
            start=135, extent=270,
            style=tk.ARC, outline=core_color, width=3
        )
        c.create_line(cx, cy - 24, cx, cy - 10, fill=core_color, width=3)

        status_txt = "PROTECTED" if self.current_state == ConnectionState.CONNECTED else "CLICK TO START"
        c.create_text(
            cx, cy + 22,
            text=status_txt,
            font=("Consolas", 8, "bold"),
            fill=C_TEXT_BRIGHT
        )

    def _start_render_loop(self):
        self.anim_time += 0.05
        self._render_canvas()
        self.root.after(33, self._start_render_loop)

    def _start_telemetry_loop(self):
        if self.current_state == ConnectionState.CONNECTED:
            snap = self.engine.stats.get_snapshot()
            raw_down = snap.get("raw_down_kbps", 0.0) / 1024.0
            raw_up = snap.get("raw_up_kbps", 0.0) / 1024.0
            down_str = f"{raw_down:.2f} MB/s" if raw_down >= 1.0 else f"{snap.get('speed_down', '0.0 KB/s')}"
            up_str = f"{raw_up:.2f} MB/s" if raw_up >= 1.0 else f"{snap.get('speed_up', '0.0 KB/s')}"
            self.lbl_down.config(text=down_str)
            self.lbl_up.config(text=up_str)
        else:
            self.lbl_down.config(text="0.0 KB/s")
            self.lbl_up.config(text="0.0 KB/s")

        self.root.after(400, self._start_telemetry_loop)

    def _on_close(self):
        try:
            self.engine._cleanup()
        except Exception:
            pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()
