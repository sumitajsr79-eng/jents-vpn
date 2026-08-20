"""
Jents Quantum Icon Studio & Generative AI Designer (v2.0)
==========================================================
Interactive AI-powered Icon Studio featuring an integrated conversational AI,
a 100,000+ procedural template matrix, custom prompt synthesis, live multi-resolution previews,
and 1-click Windows .ico (16x16 to 256x256) and .png export.
"""

import sys
import os
import math
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from PIL import Image, ImageDraw, ImageFont, ImageTk

# ── Cyberpunk Neon Palette ────────────────────────────────────────────────
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
C_TEXT_GREEN  = "#6ee7b7"

# ── Theme Palettes ────────────────────────────────────────────────────────
PALETTES = [
    {"name": "Cyber Cyan",     "c1": (0, 240, 255),   "c2": (8, 22, 54),   "accent": (0, 240, 255)},
    {"name": "Neon Emerald",   "c1": (0, 255, 157),   "c2": (5, 38, 26),   "accent": (0, 255, 157)},
    {"name": "Solar Gold",     "c1": (255, 183, 3),   "c2": (42, 28, 5),   "accent": (255, 183, 3)},
    {"name": "Hyper Violet",   "c1": (176, 38, 255),  "c2": (32, 10, 52),  "accent": (176, 38, 255)},
    {"name": "Sunset Crimson", "c1": (255, 0, 85),    "c2": (48, 10, 24),  "accent": (255, 0, 85)},
    {"name": "Electric Blue",  "c1": (59, 130, 246),  "c2": (12, 24, 60),  "accent": (59, 130, 246)},
    {"name": "Toxic Lime",     "c1": (132, 204, 22),  "c2": (22, 38, 5),   "accent": (132, 204, 22)},
    {"name": "Hot Pink",       "c1": (244, 63, 94),   "c2": (48, 12, 28),  "accent": (244, 63, 94)},
    {"name": "Stealth Carbon", "c1": (148, 163, 184), "c2": (15, 23, 42),  "accent": (71, 85, 105)},
    {"name": "Abyssal Dark",   "c1": (94, 234, 212),  "c2": (2, 6, 23),    "accent": (15, 23, 42)},
]

SHAPES = ["squircle", "shield", "circle", "hexagon", "diamond", "star", "badge", "transparent"]

GLYPH_NAMES = [
    ("⚡ Lightning Bolt", "lightning"),
    ("🛡️ Quantum Shield", "shield"),
    ("🔒 Neon Padlock", "padlock"),
    ("🚀 Turbo Rocket", "rocket"),
    ("🔥 Fire Flame", "fire"),
    ("🌐 Cyber Globe", "globe"),
    ("👁️ Sentinel Eye", "eye"),
    ("⚛️ Quantum Atom", "atom"),
    ("💎 Cyber Gem", "gem"),
    ("🎮 Game Controller", "gamepad"),
    ("👑 Royal Crown", "crown"),
    ("⭐ Star Emblem", "star"),
    ("❤️ Cyber Heart", "heart"),
    ("💻 Terminal Code", "terminal"),
    ("⚙️ Mech Gear", "gear"),
    ("🗡️ Cyber Sword", "sword"),
    ("🤖 Robot AI", "robot"),
    ("▶️ Media Play", "play_btn"),
    ("📡 WiFi Signal", "wifi"),
    ("💬 Chat Bubble", "chat"),
    ("🎵 Music Audio", "music"),
    ("🪙 Crypto Coin", "coin"),
    ("🔍 Security Lens", "search"),
    ("🧹 Cleaner Wand", "broom"),
    ("🔤 Custom Monogram", "text")
]

class IconDesignerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JENTS // QUANTUM ICON STUDIO & AI DESIGNER")
        self.root.geometry("1160x780")
        self.root.minsize(1020, 680)
        self.root.configure(bg=C_BG)

        # Center Window
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(10, (sw - 1160) // 2)
        y = max(10, (sh - 780) // 2 - 20)
        self.root.geometry(f"1160x780+{x}+{y}")

        # State Variables
        self.var_shape = tk.StringVar(value="squircle")
        self.var_glyph = tk.StringVar(value="lightning")
        self.var_palette_name = tk.StringVar(value="Cyber Cyan")
        self.var_monogram = tk.StringVar(value="J")
        self.var_badge = tk.StringVar(value="PRO")
        self.var_glow = tk.BooleanVar(value=True)
        self.var_border_width = tk.IntVar(value=6)
        self.current_template_id = tk.IntVar(value=random.randint(1, 100000))
        
        self.c1 = (0, 240, 255)
        self.c2 = (8, 22, 54)

        self.current_pil_image = None
        self.tk_canvas_img = None
        self.preview_tk_images = {}

        self._build_ui()
        self.render_and_update()

    def _build_ui(self):
        # ── Header ───────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=C_BG)
        header.pack(fill=tk.X, padx=18, pady=(12, 4))

        title_box = tk.Frame(header, bg=C_BG)
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box, text="⚡ QUANTUM ICON STUDIO & AI SYNTHESIZER",
            font=("Segoe UI", 16, "bold"),
            fg=C_CYAN, bg=C_BG
        ).pack(anchor="w")

        tk.Label(
            title_box, text="// 100,000+ PROCEDURAL TEMPLATES • NATURAL LANGUAGE AI DESIGNER • WINDOWS .ICO EXPORTER",
            font=("Consolas", 8, "bold"),
            fg=C_GREEN, bg=C_BG
        ).pack(anchor="w")

        # ── Main 3-Section Grid ──────────────────────────────────────────────
        main_grid = tk.Frame(self.root, bg=C_BG)
        main_grid.pack(fill=tk.BOTH, expand=True, padx=18, pady=(2, 8))

        # ── COLUMN 1: AI Chat & Prompt Synthesizer (340px) ───────────────────
        ai_card = tk.Frame(main_grid, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1, width=340)
        ai_card.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        ai_card.pack_propagate(False)

        self._build_ai_chat_section(ai_card)

        # ── COLUMN 2: 256x256 Master Canvas & Template Matrix (440px) ────────
        center_card = tk.Frame(main_grid, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        center_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self._build_canvas_and_matrix_section(center_card)

        # ── COLUMN 3: Multi-Resolution Windows Previews & Fine-Tuning (340px) ─
        right_card = tk.Frame(main_grid, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1, width=340)
        right_card.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_card.pack_propagate(False)

        self._build_preview_and_controls(right_card)

        # ── Bottom Export Bar ────────────────────────────────────────────────
        bot_bar = tk.Frame(self.root, bg=C_BG)
        bot_bar.pack(fill=tk.X, padx=18, pady=(0, 10))

        tk.Label(
            bot_bar, text="Outputs multi-layer Windows .ico with 16x16, 32x32, 48x48, 64x64, 128x128, 256x256 layers",
            font=("Consolas", 8), fg=C_TEXT_MUTED, bg=C_BG
        ).pack(side=tk.LEFT)

        btn_apply_app = tk.Button(
            bot_bar, text="⚡ SAVE AS APP ICON (icons/jents_icon.ico)",
            font=("Segoe UI", 9, "bold"),
            fg=C_BG, bg=C_GREEN,
            activebackground=C_CYAN, activeforeground=C_BG,
            relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
            command=self._save_to_app_icons
        )
        btn_apply_app.pack(side=tk.RIGHT, padx=(6, 0))

        btn_export_png = tk.Button(
            bot_bar, text="🖼️ EXPORT .PNG",
            font=("Segoe UI", 9, "bold"),
            fg=C_CYAN, bg=C_PANEL,
            activebackground=C_CYAN, activeforeground=C_BG,
            relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
            command=self._export_png
        )
        btn_export_png.pack(side=tk.RIGHT, padx=6)

        btn_export_ico = tk.Button(
            bot_bar, text="💾 EXPORT .ICO",
            font=("Segoe UI", 9, "bold"),
            fg=C_TEXT_BRIGHT, bg=C_BLUE,
            activebackground=C_GREEN, activeforeground=C_BG,
            relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
            command=self._export_ico
        )
        btn_export_ico.pack(side=tk.RIGHT, padx=6)

    def _build_ai_chat_section(self, parent):
        tk.Label(parent, text="🤖 QUANTUM AI ICON ARCHITECT", font=("Consolas", 9, "bold"), fg=C_CYAN, bg=C_CARD).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(parent, text="Describe what you want — AI creates it instantly:", font=("Segoe UI", 8), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w", padx=12, pady=(0, 6))

        # Chat Log Box
        chat_box_frame = tk.Frame(parent, bg=C_PANEL, highlightbackground=C_BORDER, highlightthickness=1)
        chat_box_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 6))

        self.chat_text = tk.Text(
            chat_box_frame, bg=C_PANEL, fg=C_TEXT_BRIGHT,
            font=("Segoe UI", 9), wrap=tk.WORD, relief=tk.FLAT, padx=8, pady=8, state=tk.DISABLED
        )
        scroll = ttk.Scrollbar(chat_box_frame, command=self.chat_text.yview)
        self.chat_text.configure(yscrollcommand=scroll.set)

        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._append_chat("🤖 AI Architect", "Hello! I can synthesize any icon you want from my 100,000+ template library or create custom vector graphics from your prompts.\n\nTry: 'glowing red fire gaming logo with PRO badge' or 'emerald security shield with padlock'!")

        # Quick Prompt Chips
        chips_frame = tk.Frame(parent, bg=C_CARD)
        chips_frame.pack(fill=tk.X, padx=12, pady=(0, 6))

        quick_prompts = [
            ("⚡ Gaming Cyber", "glowing red fire gaming logo with PRO badge"),
            ("🛡️ Security Shield", "emerald shield with padlock security"),
            ("🚀 Speed Booster", "gold turbo speed rocket with 10G badge"),
            ("💎 Purple Crystal", "purple crypto bitcoin diamond gem"),
            ("💻 Dark Terminal", "dark hacker developer code terminal icon")
        ]

        for lbl, prmpt in quick_prompts[:3]:
            b = tk.Button(
                chips_frame, text=lbl,
                font=("Consolas", 7), fg=C_TEXT_CYAN, bg=C_PANEL,
                relief=tk.FLAT, padx=6, pady=2, cursor="hand2",
                command=lambda p=prmpt: self._send_ai_prompt(p)
            )
            b.pack(side=tk.LEFT, padx=2)

        # Input Box
        input_frame = tk.Frame(parent, bg=C_CARD)
        input_frame.pack(fill=tk.X, padx=12, pady=(0, 10))

        self.entry_prompt = tk.Entry(
            input_frame, font=("Segoe UI", 9),
            bg=C_PANEL, fg=C_TEXT_BRIGHT,
            insertbackground=C_CYAN, relief=tk.FLAT
        )
        self.entry_prompt.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6), ipady=4)
        self.entry_prompt.bind("<Return>", lambda e: self._send_ai_prompt(self.entry_prompt.get()))

        btn_send = tk.Button(
            input_frame, text="✨ GENERATE",
            font=("Segoe UI", 8, "bold"),
            fg=C_BG, bg=C_CYAN,
            activebackground=C_GREEN, activeforeground=C_BG,
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
            command=lambda: self._send_ai_prompt(self.entry_prompt.get())
        )
        btn_send.pack(side=tk.RIGHT)

    def _build_canvas_and_matrix_section(self, parent):
        tk.Label(parent, text="256 × 256 MASTER CANVAS", font=("Consolas", 9, "bold"), fg=C_TEXT_CYAN, bg=C_CARD).pack(pady=(10, 4))

        # Checkered Canvas
        self.canvas_master = tk.Canvas(
            parent, width=256, height=256,
            bg="#030712", highlightbackground=C_BORDER, highlightthickness=2
        )
        self.canvas_master.pack(pady=4)

        # ── 100,000+ Procedural Template Matrix Controls ─────────────────────
        matrix_box = tk.Frame(parent, bg=C_PANEL, highlightbackground=C_BORDER, highlightthickness=1)
        matrix_box.pack(fill=tk.X, padx=14, pady=(8, 4))

        tk.Label(matrix_box, text="⚡ 100,000+ PROCEDURAL TEMPLATE MATRIX", font=("Consolas", 8, "bold"), fg=C_AMBER, bg=C_PANEL).pack(anchor="w", padx=10, pady=(6, 2))

        m_row = tk.Frame(matrix_box, bg=C_PANEL)
        m_row.pack(fill=tk.X, padx=10, pady=(0, 6))

        tk.Label(m_row, text="Template #", font=("Consolas", 8), fg=C_TEXT_MUTED, bg=C_PANEL).pack(side=tk.LEFT)
        e_tid = tk.Entry(m_row, textvariable=self.current_template_id, font=("Consolas", 9, "bold"), fg=C_CYAN, bg=C_CARD, width=8, relief=tk.FLAT)
        e_tid.pack(side=tk.LEFT, padx=4)
        
        btn_jump = tk.Button(
            m_row, text="LOAD ID",
            font=("Segoe UI", 7, "bold"), fg=C_TEXT_BRIGHT, bg=C_CARD,
            relief=tk.FLAT, padx=6, pady=1, cursor="hand2",
            command=self._load_template_by_id
        )
        btn_jump.pack(side=tk.LEFT, padx=2)

        btn_random = tk.Button(
            m_row, text="🎲 ROLL RANDOM (1 of 100,000+)",
            font=("Segoe UI", 8, "bold"), fg=C_BG, bg=C_AMBER,
            activebackground=C_GREEN, activeforeground=C_BG,
            relief=tk.FLAT, padx=8, pady=2, cursor="hand2",
            command=self._roll_random_template
        )
        btn_random.pack(side=tk.RIGHT)

    def _build_preview_and_controls(self, parent):
        # Multi-Resolution Preview Section
        tk.Label(parent, text="WINDOWS LIVE RESOLUTIONS", font=("Consolas", 9, "bold"), fg=C_TEXT_GREEN, bg=C_CARD).pack(anchor="w", padx=12, pady=(10, 4))

        prev_box = tk.Frame(parent, bg=C_PANEL, highlightbackground=C_BORDER, highlightthickness=1)
        prev_box.pack(fill=tk.X, padx=12, pady=(0, 8))

        # Previews in 1 row
        p_row = tk.Frame(prev_box, bg=C_PANEL)
        p_row.pack(fill=tk.X, padx=8, pady=6)

        # 64x64
        b64 = tk.Frame(p_row, bg=C_PANEL)
        b64.pack(side=tk.LEFT, expand=True)
        tk.Label(b64, text="64×64", font=("Consolas", 7), fg=C_TEXT_MUTED, bg=C_PANEL).pack()
        self.lbl_prev_64 = tk.Label(b64, bg=C_PANEL)
        self.lbl_prev_64.pack()

        # 32x32
        b32 = tk.Frame(p_row, bg=C_PANEL)
        b32.pack(side=tk.LEFT, expand=True)
        tk.Label(b32, text="32×32", font=("Consolas", 7), fg=C_TEXT_MUTED, bg=C_PANEL).pack()
        self.lbl_prev_32 = tk.Label(b32, bg=C_PANEL)
        self.lbl_prev_32.pack()

        # 16x16
        b16 = tk.Frame(p_row, bg=C_PANEL)
        b16.pack(side=tk.LEFT, expand=True)
        tk.Label(b16, text="16×16", font=("Consolas", 7), fg=C_TEXT_MUTED, bg=C_PANEL).pack()
        self.lbl_prev_16 = tk.Label(b16, bg=C_PANEL)
        self.lbl_prev_16.pack()

        # Manual Fine-Tuning Controls
        tk.Label(parent, text="MANUAL FINE-TUNING", font=("Consolas", 9, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w", padx=12, pady=(4, 2))

        c_box = tk.Frame(parent, bg=C_CARD)
        c_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 6))

        # Shape Selector
        tk.Label(c_box, text="Shape:", font=("Consolas", 8), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w")
        combo_shape = ttk.Combobox(c_box, textvariable=self.var_shape, values=SHAPES, state="readonly", font=("Segoe UI", 8))
        combo_shape.pack(fill=tk.X, pady=(0, 4))
        combo_shape.bind("<<ComboboxSelected>>", lambda e: self.render_and_update())

        # Palette Selector
        tk.Label(c_box, text="Palette:", font=("Consolas", 8), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w")
        combo_pal = ttk.Combobox(c_box, textvariable=self.var_palette_name, values=[p["name"] for p in PALETTES], state="readonly", font=("Segoe UI", 8))
        combo_pal.pack(fill=tk.X, pady=(0, 4))
        combo_pal.bind("<<ComboboxSelected>>", lambda e: self._on_palette_selected())

        # Glyph Selector
        tk.Label(c_box, text="Symbol / Glyph:", font=("Consolas", 8), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w")
        combo_gly = ttk.Combobox(c_box, textvariable=self.var_glyph, values=[g[0] for g in GLYPH_NAMES], state="readonly", font=("Segoe UI", 8))
        combo_gly.current(0)
        combo_gly.pack(fill=tk.X, pady=(0, 4))
        combo_gly.bind("<<ComboboxSelected>>", lambda e: self._on_glyph_selected(combo_gly.get()))

        # Monogram & Badge in 1 row
        mb_row = tk.Frame(c_box, bg=C_CARD)
        mb_row.pack(fill=tk.X, pady=(0, 4))

        tk.Label(mb_row, text="Initials:", font=("Consolas", 7), fg=C_TEXT_MUTED, bg=C_CARD).pack(side=tk.LEFT)
        e_mono = tk.Entry(mb_row, textvariable=self.var_monogram, font=("Segoe UI", 8, "bold"), bg=C_PANEL, fg=C_CYAN, width=4)
        e_mono.pack(side=tk.LEFT, padx=4)
        self.var_monogram.trace_add("write", lambda *args: self.render_and_update())

        tk.Label(mb_row, text="Badge:", font=("Consolas", 7), fg=C_TEXT_MUTED, bg=C_CARD).pack(side=tk.LEFT, padx=(6, 0))
        e_bdg = tk.Entry(mb_row, textvariable=self.var_badge, font=("Segoe UI", 8, "bold"), bg=C_PANEL, fg=C_RED, width=6)
        e_bdg.pack(side=tk.LEFT, padx=4)
        self.var_badge.trace_add("write", lambda *args: self.render_and_update())

        # Glow Toggle & Border Slider
        chk_glow = tk.Checkbutton(
            c_box, text="Outer Neon Bloom Glow",
            variable=self.var_glow, font=("Segoe UI", 8),
            fg=C_TEXT_BRIGHT, bg=C_CARD, selectcolor=C_PANEL,
            activebackground=C_CARD, activeforeground=C_CYAN,
            command=self.render_and_update
        )
        chk_glow.pack(anchor="w")

        s_border = tk.Scale(c_box, from_=0, to=12, orient=tk.HORIZONTAL, variable=self.var_border_width, bg=C_CARD, fg=C_TEXT_MUTED, highlightthickness=0, command=lambda v: self.render_and_update())
        s_border.pack(fill=tk.X)

    def _append_chat(self, sender, msg):
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"{sender}:\n", ("bold",))
        self.chat_text.insert(tk.END, f"{msg}\n\n")
        self.chat_text.tag_config("bold", font=("Segoe UI", 9, "bold"), foreground=C_CYAN if "AI" in sender else C_GREEN)
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

    def _send_ai_prompt(self, prompt):
        if not prompt or not prompt.strip():
            return
        prompt_text = prompt.strip()
        self.entry_prompt.delete(0, tk.END)
        self._append_chat("👤 You", prompt_text)

        # ── AI Natural Language Parsing & Synthesis Engine ───────────────────
        res = self._parse_ai_prompt(prompt_text)
        
        self.var_shape.set(res["shape"])
        self.c1 = res["c1"]
        self.c2 = res["c2"]
        self.var_glyph.set(res["glyph"])
        self.var_badge.set(res["badge"])
        self.var_glow.set(True)

        if "monogram" in res:
            self.var_monogram.set(res["monogram"])

        tid = random.randint(1000, 99999)
        self.current_template_id.set(tid)

        self.render_and_update()

        ai_reply = f"✨ Synthesized icon from prompt: '{prompt_text}'\n" \
                   f"• Template #{tid:,}\n" \
                   f"• Geometry: {res['shape'].capitalize()}\n" \
                   f"• Color: RGB{res['c1']}\n" \
                   f"• Symbol: {res['glyph'].capitalize()}\n" \
                   f"• Badge: {res['badge'] or 'None'}\n" \
                   f"Rendered in full 256x256 vector resolution with active neon bloom glow!"

        self._append_chat("🤖 AI Architect", ai_reply)

    def _parse_ai_prompt(self, prompt: str) -> dict:
        p = prompt.lower()

        # Color Detection
        color_map = {
            "cyan": ((0, 240, 255), (8, 22, 54)),
            "blue": ((59, 130, 246), (12, 24, 60)),
            "red": ((239, 68, 68), (48, 10, 20)),
            "crimson": ((255, 0, 85), (48, 10, 24)),
            "green": ((34, 197, 94), (5, 38, 24)),
            "emerald": ((0, 255, 157), (5, 38, 26)),
            "gold": ((255, 183, 3), (42, 28, 5)),
            "yellow": ((250, 204, 21), (40, 35, 10)),
            "purple": ((176, 38, 255), (32, 10, 52)),
            "violet": ((139, 92, 246), (30, 15, 50)),
            "pink": ((244, 63, 94), (48, 12, 28)),
            "orange": ((249, 115, 22), (45, 20, 5)),
            "lime": ((132, 204, 22), (22, 38, 5)),
            "carbon": ((148, 163, 184), (15, 23, 42)),
            "dark": ((94, 234, 212), (2, 6, 23)),
        }

        # Shape Detection
        shape_map = {
            "shield": "shield", "crest": "shield", "security": "shield", "guard": "shield",
            "circle": "circle", "round": "circle", "ring": "circle", "reactor": "circle",
            "hexagon": "hexagon", "hex": "hexagon",
            "diamond": "diamond", "gem": "diamond", "crystal": "diamond",
            "star": "star", "badge": "badge",
            "transparent": "transparent",
            "squircle": "squircle", "square": "squircle", "box": "squircle"
        }

        # Glyph Detection
        glyph_map = {
            "lightning": "lightning", "bolt": "lightning", "flash": "lightning", "power": "lightning", "thunder": "lightning",
            "shield": "shield", "defense": "shield", "armor": "shield",
            "lock": "padlock", "padlock": "padlock", "safe": "padlock", "crypto": "padlock",
            "rocket": "rocket", "speed": "rocket", "turbo": "rocket", "boost": "rocket", "fast": "rocket", "launch": "rocket",
            "fire": "fire", "flame": "fire", "burn": "fire", "hot": "fire", "dragon": "fire",
            "eye": "eye", "sentinel": "eye", "vision": "eye", "radar": "eye", "scan": "eye",
            "atom": "atom", "quantum": "atom", "nuclear": "atom", "science": "atom", "orbit": "atom",
            "gem": "gem", "crystal": "gem", "diamond": "gem", "ruby": "gem",
            "gamepad": "gamepad", "game": "gamepad", "gaming": "gamepad", "play": "gamepad", "controller": "gamepad",
            "globe": "globe", "world": "globe", "earth": "globe", "network": "globe", "web": "globe", "vpn": "globe",
            "crown": "crown", "king": "crown", "royal": "crown", "vip": "crown",
            "star": "star", "rank": "star",
            "heart": "heart", "health": "heart", "life": "heart", "love": "heart",
            "terminal": "terminal", "code": "terminal", "dev": "terminal", "hacker": "terminal", "console": "terminal",
            "gear": "gear", "setting": "gear", "engine": "gear", "mech": "gear",
            "sword": "sword", "blade": "sword", "warrior": "sword", "rpg": "sword",
            "robot": "robot", "ai": "robot", "bot": "robot", "cyber": "robot",
            "video": "play_btn", "youtube": "play_btn", "media": "play_btn", "stream": "play_btn",
            "wifi": "wifi", "signal": "wifi", "wireless": "wifi",
            "chat": "chat", "message": "chat", "talk": "chat", "sms": "chat",
            "music": "music", "audio": "music", "sound": "music", "song": "music",
            "coin": "coin", "bitcoin": "coin", "money": "coin", "token": "coin",
            "lens": "search", "search": "search", "find": "search",
            "clean": "broom", "cleaner": "broom", "wand": "broom"
        }

        # Match Colors
        c1, c2 = (0, 240, 255), (8, 22, 54)
        for kw, (col1, col2) in color_map.items():
            if kw in p:
                c1, c2 = col1, col2
                break

        # Match Shapes
        sel_shape = "squircle"
        for kw, shp in shape_map.items():
            if kw in p:
                sel_shape = shp
                break

        # Match Glyphs
        sel_glyph = "lightning"
        for kw, gly in glyph_map.items():
            if kw in p:
                sel_glyph = gly
                break

        # Match Badges
        sel_badge = ""
        if "pro" in p: sel_badge = "PRO"
        elif "ai" in p: sel_badge = "AI"
        elif "max" in p: sel_badge = "MAX"
        elif "vpn" in p: sel_badge = "VPN"
        elif "vip" in p: sel_badge = "VIP"
        elif "10g" in p: sel_badge = "10G"
        elif "v1" in p: sel_badge = "v1.0"
        elif "new" in p: sel_badge = "NEW"

        return {
            "c1": c1, "c2": c2,
            "shape": sel_shape,
            "glyph": sel_glyph,
            "badge": sel_badge
        }

    def _roll_random_template(self):
        tid = random.randint(1, 100000)
        self.current_template_id.set(tid)
        self._load_template_by_id()

    def _load_template_by_id(self):
        tid = self.current_template_id.get()
        # Seeded deterministic pseudo-random generator
        rng = random.Random(tid)

        shape = rng.choice(SHAPES)
        pal = rng.choice(PALETTES)
        glyph = rng.choice(GLYPH_NAMES)[1]
        badge = rng.choice(["", "PRO", "AI", "10G", "MAX", "VIP", "v1.0", "HOT", "4K"])

        self.var_shape.set(shape)
        self.var_palette_name.set(pal["name"])
        self.c1 = pal["c1"]
        self.c2 = pal["c2"]
        self.var_glyph.set(glyph)
        self.var_badge.set(badge)
        self.var_glow.set(rng.choice([True, True, False]))
        self.var_border_width.set(rng.choice([4, 6, 8]))

        self.render_and_update()
        self._append_chat("🤖 AI Architect", f"Loaded Template #{tid:,} ({pal['name']} {glyph.capitalize()} {shape.capitalize()})")

    def _on_palette_selected(self):
        pname = self.var_palette_name.get()
        for p in PALETTES:
            if p["name"] == pname:
                self.c1 = p["c1"]
                self.c2 = p["c2"]
                break
        self.render_and_update()

    def _on_glyph_selected(self, full_name):
        for name, key in GLYPH_NAMES:
            if name == full_name:
                self.var_glyph.set(key)
                break
        self.render_and_update()

    def render_and_update(self):
        """Renders 256x256 antialiased master image and updates all previews."""
        img = self._generate_icon_image()
        self.current_pil_image = img

        # 1. Update Master Canvas (256x256)
        self.tk_canvas_img = ImageTk.PhotoImage(img)
        self.canvas_master.delete("all")
        self.canvas_master.create_image(128, 128, image=self.tk_canvas_img)

        # 2. Update multi-res previews
        im64 = img.resize((56, 56), Image.Resampling.LANCZOS)
        self.preview_tk_images["64"] = ImageTk.PhotoImage(im64)
        self.lbl_prev_64.config(image=self.preview_tk_images["64"])

        im32 = img.resize((32, 32), Image.Resampling.LANCZOS)
        self.preview_tk_images["32"] = ImageTk.PhotoImage(im32)
        self.lbl_prev_32.config(image=self.preview_tk_images["32"])

        im16 = img.resize((16, 16), Image.Resampling.LANCZOS)
        self.preview_tk_images["16"] = ImageTk.PhotoImage(im16)
        self.lbl_prev_16.config(image=self.preview_tk_images["16"])

    def _generate_icon_image(self) -> Image.Image:
        img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        shape = self.var_shape.get()
        glyph = self.var_glyph.get()
        c1 = self.c1
        c2 = self.c2
        b_width = self.var_border_width.get()
        glow = self.var_glow.get()
        badge = self.var_badge.get().strip().upper()

        # ── 1. Background Geometry & Glow ────────────────────────────────────
        if shape == "squircle":
            if glow:
                for i in range(14, 0, -2):
                    alpha = int(42 * (1 - i/14))
                    draw.rounded_rectangle([16-i, 16-i, 240+i, 240+i], radius=50+i, fill=(*c1, alpha))
            draw.rounded_rectangle([16, 16, 240, 240], radius=50, fill=(*c2, 255), outline=(*c1, 255) if b_width else None, width=b_width)

        elif shape == "circle":
            if glow:
                for i in range(14, 0, -2):
                    alpha = int(42 * (1 - i/14))
                    draw.ellipse([16-i, 16-i, 240+i, 240+i], fill=(*c1, alpha))
            draw.ellipse([16, 16, 240, 240], fill=(*c2, 255), outline=(*c1, 255) if b_width else None, width=b_width)

        elif shape == "shield":
            pts = [(128, 16), (235, 45), (215, 185), (128, 245), (41, 185), (21, 45)]
            if glow:
                for i in range(10, 0, -2):
                    alpha = int(35 * (1 - i/10))
                    draw.polygon(pts, fill=(*c1, alpha))
            draw.polygon(pts, fill=(*c2, 255), outline=(*c1, 255) if b_width else None)

        elif shape == "hexagon":
            pts = [(128, 16), (235, 75), (235, 181), (128, 240), (21, 181), (21, 75)]
            if glow:
                for i in range(10, 0, -2):
                    alpha = int(35 * (1 - i/10))
                    draw.polygon(pts, fill=(*c1, alpha))
            draw.polygon(pts, fill=(*c2, 255), outline=(*c1, 255) if b_width else None)

        elif shape == "diamond":
            pts = [(128, 16), (240, 128), (128, 240), (16, 128)]
            if glow:
                for i in range(10, 0, -2):
                    alpha = int(35 * (1 - i/10))
                    draw.polygon(pts, fill=(*c1, alpha))
            draw.polygon(pts, fill=(*c2, 255), outline=(*c1, 255) if b_width else None)

        elif shape == "star":
            pts = []
            for idx in range(10):
                angle = idx * math.pi / 5 - math.pi / 2
                r = 115 if idx % 2 == 0 else 55
                pts.append((128 + int(r * math.cos(angle)), 128 + int(r * math.sin(angle))))
            if glow:
                draw.polygon(pts, fill=(*c1, 50))
            draw.polygon(pts, fill=(*c2, 255), outline=(*c1, 255) if b_width else None)

        elif shape == "badge":
            pts = []
            for idx in range(16):
                angle = idx * math.pi / 8
                r = 118 if idx % 2 == 0 else 98
                pts.append((128 + int(r * math.cos(angle)), 128 + int(r * math.sin(angle))))
            if glow:
                draw.polygon(pts, fill=(*c1, 50))
            draw.polygon(pts, fill=(*c2, 255), outline=(*c1, 255) if b_width else None)

        # ── 2. Vector Glyphs & Symbols ───────────────────────────────────────
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

        elif glyph == "rocket":
            draw.polygon([(128, 42), (162, 105), (162, 172), (94, 172), (94, 105)], fill=(*c1, 255))
            draw.polygon([(94, 138), (56, 182), (94, 176)], fill=(*c1, 255))
            draw.polygon([(162, 138), (200, 182), (162, 176)], fill=(*c1, 255))
            draw.ellipse([(114, 88), (142, 116)], fill=(*c2, 255))
            draw.polygon([(110, 175), (128, 222), (146, 175)], fill=(255, 0, 85, 255))

        elif glyph == "fire":
            pts = [(128, 40), (165, 95), (180, 150), (160, 205), (128, 220), (96, 205), (76, 150), (91, 95)]
            draw.polygon(pts, fill=(*c1, 255))
            inner = [(128, 90), (150, 135), (140, 185), (128, 200), (116, 185), (106, 135)]
            draw.polygon(inner, fill=(255, 183, 3, 255))

        elif glyph == "globe":
            draw.ellipse([64, 64, 192, 192], outline=(*c1, 255), width=6)
            draw.ellipse([92, 64, 164, 192], outline=(*c1, 255), width=4)
            draw.line([(64, 128), (192, 128)], fill=(*c1, 255), width=5)
            draw.line([(76, 96), (180, 96)], fill=(*c1, 255), width=4)
            draw.line([(76, 160), (180, 160)], fill=(*c1, 255), width=4)

        elif glyph == "eye":
            draw.ellipse([50, 90, 206, 166], outline=(*c1, 255), width=7)
            draw.ellipse([98, 98, 158, 158], fill=(*c1, 255))
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

        elif glyph == "gamepad":
            draw.rounded_rectangle([60, 95, 196, 165], radius=24, fill=(*c1, 255))
            draw.rectangle([80, 120, 108, 140], fill=(*c2, 255))
            draw.rectangle([89, 111, 99, 149], fill=(*c2, 255))
            draw.ellipse([150, 115, 162, 127], fill=(*c2, 255))
            draw.ellipse([168, 130, 180, 142], fill=(*c2, 255))

        elif glyph == "crown":
            pts = [(60, 180), (60, 110), (95, 145), (128, 80), (161, 145), (196, 110), (196, 180)]
            draw.polygon(pts, fill=(*c1, 255), outline=(255, 255, 255, 255), width=2)
            draw.rectangle([60, 185, 196, 198], fill=(*c1, 255))

        elif glyph == "star":
            pts = []
            for idx in range(10):
                angle = idx * math.pi / 5 - math.pi / 2
                r = 75 if idx % 2 == 0 else 35
                pts.append((128 + int(r * math.cos(angle)), 128 + int(r * math.sin(angle))))
            draw.polygon(pts, fill=(*c1, 255))

        elif glyph == "heart":
            draw.ellipse([70, 75, 132, 137], fill=(*c1, 255))
            draw.ellipse([124, 75, 186, 137], fill=(*c1, 255))
            draw.polygon([(74, 118), (182, 118), (128, 198)], fill=(*c1, 255))

        elif glyph == "terminal":
            draw.rounded_rectangle([55, 70, 201, 186], radius=12, fill=(*c2, 255), outline=(*c1, 255), width=5)
            draw.line([(75, 105), (95, 125), (75, 145)], fill=(*c1, 255), width=5)
            draw.line([(105, 145), (140, 145)], fill=(*c1, 255), width=5)

        elif glyph == "gear":
            draw.ellipse([80, 80, 176, 176], fill=(*c1, 255))
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                cx = 128 + int(56 * math.cos(rad))
                cy = 128 + int(56 * math.sin(rad))
                draw.rectangle([cx-10, cy-10, cx+10, cy+10], fill=(*c1, 255))
            draw.ellipse([106, 106, 150, 150], fill=(*c2, 255))

        elif glyph == "sword":
            draw.line([(70, 186), (186, 70)], fill=(*c1, 255), width=10)
            draw.polygon([(186, 70), (196, 60), (190, 80)], fill=(*c1, 255))
            draw.line([(85, 150), (115, 180)], fill=(255, 183, 3, 255), width=8)

        elif glyph == "robot":
            draw.rounded_rectangle([75, 80, 181, 176], radius=16, fill=(*c1, 255))
            draw.ellipse([95, 105, 115, 125], fill=(*c2, 255))
            draw.ellipse([141, 105, 161, 125], fill=(*c2, 255))
            draw.line([(100, 150), (156, 150)], fill=(*c2, 255), width=6)
            draw.line([(128, 80), (128, 55)], fill=(*c1, 255), width=6)
            draw.ellipse([120, 45, 136, 61], fill=(255, 0, 85, 255))

        elif glyph == "play_btn":
            draw.polygon([(95, 70), (185, 128), (95, 186)], fill=(*c1, 255))

        elif glyph == "wifi":
            draw.arc([55, 60, 201, 206], start=210, end=330, fill=(*c1, 255), width=10)
            draw.arc([80, 95, 176, 191], start=210, end=330, fill=(*c1, 255), width=8)
            draw.arc([105, 130, 151, 176], start=210, end=330, fill=(*c1, 255), width=6)
            draw.ellipse([120, 168, 136, 184], fill=(*c1, 255))

        elif glyph == "chat":
            draw.rounded_rectangle([60, 70, 196, 160], radius=20, fill=(*c1, 255))
            draw.polygon([(85, 155), (70, 190), (120, 155)], fill=(*c1, 255))
            draw.ellipse([85, 105, 99, 119], fill=(*c2, 255))
            draw.ellipse([121, 105, 135, 119], fill=(*c2, 255))
            draw.ellipse([157, 105, 171, 119], fill=(*c2, 255))

        elif glyph == "music":
            draw.ellipse([70, 140, 105, 175], fill=(*c1, 255))
            draw.ellipse([140, 120, 175, 155], fill=(*c1, 255))
            draw.line([(100, 150), (100, 75)], fill=(*c1, 255), width=8)
            draw.line([(170, 130), (170, 55)], fill=(*c1, 255), width=8)
            draw.line([(100, 75), (170, 55)], fill=(*c1, 255), width=12)

        elif glyph == "coin":
            draw.ellipse([64, 64, 192, 192], fill=(*c1, 255), outline=(255, 255, 255, 255), width=4)
            draw.ellipse([80, 80, 176, 176], outline=(*c2, 255), width=4)
            try: font = ImageFont.truetype("arialbd.ttf", 72)
            except Exception: font = ImageFont.load_default()
            draw.text((108, 86), "B", fill=(*c2, 255), font=font)

        elif glyph == "search":
            draw.ellipse([70, 70, 155, 155], outline=(*c1, 255), width=10)
            draw.line([(140, 140), (195, 195)], fill=(*c1, 255), width=14)

        elif glyph == "broom":
            draw.line([(85, 185), (175, 75)], fill=(*c1, 255), width=10)
            draw.polygon([(185, 60), (195, 60), (195, 70), (185, 70)], fill=(*c1, 255))

        elif glyph == "text":
            text = self.var_monogram.get().strip() or "J"
            try: font = ImageFont.truetype("arialbd.ttf", 100)
            except Exception: font = ImageFont.load_default()
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
            try: bfont = ImageFont.truetype("arialbd.ttf", 14)
            except Exception: bfont = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), badge, font=bfont)
            bw = bbox[2] - bbox[0]
            bh = bbox[3] - bbox[1]
            bx = bx1 + (badge_len - bw) // 2
            by = by1 + (32 - bh) // 2 - 2
            draw.text((bx, by), badge, fill=(255, 255, 255, 255), font=bfont)

        return img

    def _export_ico(self):
        if not self.current_pil_image: return
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
        if not self.current_pil_image: return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if path:
            try:
                self.current_pil_image.save(path, format="PNG")
                messagebox.showinfo("Export Successful! 🖼️", f"High-Resolution PNG saved:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export .png: {e}")

    def _save_to_app_icons(self):
        if not self.current_pil_image: return
        target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
        os.makedirs(target_dir, exist_ok=True)
        ico_path = os.path.join(target_dir, "jents_icon.ico")
        try:
            self.current_pil_image.save(
                ico_path, format="ICO",
                sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            )
            messagebox.showinfo("App Icon Updated! ⚡", f"Master icon updated at:\n{ico_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not update app icon: {e}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = IconDesignerApp()
    app.run()
