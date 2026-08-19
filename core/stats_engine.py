"""
Jents VPN — Real-Time Telemetry & Throughput Engine
===================================================
Continuously samples network delta throughput, upload/download speeds,
active connection duration, and packet metrics.
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, Callable

log = logging.getLogger("jents.stats")

class StatsEngine:
    """Monitors live network traffic rate and session telemetry."""

    def __init__(self, sample_interval: float = 0.5):
        self.sample_interval = sample_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        self.start_time: float = 0.0
        self.bytes_sent: int = 0
        self.bytes_recv: int = 0
        self.speed_up_kbps: float = 0.0
        self.speed_down_kbps: float = 0.0
        
        self._prev_sent: int = 0
        self._prev_recv: int = 0
        self._prev_time: float = 0.0

    def start(self):
        """Starts real-time stats sampling thread."""
        self.start_time = time.time()
        self._prev_time = self.start_time
        self.bytes_sent = 0
        self.bytes_recv = 0
        self.speed_up_kbps = 0.0
        self.speed_down_kbps = 0.0
        self._running = True

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def record_traffic(self, sent_bytes: int, recv_bytes: int):
        """Called by the tunnel engine to record transferred bytes."""
        self.bytes_sent += sent_bytes
        self.bytes_recv += recv_bytes

    def _run_loop(self):
        while self._running:
            now = time.time()
            dt = now - self._prev_time
            if dt >= self.sample_interval:
                dsent = self.bytes_sent - self._prev_sent
                drecv = self.bytes_recv - self._prev_recv
                
                # Convert bytes/sec to KB/s
                self.speed_up_kbps = round((dsent / dt) / 1024.0, 1)
                self.speed_down_kbps = round((drecv / dt) / 1024.0, 1)

                self._prev_sent = self.bytes_sent
                self._prev_recv = self.bytes_recv
                self._prev_time = now

            time.sleep(self.sample_interval)

    def stop(self):
        """Stops stats tracking."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def get_snapshot(self) -> Dict[str, Any]:
        """Returns snapshot of current network metrics."""
        duration_sec = int(time.time() - self.start_time) if self._running else 0
        hours = duration_sec // 3600
        minutes = (duration_sec % 3600) // 60
        seconds = duration_sec % 60
        
        return {
            "uptime": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
            "speed_down": f"{self.speed_down_kbps:.1f} KB/s",
            "speed_up": f"{self.speed_up_kbps:.1f} KB/s",
            "total_down_mb": round(self.bytes_recv / (1024 * 1024), 2),
            "total_up_mb": round(self.bytes_sent / (1024 * 1024), 2),
            "raw_down_kbps": self.speed_down_kbps,
            "raw_up_kbps": self.speed_up_kbps
        }
