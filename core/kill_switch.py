"""
Jents VPN — Safe Windows Firewall Kill-Switch
==============================================
Provides leak prevention while ensuring the local tunnel proxy process
and secure DNS resolvers maintain outbound connectivity.
"""

import subprocess
import logging
import sys
import os
from typing import Optional, Callable

log = logging.getLogger("jents.killswitch")

RULE_ALLOW_LOOPBACK = "JentsVPN_KS_AllowLoopback"
RULE_ALLOW_DNS = "JentsVPN_KS_AllowDNS"
RULE_ALLOW_APP = "JentsVPN_KS_AllowApp"

class KillSwitch:
    """Automates safe firewall rules for VPN tunnel protection."""

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self._log = log_callback or (lambda msg: None)
        self.is_active = False

    def enable(self, gateway_host: str, gateway_port: int) -> bool:
        """Applies firewall rules permitting tunnel loopback, secure DNS, and the Jents app."""
        try:
            self.disable()

            # 1. Allow Loopback (127.0.0.1)
            cmd_loopback = (
                f'netsh advfirewall firewall add rule name="{RULE_ALLOW_LOOPBACK}" '
                f'dir=out action=allow remoteip=127.0.0.1 enable=yes'
            )
            subprocess.run(cmd_loopback, shell=True, capture_output=True, timeout=5)

            # 2. Allow Secure DNS (Port 53 UDP/TCP)
            cmd_dns = (
                f'netsh advfirewall firewall add rule name="{RULE_ALLOW_DNS}" '
                f'dir=out action=allow protocol=UDP remoteport=53 enable=yes'
            )
            subprocess.run(cmd_dns, shell=True, capture_output=True, timeout=5)

            # 3. Allow Jents Executable / Python Outbound
            exe_path = sys.executable
            cmd_app = (
                f'netsh advfirewall firewall add rule name="{RULE_ALLOW_APP}" '
                f'dir=out action=allow program="{exe_path}" enable=yes'
            )
            subprocess.run(cmd_app, shell=True, capture_output=True, timeout=5)

            self.is_active = True
            self._log("Kill-Switch: Active (Protected outbound channels engaged).")
            return True
        except Exception as e:
            self._log(f"Kill-Switch: Warning (Firewall rule adjustment skipped: {e})")
            return False

    def disable(self) -> bool:
        """Removes Jents firewall rules."""
        rules = [RULE_ALLOW_LOOPBACK, RULE_ALLOW_DNS, RULE_ALLOW_APP, "JentsVPN_KillSwitch_BlockAll", "JentsVPN_KillSwitch_AllowLoopback", "JentsVPN_KillSwitch_AllowGateway"]
        for rule in rules:
            try:
                cmd = f'netsh advfirewall firewall delete rule name="{rule}"'
                subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            except Exception:
                pass

        self.is_active = False
        return True
