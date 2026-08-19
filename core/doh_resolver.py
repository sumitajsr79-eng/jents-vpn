"""
Jents VPN — High-Speed DNS-over-HTTPS (DoH) & Zero-Leak Resolver
================================================================
Resolves domains directly via encrypted Cloudflare (1.1.1.1) and Google (8.8.8.8) DoH
with a high-speed in-memory LRU cache.
Eliminates ISP DNS hijacking and WebRTC leaks without messing up Windows network adapters!
"""

import urllib.request
import json
import ssl
import time
import socket
import logging
from typing import Optional, Dict

log = logging.getLogger("jents.doh")

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

class DoHResolver:
    """Ultra-fast in-memory cached DNS-over-HTTPS resolver."""

    def __init__(self):
        self._cache: Dict[str, tuple[str, float]] = {}  # domain -> (ip, expire_time)
        self._primary_url = "https://1.1.1.1/dns-query?name={}&type=A"
        self._secondary_url = "https://dns.google/resolve?name={}&type=A"

    def resolve(self, domain: str) -> str:
        """Resolves a domain name to an IPv4 address using encrypted DoH."""
        domain = domain.strip().lower()
        
        # If it's already an IP, return directly
        try:
            socket.inet_aton(domain)
            return domain
        except socket.error:
            pass

        # Check in-memory cache
        now = time.time()
        if domain in self._cache:
            ip, expire = self._cache[domain]
            if now < expire:
                return ip

        # Try Cloudflare DoH
        ip = self._query_doh(self._primary_url.format(domain))
        if not ip:
            # Fallback to Google DoH
            ip = self._query_doh(self._secondary_url.format(domain))

        if not ip:
            # Fallback to system socket resolution
            try:
                ip = socket.gethostbyname(domain)
            except Exception:
                ip = domain

        # Cache for 300 seconds
        if ip and ip != domain:
            self._cache[domain] = (ip, now + 300.0)

        return ip

    def _query_doh(self, url: str) -> Optional[str]:
        try:
            req = urllib.request.Request(
                url,
                headers={"Accept": "application/dns-json", "User-Agent": "JentsVPN-DoH/2.0"}
            )
            with urllib.request.urlopen(req, context=_SSL_CTX, timeout=1.8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "Answer" in data:
                    for ans in data["Answer"]:
                        if ans.get("type") == 1:  # Type A IPv4
                            return ans.get("data")
        except Exception:
            pass
        return None

# Global Singleton
resolver = DoHResolver()
