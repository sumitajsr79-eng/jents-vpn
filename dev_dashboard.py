"""
Jents Quantum Developer & System Metrics Dashboard (v1.0)
==========================================================
Real-time Developer & System Command Center:
1. System Metrics (CPU total/per-core, RAM, Multi-Disk Storage, Network I/O)
2. Active Local Server Ports Scanner (PID, Process, Listening Address, 1-Click Open)
3. Multi-Repository Git Sentinel (Branch, Changes, Ahead/Behind, Last Commit, 1-Click Pull/Explorer)
4. Dual Interface: High-Performance Native Desktop HUD + Built-in Web Dashboard (http://127.0.0.1:5050)
"""

import sys
import os
import time
import json
import socket
import psutil
import subprocess
import threading
import http.server
import socketserver
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ── Cyber Deck Dark Palette ──────────────────────────────────────────────
C_BG          = "#020617"
C_PANEL       = "#070d1e"
C_CARD        = "#0a1329"
C_CARD_ALT    = "#111c38"
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

SCAN_DIRECTORIES = [
    r"D:\Sandbox",
    os.path.expanduser("~")
]

# ── System Metrics Engine ────────────────────────────────────────────────
class SystemMetricsEngine:
    def __init__(self):
        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = time.time()

    def get_metrics(self):
        # 1. CPU
        cpu_total = psutil.cpu_percent(interval=None)
        cpu_cores = psutil.cpu_percent(interval=None, percpu=True)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        
        # 2. RAM
        ram = psutil.virtual_memory()

        # 3. Disks
        disks = []
        for p in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(p.mountpoint)
                disks.append({
                    "device": p.device,
                    "mount": p.mountpoint,
                    "total_gb": round(usage.total / (1024**3), 1),
                    "used_gb": round(usage.used / (1024**3), 1),
                    "free_gb": round(usage.free / (1024**3), 1),
                    "percent": usage.percent
                })
            except Exception:
                pass

        # 4. Network I/O
        now = time.time()
        cur_net = psutil.net_io_counters()
        dt = max(0.1, now - self.last_net_time)
        down_bps = (cur_net.bytes_recv - self.last_net_io.bytes_recv) / dt
        up_bps   = (cur_net.bytes_sent - self.last_net_io.bytes_sent) / dt
        self.last_net_io = cur_net
        self.last_net_time = now

        # 5. Uptime
        boot_time = psutil.boot_time()
        uptime_sec = int(now - boot_time)
        hours = uptime_sec // 3600
        mins = (uptime_sec % 3600) // 60
        secs = uptime_sec % 60
        uptime_str = f"{hours:02d}h {mins:02d}m {secs:02d}s"

        return {
            "cpu_total": cpu_total,
            "cpu_cores": cpu_cores,
            "cpu_count": cpu_count,
            "cpu_freq_mhz": round(cpu_freq.current, 0) if cpu_freq else 0,
            "ram_percent": ram.percent,
            "ram_used_gb": round(ram.used / (1024**3), 1),
            "ram_total_gb": round(ram.total / (1024**3), 1),
            "ram_avail_gb": round(ram.available / (1024**3), 1),
            "disks": disks,
            "down_speed": f"{down_bps/1024.0:.1f} KB/s" if down_bps < 1048576 else f"{down_bps/1048576.0:.2f} MB/s",
            "up_speed": f"{up_bps/1024.0:.1f} KB/s" if up_bps < 1048576 else f"{up_bps/1048576.0:.2f} MB/s",
            "uptime": uptime_str,
            "proc_count": len(psutil.pids())
        }

# ── Active Ports Scanner ─────────────────────────────────────────────────
class ActivePortsScanner:
    @staticmethod
    def get_listening_ports():
        ports = []
        try:
            for conn in psutil.net_connections(kind="inet"):
                if conn.status == "LISTEN":
                    pname = "System"
                    if conn.pid:
                        try:
                            pname = psutil.Process(conn.pid).name()
                        except Exception:
                            pass

                    proto = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
                    ports.append({
                        "port": conn.laddr.port,
                        "ip": conn.laddr.ip,
                        "pid": conn.pid or 0,
                        "process": pname,
                        "proto": proto,
                        "status": "LISTEN"
                    })
        except Exception:
            pass

        # Sort by port number
        ports.sort(key=lambda x: x["port"])
        return ports

