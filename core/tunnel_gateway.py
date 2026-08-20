"""
Jents VPN — Universal HTTP/S CONNECT-Aware Tunnel Gateway
==========================================================
Properly chains browser HTTPS CONNECT through verified upstream relay.
No direct fallback — every request routes through the exit node.
"""

import socket
import threading
import logging
from typing import Optional, Callable, Dict, Any

log = logging.getLogger("jents.tunnel")

class TunnelGateway:
    """HTTP/S CONNECT-Aware Proxy Engine with Remote Relay Chaining."""

    def __init__(self, local_port: int = 1088,
                 stats_callback: Optional[Callable[[int, int], None]] = None,
                 log_callback: Optional[Callable[[str], None]] = None):
        self.local_port     = local_port
        self.stats_callback = stats_callback
        self._log           = log_callback or (lambda msg: None)
        self.is_running     = False
        self.active_node: Optional[Dict[str, Any]] = None
        self._server_sock: Optional[socket.socket] = None

    def _tune(self, s: socket.socket):
        try:
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 262144)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)
        except Exception:
            pass

    def start(self, node: Dict[str, Any]) -> bool:
        self.active_node = node
        try:
            self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._tune(self._server_sock)
            self._server_sock.bind(("127.0.0.1", self.local_port))
            self._server_sock.listen(512)
            self.is_running = True
            threading.Thread(target=self._accept_loop, daemon=True).start()
            self._log(f"Tunnel Engine Active on 127.0.0.1:{self.local_port} [{node.get('name', node['host'])}]")
            return True
        except Exception as e:
            self._log(f"Tunnel bind error: {e}")
            return False

    def stop(self):
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
                self._tune(client_sock)
                threading.Thread(target=self._handle, args=(client_sock,), daemon=True).start()
            except Exception:
                break

    def _recv_request(self, sock: socket.socket) -> bytes:
        """Read HTTP request headers up to double CRLF."""
        buf = b""
        sock.settimeout(8.0)
        while b"\r\n\r\n" not in buf:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
            if len(buf) > 65536:
                break
        return buf

    def _handle(self, client: socket.socket):
        """
        Forwards every request through the upstream relay.
        HTTPS CONNECT: forward CONNECT to relay, relay upstream 200, pipe TLS.
        Plain HTTP: forward full request to relay, pipe response back.
        """
        relay = None
        try:
            if not self.active_node:
                client.close()
                return

            upstream_host = self.active_node["host"]
            upstream_port = self.active_node["port"]

            raw = self._recv_request(client)
            if not raw:
                client.close()
                return

            first_line = raw.split(b"\r\n")[0].decode("utf-8", "ignore")
            parts = first_line.split(" ")
            if len(parts) < 2:
                client.close()
                return

            method = parts[0].upper()

            # Connect to upstream relay
            relay = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tune(relay)
            relay.settimeout(8.0)
            relay.connect((upstream_host, upstream_port))

            if method == "CONNECT":
                # Forward the CONNECT request to the upstream relay
                relay.sendall(raw)

                # Read relay's response (expecting "200 Connection established")
                relay_resp = b""
                relay.settimeout(8.0)
                while b"\r\n\r\n" not in relay_resp:
                    chunk = relay.recv(4096)
                    if not chunk:
                        break
                    relay_resp += chunk

                status_line = relay_resp.split(b"\r\n")[0]
                if b"200" not in status_line:
                    # Relay refused — close gracefully
                    client.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                    client.close()
                    relay.close()
                    return

                # Forward 200 to browser
                client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

                # Relay any extra bytes that came with the upstream 200 response
                header_end = relay_resp.find(b"\r\n\r\n") + 4
                if header_end < len(relay_resp):
                    client.sendall(relay_resp[header_end:])

            else:
                # Plain HTTP — forward full request to relay
                relay.sendall(raw)

            # Bidirectional full-duplex pipe
            self._pipe(client, relay)

        except Exception:
            pass
        finally:
            for s in (client, relay):
                if s:
                    try:
                        s.close()
                    except Exception:
                        pass

    def _pipe(self, s1: socket.socket, s2: socket.socket):
        """Full-duplex pipe with stats tracking."""
        done = threading.Event()

        def forward(src: socket.socket, dst: socket.socket, is_download: bool):
            src.settimeout(90.0)
            dst.settimeout(90.0)
            try:
                while self.is_running:
                    data = src.recv(32768)
                    if not data:
                        break
                    dst.sendall(data)
                    if self.stats_callback:
                        if is_download:
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
                done.set()

        t1 = threading.Thread(target=forward, args=(s1, s2, False), daemon=True)
        t2 = threading.Thread(target=forward, args=(s2, s1, True),  daemon=True)
        t1.start()
        t2.start()
        done.wait(timeout=300)
        t1.join(timeout=2)
        t2.join(timeout=2)
