"""
Test Real HTTP / HTTPS Web Traffic through TunnelGateway
"""

import unittest
import sys
import os
import urllib.request
import ssl
import time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from core.tunnel_gateway import TunnelGateway

class TestWebTunnel(unittest.TestCase):

    def test_web_browsing_through_tunnel(self):
        gateway = TunnelGateway(local_port=1099)
        started = gateway.start({"name": "Test Node", "host": "1.1.1.1", "port": 443})
        self.assertTrue(started)

        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            proxy_handler = urllib.request.ProxyHandler({
                'http': 'http://127.0.0.1:1099',
                'https': 'http://127.0.0.1:1099'
            })
            https_handler = urllib.request.HTTPSHandler(context=ctx)
            opener = urllib.request.build_opener(proxy_handler, https_handler)

            # 1. Test Plain HTTP
            req = urllib.request.Request("http://example.com", headers={'User-Agent': 'JentsVPN/1.0'})
            with opener.open(req, timeout=6.0) as resp:
                data = resp.read().decode('utf-8')
                self.assertIn("Example Domain", data)
                print(f"[TEST] HTTP through tunnel SUCCESS: example.com fetched ({len(data)} bytes)")

            # 2. Test HTTPS CONNECT Tunneling
            req_https = urllib.request.Request("https://example.com", headers={'User-Agent': 'JentsVPN/1.0'})
            with opener.open(req_https, timeout=6.0) as resp:
                status = resp.status
                self.assertEqual(status, 200)
                print(f"[TEST] HTTPS CONNECT through tunnel SUCCESS (Status {status})")

        finally:
            gateway.stop()

if __name__ == "__main__":
    unittest.main()