# ── Multi-Repository Git Scanner ─────────────────────────────────────────
class GitRepositoryScanner:
    @staticmethod
    def scan_repositories(search_paths=None):
        if not search_paths:
            search_paths = SCAN_DIRECTORIES

        discovered_paths = set()
        for base in search_paths:
            if not os.path.exists(base):
                continue
            
            # Check base
            if os.path.exists(os.path.join(base, ".git")):
                discovered_paths.add(os.path.abspath(base))
            
            # Check 1 level down
            try:
                for item in os.listdir(base):
                    sub = os.path.join(base, item)
                    if os.path.isdir(sub) and os.path.exists(os.path.join(sub, ".git")):
                        discovered_paths.add(os.path.abspath(sub))
            except Exception:
                pass

        results = []
        for path in discovered_paths:
            name = os.path.basename(path) or "Root"
            try:
                # 1. Branch
                b_res = subprocess.run("git rev-parse --abbrev-ref HEAD", cwd=path, shell=True, capture_output=True, text=True, timeout=3)
                branch = b_res.stdout.strip() or "HEAD"

                # 2. Status (untracked/modified)
                s_res = subprocess.run("git status --porcelain", cwd=path, shell=True, capture_output=True, text=True, timeout=3)
                lines = [l for l in s_res.stdout.splitlines() if l.strip()]
                modified = len(lines)

                # 3. Last commit
                c_res = subprocess.run('git log -1 --format="%h - %s (%cr)"', cwd=path, shell=True, capture_output=True, text=True, timeout=3)
                last_commit = c_res.stdout.strip() or "--"

                # 4. Ahead / Behind
                ahead, behind = 0, 0
                ab_res = subprocess.run("git rev-list --left-right --count HEAD...@{u}", cwd=path, shell=True, capture_output=True, text=True, timeout=3)
                ab_text = ab_res.stdout.strip()
                if "\t" in ab_text:
                    ahead, behind = map(int, ab_text.split("\t"))
                elif " " in ab_text:
                    ahead, behind = map(int, ab_text.split())

                # 5. Remote URL
                r_res = subprocess.run("git config --get remote.origin.url", cwd=path, shell=True, capture_output=True, text=True, timeout=3)
                remote_url = r_res.stdout.strip()

                is_clean = (modified == 0 and ahead == 0 and behind == 0)
                status_badge = "🟢 CLEAN" if is_clean else ("🟡 MODIFIED" if modified > 0 else "🔴 UNPUSHED")

                results.append({
                    "name": name,
                    "path": path,
                    "branch": branch,
                    "modified": modified,
                    "ahead": ahead,
                    "behind": behind,
                    "last_commit": last_commit,
                    "remote_url": remote_url,
                    "status_badge": status_badge,
                    "is_clean": is_clean
                })
            except Exception as e:
                results.append({
                    "name": name,
                    "path": path,
                    "branch": "Error",
                    "modified": 0,
                    "ahead": 0,
                    "behind": 0,
                    "last_commit": str(e),
                    "remote_url": "",
                    "status_badge": "⚠️ ERROR",
                    "is_clean": False
                })

        results.sort(key=lambda x: x["name"].lower())
        return results

