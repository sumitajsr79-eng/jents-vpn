"""
Jents VPN — Multi-Node Automated Prober
========================================
Performs ultra-fast concurrent latency and jitter probing across all
available edge gateways to autonomously select the best node.
"""

import socket
import time
import concurrent.futures
import logging
from typing import List, Dict, Any, Optional

log = logging.getLogger("jents.prober")

class GatewayProber:
    """Probes edge servers concurrently to find the lowest latency node."""

    def __init__(self, timeout_ms: int = 1200):
        self.timeout_sec = timeout_ms / 1000.0

    def probe_single_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Probes a single node and calculates round-trip latency in milliseconds."""
        host = node.get("test_host") or node.get("host")
        port = node.get("test_port") or node.get("port", 443)
        
        result = dict(node)
        result["latency_ms"] = 9999.0
        result["is_reachable"] = False
        result["jitter_ms"] = 0.0

        rtts = []
        for _ in range(2):  # Two quick samples
            sock = None
            try:
                start = time.perf_counter()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout_sec)
                sock.connect((host, port))
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                rtts.append(elapsed_ms)
            except Exception:
                break
            finally:
                if sock:
                    try:
                        sock.close()
                    except Exception:
                        pass

        if rtts:
            avg_rtt = sum(rtts) / len(rtts)
            jitter = abs(rtts[-1] - rtts[0]) if len(rtts) > 1 else 0.0
            result["latency_ms"] = round(avg_rtt, 1)
            result["jitter_ms"] = round(jitter, 1)
            result["is_reachable"] = True
        
        return result

    def probe_all_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Concurrently probes all nodes in parallel with thread pool."""
        if not nodes:
            return []

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(nodes), 8)) as executor:
            future_to_node = {executor.submit(self.probe_single_node, n): n for n in nodes}
            for future in concurrent.futures.as_completed(future_to_node):
                try:
                    res = future.result()
                    results.append(res)
                except Exception as e:
                    node = future_to_node[future]
                    log.warning(f"Error probing {node.get('name')}: {e}")
                    failed_node = dict(node)
                    failed_node["latency_ms"] = 9999.0
                    failed_node["is_reachable"] = False
                    results.append(failed_node)

        # Sort reachable first, then by latency
        results.sort(key=lambda x: (not x["is_reachable"], x["latency_ms"]))
        return results

    def find_best_node(self, nodes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Finds the absolute optimal edge node in milliseconds."""
        scored = self.probe_all_nodes(nodes)
        if scored and scored[0]["is_reachable"]:
            return scored[0]
        return scored[0] if scored else None
