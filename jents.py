"""
Jents VPN — Aether God Quantum Suite (Native Desktop App)
=========================================================
Launches the Aether God-Tier Cybernetic HUD in a native, dedicated desktop window
using the embedded native webview engine, with direct Python API binding.
"""

import sys
import os
import io
import ctypes
import logging

from config.config_manager import ConfigManager
from core.auto_engine import JentsEngine

# Logging
LOG_FILE = os.path.join(
    os.path.dirname(sys.executable) if getattr(sys, "frozen", False)
    else os.path.dirname(os.path.abspath(__file__)),
    "jents_debug.log"
)

try:
    _log_fh = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
    sys.stdout = _log_fh
    sys.stderr = _log_fh
except Exception:
    if sys.stdout is None:
        sys.stdout = io.StringIO()
    if sys.stderr is None:
        sys.stderr = io.StringIO()

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def request_admin():
    """Requests administrative privileges if not already elevated."""
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

class VpnJsApi:
    """Direct high-speed JS-to-Python bridge inside the native desktop window."""

    def __init__(self, engine: JentsEngine):
        self.engine = engine

    def connect(self, region="auto"):
        region_map = {"auto": 0, "de": 1, "fr": 2, "us": 3, "sg": 4, "jp": 5}
        idx = region_map.get(region, 0)
        self.engine.select_preset(idx)
        self.engine.trigger_connect()
        return {"status": "connecting", "region": region}

    def disconnect(self):
        self.engine.trigger_disconnect()
        return {"status": "disconnecting"}

    def get_status(self):
        state = self.engine.state
        is_conn = (state == "CONNECTED")
        snap = self.engine.stats.get_snapshot() if hasattr(self.engine, "stats") else {}
        down_mbps = round((snap.get("raw_down_kbps", 0.0) / 1024.0) * 8.0, 2)
        up_mbps = round((snap.get("raw_up_kbps", 0.0) / 1024.0) * 8.0, 2)
        active_gw = self.engine.active_gateway or {}
        return {
            "isConnected": is_conn,
            "state": state,
            "server": active_gw.get("name", "Quantum Auto-Turbo"),
            "flag": active_gw.get("flag", "⚡"),
            "activeIp": active_gw.get("remote_ip", "103.88.134.21"),
            "downMbps": max(0.5, down_mbps) if is_conn else 0.0,
            "upMbps": max(0.2, up_mbps) if is_conn else 0.0,
            "ping": active_gw.get("latency_ms", 18),
            "uptime": snap.get("uptime", "00:00:00")
        }

def main():
    print("=== JENTS AETHER GOD DESKTOP SUITE STARTING ===")
    request_admin()

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_dir = sys._MEIPASS
    elif getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    cfg = ConfigManager()
    engine = JentsEngine(config_manager=cfg)
    api = VpnJsApi(engine)

    html_path = os.path.join(base_dir, "ui_web", "index.html")
    if not os.path.exists(html_path):
        # Fallback to local search
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_web", "index.html")

    try:
        import webview
        # Create a dedicated, native, dark-themed cyberpunk desktop window
        window = webview.create_window(
            title="AETHER // GOD-TIER QUANTUM VPN",
            url=html_path,
            js_api=api,
            width=1180,
            height=780,
            resizable=True,
            min_size=(900, 600),
            background_color="#020617"
        )
        print("Launching native Aether God Desktop Window...")
        webview.start(debug=False)
    except Exception as e:
        print(f"Native WebView error: {e}. Falling back to native canvas UI...")
        try:
            from ui.jents_window import JentsWindow
            app = JentsWindow()
            app.run()
        except Exception as e2:
            print(f"Fallback UI error: {e2}")
    finally:
        engine._cleanup()

if __name__ == "__main__":
    main()