# ── Built-in Web Server Dashboard ────────────────────────────────────────
HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>⚡ Jents Quantum Developer Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
  <style>
    body { background-color: #020617; font-family: 'Inter', sans-serif; color: #f8fafc; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    .glass-card { background: rgba(10, 19, 41, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(56, 189, 248, 0.2); }
  </style>
</head>
<body class="p-6 max-w-7xl mx-auto space-y-6">
  <!-- Header -->
  <header class="flex justify-between items-center border-b border-slate-800 pb-4">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-xl text-cyan-400">⚡</div>
      <div>
        <h1 class="text-xl font-black font-mono tracking-widest text-cyan-400">JENTS // DEVELOPER HUD</h1>
        <p class="text-xs text-slate-400 font-mono">Real-time System Metrics • Active Server Ports • Git Repositories</p>
      </div>
    </div>
    <div class="text-right font-mono text-xs text-slate-400">
      <div>UPTIME: <span id="uptime" class="text-cyan-300 font-bold">--</span></div>
      <div>PROCESSES: <span id="procs" class="text-emerald-400 font-bold">--</span></div>
    </div>
  </header>

  <!-- Section 1: System Metrics KPIs -->
  <div class="grid grid-cols-1 md:grid-cols-4 gap-4 font-mono text-xs">
    <div class="glass-card p-4 rounded-xl">
      <div class="text-slate-400 mb-1">⚡ CPU USAGE</div>
      <div id="cpuVal" class="text-2xl font-bold text-cyan-300">0%</div>
      <div id="cpuDetail" class="text-[10px] text-slate-500">-- cores</div>
      <div class="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
        <div id="cpuBar" class="bg-cyan-400 h-full w-0 transition-all duration-300"></div>
      </div>
    </div>

    <div class="glass-card p-4 rounded-xl">
      <div class="text-slate-400 mb-1">🧠 RAM UTILIZATION</div>
      <div id="ramVal" class="text-2xl font-bold text-emerald-300">0%</div>
      <div id="ramDetail" class="text-[10px] text-slate-500">-- / -- GB</div>
      <div class="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
        <div id="ramBar" class="bg-emerald-400 h-full w-0 transition-all duration-300"></div>
      </div>
    </div>

    <div class="glass-card p-4 rounded-xl">
      <div class="text-slate-400 mb-1">🚀 NETWORK THROUGHPUT</div>
      <div class="flex justify-between mt-1">
        <div><span class="text-slate-400">DOWN:</span> <span id="netDown" class="text-cyan-300 font-bold">0.0 KB/s</span></div>
        <div><span class="text-slate-400">UP:</span> <span id="netUp" class="text-amber-300 font-bold">0.0 KB/s</span></div>
      </div>
      <div class="text-[10px] text-slate-500 mt-2">Active Interface Real-Time I/O</div>
    </div>

    <div class="glass-card p-4 rounded-xl">
      <div class="text-slate-400 mb-1">💾 STORAGE DISKS</div>
      <div id="diskList" class="space-y-1 mt-1 text-[10px]"></div>
    </div>
  </div>

  <!-- Section 2: Active Server Ports & Git Repositories (2 Columns) -->
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
    <!-- Active Server Ports (5 cols) -->
    <div class="lg:col-span-5 glass-card p-4 rounded-xl flex flex-col">
      <div class="flex justify-between items-center border-b border-slate-800 pb-2 mb-3">
        <h3 class="font-mono font-bold text-sm text-cyan-400">📡 ACTIVE LISTENING PORTS</h3>
        <span id="portCount" class="text-xs font-mono text-slate-400">0 Ports</span>
      </div>
      <div class="overflow-y-auto max-h-96 space-y-1.5 font-mono text-xs pr-1" id="portList"></div>
    </div>

    <!-- Git Multi-Repository Monitor (7 cols) -->
    <div class="lg:col-span-7 glass-card p-4 rounded-xl flex flex-col">
      <div class="flex justify-between items-center border-b border-slate-800 pb-2 mb-3">
        <h3 class="font-mono font-bold text-sm text-emerald-400">📂 GIT MULTI-REPO SENTINEL</h3>
        <span id="repoCount" class="text-xs font-mono text-slate-400">0 Repositories</span>
      </div>
      <div class="overflow-y-auto max-h-96 space-y-2 font-mono text-xs pr-1" id="repoList"></div>
    </div>
  </div>

  <script>
    async function updateDashboard() {
      try {
        const res = await fetch('/api/data');
        const data = await res.json();

        // Metrics
        const m = data.metrics;
        document.getElementById('cpuVal').innerText = `${m.cpu_total}%`;
        document.getElementById('cpuDetail').innerText = `${m.cpu_count} Logical Threads • ${m.cpu_freq_mhz} MHz`;
        document.getElementById('cpuBar').style.width = `${m.cpu_total}%`;

        document.getElementById('ramVal').innerText = `${m.ram_percent}%`;
        document.getElementById('ramDetail').innerText = `${m.ram_used_gb} GB / ${m.ram_total_gb} GB (${m.ram_avail_gb} GB free)`;
        document.getElementById('ramBar').style.width = `${m.ram_percent}%`;

        document.getElementById('netDown').innerText = m.down_speed;
        document.getElementById('netUp').innerText = m.up_speed;
        document.getElementById('uptime').innerText = m.uptime;
        document.getElementById('procs').innerText = m.proc_count;

        // Disks
        const dBox = document.getElementById('diskList');
        dBox.innerHTML = m.disks.map(d => `
          <div>
            <div class="flex justify-between"><span>${d.device} (${d.mount})</span><span>${d.percent}% (${d.free_gb} GB free)</span></div>
            <div class="w-full bg-slate-800 h-1 rounded-full overflow-hidden mt-0.5"><div class="bg-cyan-400 h-full" style="width: ${d.percent}%"></div></div>
          </div>
        `).join('');

        // Ports
        const pBox = document.getElementById('portList');
        document.getElementById('portCount').innerText = `${data.ports.length} Active Ports`;
        pBox.innerHTML = data.ports.map(p => `
          <div class="p-2 rounded bg-slate-900/80 border border-slate-800 flex justify-between items-center hover:border-cyan-500/40">
            <div>
              <div class="font-bold text-cyan-300">Port :${p.port} <span class="text-[10px] text-slate-400">[${p.proto}]</span></div>
              <div class="text-[10px] text-slate-400">${p.process} (PID: ${p.pid})</div>
            </div>
            <a href="http://localhost:${p.port}" target="_blank" class="px-2 py-1 bg-cyan-500/20 text-cyan-300 rounded border border-cyan-500/40 text-[10px] hover:bg-cyan-500 hover:text-slate-950 font-bold">OPEN</a>
          </div>
        `).join('');

        // Git Repos
        const gBox = document.getElementById('repoList');
        document.getElementById('repoCount').innerText = `${data.repos.length} Repositories`;
        gBox.innerHTML = data.repos.map(r => `
          <div class="p-2.5 rounded bg-slate-900/80 border border-slate-800 space-y-1 hover:border-emerald-500/40">
            <div class="flex justify-between items-center">
              <span class="font-bold text-emerald-300 text-sm">📁 ${r.name} <span class="text-[11px] text-slate-400 font-normal">(${r.branch})</span></span>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${r.is_clean ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'}">${r.status_badge}</span>
            </div>
            <div class="text-[10px] text-slate-400 truncate">Last: ${r.last_commit}</div>
            <div class="flex justify-between items-center text-[10px] text-slate-500 pt-1">
              <span>Changes: <strong class="text-amber-400">${r.modified} files</strong> • Ahead: ${r.ahead} / Behind: ${r.behind}</span>
              <span class="text-slate-600 truncate max-w-xs">${r.path}</span>
            </div>
          </div>
        `).join('');

      } catch(e) {}
    }

    setInterval(updateDashboard, 1500);
    updateDashboard();
  </script>
</body>
</html>
"""

class DashboardHttpHandler(http.server.BaseHTTPRequestHandler):
    metrics_engine = SystemMetricsEngine()

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode("utf-8"))
        elif self.path == "/api/data":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            data = {
                "metrics": self.metrics_engine.get_metrics(),
                "ports": ActivePortsScanner.get_listening_ports(),
                "repos": GitRepositoryScanner.scan_repositories()
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

# ── Native Desktop HUD Application (Tkinter) ─────────────────────────────
class DevDashboardApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JENTS // QUANTUM DEVELOPER COMMAND CENTER")
        self.root.geometry("1180x760")
        self.root.minsize(1020, 680)
        self.root.configure(bg=C_BG)

        # Center Window
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(10, (sw - 1180) // 2)
        y = max(10, (sh - 760) // 2 - 20)
        self.root.geometry(f"1180x760+{x}+{y}")

        self.metrics_engine = SystemMetricsEngine()
        self.web_server_thread = None
        self.is_web_server_running = False

        self._init_styles()
        self._build_ui()
        self._start_background_pollers()

    def _init_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
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
        style.map("Treeview", background=[("selected", C_BLUE)], foreground=[("selected", C_TEXT_BRIGHT)])
        style.map("Treeview.Heading", background=[("active", C_CARD_ALT)])

    def _build_ui(self):
        # ── Top Header ────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=C_BG)
        header.pack(fill=tk.X, padx=18, pady=(12, 6))

        title_box = tk.Frame(header, bg=C_BG)
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box, text="⚡ JENTS DEVELOPER COMMAND CENTER",
            font=("Segoe UI", 16, "bold"),
            fg=C_CYAN, bg=C_BG
        ).pack(anchor="w")

        tk.Label(
            title_box, text="// REAL-TIME SYSTEM METRICS • ACTIVE SERVER PORTS • GIT MULTI-REPO SENTINEL",
            font=("Consolas", 8, "bold"),
            fg=C_GREEN, bg=C_BG
        ).pack(anchor="w")

        # Top Action Buttons
        btn_box = tk.Frame(header, bg=C_BG)
        btn_box.pack(side=tk.RIGHT)

        self.btn_web = tk.Button(
            btn_box, text="🌐 LAUNCH WEB DASHBOARD (Port 5050)",
            font=("Segoe UI", 8, "bold"),
            fg=C_BG, bg=C_CYAN,
            activebackground=C_GREEN, activeforeground=C_BG,
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
            command=self._launch_web_dashboard
        )
        self.btn_web.pack(side=tk.LEFT, padx=4)

        btn_refresh = tk.Button(
            btn_box, text="🔄 REFRESH ALL",
            font=("Segoe UI", 8, "bold"),
            fg=C_TEXT_BRIGHT, bg=C_PANEL,
            activebackground=C_CYAN, activeforeground=C_BG,
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
            command=self._refresh_all
        )
        btn_refresh.pack(side=tk.LEFT, padx=4)

        # ── KPI System Metrics Row ───────────────────────────────────────────
        kpi_row = tk.Frame(self.root, bg=C_BG)
        kpi_row.pack(fill=tk.X, padx=18, pady=(2, 10))

        self.kpi_cards = {}
        cards_cfg = [
            ("⚡ CPU USAGE", "0%", C_CYAN, "cpu"),
            ("🧠 RAM USAGE", "0%", C_GREEN, "ram"),
            ("🚀 NETWORK I/O", "0.0 KB/s", C_TEXT_CYAN, "net"),
            ("💾 DISK USAGE", "Scanning...", C_AMBER, "disk"),
            ("⏱️ SYSTEM UPTIME", "00:00:00", C_PURPLE, "uptime")
        ]

        for i, (lbl, default, col, key) in enumerate(cards_cfg):
            card = tk.Frame(kpi_row, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0 if i == 0 else 4, 0 if i == len(cards_cfg)-1 else 4))

            tk.Label(card, text=lbl, font=("Consolas", 7, "bold"), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor="w", padx=10, pady=(6, 1))
            val_lbl = tk.Label(card, text=default, font=("Consolas", 12, "bold"), fg=col, bg=C_CARD)
            val_lbl.pack(anchor="w", padx=10, pady=(0, 6))
            self.kpi_cards[key] = val_lbl

        # ── 2-Column Split: Ports Scanner & Git Sentinel ──────────────────────
        body_split = tk.Frame(self.root, bg=C_BG)
        body_split.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 10))

        # ── LEFT: Active Server Ports (480px) ─────────────────────────────────
        left_card = tk.Frame(body_split, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1, width=480)
        left_card.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_card.pack_propagate(False)

        # Port Header
        port_hdr = tk.Frame(left_card, bg=C_CARD)
        port_hdr.pack(fill=tk.X, padx=12, pady=(10, 4))

        tk.Label(port_hdr, text="📡 ACTIVE SERVER PORTS", font=("Consolas", 9, "bold"), fg=C_CYAN, bg=C_CARD).pack(side=tk.LEFT)
        self.lbl_port_count = tk.Label(port_hdr, text="0 Ports", font=("Consolas", 8), fg=C_TEXT_MUTED, bg=C_CARD)
        self.lbl_port_count.pack(side=tk.RIGHT)

        # Search box
        p_search_frame = tk.Frame(left_card, bg=C_CARD)
        p_search_frame.pack(fill=tk.X, padx=12, pady=(0, 6))
        tk.Label(p_search_frame, text="🔍 Filter:", font=("Segoe UI", 8), fg=C_TEXT_MUTED, bg=C_CARD).pack(side=tk.LEFT)
        self.port_filter_var = tk.StringVar()
        self.port_filter_var.trace_add("write", lambda *args: self._filter_ports())
        e_pfilter = tk.Entry(p_search_frame, textvariable=self.port_filter_var, font=("Segoe UI", 8), bg=C_PANEL, fg=C_TEXT_BRIGHT, relief=tk.FLAT)
        e_pfilter.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

        # Ports Treeview
        p_table_frame = tk.Frame(left_card, bg=C_CARD)
        p_table_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        p_cols = ("port", "proto", "process", "pid", "ip")
        self.port_tree = ttk.Treeview(p_table_frame, columns=p_cols, show="headings", selectmode="browse")

        self.port_tree.heading("port", text="PORT")
        self.port_tree.heading("proto", text="PROTO")
        self.port_tree.heading("process", text="PROCESS")
        self.port_tree.heading("pid", text="PID")
        self.port_tree.heading("ip", text="ADDRESS")

        self.port_tree.column("port", width=65, anchor="center")
        self.port_tree.column("proto", width=55, anchor="center")
        self.port_tree.column("process", width=140, anchor="w")
        self.port_tree.column("pid", width=60, anchor="center")
        self.port_tree.column("ip", width=110, anchor="center")

        p_scroll = ttk.Scrollbar(p_table_frame, orient="vertical", command=self.port_tree.yview)
        self.port_tree.configure(yscrollcommand=p_scroll.set)

        self.port_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        p_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Port action bar
        p_act_bar = tk.Frame(left_card, bg=C_CARD)
        p_act_bar.pack(fill=tk.X, padx=12, pady=(0, 10))

        btn_open_port = tk.Button(
            p_act_bar, text="🌐 OPEN IN BROWSER",
            font=("Segoe UI", 8, "bold"), fg=C_BG, bg=C_CYAN,
            relief=tk.FLAT, padx=8, pady=3, cursor="hand2",
            command=self._open_selected_port
        )
        btn_open_port.pack(side=tk.LEFT)

        btn_kill_proc = tk.Button(
            p_act_bar, text="🛑 KILL PROCESS",
            font=("Segoe UI", 8, "bold"), fg=C_RED, bg=C_PANEL,
            relief=tk.FLAT, padx=8, pady=3, cursor="hand2",
            command=self._kill_selected_process
        )
        btn_kill_proc.pack(side=tk.RIGHT)

        # ── RIGHT: Multi-Repository Git Sentinel ──────────────────────────────
        right_card = tk.Frame(body_split, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        right_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Git Header
        git_hdr = tk.Frame(right_card, bg=C_CARD)
        git_hdr.pack(fill=tk.X, padx=12, pady=(10, 4))

        tk.Label(git_hdr, text="📂 GIT MULTI-REPO SENTINEL", font=("Consolas", 9, "bold"), fg=C_GREEN, bg=C_CARD).pack(side=tk.LEFT)
        self.lbl_repo_count = tk.Label(git_hdr, text="0 Repositories", font=("Consolas", 8), fg=C_TEXT_MUTED, bg=C_CARD)
        self.lbl_repo_count.pack(side=tk.RIGHT)

        # Git Treeview
        g_table_frame = tk.Frame(right_card, bg=C_CARD)
        g_table_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        g_cols = ("status", "name", "branch", "modified", "sync", "commit")
        self.git_tree = ttk.Treeview(g_table_frame, columns=g_cols, show="headings", selectmode="browse")

        self.git_tree.heading("status", text="STATUS")
        self.git_tree.heading("name", text="REPOSITORY")
        self.git_tree.heading("branch", text="BRANCH")
        self.git_tree.heading("modified", text="CHANGES")
        self.git_tree.heading("sync", text="SYNC (AHEAD/BEHIND)")
        self.git_tree.heading("commit", text="LAST COMMIT")

        self.git_tree.column("status", width=95, anchor="center")
        self.git_tree.column("name", width=140, anchor="w")
        self.git_tree.column("branch", width=90, anchor="center")
        self.git_tree.column("modified", width=80, anchor="center")
        self.git_tree.column("sync", width=130, anchor="center")
        self.git_tree.column("commit", width=220, anchor="w")

        g_scroll = ttk.Scrollbar(g_table_frame, orient="vertical", command=self.git_tree.yview)
        self.git_tree.configure(yscrollcommand=g_scroll.set)

        self.git_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        g_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Git Action Bar
        g_act_bar = tk.Frame(right_card, bg=C_CARD)
        g_act_bar.pack(fill=tk.X, padx=12, pady=(0, 10))

        btn_pull = tk.Button(
            g_act_bar, text="⬇️ GIT PULL",
            font=("Segoe UI", 8, "bold"), fg=C_BG, bg=C_GREEN,
            relief=tk.FLAT, padx=8, pady=3, cursor="hand2",
            command=self._pull_selected_repo
        )
        btn_pull.pack(side=tk.LEFT, padx=(0, 4))

        btn_fetch = tk.Button(
            g_act_bar, text="🔄 GIT FETCH",
            font=("Segoe UI", 8, "bold"), fg=C_TEXT_BRIGHT, bg=C_PANEL,
            relief=tk.FLAT, padx=8, pady=3, cursor="hand2",
            command=self._fetch_selected_repo
        )
        btn_fetch.pack(side=tk.LEFT, padx=4)

        btn_terminal = tk.Button(
            g_act_bar, text="💻 TERMINAL",
            font=("Segoe UI", 8, "bold"), fg=C_CYAN, bg=C_PANEL,
            relief=tk.FLAT, padx=8, pady=3, cursor="hand2",
            command=self._open_repo_terminal
        )
        btn_terminal.pack(side=tk.LEFT, padx=4)

        btn_explorer = tk.Button(
            g_act_bar, text="📁 EXPLORER",
            font=("Segoe UI", 8, "bold"), fg=C_TEXT_BRIGHT, bg=C_PANEL,
            relief=tk.FLAT, padx=8, pady=3, cursor="hand2",
            command=self._open_repo_explorer
        )
        btn_explorer.pack(side=tk.LEFT, padx=4)

        btn_github = tk.Button(
            g_act_bar, text="🌐 OPEN GITHUB",
            font=("Segoe UI", 8, "bold"), fg=C_AMBER, bg=C_PANEL,
            relief=tk.FLAT, padx=8, pady=3, cursor="hand2",
            command=self._open_repo_github
        )
        btn_github.pack(side=tk.RIGHT)

        self.all_ports_data = []
        self.all_repos_data = []

    def _start_background_pollers(self):
        # 1. Fast Metrics Poller (1.5s)
        def _metrics_loop():
            while True:
                try:
                    m = self.metrics_engine.get_metrics()
                    self.root.after(0, lambda: self._update_metrics_ui(m))
                except Exception:
                    pass
                time.sleep(1.5)

        # 2. Port & Git Poller (4.0s)
        def _slow_loop():
            while True:
                try:
                    ports = ActivePortsScanner.get_listening_ports()
                    repos = GitRepositoryScanner.scan_repositories()
                    self.root.after(0, lambda: self._update_ports_and_repos_ui(ports, repos))
                except Exception:
                    pass
                time.sleep(4.0)

        threading.Thread(target=_metrics_loop, daemon=True).start()
        threading.Thread(target=_slow_loop, daemon=True).start()

    def _update_metrics_ui(self, m):
        self.kpi_cards["cpu"].config(text=f"{m['cpu_total']}% ({m['cpu_count']} cores)")
        self.kpi_cards["ram"].config(text=f"{m['ram_percent']}% ({m['ram_used_gb']}/{m['ram_total_gb']}GB)")
        self.kpi_cards["net"].config(text=f"↓ {m['down_speed']}  ↑ {m['up_speed']}")
        
        # Format primary disk
        if m["disks"]:
            d0 = m["disks"][0]
            self.kpi_cards["disk"].config(text=f"{d0['device']} {d0['percent']}% ({d0['free_gb']}GB free)")
        
        self.kpi_cards["uptime"].config(text=m["uptime"])

    def _update_ports_and_repos_ui(self, ports, repos):
        self.all_ports_data = ports
        self.all_repos_data = repos
        self._filter_ports()
        self._render_repos_tree()

    def _filter_ports(self):
        query = self.port_filter_var.get().lower().strip()
        self.port_tree.delete(*self.port_tree.get_children())

        filtered = []
        for p in self.all_ports_data:
            if query:
                searchable = f"{p['port']} {p['proto']} {p['process']} {p['pid']} {p['ip']}".lower()
                if query not in searchable:
                    continue
            filtered.append(p)
            self.port_tree.insert("", tk.END, values=(
                f":{p['port']}",
                p["proto"],
                p["process"],
                p["pid"],
                p["ip"]
            ))

        self.lbl_port_count.config(text=f"{len(filtered)} Ports")

    def _render_repos_tree(self):
        self.git_tree.delete(*self.git_tree.get_children())
        for r in self.all_repos_data:
            sync_str = f"Ahead {r['ahead']} / Behind {r['behind']}"
            changes_str = f"{r['modified']} files" if r['modified'] > 0 else "Clean"

            self.git_tree.insert("", tk.END, values=(
                r["status_badge"],
                r["name"],
                r["branch"],
                changes_str,
                sync_str,
                r["last_commit"]
            ))

        self.lbl_repo_count.config(text=f"{len(self.all_repos_data)} Repositories")

    def _get_selected_repo(self):
        sel = self.git_tree.selection()
        if not sel:
            messagebox.showwarning("Select Repository", "Please select a repository from the list.")
            return None
        idx = self.git_tree.index(sel[0])
        if idx < len(self.all_repos_data):
            return self.all_repos_data[idx]
        return None

    def _get_selected_port(self):
        sel = self.port_tree.selection()
        if not sel:
            messagebox.showwarning("Select Port", "Please select a port from the list.")
            return None
        values = self.port_tree.item(sel[0], "values")
        port_str = values[0].replace(":", "")
        return int(port_str) if port_str.isdigit() else None

    def _open_selected_port(self):
        port = self._get_selected_port()
        if port:
            webbrowser.open(f"http://localhost:{port}")

    def _kill_selected_process(self):
        sel = self.port_tree.selection()
        if not sel:
            messagebox.showwarning("Select Port", "Please select a port entry to kill.")
            return
        values = self.port_tree.item(sel[0], "values")
        pid_str = values[3]
        proc_name = values[2]
        if pid_str and pid_str != "0" and pid_str.isdigit():
            pid = int(pid_str)
            if messagebox.askyesno("Confirm Kill", f"Are you sure you want to terminate process '{proc_name}' (PID {pid})?"):
                try:
                    p = psutil.Process(pid)
                    p.terminate()
                    messagebox.showinfo("Process Terminated", f"Successfully terminated '{proc_name}' (PID {pid}).")
                    self._refresh_all()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to terminate process: {e}")

    def _pull_selected_repo(self):
        repo = self._get_selected_repo()
        if repo:
            try:
                res = subprocess.run("git pull", cwd=repo["path"], shell=True, capture_output=True, text=True, timeout=10)
                messagebox.showinfo(f"Git Pull: {repo['name']}", res.stdout or res.stderr or "Pull completed.")
                self._refresh_all()
            except Exception as e:
                messagebox.showerror("Git Pull Error", f"Failed to pull {repo['name']}: {e}")

    def _fetch_selected_repo(self):
        repo = self._get_selected_repo()
        if repo:
            try:
                res = subprocess.run("git fetch", cwd=repo["path"], shell=True, capture_output=True, text=True, timeout=10)
                messagebox.showinfo(f"Git Fetch: {repo['name']}", res.stdout or res.stderr or "Fetch completed.")
                self._refresh_all()
            except Exception as e:
                messagebox.showerror("Git Fetch Error", f"Failed to fetch {repo['name']}: {e}")

    def _open_repo_terminal(self):
        repo = self._get_selected_repo()
        if repo:
            subprocess.Popen(f'start powershell -NoExit -Command "Set-Location \\"{repo["path"]}\\""', shell=True)

    def _open_repo_explorer(self):
        repo = self._get_selected_repo()
        if repo:
            os.startfile(repo["path"])

    def _open_repo_github(self):
        repo = self._get_selected_repo()
        if repo:
            url = repo.get("remote_url", "")
            if url:
                if url.startswith("git@github.com:"):
                    url = "https://github.com/" + url[15:]
                if url.endswith(".git"):
                    url = url[:-4]
                webbrowser.open(url)
            else:
                messagebox.showinfo("No Remote", f"No GitHub remote URL found for '{repo['name']}'.")

    def _launch_web_dashboard(self):
        if not self.is_web_server_running:
            def _serve():
                try:
                    server = socketserver.TCPServer(("127.0.0.1", 5050), DashboardHttpHandler)
                    self.is_web_server_running = True
                    server.serve_forever()
                except Exception:
                    pass

            self.web_server_thread = threading.Thread(target=_serve, daemon=True)
            self.web_server_thread.start()
            time.sleep(0.5)

        webbrowser.open("http://127.0.0.1:5050")

    def _refresh_all(self):
        ports = ActivePortsScanner.get_listening_ports()
        repos = GitRepositoryScanner.scan_repositories()
        self._update_ports_and_repos_ui(ports, repos)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = DevDashboardApp()
    app.run()
