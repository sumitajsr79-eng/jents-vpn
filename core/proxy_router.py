"""
Jents VPN — Windows System Proxy & Route Manager
=================================================
Sets BOTH WinINet (registry) AND WinHTTP (netsh) proxy to guarantee
ALL Windows applications — Chrome, Edge, Firefox WinHTTP mode,
elevated processes, command-line tools — route through the tunnel.
"""

import winreg
import subprocess
import ctypes
import logging
from typing import Optional, Callable

log = logging.getLogger("jents.router")

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"


def _run(cmd: str, timeout: int = 6) -> bool:
    """Run a shell command silently. Returns True on success."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, timeout=timeout
        )
        return result.returncode == 0
    except Exception:
        return False


def notify_wininet():
    """Broadcasts internet settings change so all WinINet consumers reload immediately."""
    try:
        INTERNET_OPTION_SETTINGS_CHANGED = 39
        INTERNET_OPTION_REFRESH = 37
        fn = ctypes.windll.Wininet.InternetSetOptionW
        fn(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
        fn(0, INTERNET_OPTION_REFRESH, 0, 0)
    except Exception:
        pass


class ProxyRouter:
    """
    Sets Windows system proxy on BOTH WinINet and WinHTTP layers.

    WinINet → affects: Chrome, Edge (Chromium), IE, all UWP apps
    WinHTTP → affects: elevated/admin processes, PowerShell, many Win32 apps
    """

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self._log = log_callback or (lambda msg: None)
        self.is_active = False
        self._saved_enable = None
        self._saved_server = None
        self._saved_override = None

    def enable(self, local_port: int) -> bool:
        """Points all Windows system traffic at 127.0.0.1:local_port."""
        proxy_str = f"127.0.0.1:{local_port}"
        success = True

        # ── 1. WinINet via Registry ─────────────────────────────────────────
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_ALL_ACCESS
            ) as key:
                # Save originals for clean restore
                try:
                    self._saved_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
                except FileNotFoundError:
                    self._saved_enable = 0
                try:
                    self._saved_server, _ = winreg.QueryValueEx(key, "ProxyServer")
                except FileNotFoundError:
                    self._saved_server = ""
                try:
                    self._saved_override, _ = winreg.QueryValueEx(key, "ProxyOverride")
                except FileNotFoundError:
                    self._saved_override = ""

                winreg.SetValueEx(key, "ProxyEnable",   0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "ProxyServer",   0, winreg.REG_SZ,    proxy_str)
                winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ,
                                  "<local>;localhost;127.0.0.1;::1")

            notify_wininet()
            self._log(f"WinINet: Proxy -> {proxy_str}")
        except PermissionError:
            self._log("WinINet: Permission denied — run as Administrator.")
            success = False
        except Exception as e:
            self._log(f"WinINet: Registry error: {e}")
            success = False

        # ── 2. WinHTTP via netsh (catches elevated/admin processes) ─────────
        # This is the CRITICAL layer that Chrome/Edge use when running elevated.
        winhttp_ok = _run(
            f'netsh winhttp set proxy proxy-server="{proxy_str}" '
            f'bypass-list="<local>;localhost;127.0.0.1"'
        )
        if winhttp_ok:
            self._log(f"WinHTTP: Proxy -> {proxy_str}")
        else:
            self._log("WinHTTP: Could not set netsh proxy (non-fatal, WinINet still active)")

        # ── 3. Flush DNS cache ──────────────────────────────────────────────
        _run("ipconfig /flushdns")

        self.is_active = success
        self._log(f"System Router: All traffic -> 127.0.0.1:{local_port}")
        return success

    def disable(self) -> bool:
        """Restores original WinINet and WinHTTP proxy settings exactly."""
        restored = True

        # ── 1. Restore WinINet Registry ─────────────────────────────────────
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_ALL_ACCESS
            ) as key:
                winreg.SetValueEx(
                    key, "ProxyEnable", 0, winreg.REG_DWORD,
                    self._saved_enable if self._saved_enable is not None else 0
                )
                winreg.SetValueEx(
                    key, "ProxyServer", 0, winreg.REG_SZ,
                    self._saved_server if self._saved_server is not None else ""
                )
                winreg.SetValueEx(
                    key, "ProxyOverride", 0, winreg.REG_SZ,
                    self._saved_override if self._saved_override is not None else ""
                )
            notify_wininet()
            self._log("WinINet: Original settings restored.")
        except Exception as e:
            self._log(f"WinINet: Restore failed: {e}")
            restored = False

        # ── 2. Restore WinHTTP to Direct ────────────────────────────────────
        winhttp_ok = _run("netsh winhttp reset proxy")
        if winhttp_ok:
            self._log("WinHTTP: Reset to direct (no proxy).")
        else:
            self._log("WinHTTP: Reset failed (non-fatal).")

        # ── 3. Flush DNS again ──────────────────────────────────────────────
        _run("ipconfig /flushdns")

        self.is_active = False
        self._log("System Router: Original network settings restored.")
        return restored

    def emergency_restore(self):
        """
        Hard emergency reset — called on startup and crash.
        Disables all proxy without needing saved state.
        """
        # WinINet
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_ALL_ACCESS
            ) as key:
                winreg.SetValueEx(key, "ProxyEnable",   0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "ProxyServer",   0, winreg.REG_SZ,    "")
                winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ,    "")
            notify_wininet()
        except Exception:
            pass
        # WinHTTP
        _run("netsh winhttp reset proxy")
        _run("ipconfig /flushdns")
        self.is_active = False
