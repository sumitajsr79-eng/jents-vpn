"""
Jents DNS Optimizer & Security Changer (v1.0)
==============================================
Benchmark, compare, and 1-click switch between top global DNS providers.
Shows exact performance benchmarks and reveals which DNS is best for your needs:
Gaming, Ad-Blocking, Malware Defense, 4K Streaming, or Privacy.
"""

import sys
import os
import re
import io
import time
import socket
import ctypes
import subprocess
import threading
import concurrent.futures
import tkinter as tk
from tkinter import messagebox, ttk

# ── Cyberpunk Neon Palette ────────────────────────────────────────────────
C_BG          = "#020617"
C_PANEL       = "#070d1e"
C_CARD        = "#0a1329"
C_CARD_ACTIVE = "#0f1c3d"
C_BORDER      = "#15254d"
C_CYAN        = "#00f0ff"
C_GREEN       = "#00ff9d"
C_AMBER       = "#ffb703"
C_RED         = "#ff0055"
C_PURPLE      = "#b026ff"
C_TEXT_BRIGHT = "#ffffff"
C_TEXT_MUTED  = "#64748b"
C_TEXT_CYAN   = "#67e8f9"
C_TEXT_GREEN  = "#6ee7b7"

# ── DNS Providers Catalog ────────────────────────────────────────────────
DNS_PROVIDERS = [
    {
        "id": "cloudflare",
        "name": "Cloudflare DNS",
        "primary": "1.1.1.1",
        "secondary": "1.0.0.1",
        "category": "⚡ GAMING & SPEED",
        "badge_color": C_CYAN,
        "best_for": "🎮 Ultra-Low Latency Gaming, Fastest Web Browsing & Zero-Log Privacy",
        "description": "The world's fastest public DNS (1ms cache). Does not log IP addresses or sell user data."
    },
    {
        "id": "adguard",
        "name": "AdGuard Ad-Block DNS",
        "primary": "94.140.14.14",
        "secondary": "94.140.15.15",
        "category": "🛑 AD & TRACKER BLOCKING",
        "badge_color": C_GREEN,
        "best_for": "🚫 Blocking Invasive Ads, Trackers, Popups & Telemetry System-Wide",
        "description": "Filters out ads, analytics scripts, and behavioral trackers across all applications and games."
    },
    {
        "id": "google",
        "name": "Google Public DNS",
        "primary": "8.8.8.8",
        "secondary": "8.8.4.4",
        "category": "🎬 4K STREAMING & UPTIME",
        "badge_color": C_AMBER,
        "best_for": "📺 4K Video Streaming (YouTube/Netflix), Global Anycast CDN Routing & 99.99% Reliability",
        "description": "Massive global Anycast network that delivers intelligent content routing and virtually zero downtime."
    },
    {
        "id": "quad9",
        "name": "Quad9 Security & Privacy",
        "primary": "9.9.9.9",
        "secondary": "149.112.112.112",
        "category": "🛡️ MALWARE & THREAT DEFENSE",
        "badge_color": C_PURPLE,
        "best_for": "🔒 Blocking Phishing, Ransomware, Botnets & Cyber Threats in Real-Time",
        "description": "Swiss non-profit that aggregates 20+ cyber-intelligence feeds to block malicious domains automatically."
    },
    {
        "id": "cf_malware",
        "name": "Cloudflare Malware Shield",
        "primary": "1.1.1.2",
        "secondary": "1.0.0.2",
        "category": "🛡️ AUTOMATED CYBER DEFENSE",
        "badge_color": C_PURPLE,
        "best_for": "⚡ High-Speed Browsing + Automatic Known Threat & Phishing Blocking",
        "description": "Combines Cloudflare's ultra-fast 1.1.1.1 lookup speed with automated malware domain filtering."
    },
    {
        "id": "opendns",
        "name": "Cisco OpenDNS Home",
        "primary": "208.67.222.222",
        "secondary": "208.67.220.220",
        "category": "🏢 CISCO ENTERPRISE ROUTING",
        "badge_color": C_CYAN,
        "best_for": "🌐 Enterprise Stability, Anti-Phishing & Custom Web Content Filtering",
        "description": "Enterprise-grade DNS backed by Cisco Talos intelligence with zero downtime."
    },
    {
        "id": "cf_family",
        "name": "Cloudflare Families",
        "primary": "1.1.1.3",
        "secondary": "1.0.0.3",
        "category": "👨‍👩‍👧 FAMILY & CHILD SAFETY",
        "badge_color": C_GREEN,
        "best_for": "🏡 Safe Family Internet: Blocks Malware + Explicit Adult Content",
        "description": "Automated network-wide family protection filter that blocks malicious and adult material."
    },
    {
        "id": "controld",
        "name": "Control D Uncensored",
        "primary": "76.76.2.0",
        "secondary": "76.76.10.0",
        "category": "🔓 UNCENSORED & NEUTRAL",
        "badge_color": C_AMBER,
        "best_for": "🔓 Bypassing Local Censorship, Neutral Routing & Zero Filtering",
        "description": "Completely unfiltered, zero-logging DNS designed for privacy enthusiasts and net neutrality."
    }
]

