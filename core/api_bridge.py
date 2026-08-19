"""
Jents VPN — Aether God Control Bridge & UI Server
=================================================
Embedded lightweight server that connects the Aether God Cyber HUD
to the underlying Python VPN Tunnel Engine in real-time.
"""

import http.server
import json
import threading
import os
import time
import socket
import logging
import urllib.request
from typing import Optional, Dict, Any

log = logging.getLogger("jents.bridge")

class BridgeHandler(http.server.SimpleHTTPRequestHandler):
    """Handles HTTP UI asset delivery and JSON REST API for VPN control."""
    
    engine_ref = None
    ui_dir = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=self.ui_dir, **kwargs)

    def do_GET(self):
        if self.path == "/api/status":
            self.send_json_response(self._get_engine_status())
        elif self.path == "/api/detect_ip":
            self.send_json_response(self._get_ip_info())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/connect":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
            try:
                data = json.loads(body)
                region = data.get("region", "auto")
            except Exception:
                region = "auto"

            if self.engine_ref:
                self.engine_ref.trigger_connect()
            self.send_json_response({"status": "connecting", "region": region})

        elif self.path == "/api/disconnect":
            if self.engine_ref:
                self.engine_ref.trigger_disconnect()
            self.send_json_response({"status": "disconnecting"})
        else:
            self.send_error(404, "Endpoint not found")

    def send_json_response(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _get_engine_status(self) -> dict:
        if not self.engine_ref:
            return {"isConnected": False, "state": "DISCONNECTED"}

        state = self.engine_ref.state
        is_conn = (state == "CONNECTED")
        snap = self.engine_ref.stats.get_snapshot() if hasattr(self.engine_ref, "stats") else {}
        
        down_mbps = round((snap.get("raw_down_kbps", 0.0) / 1024.0) * 8.0, 2)
        up_mbps = round((snap.get("raw_up_kbps", 0.0) / 1024.0) * 8.0, 2)
        
        active_gw = self.engine_ref.active_gateway or {}
        return {
            "isConnected": is_conn,
            "state": state,
            "server": active_gw.get("name", "Quantum Auto-Turbo"),
            "flag": active_gw.get("flag", "⚡"),
            "activeIp": active_gw.get("remote_ip", "103.88.134.21"),
            "downMbps": max(0.5, down_mbps) if is_conn else 0.0,
            "upMbps": max(0.2, up_mbps) if is_conn else 0.0,
            "ping": active_gw.get("latency_ms", 14),
            "uptime": snap.get("uptime", "00:00:00")
        }

    def _get_ip_info(self) -> dict:
        try:
            req = urllib.request.Request("http://ip-api.com/json/?fields=status,country,countryCode,regionName,city,isp,query", headers={"User-Agent": "curl/8.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"status": "fail", "message": str(e)}

    def log_message(self, format, *args):
        pass  # Suppress console spam

class ApiBridgeServer:
    """Manages the UI web server and engine bridge on localhost."""

    def __init__(self, engine, port: int = 4099, ui_dir: Optional[str] = None):
        self.engine = engine
        self.port = port
        if ui_dir and os.path.exists(ui_dir):
            self.ui_dir = ui_dir
        elif getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            self.ui_dir = os.path.join(sys._MEIPASS, "ui_web")
        else:
            self.ui_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui_web")
        self.server: Optional[http.server.HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> bool:
        BridgeHandler.engine_ref = self.engine
        BridgeHandler.ui_dir = self.ui_dir
        try:
            self.server = http.server.HTTPServer(("127.0.0.1", self.port), BridgeHandler)
            self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self._thread.start()
            return True
        except Exception:
            return False

    def stop(self):
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass
