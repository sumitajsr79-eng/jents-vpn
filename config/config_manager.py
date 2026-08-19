"""
Jents VPN — Configuration Manager
==================================
Handles loading, caching, and persisting runtime configuration,
server fleet lists, and user state with robust fallbacks.
"""

import json
import os
import logging
from typing import Dict, Any, List

log = logging.getLogger("jents.config")

class ConfigManager:
    """Manages Jents configuration and server gateways."""

    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = config_dir
        self.default_file = os.path.join(self.config_dir, "default_nodes.json")
        self.user_file = os.path.join(self.config_dir, "user_config.json")
        self._data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """Loads default config and overlays user customizations if present."""
        data = {
            "version": "1.0.0",
            "app_name": "Jents VPN",
            "kill_switch_enabled": True,
            "dns_guard_enabled": True,
            "primary_dns": "1.1.1.1",
            "secondary_dns": "1.0.0.1",
            "local_port": 1088,
            "probe_timeout_ms": 1200,
            "gateways": []
        }

        if os.path.exists(self.default_file):
            try:
                with open(self.default_file, "r", encoding="utf-8") as f:
                    defaults = json.load(f)
                    data.update(defaults)
            except Exception as e:
                log.warning(f"Failed to parse default config: {e}")

        if os.path.exists(self.user_file):
            try:
                with open(self.user_file, "r", encoding="utf-8") as f:
                    user_cfg = json.load(f)
                    data.update(user_cfg)
            except Exception as e:
                log.warning(f"Failed to parse user config: {e}")

        return data

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value
        self.save()

    def get_gateways(self) -> List[Dict[str, Any]]:
        return self._data.get("gateways", [])

    def save(self):
        """Persists current state to user_config.json."""
        try:
            with open(self.user_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            log.error(f"Failed to save user config: {e}")
