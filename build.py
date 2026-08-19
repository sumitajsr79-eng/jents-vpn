"""
Jents VPN — Automated Executable Builder
========================================
Compiles Jents into a standalone, portable Windows .exe
with embedded icons, configuration, and UAC manifest.
"""

import os
import subprocess
import sys

def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    entry_point = os.path.join(base_dir, "jents.py")
    icon_path = os.path.join(base_dir, "icons", "jents_icon.ico")
    config_path = os.path.join(base_dir, "config", "default_nodes.json")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=Jents_VPN",
        "--onefile",
        "--windowed",
        "--uac-admin",  # Request admin privileges automatically on launch
        f"--icon={icon_path}",
        f"--add-data={config_path};config",
        f"--add-data={icon_path};icons",
        entry_point
    ]

    print("[BUILD] Compiling Jents VPN into standalone executable...")
    result = subprocess.run(cmd, cwd=base_dir)
    if result.returncode == 0:
        dist_exe = os.path.join(base_dir, "dist", "Jents_VPN.exe")
        print(f"\n[SUCCESS] Jents VPN compiled successfully!")
        print(f"[EXECUTABLE] {dist_exe}")
    else:
        print("\n[FAILED] PyInstaller build encountered an error.")

if __name__ == "__main__":
    build()
