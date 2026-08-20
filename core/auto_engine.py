"""
Jents VPN — Quantum Autonomous Master Engine (Remote Chained Edition)
=====================================================================
Connects through verified global exit nodes so the external IP address actually changes.
Performs live self-test before activating Windows system proxy.
"""

import threading
import time
import logging
import atexit
import urllib.request
import ssl
from typing import Optional, Callable, Dict, Any

from core.crypto_session import CryptoSession
from core.fleet_manager import FleetManager
from core.tunnel_gateway import TunnelGateway
from core.proxy_router import ProxyRouter
from core.stats_engine import StatsEngine
from config.config_manager import ConfigManager

log = logging.getLogger("jents.engine")

class ConnectionState:
    DISCONNECTED  = "DISCONNECTED"
    PROBING       = "PROBING"
    SECURING      = "SECURING"
    CONNECTED     = "CONNECTED"
    DISCONNECTING = "DISCONNECTING"
    ERROR         = "ERROR"

GATEWAY_PRESETS = [
    {"id": "auto", "name": "Auto-Turbo Fastest",        "flag": "⚡"},
    {"id": "de",   "name": "Germany (Frankfurt)",       "flag": "🇩🇪"},
    {"id": "us",   "name": "United States (Richmond)",  "flag": "🇺🇸"},
    {"id": "nl",   "name": "Netherlands (Amsterdam)",   "flag": "🇳🇱"},
    {"id": "fr",   "name": "France (Paris)",            "flag": "🇫🇷"},
    {"id": "sg",   "name": "Singapore / Asia Turbo",    "flag": "🇸🇬"},
    {"id": "jp",   "name": "Japan / East Asia",         "flag": "🇯🇵"},
]

_TEST_SSL = ssl.create_default_context()
_TEST_SSL.check_hostname = False
_TEST_SSL.verify_mode    = ssl.CERT_NONE

class JentsEngine:
    """Single-click VPN engine connecting through verified remote exit nodes."""

    def __init__(self, config_manager: ConfigManager,
                 state_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
                 log_callback:   Optional[Callable[[str], None]] = None):
        self.cfg            = config_manager
        self.state_callback = state_callback or (lambda s, m: None)
        self.log_callback   = log_callback   or (lambda m: None)

        self.state         = ConnectionState.DISCONNECTED
        self.crypto_session: Optional[CryptoSession] = None
        self.fleet_manager = FleetManager(log_callback=self.log_callback)
        self.stats         = StatsEngine()
        self.local_port    = self.cfg.get("local_port", 1088)

        self.tunnel        = TunnelGateway(
            local_port      = self.local_port,
            stats_callback  = self.stats.record_traffic,
            log_callback    = self.log_callback
        )
        self.proxy_router  = ProxyRouter(log_callback=self.log_callback)
        self.active_gateway: Optional[Dict[str, Any]] = None
        self.selected_preset_index = 0

        atexit.register(self._emergency_cleanup)
        self._startup_cleanup()

    def _startup_cleanup(self):
        """Removes any leftover proxy from a previous session."""
        self.proxy_router.emergency_restore()
        self.tunnel.stop()

    def _emergency_cleanup(self):
        try:
            self.proxy_router.emergency_restore()
            self.tunnel.stop()
        except Exception:
            pass

    def select_preset(self, index: int):
        if 0 <= index < len(GATEWAY_PRESETS):
            self.selected_preset_index = index

    def trigger_connect(self):
        if self.state not in (ConnectionState.DISCONNECTED, ConnectionState.ERROR):
            return
        threading.Thread(target=self._connect_sequence, daemon=True).start()

    def trigger_disconnect(self):
        if self.state == ConnectionState.DISCONNECTED:
            return
        threading.Thread(target=self._disconnect_sequence, daemon=True).start()

    def _set_state(self, state: str, meta: Optional[Dict[str, Any]] = None):
        self.state = state
        payload = meta or {}
        if self.active_gateway:
            payload["gateway"]  = self.active_gateway
        if self.crypto_session:
            payload["crypto"]   = self.crypto_session.get_session_info()
        self.state_callback(self.state, payload)

    def _connect_sequence(self):
        try:
            self.log_callback("Engine: Initiating remote VPN connection...")
            self._set_state(ConnectionState.PROBING)

            # 1. Ephemeral crypto session
            self.crypto_session = CryptoSession()
            self.log_callback(f"Crypto: Session ready ({self.crypto_session.cipher_suite})")

            # 2. Find and validate remote exit node
            preset = GATEWAY_PRESETS[self.selected_preset_index]
            region_id = preset["id"]
            best_node = self.fleet_manager.get_exit_node(region_id)
            if not best_node:
                raise RuntimeError("No remote exit node responded. Check internet connection.")

            self.active_gateway = best_node
            self._set_state(ConnectionState.SECURING)

            # 3. Spool local tunnel chained to remote exit node
            self.tunnel.stop()
            time.sleep(0.15)
            if not self.tunnel.start(best_node):
                raise RuntimeError(f"Cannot bind local port {self.local_port}.")

            time.sleep(0.3)

            # 4. Mandatory Self-Test: verify external IP changed through tunnel
            self.log_callback("Self-test: Verifying remote IP change...")
            ok, new_ip, rtt_ms = self._self_test_tunnel()
            if not ok:
                self.tunnel.stop()
                raise RuntimeError(f"Remote tunnel test failed: {new_ip}")

            self.log_callback(f"Self-test: OK! Verified External IP -> {new_ip} ({rtt_ms}ms)")
            self.active_gateway["remote_ip"] = new_ip

            # 5. Apply Windows system proxy
            if not self.proxy_router.enable(self.local_port):
                self.tunnel.stop()
                raise RuntimeError("Could not set Windows system proxy.")

            # 6. Start telemetry
            self.stats.start()

            # 7. CONNECTED
            flag = best_node.get("flag", "🌐")
            loc_name = best_node.get("name", "Remote VPN")
            self._set_state(ConnectionState.CONNECTED, {
                "ip":       new_ip,
                "location": loc_name,
                "flag":     flag,
                "ping":     f"{rtt_ms} ms"
            })
            self.log_callback(f"Jents VPN: CONNECTED! New IP: {new_ip} ({loc_name})")

        except Exception as e:
            log.exception("Connection failed")
            self.log_callback(f"ERROR: {e}")
            self._cleanup()
            self._set_state(ConnectionState.ERROR, {"error": str(e)})

    def _self_test_tunnel(self) -> tuple[bool, str, int]:
        """Verifies that traffic through 127.0.0.1 changes the external IP."""
        proxy_url = f"http://127.0.0.1:{self.local_port}"
        proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
        opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=_TEST_SSL))

        for url in ["https://icanhazip.com", "http://icanhazip.com"]:
            try:
                t0 = time.perf_counter()
                req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
                with opener.open(req, timeout=5.0) as resp:
                    remote_ip = resp.read().decode("utf-8", "ignore").strip()
                    rtt = int((time.perf_counter() - t0) * 1000)
                    if remote_ip:
                        return True, remote_ip, rtt
            except Exception as e:
                last_err = str(e)
                continue
        return False, last_err, 0

    def _disconnect_sequence(self):
        self._set_state(ConnectionState.DISCONNECTING)
        self.log_callback("Engine: Disconnecting and restoring your original IP...")
        self._cleanup()
        self._set_state(ConnectionState.DISCONNECTED)
        self.log_callback("Engine: Disconnected. Original IP restored.")

    def _cleanup(self):
        self.proxy_router.disable()
        self.tunnel.stop()
        self.stats.stop()
        self.active_gateway = None
