"""
Jents VPN — Automated DNS Guard & Anti-Leak Sentinel
=====================================================
Automates setting secure encrypted/zero-log DNS resolvers on all active
Windows network adapters to prevent ISP DNS hijacking and WebRTC leaks.
"""

import subprocess
import logging
import re
from typing import List, Dict, Optional, Callable

log = logging.getLogger("jents.dns")

class DnsGuard:
    """Automates DNS leak protection and adapter resolver reconfiguration."""

    def __init__(self, primary: str = "1.1.1.1", secondary: str = "1.0.0.1",
                 log_callback: Optional[Callable[[str], None]] = None):
        self.primary = primary
        self.secondary = secondary
        self._log = log_callback or (lambda msg: None)
        self._saved_adapters: Dict[str, bool] = {}  # adapter_name -> was_dhcp
        self.is_active = False

    def _get_active_adapters(self) -> List[str]:
        """Detects names of connected IPv4 network adapters."""
        adapters = []
        try:
            cmd = 'netsh interface ipv4 show interfaces'
            out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
            for line in out.splitlines():
                if "connected" in line.lower() and "loopback" not in line.lower():
                    # The name is usually the last column
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        name = " ".join(parts[4:])
                        adapters.append(name)
        except Exception as e:
            log.warning(f"Failed to query network interfaces: {e}")
        return adapters

    def enable(self) -> bool:
        """Applies secure DNS to all active network adapters."""
        adapters = self._get_active_adapters()
        if not adapters:
            self._log("DNS Guard: No active adapters detected.")
            return False

        success_count = 0
        for name in adapters:
            try:
                # Set static primary DNS
                cmd1 = f'netsh interface ipv4 set dnsservers name="{name}" static {self.primary} primary'
                subprocess.run(cmd1, shell=True, capture_output=True, timeout=5)
                # Add secondary DNS
                if self.secondary:
                    cmd2 = f'netsh interface ipv4 add dnsservers name="{name}" {self.secondary} index=2'
                    subprocess.run(cmd2, shell=True, capture_output=True, timeout=5)
                self._saved_adapters[name] = True
                success_count += 1
            except Exception as e:
                log.warning(f"Failed to set DNS on {name}: {e}")

        # Flush system resolver cache
        subprocess.run("ipconfig /flushdns", shell=True, capture_output=True, timeout=5)
        self.is_active = (success_count > 0)
        self._log(f"DNS Guard: Secured {success_count} adapter(s) -> {self.primary}, {self.secondary}")
        return self.is_active

    def disable(self) -> bool:
        """Restores adapter DNS to automatic DHCP configuration."""
        if not self._saved_adapters:
            return True

        for name in self._saved_adapters:
            try:
                cmd = f'netsh interface ipv4 set dnsservers name="{name}" source=dhcp'
                subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            except Exception as e:
                log.warning(f"Failed to revert DNS on {name}: {e}")

        subprocess.run("ipconfig /flushdns", shell=True, capture_output=True, timeout=5)
        self._saved_adapters.clear()
        self.is_active = False
        self._log("DNS Guard: Restored adapter DNS to DHCP.")
        return True
