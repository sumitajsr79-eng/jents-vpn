"""
Jents Quantum Icon Studio & App Icon Designer (v1.0)
====================================================
Interactive visual studio to design, customize, preview in multi-resolution,
and export professional Windows .ico (16x16 to 256x256) and .png icons for all applications.
"""

import sys
import os
import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from PIL import Image, ImageDraw, ImageFont, ImageTk

# ── Cyberpunk Palette ────────────────────────────────────────────────────
C_BG          = "#020617"
C_PANEL       = "#070d1e"
C_CARD        = "#0a1329"
C_CARD_HOVER  = "#0f1c3d"
C_BORDER      = "#15254d"
C_CYAN        = "#00f0ff"
C_GREEN       = "#00ff9d"
C_AMBER       = "#ffb703"
C_RED         = "#ff0055"
C_PURPLE      = "#b026ff"
C_BLUE        = "#3b82f6"
C_TEXT_BRIGHT = "#ffffff"
C_TEXT_MUTED  = "#64748b"
C_TEXT_CYAN   = "#67e8f9"

# Preset Themes
PRESET_THEMES = [
    {"name": "Cyber Cyan", "c1": (0, 240, 255), "c2": (10, 25, 60), "outline": (0, 240, 255)},
    {"name": "Neon Emerald", "c1": (0, 255, 157), "c2": (5, 40, 30), "outline": (0, 255, 157)},
    {"name": "Hyper Violet", "c1": (176, 38, 255), "c2": (35, 10, 55), "outline": (176, 38, 255)},
    {"name": "Sunset Crimson", "c1": (255, 0, 85), "c2": (50, 10, 25), "outline": (255, 0, 85)},
    {"name": "Solar Gold", "c1": (255, 183, 3), "c2": (45, 30, 5), "outline": (255, 183, 3)},
    {"name": "Stealth Carbon", "c1": (148, 163, 184), "c2": (15, 23, 42), "outline": (51, 65, 85)},
]

# Preset Glyphs
GLYPHS = [
    ("⚡ Lightning Bolt", "lightning"),
    ("🛡️ Quantum Shield", "shield"),
    ("🔒 Neon Padlock", "padlock"),
    ("🌐 Cyber Globe", "globe"),
    ("🚀 Rocket Speed", "rocket"),
    ("👁️ Sentinel Eye", "eye"),
    ("⚛️ Quantum Orbit", "atom"),
    ("💎 Cyber Gem", "gem"),
    ("⚙️ Mech Gear", "gear"),
    ("🎮 Cyber Gamepad", "gamepad"),
    ("🔍 Security Lens", "search"),
    ("🧹 Cleaner Wand", "broom"),
    ("🔤 Custom Monogram", "text")
]

class IconDesignerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JENTS // QUANTUM ICON STUDIO")
        self.root.geometry("1100x740")
        self.root.minsize(980, 640)
        self.root.configure(bg=C_BG)

        # Center on screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(10, (sw - 1100) // 2)
        y = max(10, (sh - 740) // 2 - 20)
        self.root.geometry(f"1100x740+{x}+{y}")

        # State variables
        self.var_shape = tk.StringVar(value="squircle")
        self.var_glyph = tk.StringVar(value="lightning")
        self.var_theme = tk.StringVar(value="Cyber Cyan")
        self.var_monogram = tk.StringVar(value="J")
        self.var_badge = tk.StringVar(value="PRO")
        self.var_glow = tk.BooleanVar(value=True)
        self.var_border_width = tk.IntVar(value=6)
        self.var_glyph_scale = tk.DoubleVar(value=1.0)
        
        self.custom_c1 = (0, 240, 255)
        self.custom_c2 = (10, 25, 60)

        self.current_pil_image = None
        self.tk_canvas_img = None
        self.preview_tk_images = {}

        self._build_ui()
        self.render_and_update()

    def _build_ui(self):
        # ── Header ───────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=C_BG)
        header.pack(fill=tk.X, padx=20, pady=(14, 6))

        title_box = tk.Frame(header, bg=C_BG)
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box, text="🎨 QUANTUM ICON STUDIO",
            font=("Segoe UI", 16, "bold"),
            fg=C_CYAN, bg=C_BG
        ).pack(anchor="w")

        tk.Label(
            title_box, text="// MULTI-RESOLUTION WINDOWS .ICO & PNG DESIGNER FOR ALL APPS",
            font=("Consolas", 8, "bold"),
            fg=C_GREEN, bg=C_BG
        ).pack(anchor="w")

        # ── Main 3-Column Layout ─────────────────────────────────────────────
        main_grid = tk.Frame(self.root, bg=C_BG)
        main_grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=(4, 10))

        # LEFT: Control Panel (320px)
        ctrl_card = tk.Frame(main_grid, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1, width=330)
        ctrl_card.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        ctrl_card.pack_propagate(False)

        # Scrollable Control Area
        c_canvas = tk.Canvas(ctrl_card, bg=C_CARD, highlightthickness=0)
        c_scroll = ttk.Scrollbar(ctrl_card, orient="vertical", command=c_canvas.yview)
        c_frame = tk.Frame(c_canvas, bg=C_CARD)

        c_frame.bind("<Configure>", lambda e: c_canvas.configure(scrollregion=c_canvas.bbox("all")))
        c_canvas.create_window((0, 0), window=c_frame, anchor="nw", width=310)
        c_canvas.configure(yscrollcommand=c_scroll.set)

        c_canvas.pack(side="left", fill="both", expand=True)
        c_scroll.pack(side="right", fill="y")

        self._build_controls(c_frame)

        # CENTER: Master 256x256 Canvas Preview (400px)
        center_card = tk.Frame(main_grid, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        center_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(center_card, text="256 × 256 MASTER CANVAS", font=("Consolas", 9, "bold"), fg=C_TEXT_CYAN, bg=C_CARD).pack(pady=(12, 6))

        # Checkered background canvas
        self.canvas_master = tk.Canvas(center_card, width=256, height=256, bg="#050914", highlightbackground=C_BORDER, highlightthickness=2)
        self.canvas_master.pack(pady=10)

        # Quick Preset Buttons
        tk.Label(center_card, text="ONE-CLICK APP TEMPLATES", font=("Consolas", 8, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(pady=(12, 4))
        
        tpl_box = tk.Frame(center_card, bg=C_CARD)
        tpl_box.pack(fill=tk.X, padx=14)

        presets = [
            ("⚡ Quantum VPN", "squircle", "Cyber Cyan", "lightning", "10G"),
            ("🛡️ Sentinel Shield", "shield", "Neon Emerald", "shield", "PRO"),
            ("🚀 Turbo DNS", "circle", "Solar Gold", "rocket", "DNS"),
            ("🔒 Cyber Lock", "squircle", "Hyper Violet", "padlock", "AI"),
            ("🎮 Game Booster", "hexagon", "Sunset Crimson", "gamepad", "MAX"),
            ("👁️ Security Eye", "circle", "Cyber Cyan", "eye", "SEC")
        ]

        for i, (name, shp, thm, gly, bdg) in enumerate(presets):
            row = i // 2
            col = i % 2
            b = tk.Button(
                tpl_box, text=name,
                font=("Segoe UI", 8, "bold"),
                fg=C_TEXT_BRIGHT, bg=C_PANEL,
                activebackground=C_CYAN, activeforeground=C_BG,
                relief=tk.FLAT, padx=6, pady=4, cursor="hand2",
                command=lambda s=shp, t=thm, g=gly, bg=bdg: self._apply_template(s, t, g, bg)
            )
            b.grid(row=row, column=col, sticky="ew", padx=3, pady=2)
        tpl_box.columnconfigure(0, weight=1)
        tpl_box.columnconfigure(1, weight=1)

        # RIGHT: Multi-Resolution Windows Previews (280px)
        preview_card = tk.Frame(main_grid, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1, width=280)
        preview_card.pack(side=tk.RIGHT, fill=tk.Y)
        preview_card.pack_propagate(False)

        tk.Label(preview_card, text="WINDOWS ICON SIZES", font=("Consolas", 9, "bold"), fg=C_TEXT_GREEN, bg=C_CARD).pack(pady=(12, 8))

        self.preview_canvas_box = tk.Frame(preview_card, bg=C_CARD)
        self.preview_canvas_box.pack(fill=tk.BOTH, expand=True, padx=14)

        self._build_preview_sizes(self.preview_canvas_box)

        # ── Bottom Action Bar ────────────────────────────────────────────────
        bot_bar = tk.Frame(self.root, bg=C_BG)
        bot_bar.pack(fill=tk.X, padx=20, pady=(0, 14))

        tk.Label(
            bot_bar, text="Outputs true multi-layer Windows .ico with 16x16 to 256x256 embedded bitmaps",
            font=("Consolas", 8), fg=C_TEXT_MUTED, bg=C_BG
        ).pack(side=tk.LEFT)

        btn_apply_app = tk.Button(
            bot_bar, text="⚡ SAVE AS APP ICON (icons/jents_icon.ico)",
            font=("Segoe UI", 9, "bold"),
            fg=C_BG, bg=C_GREEN,
            activebackground=C_CYAN, activeforeground=C_BG,
            relief=tk.FLAT, padx=12, pady=7, cursor="hand2",
            command=self._save_to_app_icons
        )
        btn_apply_app.pack(side=tk.RIGHT, padx=(6, 0))

        btn_export_png = tk.Button(
            bot_bar, text="🖼️ EXPORT .PNG",
            font=("Segoe UI", 9, "bold"),
            fg=C_CYAN, bg=C_PANEL,
            activebackground=C_CYAN, activeforeground=C_BG,
            relief=tk.FLAT, padx=12, pady=7, cursor="hand2",
            command=self._export_png
        )
        btn_export_png.pack(side=tk.RIGHT, padx=6)

        btn_export_ico = tk.Button(
            bot_bar, text="💾 EXPORT .ICO",
            font=("Segoe UI", 9, "bold"),
            fg=C_TEXT_BRIGHT, bg=C_BLUE,
            activebackground=C_GREEN, activeforeground=C_BG,
            relief=tk.FLAT, padx=12, pady=7, cursor="hand2",
            command=self._export_ico
        )
        btn_export_ico.pack(side=tk.RIGHT, padx=6)

    def _build_controls(self, parent):
        pad_x = 12

        # 1. Shape Selector
        tk.Label(parent, text="BACKGROUND SHAPE", font=("Consolas", 8, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w", padx=pad_x, pady=(10, 2))
        shapes = [
            ("Squircle (Modern)", "squircle"),
            ("Hexagon Shield", "hexagon"),
            ("Circular Reactor", "circle"),
            ("Diamond Gem", "diamond"),
            ("Hologram Shield", "shield"),
            ("Transparent Canvas", "transparent")
        ]
        for name, val in shapes:
            r = tk.Radiobutton(
                parent, text=name, value=val, variable=self.var_shape,
                font=("Segoe UI", 8), fg=C_TEXT_BRIGHT, bg=C_CARD,
                selectcolor=C_PANEL, activebackground=C_CARD, activeforeground=C_CYAN,
                command=self.render_and_update
            )
            r.pack(anchor="w", padx=pad_x+4)

        # 2. Color Theme Palette
        tk.Label(parent, text="COLOR PALETTE", font=("Consolas", 8, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w", padx=pad_x, pady=(10, 2))
        combo_theme = ttk.Combobox(parent, textvariable=self.var_theme, values=[t["name"] for t in PRESET_THEMES], state="readonly", font=("Segoe UI", 8))
        combo_theme.pack(fill=tk.X, padx=pad_x, pady=(0, 4))
        combo_theme.bind("<<ComboboxSelected>>", lambda e: self._on_theme_selected())

        # 3. Glyph / Symbol Selector
        tk.Label(parent, text="CORE SYMBOL / GLYPH", font=("Consolas", 8, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w", padx=pad_x, pady=(10, 2))
        combo_glyph = ttk.Combobox(parent, textvariable=self.var_glyph, values=[g[0] for g in GLYPHS], state="readonly", font=("Segoe UI", 8))
        combo_glyph.current(0)
        combo_glyph.pack(fill=tk.X, padx=pad_x, pady=(0, 4))
        combo_glyph.bind("<<ComboboxSelected>>", lambda e: self._on_glyph_selected(combo_glyph.get()))

        # Monogram input (if text glyph selected)
        self.monogram_frame = tk.Frame(parent, bg=C_CARD)
        self.monogram_frame.pack(fill=tk.X, padx=pad_x, pady=(0, 4))
        tk.Label(self.monogram_frame, text="Custom Letters:", font=("Consolas", 7), fg=C_TEXT_MUTED, bg=C_CARD).pack(side=tk.LEFT)
        e_mono = tk.Entry(self.monogram_frame, textvariable=self.var_monogram, font=("Segoe UI", 8, "bold"), bg=C_PANEL, fg=C_CYAN, width=8, insertbackground=C_CYAN)
        e_mono.pack(side=tk.RIGHT)
        self.var_monogram.trace_add("write", lambda *args: self.render_and_update())

        # 4. Badge / Overlay
        tk.Label(parent, text="CORNER BADGE (OPTIONAL)", font=("Consolas", 8, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w", padx=pad_x, pady=(8, 2))
        e_badge = tk.Entry(parent, textvariable=self.var_badge, font=("Segoe UI", 8, "bold"), bg=C_PANEL, fg=C_RED, insertbackground=C_RED)
        e_badge.pack(fill=tk.X, padx=pad_x, pady=(0, 6))
        self.var_badge.trace_add("write", lambda *args: self.render_and_update())

        # 5. Sliders: Glow & Border
        tk.Label(parent, text="BORDER & GLOW EFFECTS", font=("Consolas", 8, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w", padx=pad_x, pady=(6, 2))
        
        chk_glow = tk.Checkbutton(
            parent, text="Outer Neon Bloom Glow",
            variable=self.var_glow, font=("Segoe UI", 8),
            fg=C_TEXT_BRIGHT, bg=C_CARD, selectcolor=C_PANEL,
            activebackground=C_CARD, activeforeground=C_CYAN,
            command=self.render_and_update
        )
        chk_glow.pack(anchor="w", padx=pad_x)

        tk.Label(parent, text="Border Width:", font=("Consolas", 7), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w", padx=pad_x, pady=(4, 0))
        s_border = tk.Scale(parent, from_=0, to=14, orient=tk.HORIZONTAL, variable=self.var_border_width, bg=C_CARD, fg=C_TEXT_MUTED, highlightthickness=0, command=lambda v: self.render_and_update())
        s_border.pack(fill=tk.X, padx=pad_x)

    def _build_preview_sizes(self, parent):
        # 128x128 Preview
        r1 = tk.Frame(parent, bg=C_CARD)
        r1.pack(fill=tk.X, pady=4)
        tk.Label(r1, text="128×128 (Large):", font=("Consolas", 7), fg=C_TEXT_MUTED, bg=C_CARD).pack(side=tk.LEFT)
        self.lbl_prev_128 = tk.Label(r1, bg=C_CARD)
        self.lbl_prev_128.pack(side=tk.RIGHT)

        # 64x64 Preview
        r2 = tk.Frame(parent, bg=C_CARD)
        r2.pack(fill=tk.X, pady=4)
        tk.Label(r2, text="64×64 (Folder):", font=("Consolas", 7), fg=C_TEXT_MUTED, bg=C_CARD).pack(side=tk.LEFT)
        self.lbl_prev_64 = tk.Label(r2, bg=C_CARD)
        self.lbl_prev_64.pack(side=tk.RIGHT)

        # 32x32 Preview
        r3 = tk.Frame(parent, bg=C_CARD)
        r3.pack(fill=tk.X, pady=4)
        tk.Label(r3, text="32×32 (Desktop):", font=("Consolas", 7), fg=C_TEXT_MUTED, bg=C_CARD).pack(side=tk.LEFT)
        self.lbl_prev_32 = tk.Label(r3, bg=C_CARD)
        self.lbl_prev_32.pack(side=tk.RIGHT)

        # 16x16 Preview
        r4 = tk.Frame(parent, bg=C_CARD)
        r4.pack(fill=tk.X, pady=4)
        tk.Label(r4, text="16×16 (Taskbar):", font=("Consolas", 7), fg=C_TEXT_MUTED, bg=C_CARD).pack(side=tk.LEFT)
        self.lbl_prev_16 = tk.Label(r4, bg=C_CARD)
        self.lbl_prev_16.pack(side=tk.RIGHT)

    def _on_theme_selected(self):
        tname = self.var_theme.get()
        for t in PRESET_THEMES:
            if t["name"] == tname:
                self.custom_c1 = t["c1"]
                self.custom_c2 = t["c2"]
                break
        self.render_and_update()

    def _on_glyph_selected(self, full_name):
        for name, key in GLYPHS:
            if name == full_name:
                self.var_glyph.set(key)
                break
        self.render_and_update()

    def _apply_template(self, shp, thm, gly, bdg):
        self.var_shape.set(shp)
        self.var_theme.set(thm)
        self._on_theme_selected()
        self.var_glyph.set(gly)
        self.var_badge.set(bdg)
        self.render_and_update()

    def render_and_update(self):
        """Renders the 256x256 master icon and pushes to all UI previews."""
        img = self._generate_icon_image()
        self.current_pil_image = img

        # 1. Update Master Canvas (256x256)
        self.tk_canvas_img = ImageTk.PhotoImage(img)
        self.canvas_master.delete("all")
        self.canvas_master.create_image(128, 128, image=self.tk_canvas_img)

        # 2. Update multi-res previews
        im128 = img.resize((72, 72), Image.Resampling.LANCZOS)
        self.preview_tk_images["128"] = ImageTk.PhotoImage(im128)
        self.lbl_prev_128.config(image=self.preview_tk_images["128"])

        im64 = img.resize((48, 48), Image.Resampling.LANCZOS)
        self.preview_tk_images["64"] = ImageTk.PhotoImage(im64)
        self.lbl_prev_64.config(image=self.preview_tk_images["64"])

        im32 = img.resize((32, 32), Image.Resampling.LANCZOS)
        self.preview_tk_images["32"] = ImageTk.PhotoImage(im32)
        self.lbl_prev_32.config(image=self.preview_tk_images["32"])

        im16 = img.resize((16, 16), Image.Resampling.LANCZOS)
        self.preview_tk_images["16"] = ImageTk.PhotoImage(im16)
        self.lbl_prev_16.config(image=self.preview_tk_images["16"])

    def _generate_icon_image(self) -> Image.Image:
        """Draws full 256x256 antialiased icon with glows, shapes, and badges."""
        img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        shape = self.var_shape.get()
        glyph = self.var_glyph.get()
        c1 = self.custom_c1
        c2 = self.custom_c2
        b_width = self.var_border_width.get()
        glow = self.var_glow.get()
        badge = self.var_badge.get().strip().upper()

        # ── 1. Background Shape & Glow ───────────────────────────────────────
        if shape == "squircle":
            if glow:
                for i in range(14, 0, -2):
                    alpha = int(45 * (1 - i/14))
                    draw.rounded_rectangle([16-i, 16-i, 240+i, 240+i], radius=50+i, fill=(*c1, alpha))
            draw.rounded_rectangle([16, 16, 240, 240], radius=50, fill=(*c2, 255), outline=(*c1, 255) if b_width else None, width=b_width)

        elif shape == "circle":
            if glow:
                for i in range(14, 0, -2):
                    alpha = int(45 * (1 - i/14))
                    draw.ellipse([16-i, 16-i, 240+i, 240+i], fill=(*c1, alpha))
            draw.ellipse([16, 16, 240, 240], fill=(*c2, 255), outline=(*c1, 255) if b_width else None, width=b_width)

        elif shape == "shield":
            pts = [(128, 16), (235, 45), (215, 185), (128, 245), (41, 185), (21, 45)]
            if glow:
                for i in range(10, 0, -2):
                    alpha = int(35 * (1 - i/10))
                    draw.polygon([(x, y) for x, y in pts], fill=(*c1, alpha))
            draw.polygon(pts, fill=(*c2, 255), outline=(*c1, 255) if b_width else None)

        elif shape == "hexagon":
            pts = [(128, 16), (235, 75), (235, 181), (128, 240), (21, 181), (21, 75)]
            if glow:
                for i in range(10, 0, -2):
                    alpha = int(35 * (1 - i/10))
                    draw.polygon([(x, y) for x, y in pts], fill=(*c1, alpha))
            draw.polygon(pts, fill=(*c2, 255), outline=(*c1, 255) if b_width else None)

        elif shape == "diamond":
            pts = [(128, 16), (240, 128), (128, 240), (16, 128)]
            if glow:
                for i in range(10, 0, -2):
                    alpha = int(35 * (1 - i/10))
                    draw.polygon([(x, y) for x, y in pts], fill=(*c1, alpha))
            draw.polygon(pts, fill=(*c2, 255), outline=(*c1, 255) if b_width else None)

        # ── 2. Render Glyph / Vector Graphic ──────────────────────────────────
        if glyph == "lightning":
            draw.polygon([(142, 38), (78, 138), (130, 138), (114, 226), (188, 118), (136, 118)], fill=(*c1, 255))
        
        elif glyph == "shield":
            draw.polygon([(128, 55), (195, 75), (180, 165), (128, 210), (76, 165), (61, 75)], fill=(*c1, 255))
            draw.polygon([(128, 75), (175, 90), (164, 155), (128, 190), (92, 155), (81, 90)], fill=(*c2, 255))
            draw.polygon([(128, 95), (150, 105), (145, 145), (128, 165), (111, 145), (106, 105)], fill=(*c1, 255))

        elif glyph == "padlock":
            draw.rounded_rectangle([78, 110, 178, 206], radius=16, fill=(*c1, 255))
            draw.arc([92, 58, 164, 135], start=180, end=0, fill=(*c1, 255), width=16)
            draw.ellipse([118, 142, 138, 162], fill=(*c2, 255))
            draw.polygon([(124, 156), (132, 156), (134, 180), (122, 180)], fill=(*c2, 255))

        elif glyph == "globe":
            draw.ellipse([64, 64, 192, 192], outline=(*c1, 255), width=6)
            draw.ellipse([92, 64, 164, 192], outline=(*c1, 255), width=4)
            draw.line([(64, 128), (192, 128)], fill=(*c1, 255), width=5)
            draw.line([(76, 96), (180, 96)], fill=(*c1, 255), width=4)
            draw.line([(76, 160), (180, 160)], fill=(*c1, 255), width=4)

        elif glyph == "rocket":
            # Body
            draw.polygon([(128, 45), (160, 110), (160, 175), (96, 175), (96, 110)], fill=(*c1, 255))
            # Fins
            draw.polygon([(96, 140), (60, 185), (96, 180)], fill=(*c1, 255))
            draw.polygon([(160, 140), (196, 185), (160, 180)], fill=(*c1, 255))
            # Porthole
            draw.ellipse([114, 90, 142, 118], fill=(*c2, 255), outline=(*c1, 255), width=3)
            # Flame
            draw.polygon([(112, 178), (128, 222), (144, 178)], fill=(255, 0, 85, 255))

        elif glyph == "eye":
            draw.ellipse([50, 90, 206, 166], outline=(*c1, 255), width=6)
            draw.ellipse([100, 100, 156, 156], fill=(*c1, 255))
            draw.ellipse([116, 116, 140, 140], fill=(*c2, 255))

        elif glyph == "atom":
            draw.ellipse([112, 112, 144, 144], fill=(*c1, 255))
            draw.arc([55, 95, 201, 161], start=0, end=360, fill=(*c1, 255), width=5)
            draw.arc([95, 55, 161, 201], start=0, end=360, fill=(*c1, 255), width=5)

        elif glyph == "gem":
            pts = [(128, 50), (200, 100), (160, 205), (96, 205), (56, 100)]
            draw.polygon(pts, fill=(*c1, 255), outline=(255, 255, 255, 255), width=3)
            draw.line([(56, 100), (200, 100)], fill=(*c2, 255), width=4)
            draw.line([(128, 50), (128, 205)], fill=(*c2, 255), width=3)

        elif glyph == "gear":
            draw.ellipse([80, 80, 176, 176], fill=(*c1, 255))
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                cx = 128 + int(56 * math.cos(rad))
                cy = 128 + int(56 * math.sin(rad))
                draw.rectangle([cx-10, cy-10, cx+10, cy+10], fill=(*c1, 255))
            draw.ellipse([106, 106, 150, 150], fill=(*c2, 255))

        elif glyph == "gamepad":
            draw.rounded_rectangle([60, 95, 196, 165], radius=24, fill=(*c1, 255))
            # D-pad
            draw.rectangle([80, 120, 108, 140], fill=(*c2, 255))
            draw.rectangle([89, 111, 99, 149], fill=(*c2, 255))
            # Buttons
            draw.ellipse([150, 115, 162, 127], fill=(*c2, 255))
            draw.ellipse([168, 130, 180, 142], fill=(*c2, 255))

        elif glyph == "search":
            draw.ellipse([70, 70, 155, 155], outline=(*c1, 255), width=10)
            draw.line([(140, 140), (195, 195)], fill=(*c1, 255), width=14)

        elif glyph == "broom":
            draw.line([(85, 185), (175, 75)], fill=(*c1, 255), width=8)
            # Sparkles
            draw.polygon([(185, 60), (195, 60), (195, 70), (185, 70)], fill=(*c1, 255))
            draw.polygon([(160, 45), (168, 45), (168, 53), (160, 53)], fill=(*c1, 255))

        elif glyph == "text":
            text = self.var_monogram.get().strip() or "J"
            # Draw bold monogram centered
            try:
                font = ImageFont.truetype("arialbd.ttf", 100)
            except Exception:
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = (256 - tw) // 2
            ty = (256 - th) // 2 - 10
            draw.text((tx, ty), text, fill=(*c1, 255), font=font)

        # ── 3. Corner Badge Overlay ──────────────────────────────────────────
        if badge:
            badge_len = max(38, len(badge) * 14 + 18)
            bx1 = 246 - badge_len
            bx2 = 246
            by1 = 16
            by2 = 48
            draw.rounded_rectangle([bx1, by1, bx2, by2], radius=8, fill=(255, 0, 85, 255))
            
            try:
                bfont = ImageFont.truetype("arialbd.ttf", 14)
            except Exception:
                bfont = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), badge, font=bfont)
            bw = bbox[2] - bbox[0]
            bh = bbox[3] - bbox[1]
            bx = bx1 + (badge_len - bw) // 2
            by = by1 + (32 - bh) // 2 - 2
            draw.text((bx, by), badge, fill=(255, 255, 255, 255), font=bfont)

        return img

    def _export_ico(self):
        if not self.current_pil_image:
            return
        path = filedialog.asksaveasfilename(defaultextension=".ico", filetypes=[("Windows Icon", "*.ico")])
        if path:
            try:
                self.current_pil_image.save(
                    path, format="ICO",
                    sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                )
                messagebox.showinfo("Export Successful! 💾", f"Icon successfully saved with all 6 Windows resolutions:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export .ico: {e}")

    def _export_png(self):
        if not self.current_pil_image:
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if path:
            try:
                self.current_pil_image.save(path, format="PNG")
                messagebox.showinfo("Export Successful! 🖼️", f"High-Resolution PNG saved:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export .png: {e}")

    def _save_to_app_icons(self):
        """Saves directly to jents_vpn/icons/jents_icon.ico."""
        if not self.current_pil_image:
            return
        target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
        os.makedirs(target_dir, exist_ok=True)
        ico_path = os.path.join(target_dir, "jents_icon.ico")

        try:
            self.current_pil_image.save(
                ico_path, format="ICO",
                sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            )
            messagebox.showinfo(
                "App Icon Updated! ⚡",
                f"Successfully updated master application icon at:\n{ico_path}\n\nAll future builds will now use this custom icon!"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not update app icon: {e}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = IconDesignerApp()
    app.run()
