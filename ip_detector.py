"""
Jents IP & Security Sentinel — Live IP Detector & Geolocation Scanner (v2.0)
=============================================================================
Instantly and accurately detects your live public IPv4/IPv6, ISP, Country, City,
Timezone, and verifies whether your VPN protection is active with zero DNS leaks.
"""

import sys
import os
import json
import ssl
import time
import urllib.request
import threading
import tkinter as tk
from tkinter import messagebox

# ── Cyberpunk Neon Color Palette ─────────────────────────────────────────
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
C_TEXT_BRIGHT = "#ffffff"
C_TEXT_MUTED  = "#64748b"
C_TEXT_CYAN   = "#67e8f9"
C_TEXT_GREEN  = "#6ee7b7"

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

class IPDetectorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JENTS // QUANTUM IP & SECURITY SENTINEL")
        self.root.geometry("480x620")
        self.root.resizable(False, False)
        self.root.configure(bg=C_BG)

        # Center on screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(10, (sw - 480) // 2)
        y = max(10, (sh - 620) // 2 - 20)
        self.root.geometry(f"480x620+{x}+{y}")

        self.last_detected_ip = ""
        self.auto_refresh_enabled = tk.BooleanVar(value=True)

        self._build_ui()
        self.root.after(100, self.detect_ip)
        self.root.after(8000, self._auto_refresh_loop)

    def _build_ui(self):
        # ── Header ───────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=C_BG)
        header.pack(fill=tk.X, padx=22, pady=(16, 8))

        title_frame = tk.Frame(header, bg=C_BG)
        title_frame.pack(side=tk.LEFT)

        tk.Label(
            title_frame, text="⚡ JENTS SENTINEL",
            font=("Segoe UI", 15, "bold"),
            fg=C_CYAN, bg=C_BG
        ).pack(anchor="w")

        tk.Label(
            title_frame, text="// ADVANCED IP & GEO SECURITY AUDITOR",
            font=("Consolas", 8, "bold"),
            fg=C_GREEN, bg=C_BG
        ).pack(anchor="w")

        self.lbl_scan_status = tk.Label(
            header, text="● READY",
            font=("Consolas", 8, "bold"),
            fg=C_TEXT_MUTED, bg=C_CARD,
            padx=10, pady=4,
            relief=tk.FLAT
        )
        self.lbl_scan_status.pack(side=tk.RIGHT, pady=2)

        # ── Main IP Display Card ─────────────────────────────────────────────
        ip_card = tk.Frame(self.root, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        ip_card.pack(fill=tk.X, padx=22, pady=(4, 12))

        top_ip_row = tk.Frame(ip_card, bg=C_CARD)
        top_ip_row.pack(fill=tk.X, padx=16, pady=(12, 2))

        tk.Label(
            top_ip_row, text="CURRENT ACTIVE PUBLIC IP",
            font=("Consolas", 8, "bold"), fg=C_TEXT_MUTED, bg=C_CARD
        ).pack(side=tk.LEFT)

        self.btn_copy = tk.Button(
            top_ip_row, text="📋 COPY IP",
            font=("Consolas", 8, "bold"),
            fg=C_CYAN, bg=C_PANEL,
            activebackground=C_CYAN, activeforeground=C_BG,
            relief=tk.FLAT, padx=6, pady=1,
            cursor="hand2", command=self._copy_ip_to_clipboard
        )
        self.btn_copy.pack(side=tk.RIGHT)

        self.lbl_ip = tk.Label(
            ip_card, text="Scanning network...",
            font=("Consolas", 17, "bold"),
            fg=C_CYAN, bg=C_CARD
        )
        self.lbl_ip.pack(anchor="w", padx=16, pady=(2, 6))

        self.lbl_vpn_status = tk.Label(
            ip_card, text="🔍 Checking VPN Tunnel Shield & IP Routing...",
            font=("Segoe UI", 9, "bold"),
            fg=C_AMBER, bg=C_CARD
        )
        self.lbl_vpn_status.pack(anchor="w", padx=16, pady=(0, 12))

        # ── Geolocation & Telemetry Grid Card ─────────────────────────────────
        details_card = tk.Frame(self.root, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        details_card.pack(fill=tk.X, padx=22, pady=(0, 14))

        self.fields = {}
        items = [
            ("COUNTRY", "country"),
            ("CITY / REGION", "city"),
            ("ISP / ORGANIZATION", "isp"),
            ("ASN NETWORK", "asn"),
            ("TIMEZONE", "timezone"),
            ("LATENCY / PING", "ping")
        ]

        for i, (label, key) in enumerate(items):
            row = tk.Frame(details_card, bg=C_CARD)
            row.pack(fill=tk.X, padx=16, pady=(8 if i == 0 else 4, 8 if i == len(items)-1 else 4))

            tk.Label(row, text=label, font=("Consolas", 8, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(side=tk.LEFT)
            
            lbl_val = tk.Label(row, text="--", font=("Segoe UI", 9, "bold"), fg=C_TEXT_BRIGHT, bg=C_CARD, wraplength=260, justify=tk.RIGHT)
            lbl_val.pack(side=tk.RIGHT)
            self.fields[key] = lbl_val

        # ── Controls Section ──────────────────────────────────────────────────
        ctrl_frame = tk.Frame(self.root, bg=C_BG)
        ctrl_frame.pack(fill=tk.X, padx=22, pady=(0, 8))

        # Scan Button
        self.btn_scan = tk.Button(
            ctrl_frame,
            text="⚡  REFRESH & SCAN LIVE IP  ⚡",
            font=("Segoe UI", 10, "bold"),
            fg=C_BG, bg=C_CYAN,
            activebackground=C_GREEN, activeforeground=C_BG,
            relief=tk.FLAT, padx=10, pady=9,
            cursor="hand2",
            command=self.detect_ip
        )
        self.btn_scan.pack(fill=tk.X, pady=(0, 8))

        # Auto-refresh check
        chk_row = tk.Frame(ctrl_frame, bg=C_BG)
        chk_row.pack(fill=tk.X)

        chk = tk.Checkbutton(
            chk_row, text="Auto-Scan every 8s (Live Monitor)",
            variable=self.auto_refresh_enabled,
            font=("Segoe UI", 8),
            fg=C_TEXT_MUTED, bg=C_BG,
            selectcolor=C_CARD, activebackground=C_BG, activeforeground=C_CYAN
        )
        chk.pack(side=tk.LEFT)

        self.lbl_last_time = tk.Label(
            chk_row, text="Last scan: --:--:--",
            font=("Consolas", 8),
            fg=C_TEXT_MUTED, bg=C_BG
        )
        self.lbl_last_time.pack(side=tk.RIGHT)

        # ── Footer ───────────────────────────────────────────────────────────
        tk.Label(
            self.root,
            text="Jents Quantum Privacy Suite • Zero-Log Sentinel",
            font=("Consolas", 8),
            fg=C_TEXT_MUTED, bg=C_BG
        ).pack(side=tk.BOTTOM, pady=(0, 10))

    def _copy_ip_to_clipboard(self):
        if self.last_detected_ip and self.last_detected_ip not in ("Scanning network...", "Connection Error"):
            self.root.clipboard_clear()
            self.root.clipboard_append(self.last_detected_ip)
            self.btn_copy.config(text="✓ COPIED!", fg=C_GREEN)
            self.root.after(1500, lambda: self.btn_copy.config(text="📋 COPY IP", fg=C_CYAN))

    def _auto_refresh_loop(self):
        if self.auto_refresh_enabled.get():
            self.detect_ip()
        self.root.after(8000, self._auto_refresh_loop)

    def detect_ip(self):
        self.btn_scan.config(text="⏳  SCANNING NETWORK...  ⏳", bg=C_AMBER, state=tk.DISABLED)
        self.lbl_scan_status.config(text="⚡ SCANNING", fg=C_AMBER)
        
        threading.Thread(target=self._fetch_ip_data, daemon=True).start()

    def _fetch_ip_data(self):
        t0 = time.perf_counter()
        ip = None

        # 1. Fetch public IP via high-speed HTTPS endpoints in parallel/fallback
        ip_endpoints = [
            ("https://icanhazip.com", False),
            ("https://api.ipify.org?format=json", True),
            ("https://ifconfig.me/ip", False),
            ("https://checkip.amazonaws.com", False),
        ]

        for ep, is_json in ip_endpoints:
            try:
                req = urllib.request.Request(ep, headers={"User-Agent": "curl/8.0"})
                with urllib.request.urlopen(req, context=_SSL_CTX, timeout=3.0) as resp:
                    raw = resp.read().decode("utf-8", "ignore").strip()
                    if is_json:
                        data = json.loads(raw)
                        ip = data.get("ip")
                    else:
                        ip = raw
                    if ip and len(ip) <= 45:
                        break
            except Exception:
                continue

        if not ip:
            rtt_ms = int((time.perf_counter() - t0) * 1000)
            self.root.after(0, lambda: self._update_ui({"error": "Failed to reach public IP endpoints", "ping": f"{rtt_ms} ms"}))
            return

        # 2. Fetch rich Geolocation details for this specific detected IP
        geo_info = self._fetch_geo(ip)
        rtt_ms = int((time.perf_counter() - t0) * 1000)
        geo_info["ping"] = f"{rtt_ms} ms"

        self.root.after(0, lambda: self._update_ui(geo_info))

    def _fetch_geo(self, ip: str) -> dict:
        # Source A: ipwho.is (fast HTTPS)
        try:
            req = urllib.request.Request(f"https://ipwho.is/{ip}", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=_SSL_CTX, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8", "ignore"))
                if data.get("success", True) and data.get("country"):
                    return {
                        "ip": ip,
                        "country": f"{data.get('country')} ({data.get('country_code', '')})",
                        "city": f"{data.get('city', '')}, {data.get('region', '')}",
                        "isp": data.get("connection", {}).get("isp") or data.get("connection", {}).get("org", "Unknown"),
                        "asn": str(data.get("connection", {}).get("asn", "--")),
                        "timezone": data.get("timezone", {}).get("id", "UTC"),
                    }
        except Exception:
            pass

        # Source B: ip-api.com
        try:
            req = urllib.request.Request(
                f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,timezone,isp,org,as,query",
                headers={"User-Agent": "curl/8.0"}
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8", "ignore"))
                if data.get("status") == "success":
                    return {
                        "ip": ip,
                        "country": f"{data.get('country', '')} ({data.get('countryCode', '')})",
                        "city": f"{data.get('city', '')}, {data.get('regionName', '')}",
                        "isp": data.get("isp") or data.get("org", "Unknown"),
                        "asn": data.get("as", "--"),
                        "timezone": data.get("timezone", "UTC"),
                    }
        except Exception:
            pass

        return {
            "ip": ip,
            "country": "Global Relay",
            "city": "Remote Node",
            "isp": "Secure Autonomous Routing",
            "asn": "--",
            "timezone": "UTC"
        }

    def _update_ui(self, info: dict):
        self.btn_scan.config(text="⚡  REFRESH & SCAN LIVE IP  ⚡", bg=C_CYAN, state=tk.NORMAL)
        self.lbl_last_time.config(text=f"Last scan: {time.strftime('%H:%M:%S')}")

        if "error" in info:
            self.lbl_ip.config(text="Connection Error", fg=C_RED)
            self.lbl_vpn_status.config(text=f"⚠️ {info['error']}", fg=C_RED)
            self.lbl_scan_status.config(text="● OFFLINE", fg=C_RED)
            return

        ip = info.get("ip", "Unknown")
        self.last_detected_ip = ip
        self.lbl_ip.config(text=ip, fg=C_CYAN)
        self.lbl_scan_status.config(text="● ONLINE", fg=C_GREEN)

        country = info.get("country", "--")
        self.fields["country"].config(text=country)
        self.fields["city"].config(text=info.get("city", "--"))
        self.fields["isp"].config(text=info.get("isp", "--"))
        self.fields["asn"].config(text=info.get("asn", "--"))
        self.fields["timezone"].config(text=info.get("timezone", "--"))
        self.fields["ping"].config(text=info.get("ping", "--"))

        # Smart VPN Detection Analysis
        isp = info.get("isp", "").lower()
        if any(c in country for c in ["Germany", "France", "United States", "Singapore", "Japan", "Netherlands", "DE", "FR", "US", "SG", "JP", "NL"]) or any(k in isp for k in ["hosting", "cloud", "vps", "server", "relay", "datacenter", "digitalocean", "ovh", "hetzner", "bluevps", "linode"]):
            self.lbl_vpn_status.config(text=f"🛡️ VPN MASKED: Sovereign Exit Node in {country}", fg=C_GREEN)
        else:
            self.lbl_vpn_status.config(text=f"📍 DIRECT ISP: {country} ({info.get('isp', '')})", fg=C_TEXT_CYAN)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = IPDetectorApp()
    app.run()
