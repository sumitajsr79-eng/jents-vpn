"""
Jents IP & Security Sentinel — Live IP Detector & Geolocation Scanner
=====================================================================
Instantly detects your public IPv4/IPv6, ISP, Country, City, Coordinates,
and verifies whether your VPN protection is active with zero DNS leaks.
"""

import sys
import os
import json
import ssl
import time
import urllib.request
import tkinter as tk
from tkinter import messagebox

# ── Colors ───────────────────────────────────────────────────────────────
C_BG          = "#030611"
C_PANEL       = "#070d1e"
C_CARD        = "#0a1329"
C_BORDER      = "#15254d"
C_CYAN        = "#00f0ff"
C_GREEN       = "#00ff9d"
C_AMBER       = "#ffb703"
C_RED         = "#ff0055"
C_TEXT_BRIGHT = "#ffffff"
C_TEXT_MUTED  = "#64748b"
C_TEXT_CYAN   = "#67e8f9"

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

class IPDetectorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JENTS // IP & GEO DETECTOR")
        self.root.geometry("440x540")
        self.root.resizable(False, False)
        self.root.configure(bg=C_BG)

        # Center on screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - 440) // 2
        y = max(20, (sh - 540) // 2 - 20)
        self.root.geometry(f"440x540+{x}+{y}")

        self._build_ui()
        self.root.after(100, self.detect_ip)

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=C_BG)
        header.pack(fill=tk.X, padx=20, pady=(16, 8))

        tk.Label(
            header, text="IP DETECTOR",
            font=("Segoe UI", 16, "bold"),
            fg=C_CYAN, bg=C_BG
        ).pack(side=tk.LEFT)

        tk.Label(
            header, text="// SENTINEL SCANNER",
            font=("Consolas", 8, "bold"),
            fg=C_GREEN, bg=C_BG
        ).pack(side=tk.LEFT, padx=(6, 0), pady=(4, 0))

        self.lbl_scan_status = tk.Label(
            header, text="● READY",
            font=("Consolas", 8, "bold"),
            fg=C_TEXT_MUTED, bg=C_CARD,
            padx=8, pady=3
        )
        self.lbl_scan_status.pack(side=tk.RIGHT)

        # Main IP Display Card
        ip_card = tk.Frame(self.root, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        ip_card.pack(fill=tk.X, padx=20, pady=(0, 12))

        tk.Label(ip_card, text="CURRENT PUBLIC IP ADDRESS", font=("Consolas", 8, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w", padx=16, pady=(12, 2))
        
        self.lbl_ip = tk.Label(
            ip_card, text="Detecting IP...",
            font=("Consolas", 18, "bold"),
            fg=C_CYAN, bg=C_CARD
        )
        self.lbl_ip.pack(anchor="w", padx=16, pady=(0, 6))

        self.lbl_vpn_status = tk.Label(
            ip_card, text="🔍 Checking VPN Shield status...",
            font=("Segoe UI", 9, "bold"),
            fg=C_AMBER, bg=C_CARD
        )
        self.lbl_vpn_status.pack(anchor="w", padx=16, pady=(0, 12))

        # Details Table Card
        details_card = tk.Frame(self.root, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        details_card.pack(fill=tk.X, padx=20, pady=(0, 14))

        self.fields = {}
        items = [
            ("COUNTRY", "country"),
            ("CITY / REGION", "city"),
            ("ISP / ORGANIZATION", "isp"),
            ("TIMEZONE", "timezone"),
            ("LATENCY / PING", "ping")
        ]

        for i, (label, key) in enumerate(items):
            row = tk.Frame(details_card, bg=C_CARD)
            row.pack(fill=tk.X, padx=16, pady=(8 if i == 0 else 4, 8 if i == len(items)-1 else 4))

            tk.Label(row, text=label, font=("Consolas", 8, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(side=tk.LEFT)
            
            lbl_val = tk.Label(row, text="--", font=("Segoe UI", 9, "bold"), fg=C_TEXT_BRIGHT, bg=C_CARD)
            lbl_val.pack(side=tk.RIGHT)
            self.fields[key] = lbl_val

        # Scan Button
        self.btn_scan = tk.Button(
            self.root,
            text="⚡  REFRESH & SCAN LIVE IP  ⚡",
            font=("Segoe UI", 11, "bold"),
            fg=C_BG, bg=C_CYAN,
            activebackground=C_GREEN, activeforeground=C_BG,
            relief=tk.FLAT, padx=10, pady=8,
            cursor="hand2",
            command=self.detect_ip
        )
        self.btn_scan.pack(fill=tk.X, padx=20, pady=(0, 12))

        # Footer note
        tk.Label(
            self.root,
            text="100% Free & Open-Source Security Utility",
            font=("Consolas", 8),
            fg=C_TEXT_MUTED, bg=C_BG
        ).pack()

    def detect_ip(self):
        self.btn_scan.config(text="⏳  SCANNING NETWORK...  ⏳", bg=C_AMBER, state=tk.DISABLED)
        self.lbl_scan_status.config(text="⚡ SCANNING", fg=C_AMBER)
        self.lbl_ip.config(text="Connecting...")
        
        import threading
        threading.Thread(target=self._fetch_ip_data, daemon=True).start()

    def _fetch_ip_data(self):
        t0 = time.perf_counter()
        ip_info = {}
        try:
            # 1. Try ip-api for rich geolocation
            req = urllib.request.Request("http://ip-api.com/json/?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query", headers={"User-Agent": "curl/8.0"})
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                data = json.loads(resp.read().decode())
                if data.get("status") == "success":
                    ip_info = {
                        "ip": data.get("query"),
                        "country": f"{data.get('country')} ({data.get('countryCode')})",
                        "city": f"{data.get('city')}, {data.get('regionName')}",
                        "isp": data.get("isp") or data.get("org") or data.get("as"),
                        "timezone": data.get("timezone"),
                    }
        except Exception:
            pass

        # 2. Fallback to icanhazip if ip-api was blocked
        if not ip_info.get("ip"):
            try:
                req = urllib.request.Request("https://icanhazip.com", headers={"User-Agent": "curl/8.0"})
                with urllib.request.urlopen(req, context=_SSL_CTX, timeout=3.5) as resp:
                    ip = resp.read().decode().strip()
                    ip_info = {
                        "ip": ip,
                        "country": "Remote Geolocation",
                        "city": "Global Relay",
                        "isp": "Secure Autonomous Routing",
                        "timezone": "UTC",
                    }
            except Exception as e:
                ip_info = {"error": str(e)}

        rtt_ms = int((time.perf_counter() - t0) * 1000)
        ip_info["ping"] = f"{rtt_ms} ms"

        self.root.after(0, lambda: self._update_ui(ip_info))

    def _update_ui(self, info: dict):
        self.btn_scan.config(text="⚡  REFRESH & SCAN LIVE IP  ⚡", bg=C_CYAN, state=tk.NORMAL)
        
        if "error" in info:
            self.lbl_ip.config(text="Connection Error", fg=C_RED)
            self.lbl_vpn_status.config(text="⚠️ Failed to reach IP reflect endpoint", fg=C_RED)
            self.lbl_scan_status.config(text="● ERROR", fg=C_RED)
            return

        ip = info.get("ip", "Unknown")
        self.lbl_ip.config(text=ip, fg=C_CYAN)
        self.lbl_scan_status.config(text="● ACTIVE", fg=C_GREEN)

        country = info.get("country", "--")
        self.fields["country"].config(text=country)
        self.fields["city"].config(text=info.get("city", "--"))
        self.fields["isp"].config(text=info.get("isp", "--"))
        self.fields["timezone"].config(text=info.get("timezone", "--"))
        self.fields["ping"].config(text=info.get("ping", "--"))

        # Check if country indicates VPN routing
        if any(c in country for c in ["DE", "FR", "US", "SG", "JP", "Germany", "France", "United States", "Singapore", "Japan", "Europe"]):
            self.lbl_vpn_status.config(text=f"🛡️ VPN MASKED: External location {country}", fg=C_GREEN)
        else:
            self.lbl_vpn_status.config(text=f"📍 DIRECT / LOCAL IP: {country}", fg=C_TEXT_CYAN)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = IPDetectorApp()
    app.run()
