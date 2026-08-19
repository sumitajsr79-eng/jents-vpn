"""
Jents VPN — Universal Chained Remote Tunnel Gateway
===================================================
Chains all client browser/app connections through the verified remote exit node,
so the external IP address actually changes to Germany, France, US, or Singapore.
"""

import socket
import threading
import struct
import logging
import time
from typing import Optional, Callable, Dict, Any

log = logging.getLogger("jents.tunnel")

class TunnelGateway:
    """Universal High-Speed Proxy Engine with Remote Chaining."""

    def __init__(self, local_port: int = 1088, stats_callback: Optional[Callable[[int, int], None]] = None,
                 log_callback: Optional[Callable[[str], None]] = None):
        self.local_port = local_port
        self.stats_callback = stats_callback
        self._log = log_callback or (lambda msg: None)
        self.is_running = False
        self.active_node: Optional[Dict[str, Any]] = None
        self._server_sock: Optional[socket.socket] = None
        self._listener_thread: Optional[threading.Thread] = None

    def _tune_socket(self, s: socket.socket):
        """Applies kernel tuning: TCP_NODELAY (zero lag) and 256KB buffer windows."""
        try:
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 262144)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)
        except Exception:
            pass

    def start(self, node: Dict[str, Any]) -> bool:
        """Starts local tunnel server on 127.0.0.1:port."""
        self.active_node = node
        try:
            self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._tune_socket(self._server_sock)
            self._server_sock.bind(("127.0.0.1", self.local_port))
            self._server_sock.listen(512)
            self.is_running = True

            self._listener_thread = threading.Thread(target=self._accept_loop, daemon=True)
            self._listener_thread.start()
            
            node_desc = node.get("remote_ip") or node.get("name")
            self._log(f"Tunnel: 127.0.0.1:{self.local_port} -> Remote Node: {node_desc}")
            return True
        except Exception as e:
            self._log(f"Tunnel Engine Error: {e}")
            return False

    def stop(self):
        """Stops proxy engine."""
        self.is_running = False
        if self._server_sock:
            try:
                self._server_sock.close()
            except Exception:
                pass
            self._server_sock = None

    def _accept_loop(self):
        while self.is_running:
            try:
                client_sock, _ = self._server_sock.accept()
                self._tune_socket(client_sock)
                t = threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True)
                t.start()
            except Exception:
                break

    def _handle_client(self, client_sock: socket.socket):
        """Chains connection through verified remote exit node."""
        client_sock.settimeout(12.0)
        remote_sock = None
        try:
            if not self.active_node:
                client_sock.close()
                return

            upstream_host = self.active_node["host"]
            upstream_port = self.active_node["port"]

            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tune_socket(remote_sock)
            remote_sock.settimeout(8.0)
            remote_sock.connect((upstream_host, upstream_port))

            self._pipe_sockets(client_sock, remote_sock)

        except Exception:
            pass
        finally:
            try:
                client_sock.close()
            except Exception:
                pass
            if remote_sock:
                try:
                    remote_sock.close()
                except Exception:
                    pass

    def _pipe_sockets(self, s1: socket.socket, s2: socket.socket):
        """Full-duplex bidirectional streaming threads with graceful shutdown."""
        def forward(src: socket.socket, dst: socket.socket, is_down: bool):
            src.settimeout(30.0)
            dst.settimeout(30.0)
            try:
                while self.is_running:
                    data = src.recv(65536)
                    if not data:
                        break
                    dst.sendall(data)
                    if self.stats_callback:
                        if is_down:
                            self.stats_callback(len(data), 0)
                        else:
                            self.stats_callback(0, len(data))
            except Exception:
                pass
            finally:
                try:
                    dst.shutdown(socket.SHUT_WR)
                except Exception:
                    pass

        # Thread 1: Client -> Remote (Upload)
        t1 = threading.Thread(target=forward, args=(s1, s2, False), daemon=True)
        # Thread 2: Remote -> Client (Download)
        t2 = threading.Thread(target=forward, args=(s2, s1, True), daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
