"""
Jents VPN — Entry Point
"""
import sys
import os
import io
import ctypes
import logging
import traceback

# ── Route stdout/stderr to a log file in the exe directory ──────────────────
# This is CRITICAL — PyInstaller windowed apps have no console, so all errors
# would be silently swallowed. Instead we write to a file we can read later.
LOG_FILE = os.path.join(
    os.path.dirname(sys.executable) if getattr(sys, "frozen", False)
    else os.path.dirname(os.path.abspath(__file__)),
    "jents_debug.log"
)

try:
    _log_fh = open(LOG_FILE, "w", encoding="utf-8", buffering=1)
    sys.stdout = _log_fh
    sys.stderr = _log_fh
except Exception:
    if sys.stdout is None:
        sys.stdout = io.StringIO()
    if sys.stderr is None:
        sys.stderr = io.StringIO()

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
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
            pass  # User declined — runs with user-level capabilities

def main():
    try:
        print("=== Jents VPN Starting ===")
        print(f"Frozen: {getattr(sys, 'frozen', False)}")
        print(f"Executable: {sys.executable}")

        request_admin()
        print("Admin check passed")

        # Add project root to sys.path
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)

        print(f"Base dir: {base_dir}")
        print(f"sys.path: {sys.path[:3]}")

        from ui.jents_window import JentsWindow
        print("JentsWindow imported OK")
        app = JentsWindow()
        print("JentsWindow created OK — starting mainloop")
        app.run()

    except Exception as e:
        print(f"FATAL ERROR: {e}")
        print(traceback.format_exc())
        sys.stdout.flush()
        # Show error in a messagebox so user knows something went wrong
        try:
            import tkinter.messagebox as mb
            mb.showerror("Jents VPN — Startup Error",
                         f"Fatal error starting Jents VPN:\n\n{e}\n\nCheck jents_debug.log for details.")
        except Exception:
            pass

if __name__ == "__main__":
    main()
