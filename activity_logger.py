"""
Jents Activity Sentinel & Network Security Monitor (v1.0)
==========================================================
Real-time activity logger tracking process connections, network traffic,
DNS queries, public IP changes, and security events with a high-tech Cyber Deck UI.
"""

import sys
import os
import time
import json
import csv
import socket
import threading
import psutil
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ── Cyber Deck Theme Palette ─────────────────────────────────────────────
C_BG          = "#030712"
C_PANEL       = "#0b1329"
C_CARD        = "#0f172a"
C_CARD_ALT    = "#1e293b"
C_BORDER      = "#1e293b"
C_BORDER_GLOW = "#38bdf8"
C_CYAN        = "#06b6d4"
C_BLUE        = "#3b82f6"
C_INDIGO      = "#6366f1"
C_GREEN       = "#10b981"
C_AMBER       = "#f59e0b"
C_RED         = "#ef4444"
C_PURPLE      = "#a855f7"
C_TEXT_BRIGHT = "#f8fafc"
C_TEXT_MUTED  = "#94a3b8"
C_TEXT_CYAN   = "#38bdf8"
C_TEXT_GREEN  = "#34d399"

class ActivityLoggerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JENTS // QUANTUM ACTIVITY SENTINEL")
        self.root.geometry("1020x700")
        self.root.minsize(800, 500)
        self.root.configure(bg=C_BG)

        # Center Window
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(10, (sw - 1020) // 2)
        y = max(10, (sh - 700) // 2 - 20)
        self.root.geometry(f"1020x700+{x}+{y}")

        self.is_paused = False
        self.events_data = []
        self.seen_connections = set()
        self.last_net_io = psutil.net_io_counters()
        self.last_io_time = time.time()
        self.current_ip = "Detecting..."
        self.current_geo = "Detecting..."
        self.filter_category = "ALL"

        self._init_styles()
        self._build_ui()
        
        # Start background workers
        threading.Thread(target=self._network_monitor_loop, daemon=True).start()
        threading.Thread(target=self._ip_sentinel_loop, daemon=True).start()

    def _init_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Treeview styling
        style.configure(
            "Treeview",
            background=C_CARD,
            foreground=C_TEXT_BRIGHT,
            fieldbackground=C_CARD,
            rowheight=26,
            font=("Segoe UI", 9)
        )
        style.configure(
            "Treeview.Heading",
            background=C_PANEL,
            foreground=C_TEXT_CYAN,
            font=("Consolas", 8, "bold"),
            relief=tk.FLAT
        )
        style.map("Treeview", background=[("selected", C_INDIGO)], foreground=[("selected", C_TEXT_BRIGHT)])
        style.map("Treeview.Heading", background=[("active", C_CARD_ALT)])

    def _build_ui(self):
        # ── Header ───────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=C_BG)
        header.pack(fill=tk.X, padx=18, pady=(14, 6))

        title_box = tk.Frame(header, bg=C_BG)
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box, text="⚡ ACTIVITY SENTINEL",
            font=("Segoe UI", 16, "bold"),
            fg=C_CYAN, bg=C_BG
        ).pack(anchor="w")

        tk.Label(
            title_box, text="// LIVE NETWORK ACTIVITY, PROCESS & SECURITY TELEMETRY",
            font=("Consolas", 8, "bold"),
            fg=C_INDIGO, bg=C_BG
        ).pack(anchor="w")

        self.lbl_status = tk.Label(
            header, text="● MONITORING LIVE",
            font=("Consolas", 8, "bold"),
            fg=C_GREEN, bg=C_CARD,
            padx=10, pady=4
        )
        self.lbl_status.pack(side=tk.RIGHT)

        # ── KPI Telemetry Row ────────────────────────────────────────────────
        kpi_row = tk.Frame(self.root, bg=C_BG)
        kpi_row.pack(fill=tk.X, padx=18, pady=(4, 10))

        self.kpi_cards = {}
        kpi_configs = [
            ("TOTAL EVENTS", "0", C_CYAN, "events"),
            ("ACTIVE SOCKETS", "0", C_GREEN, "sockets"),
            ("DOWNLOAD RATE", "0.0 KB/s", C_TEXT_CYAN, "down_rate"),
            ("UPLOAD RATE", "0.0 KB/s", C_AMBER, "up_rate"),
            ("CURRENT PUBLIC IP", "Detecting...", C_PURPLE, "ip")
        ]

        for i, (label, default, color, key) in enumerate(kpi_configs):
            card = tk.Frame(kpi_row, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0 if i == 0 else 4, 0 if i == len(kpi_configs)-1 else 4))

            tk.Label(card, text=label, font=("Consolas", 7, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w", padx=10, pady=(6, 1))
            val_lbl = tk.Label(card, text=default, font=("Consolas", 11, "bold"), fg=color, bg=C_CARD)
            val_lbl.pack(anchor="w", padx=10, pady=(0, 6))
            self.kpi_cards[key] = val_lbl

        # ── Filter & Search Toolbar ──────────────────────────────────────────
        toolbar = tk.Frame(self.root, bg=C_BG)
        toolbar.pack(fill=tk.X, padx=18, pady=(0, 8))

        # Filter Category Buttons
        cat_box = tk.Frame(toolbar, bg=C_BG)
        cat_box.pack(side=tk.LEFT)

        self.cat_btns = {}
        for cat in ["ALL", "HTTP/S", "DNS", "SYSTEM", "SECURITY"]:
            b = tk.Button(
                cat_box, text=cat,
                font=("Consolas", 8, "bold"),
                fg=C_TEXT_BRIGHT if cat == "ALL" else C_TEXT_MUTED,
                bg=C_INDIGO if cat == "ALL" else C_CARD,
                activebackground=C_INDIGO, activeforeground=C_TEXT_BRIGHT,
                relief=tk.FLAT, padx=8, pady=3, cursor="hand2",
                command=lambda c=cat: self._set_category(c)
            )
            b.pack(side=tk.LEFT, padx=2)
            self.cat_btns[cat] = b

        # Search Box
        search_box = tk.Frame(toolbar, bg=C_BG)
        search_box.pack(side=tk.RIGHT)

        tk.Label(search_box, text="🔍", font=("Segoe UI", 9), fg=C_TEXT_MUTED, bg=C_BG).pack(side=tk.LEFT, padx=(0, 4))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._apply_search())
        
        search_entry = tk.Entry(
            search_box, textvariable=self.search_var,
            font=("Segoe UI", 9), bg=C_CARD, fg=C_TEXT_BRIGHT,
            insertbackground=C_CYAN, relief=tk.FLAT, width=24
        )
        search_entry.pack(side=tk.LEFT)

        # ── Activity Data Table ──────────────────────────────────────────────
        table_frame = tk.Frame(self.root, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 10))

        cols = ("time", "process", "pid", "proto", "remote", "port", "category", "status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("time", text="TIMESTAMP")
        self.tree.heading("process", text="PROCESS NAME")
        self.tree.heading("pid", text="PID")
        self.tree.heading("proto", text="PROTO")
        self.tree.heading("remote", text="REMOTE DESTINATION")
        self.tree.heading("port", text="PORT")
        self.tree.heading("category", text="CATEGORY")
        self.tree.heading("status", text="STATE")

        self.tree.column("time", width=85, anchor="center")
        self.tree.column("process", width=140, anchor="w")
        self.tree.column("pid", width=55, anchor="center")
        self.tree.column("proto", width=60, anchor="center")
        self.tree.column("remote", width=260, anchor="w")
        self.tree.column("port", width=65, anchor="center")
        self.tree.column("category", width=90, anchor="center")
        self.tree.column("status", width=95, anchor="center")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # ── Bottom Control Bar ───────────────────────────────────────────────
        bottom_bar = tk.Frame(self.root, bg=C_BG)
        bottom_bar.pack(fill=tk.X, padx=18, pady=(0, 12))

        self.btn_pause = tk.Button(
            bottom_bar, text="⏸️ PAUSE STREAM",
            font=("Segoe UI", 9, "bold"),
            fg=C_TEXT_BRIGHT, bg=C_CARD,
            activebackground=C_CARD_ALT, activeforeground=C_TEXT_BRIGHT,
            relief=tk.FLAT, padx=12, pady=5, cursor="hand2",
            command=self._toggle_pause
        )
        self.btn_pause.pack(side=tk.LEFT, padx=(0, 6))

        btn_clear = tk.Button(
            bottom_bar, text="🧹 CLEAR LOGS",
            font=("Segoe UI", 9, "bold"),
            fg=C_TEXT_MUTED, bg=C_CARD,
            activebackground=C_CARD_ALT, activeforeground=C_TEXT_BRIGHT,
            relief=tk.FLAT, padx=10, pady=5, cursor="hand2",
            command=self._clear_logs
        )
        btn_clear.pack(side=tk.LEFT, padx=6)

        btn_export_csv = tk.Button(
            bottom_bar, text="💾 EXPORT CSV",
            font=("Segoe UI", 9, "bold"),
            fg=C_CYAN, bg=C_PANEL,
            activebackground=C_CYAN, activeforeground=C_BG,
            relief=tk.FLAT, padx=12, pady=5, cursor="hand2",
            command=self._export_csv
        )
        btn_export_csv.pack(side=tk.RIGHT, padx=(6, 0))

        btn_export_json = tk.Button(
            bottom_bar, text="📋 EXPORT JSON",
            font=("Segoe UI", 9, "bold"),
            fg=C_GREEN, bg=C_PANEL,
            activebackground=C_GREEN, activeforeground=C_BG,
            relief=tk.FLAT, padx=12, pady=5, cursor="hand2",
            command=self._export_json
        )
        btn_export_json.pack(side=tk.RIGHT, padx=6)

    def _set_category(self, cat):
        self.filter_category = cat
        for c, b in self.cat_btns.items():
            if c == cat:
                b.config(bg=C_INDIGO, fg=C_TEXT_BRIGHT)
            else:
                b.config(bg=C_CARD, fg=C_TEXT_MUTED)
        self._apply_search()

    def _apply_search(self):
        query = self.search_var.get().lower().strip()
        self.tree.delete(*self.tree.get_children())

        for ev in self.events_data:
            cat_match = (self.filter_category == "ALL" or ev["category"] == self.filter_category)
            if not cat_match:
                continue

            if query:
                searchable = f"{ev['process']} {ev['remote']} {ev['port']} {ev['category']} {ev['status']}".lower()
                if query not in searchable:
                    continue

            self._insert_tree_row(ev)

    def _insert_tree_row(self, ev):
        self.tree.insert(
            "", 0,
            values=(
                ev["time"],
                ev["process"],
                ev["pid"],
                ev["proto"],
                ev["remote"],
                ev["port"],
                ev["category"],
                ev["status"]
            )
        )

    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.config(text="▶️ RESUME STREAM", fg=C_AMBER)
            self.lbl_status.config(text="⏸️ STREAM PAUSED", fg=C_AMBER)
        else:
            self.btn_pause.config(text="⏸️ PAUSE STREAM", fg=C_TEXT_BRIGHT)
            self.lbl_status.config(text="● MONITORING LIVE", fg=C_GREEN)

    def _clear_logs(self):
        self.events_data.clear()
        self.tree.delete(*self.tree.get_children())
        self.kpi_cards["events"].config(text="0")

    def _export_csv(self):
        if not self.events_data:
            messagebox.showwarning("Export", "No activity events logged yet.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            try:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["time", "process", "pid", "proto", "remote", "port", "category", "status"])
                    writer.writeheader()
                    writer.writerows(self.events_data)
                messagebox.showinfo("Export Successful", f"Exported {len(self.events_data)} records to CSV!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {e}")

    def _export_json(self):
        if not self.events_data:
            messagebox.showwarning("Export", "No activity events logged yet.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.events_data, f, indent=2)
                messagebox.showinfo("Export Successful", f"Exported {len(self.events_data)} records to JSON!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export JSON: {e}")

    def _network_monitor_loop(self):
        """Continuously monitors active network connections & bandwidth."""
        while True:
            try:
                # 1. Bandwidth calculations
                now = time.time()
                cur_io = psutil.net_io_counters()
                dt = max(0.1, now - self.last_io_time)
                
                down_bps = (cur_io.bytes_recv - self.last_net_io.bytes_recv) / dt
                up_bps   = (cur_io.bytes_sent - self.last_net_io.bytes_sent) / dt
                
                self.last_net_io = cur_io
                self.last_io_time = now

                down_str = f"{down_bps/1024.0:.1f} KB/s" if down_bps < 1048576 else f"{down_bps/1048576.0:.2f} MB/s"
                up_str   = f"{up_bps/1024.0:.1f} KB/s" if up_bps < 1048576 else f"{up_bps/1048576.0:.2f} MB/s"

                # 2. Connection socket polling
                connections = psutil.net_connections(kind="inet")
                active_socks = len(connections)
                
                new_events = []
                for conn in connections:
                    if conn.status == "LISTEN" or not conn.raddr:
                        continue
                    
                    remote_ip = conn.raddr.ip
                    remote_port = conn.raddr.port
                    
                    if remote_ip.startswith("127.") or remote_ip == "::1":
                        continue

                    conn_key = (conn.pid, remote_ip, remote_port, conn.type)
                    if conn_key not in self.seen_connections:
                        self.seen_connections.add(conn_key)
                        if len(self.seen_connections) > 10000:
                            self.seen_connections.clear()

                        # Process name lookup
                        pname = "System"
                        if conn.pid:
                            try:
                                p = psutil.Process(conn.pid)
                                pname = p.name()
                            except Exception:
                                pass

                        proto_str = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
                        
                        # Category detection
                        if remote_port in (443, 8443, 80, 8080):
                            cat = "HTTP/S"
                        elif remote_port in (53, 853):
                            cat = "DNS"
                        elif remote_port in (21, 23, 25, 110, 143):
                            cat = "SECURITY"
                        else:
                            cat = "SYSTEM"

                        ev = {
                            "time": time.strftime("%H:%M:%S"),
                            "process": pname,
                            "pid": str(conn.pid or "--"),
                            "proto": proto_str,
                            "remote": remote_ip,
                            "port": str(remote_port),
                            "category": cat,
                            "status": conn.status
                        }
                        new_events.append(ev)

                # Push to UI thread
                self.root.after(0, lambda d=down_str, u=up_str, s=active_socks, evs=new_events: self._update_ui_state(d, u, s, evs))

            except Exception:
                pass

            time.sleep(1.2)

    def _update_ui_state(self, down_str, up_str, active_socks, new_events):
        self.kpi_cards["down_rate"].config(text=down_str)
        self.kpi_cards["up_rate"].config(text=up_str)
        self.kpi_cards["sockets"].config(text=str(active_socks))

        if not self.is_paused and new_events:
            for ev in new_events:
                self.events_data.append(ev)
                if len(self.events_data) > 3000:
                    self.events_data.pop(0)

                cat_match = (self.filter_category == "ALL" or ev["category"] == self.filter_category)
                query = self.search_var.get().lower().strip()
                query_match = True
                if query:
                    searchable = f"{ev['process']} {ev['remote']} {ev['port']} {ev['category']} {ev['status']}".lower()
                    query_match = (query in searchable)

                if cat_match and query_match:
                    self._insert_tree_row(ev)
                    # Limit items in treeview
                    children = self.tree.get_children()
                    if len(children) > 1000:
                        self.tree.delete(children[-1])

            self.kpi_cards["events"].config(text=str(len(self.events_data)))

    def _ip_sentinel_loop(self):
        """Monitors public IP changes in the background."""
        last_ip = ""
        while True:
            try:
                req = urllib.request.Request("https://icanhazip.com", headers={"User-Agent": "curl/8.0"})
                with urllib.request.urlopen(req, timeout=4.0) as resp:
                    ip = resp.read().decode("utf-8", "ignore").strip()
                    if ip and ip != last_ip:
                        last_ip = ip
                        self.current_ip = ip
                        self.root.after(0, lambda i=ip: self.kpi_cards["ip"].config(text=i))

                        # Log IP change event
                        ev = {
                            "time": time.strftime("%H:%M:%S"),
                            "process": "Jents Sentinel",
                            "pid": str(os.getpid()),
                            "proto": "HTTPS",
                            "remote": ip,
                            "port": "443",
                            "category": "SECURITY",
                            "status": "IP CHANGED"
                        }
                        self.root.after(0, lambda e=ev: self._update_ui_state(
                            self.kpi_cards["down_rate"].cget("text"),
                            self.kpi_cards["up_rate"].cget("text"),
                            int(self.kpi_cards["sockets"].cget("text") or 0),
                            [e]
                        ))
            except Exception:
                pass
            time.sleep(6.0)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ActivityLoggerApp()
    app.run()