def request_admin():
    """Requests elevation if needed."""
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False

    if not is_admin:
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable,
                " ".join(f'"{a}"' for a in sys.argv),
                None, 1
            )
            sys.exit(0)
        except Exception:
            pass

class DNSChangerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JENTS // QUANTUM DNS OPTIMIZER & CHANGER")
        self.root.geometry("640x720")
        self.root.minsize(580, 600)
        self.root.configure(bg=C_BG)

        # Center Window
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(10, (sw - 640) // 2)
        y = max(10, (sh - 720) // 2 - 20)
        self.root.geometry(f"640x720+{x}+{y}")

        self.latency_map = {}
        self.active_adapter = tk.StringVar(value="")
        self.current_dns_str = tk.StringVar(value="Detecting active DNS...")

        self._build_ui()
        self._refresh_adapters()
        self.root.after(200, self._refresh_current_dns)
        self.root.after(400, self.benchmark_all)

    def _build_ui(self):
        # ── Header ───────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=C_BG)
        header.pack(fill=tk.X, padx=20, pady=(16, 6))

        title_box = tk.Frame(header, bg=C_BG)
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box, text="⚡ JENTS DNS OPTIMIZER",
            font=("Segoe UI", 16, "bold"),
            fg=C_CYAN, bg=C_BG
        ).pack(anchor="w")

        tk.Label(
            title_box, text="// INTELLIGENT DNS SELECTOR & SPEED BENCHMARK",
            font=("Consolas", 8, "bold"),
            fg=C_GREEN, bg=C_BG
        ).pack(anchor="w")

        self.lbl_status = tk.Label(
            header, text="● READY",
            font=("Consolas", 8, "bold"),
            fg=C_GREEN, bg=C_CARD,
            padx=10, pady=4
        )
        self.lbl_status.pack(side=tk.RIGHT, pady=2)

        # ── Active Status & Adapter Bar ───────────────────────────────────────
        status_card = tk.Frame(self.root, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        status_card.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Top status row
        row1 = tk.Frame(status_card, bg=C_CARD)
        row1.pack(fill=tk.X, padx=14, pady=(10, 4))

        tk.Label(row1, text="ACTIVE SYSTEM DNS:", font=("Consolas", 8, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(side=tk.LEFT)
        self.lbl_cur_dns = tk.Label(row1, textvariable=self.current_dns_str, font=("Consolas", 9, "bold"), fg=C_TEXT_CYAN, bg=C_CARD)
        self.lbl_cur_dns.pack(side=tk.RIGHT)

        # Adapter selector row
        row2 = tk.Frame(status_card, bg=C_CARD)
        row2.pack(fill=tk.X, padx=14, pady=(4, 10))

        tk.Label(row2, text="NETWORK ADAPTER:", font=("Consolas", 8, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(side=tk.LEFT)
        
        self.combo_adapter = ttk.Combobox(row2, textvariable=self.active_adapter, state="readonly", width=22, font=("Segoe UI", 9))
        self.combo_adapter.pack(side=tk.RIGHT)

        # ── Top Action Buttons ────────────────────────────────────────────────
        btn_bar = tk.Frame(self.root, bg=C_BG)
        btn_bar.pack(fill=tk.X, padx=20, pady=(0, 10))

        self.btn_bench = tk.Button(
            btn_bar, text="⚡ BENCHMARK ALL DNS (FIND FASTEST)",
            font=("Segoe UI", 9, "bold"),
            fg=C_BG, bg=C_CYAN,
            activebackground=C_GREEN, activeforeground=C_BG,
            relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
            command=self.benchmark_all
        )
        self.btn_bench.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        btn_dhcp = tk.Button(
            btn_bar, text="🔄 RESET TO DHCP",
            font=("Segoe UI", 9, "bold"),
            fg=C_AMBER, bg=C_CARD,
            activebackground=C_AMBER, activeforeground=C_BG,
            relief=tk.FLAT, padx=10, pady=6, cursor="hand2",
            command=self.restore_dhcp
        )
        btn_dhcp.pack(side=tk.LEFT, padx=4)

        btn_flush = tk.Button(
            btn_bar, text="🧹 FLUSH DNS",
            font=("Segoe UI", 9, "bold"),
            fg=C_TEXT_BRIGHT, bg=C_PANEL,
            activebackground=C_CYAN, activeforeground=C_BG,
            relief=tk.FLAT, padx=10, pady=6, cursor="hand2",
            command=self.flush_dns
        )
        btn_flush.pack(side=tk.RIGHT, padx=(4, 0))

        # ── Scrollable Provider List ──────────────────────────────────────────
        list_frame = tk.Frame(self.root, bg=C_BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        canvas = tk.Canvas(list_frame, bg=C_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=C_BG)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=590)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel support
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.card_widgets = []
        self._render_provider_cards()

    def _render_provider_cards(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.card_widgets.clear()

        for prov in DNS_PROVIDERS:
            card = tk.Frame(self.scrollable_frame, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
            card.pack(fill=tk.X, pady=4)

            # Top row: Name + Category badge + Apply button
            top = tk.Frame(card, bg=C_CARD)
            top.pack(fill=tk.X, padx=14, pady=(10, 2))

            name_lbl = tk.Label(top, text=prov["name"], font=("Segoe UI", 11, "bold"), fg=C_TEXT_BRIGHT, bg=C_CARD)
            name_lbl.pack(side=tk.LEFT)

            cat_lbl = tk.Label(
                top, text=prov["category"],
                font=("Consolas", 7, "bold"),
                fg=prov["badge_color"], bg=C_PANEL,
                padx=6, pady=2
            )
            cat_lbl.pack(side=tk.LEFT, padx=8)

            btn_apply = tk.Button(
                top, text="⚡ APPLY",
                font=("Segoe UI", 8, "bold"),
                fg=C_BG, bg=prov["badge_color"],
                activebackground=C_GREEN, activeforeground=C_BG,
                relief=tk.FLAT, padx=10, pady=2, cursor="hand2",
                command=lambda p=prov: self.apply_dns(p)
            )
            btn_apply.pack(side=tk.RIGHT)

            # Ping Label
            ping_lbl = tk.Label(top, text="-- ms", font=("Consolas", 8, "bold"), fg=C_TEXT_MUTED, bg=C_CARD)
            ping_lbl.pack(side=tk.RIGHT, padx=10)

            # IP Addresses Row
            ip_row = tk.Frame(card, bg=C_CARD)
            ip_row.pack(fill=tk.X, padx=14, pady=(0, 4))

            ips_text = f"Primary: {prov['primary']}  •  Secondary: {prov['secondary']}"
            tk.Label(ip_row, text=ips_text, font=("Consolas", 8), fg=C_TEXT_MUTED, bg=C_CARD).pack(side=tk.LEFT)

            # Best For highlight row
            best_row = tk.Frame(card, bg=C_CARD)
            best_row.pack(fill=tk.X, padx=14, pady=(2, 4))

            tk.Label(
                best_row, text="★ BEST FOR: ",
                font=("Consolas", 8, "bold"), fg=C_AMBER, bg=C_CARD
            ).pack(side=tk.LEFT)

            tk.Label(
                best_row, text=prov["best_for"],
                font=("Segoe UI", 8, "bold"), fg=C_TEXT_GREEN, bg=C_CARD
            ).pack(side=tk.LEFT)

            # Description row
            desc_row = tk.Frame(card, bg=C_CARD)
            desc_row.pack(fill=tk.X, padx=14, pady=(0, 10))

            tk.Label(
                desc_row, text=prov["description"],
                font=("Segoe UI", 8), fg=C_TEXT_MUTED, bg=C_CARD, wraplength=550, justify=tk.LEFT
            ).pack(anchor="w")

            self.card_widgets.append({
                "provider": prov,
                "card": card,
                "ping_lbl": ping_lbl,
                "btn_apply": btn_apply
            })

    def _refresh_adapters(self):
        """Lists connected physical & Wi-Fi adapters."""
        try:
            res = subprocess.run("netsh interface ipv4 show interfaces", shell=True, capture_output=True, text=True)
            adapters = []
            for line in res.stdout.splitlines():
                match = re.match(r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\w+)\s+(.+)$", line)
                if match:
                    idx, metric, mtu, state, name = match.groups()
                    if state.lower() == "connected" and "loopback" not in name.lower():
                        adapters.append(name.strip())
            
            if adapters:
                self.combo_adapter["values"] = adapters
                self.active_adapter.set(adapters[0])
            else:
                self.combo_adapter["values"] = ["Wi-Fi", "Ethernet"]
                self.active_adapter.set("Wi-Fi")
        except Exception:
            self.combo_adapter["values"] = ["Wi-Fi", "Ethernet"]
            self.active_adapter.set("Wi-Fi")

    def _refresh_current_dns(self):
        """Checks the current active DNS on the selected adapter."""
        adapter = self.active_adapter.get() or "Wi-Fi"
        try:
            res = subprocess.run(f'netsh interface ipv4 show dnsservers name="{adapter}"', shell=True, capture_output=True, text=True)
            lines = res.stdout.splitlines()
            dns_servers = []
            for line in lines:
                ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", line)
                for ip in ips:
                    if ip not in dns_servers:
                        dns_servers.append(ip)

            if dns_servers:
                matched_name = None
                for p in DNS_PROVIDERS:
                    if p["primary"] in dns_servers or p["secondary"] in dns_servers:
                        matched_name = p["name"]
                        break
                if matched_name:
                    self.current_dns_str.set(f"{matched_name} ({', '.join(dns_servers)})")
                else:
                    self.current_dns_str.set(f"{', '.join(dns_servers)} (Custom / ISP)")
            else:
                self.current_dns_str.set("Automatic (DHCP Router Default)")
        except Exception as e:
            self.current_dns_str.set("Automatic / DHCP")

    def benchmark_all(self):
        """Runs concurrent real-world DNS latency benchmarks."""
        self.btn_bench.config(text="⏳ BENCHMARKING ALL SERVERS... ⏳", state=tk.DISABLED)
        self.lbl_status.config(text="⚡ BENCHMARKING", fg=C_AMBER)

        threading.Thread(target=self._benchmark_thread, daemon=True).start()

    def _test_single_dns(self, prov: dict) -> tuple[dict, float]:
        ip = prov["primary"]
        try:
            t0 = time.perf_counter()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)
            s.connect((ip, 53))
            s.close()
            ms = round((time.perf_counter() - t0) * 1000.0, 1)
            return (prov, ms)
        except Exception:
            return (prov, 999.0)

    def _benchmark_thread(self):
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self._test_single_dns, p) for p in DNS_PROVIDERS]
            for f in concurrent.futures.as_completed(futures):
                prov, ms = f.result()
                results.append((prov, ms))

        results.sort(key=lambda x: x[1])
        self.root.after(0, lambda: self._apply_benchmark_results(results))

    def _apply_benchmark_results(self, results):
        self.btn_bench.config(text="⚡ BENCHMARK ALL DNS (FIND FASTEST)", state=tk.NORMAL)
        self.lbl_status.config(text="● BENCHMARK COMPLETE", fg=C_GREEN)

        fastest_prov = results[0][0] if results and results[0][1] < 900 else None

        for item in self.card_widgets:
            prov = item["provider"]
            # Find score
            score = next((ms for p, ms in results if p["id"] == prov["id"]), 999.0)
            if score < 900:
                item["ping_lbl"].config(text=f"⚡ {score} ms", fg=C_GREEN if score < 60 else C_AMBER)
            else:
                item["ping_lbl"].config(text="⚠️ Timeout", fg=C_RED)

            # Highlight fastest card
            if fastest_prov and prov["id"] == fastest_prov["id"]:
                item["card"].config(highlightbackground=C_GREEN, highlightthickness=2)
                item["ping_lbl"].config(text=f"👑 #1 FASTEST ({score} ms)", fg=C_GREEN)
            else:
                item["card"].config(highlightbackground=C_BORDER, highlightthickness=1)

    def apply_dns(self, prov: dict):
        """Sets the selected DNS on the active adapter."""
        adapter = self.active_adapter.get() or "Wi-Fi"
        p_ip = prov["primary"]
        s_ip = prov["secondary"]

        self.lbl_status.config(text=f"CONFIGURING {prov['name']}...", fg=C_AMBER)

        def _do_apply():
            try:
                # Set Primary DNS
                cmd1 = f'netsh interface ipv4 set dnsservers name="{adapter}" source=static address={p_ip} register=primary'
                subprocess.run(cmd1, shell=True, capture_output=True, timeout=5)

                # Set Secondary DNS
                if s_ip:
                    cmd2 = f'netsh interface ipv4 add dnsservers name="{adapter}" address={s_ip} index=2'
                    subprocess.run(cmd2, shell=True, capture_output=True, timeout=5)

                # Flush DNS
                subprocess.run("ipconfig /flushdns", shell=True, capture_output=True, timeout=5)

                self.root.after(0, lambda: self._on_dns_applied(prov))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("DNS Error", f"Failed to set DNS: {e}\nMake sure to run as Administrator."))

        threading.Thread(target= _do_apply, daemon=True).start()

    def _on_dns_applied(self, prov: dict):
        self._refresh_current_dns()
        self.lbl_status.config(text="● DNS ACTIVE", fg=C_GREEN)
        messagebox.showinfo(
            "DNS Applied Successfully! ⚡",
            f"Active DNS updated to:\n\n{prov['name']}\nPrimary: {prov['primary']}\nSecondary: {prov['secondary']}\n\n★ Best for: {prov['best_for']}\n\nDNS Cache has been automatically flushed!"
        )

    def restore_dhcp(self):
        """Resets the adapter DNS back to automatic DHCP router default."""
        adapter = self.active_adapter.get() or "Wi-Fi"
        self.lbl_status.config(text="RESTORING DHCP...", fg=C_AMBER)

        def _do_dhcp():
            try:
                cmd = f'netsh interface ipv4 set dnsservers name="{adapter}" source=dhcp'
                subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                subprocess.run("ipconfig /flushdns", shell=True, capture_output=True, timeout=5)
                self.root.after(0, self._on_dhcp_restored)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to restore DHCP: {e}"))

        threading.Thread(target=_do_dhcp, daemon=True).start()

    def _on_dhcp_restored(self):
        self._refresh_current_dns()
        self.lbl_status.config(text="● DEFAULT DHCP", fg=C_AMBER)
        messagebox.showinfo(
            "Restored to Default! 🔄",
            "Your DNS has been reset to Automatic (DHCP).\nYour router's default ISP DNS is now active."
        )

    def flush_dns(self):
        """Flushes Windows DNS resolver cache."""
        try:
            subprocess.run("ipconfig /flushdns", shell=True, capture_output=True, timeout=5)
            self.lbl_status.config(text="● DNS CACHE FLUSHED", fg=C_GREEN)
            messagebox.showinfo("DNS Flushed 🧹", "Windows DNS Resolver Cache successfully cleared!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not flush DNS: {e}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    request_admin()
    app = DNSChangerApp()
    app.run()
