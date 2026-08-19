"""
Jents VPN — 100% Native Windows Desktop Client
===============================================
Zero-localhost, zero-browser native desktop application with full Cyberpunk HUD,
60 FPS Quantum Arc Reactor core, live telemetry, and autonomous tunnel engine.
"""

import sys
import os
import io
import ctypes
import logging

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
    print("=== JENTS NATIVE DESKTOP VPN STARTING ===")
    request_admin()

    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    # Launch 100% Native Desktop Window (No browser / No localhost)
    from ui.jents_window import JentsWindow
    app = JentsWindow()
    app.run()

if __name__ == "__main__":
    main()
