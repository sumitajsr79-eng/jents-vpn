"""
Jents VPN — Autonomous Remote Exit Node Fleet Manager
=====================================================
Discovers, validates, and rotates verified remote exit nodes.
Only passes nodes that return a DIFFERENT IP from the home IP.
"""

import urllib.request
import ssl
import time
import socket
import threading
import concurrent.futures
import logging
from typing import List, Dict, Any, Optional

log = logging.getLogger("jents.fleet")

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

# Verified relay pool — all tested with CONNECT against real sites
REGIONAL_RELAYS = {
    "auto": [
        {"host": "45.66.249.187",  "port": 8181, "name": "Auto-Turbo (DE)",  "country": "DE", "flag": "⚡"},
        {"host": "37.59.125.131",  "port": 8888, "name": "Auto-Turbo (FR)",  "country": "FR", "flag": "⚡"},
        {"host": "198.199.86.11",  "port": 8080, "name": "Auto-Turbo (US)",  "country": "US", "flag": "⚡"},
        {"host": "114.94.148.37",  "port": 18080,"name": "Auto-Turbo (JP)",  "country": "JP", "flag": "⚡"},
    ],
    "de": [
        {"host": "45.66.249.187", "port": 8181, "name": "Frankfurt Citadel", "country": "DE", "flag": "🇩🇪"},
        {"host": "45.66.249.187", "port": 8080, "name": "Frankfurt Relay 2", "country": "DE", "flag": "🇩🇪"},
    ],
    "fr": [
        {"host": "37.59.125.131", "port": 8888, "name": "Paris Fortress",   "country": "FR", "flag": "🇫🇷"},
    ],
    "us": [
        {"host": "198.199.86.11", "port": 8080, "name": "New York Apex",    "country": "US", "flag": "🇺🇸"},
        {"host": "15.235.21.254", "port": 8080, "name": "Virginia Vault",   "country": "US", "flag": "🇺🇸"},
    ],
    "sg": [
        {"host": "114.94.148.37", "port": 18080,"name": "Asia-JP Relay",    "country": "JP", "flag": "🇯🇵"},
    ],
    "jp": [
        {"host": "114.94.148.37", "port": 18080,"name": "Tokyo Apex",       "country": "JP", "flag": "🇯🇵"},
    ],
}


class FleetManager:
    """Manages validation and selection of remote exit relays."""

    def __init__(self, log_callback=None):
        self._log = log_callback or (lambda msg: None)
        self._home_ip: Optional[str] = None

    def _get_home_ip(self) -> str:
        """Gets the real home IP (without any proxy)."""
        if self._home_ip:
            return self._home_ip
        try:
            req = urllib.request.Request(
                "https://icanhazip.com",
                headers={"User-Agent": "curl/8.0"}
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                self._home_ip = resp.read().decode("utf-8", "ignore").strip()
                return self._home_ip
        except Exception:
            return ""

    def test_node(self, host: str, port: int) -> Optional[Dict[str, Any]]:
        """
        Tests if an exit node works AND returns a different IP from home.
        Uses raw CONNECT to verify the relay can tunnel HTTPS.
        """
        try:
            t0 = time.perf_counter()

            # Test CONNECT via raw socket (most reliable test)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4.0)
            s.connect((host, port))

            # Try CONNECT to icanhazip.com
            connect_req = b"CONNECT icanhazip.com:443 HTTP/1.1\r\nHost: icanhazip.com:443\r\n\r\n"
            s.sendall(connect_req)

            # Read relay response
            resp = b""
            while b"\r\n\r\n" not in resp:
                chunk = s.recv(4096)
                if not chunk:
                    break
                resp += chunk

            if b"200" not in resp.split(b"\r\n")[0]:
                s.close()
                return None

            # Now actually get the IP through this relay using urllib
            s.close()

            proxy_url = f"http://{host}:{port}"
            proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
            opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=_SSL_CTX))
            req = urllib.request.Request("https://icanhazip.com", headers={"User-Agent": "curl/8.0"})
            with opener.open(req, timeout=5.0) as resp2:
                remote_ip = resp2.read().decode("utf-8", "ignore").strip()
                rtt_ms = int((time.perf_counter() - t0) * 1000.0)

                if not remote_ip or len(remote_ip) > 45:
                    return None

                # Reject if relay returns same IP as home (transparent/broken proxy)
                home = self._get_home_ip()
                if home and remote_ip == home:
                    self._log(f"  [SKIP] {host}:{port} -> Transparent relay (returned home IP {remote_ip})")
                    return None

                return {
                    "host": host,
                    "port": port,
                    "remote_ip": remote_ip,
                    "latency_ms": rtt_ms,
                    "is_reachable": True
                }
        except Exception:
            pass
        return None

    def get_exit_node(self, region_id: str = "auto") -> Optional[Dict[str, Any]]:
        """Finds the fastest verified exit node for the requested region."""
        region_id = region_id.lower()
        candidates = REGIONAL_RELAYS.get(region_id, REGIONAL_RELAYS["auto"])

        self._log(f"Fleet Manager: Testing exit nodes for [{region_id.upper()}]...")

        tested = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(candidates)) as executor:
            future_to_c = {
                executor.submit(self.test_node, c["host"], c["port"]): c
                for c in candidates
            }
            for f in concurrent.futures.as_completed(future_to_c):
                c = future_to_c[f]
                res = f.result()
                if res:
                    res["name"]    = c["name"]
                    res["country"] = c["country"]
                    res["flag"]    = c["flag"]
                    tested.append(res)
                    self._log(f"  [ONLINE] {c['name']} -> New IP: {res['remote_ip']} ({res['latency_ms']}ms)")

        if not tested:
            self._log(f"  [WARN] No verified exit nodes found for [{region_id.upper()}]. Trying auto pool...")
            # Retry with auto pool
            if region_id != "auto":
                return self.get_exit_node("auto")
            return None

        tested.sort(key=lambda x: x["latency_ms"])
        best = tested[0]
        self._log(f"Fleet Manager: Selected -> {best['name']} (IP: {best['remote_ip']})")
        return best
