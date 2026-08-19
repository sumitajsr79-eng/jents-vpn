"""
Jents VPN — Aether God Quantum Suite
====================================
Launches the full Aether God-Tier Cybernetic Masterpiece UI
connected to the underlying high-speed autonomous Python VPN engine.
"""

import sys
import os
import io
import ctypes
import logging
import webbrowser
import time
import threading

from config.config_manager import ConfigManager
from core.auto_engine import JentsEngine
from core.api_bridge import ApiBridgeServer

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

def main():
    print("=== JENTS // AETHER GOD-TIER VPN STARTING ===")
    request_admin()

    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    cfg = ConfigManager()
    engine = JentsEngine(config_manager=cfg)

    # Start API Bridge Server on localhost:4099
    ui_path = os.path.join(base_dir, "ui_web")
    bridge = ApiBridgeServer(engine=engine, port=4099, ui_dir=ui_path)
    bridge.start()
    print("Aether God API Bridge active on http://127.0.0.1:4099/")

    # Launch HUD in default browser / webview
    time.sleep(0.3)
    webbrowser.open("http://127.0.0.1:4099/")

    print("Interface launched! Press Ctrl+C or close terminal to stop.")
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        bridge.stop()
        engine._cleanup()

if __name__ == "__main__":
    main()
