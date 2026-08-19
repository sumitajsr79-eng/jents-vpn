"""
Jents VPN — Comprehensive Automated Test Suite
================================================
Validates all autonomous subsystems:
1. Ephemeral Crypto & Token Negotiation
2. Concurrent Multi-Node Latency Probing
3. Real-Time Telemetry & Stats Engine
4. Full Automated Connect & Disconnect Life Cycle
"""

import unittest
import sys
import os
import time

# Set up paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from config.config_manager import ConfigManager
from core.crypto_session import CryptoSession
from core.prober import GatewayProber
from core.stats_engine import StatsEngine
from core.auto_engine import JentsEngine, ConnectionState

class TestJentsSubsystems(unittest.TestCase):

    def test_crypto_session(self):
        """Tests ephemeral keypair generation and auth tokens."""
        session = CryptoSession()
        self.assertIsNotNone(session.session_id)
        self.assertEqual(len(session.session_id), 32)
        self.assertIsNotNone(session.public_key_b64)
        
        token = session.generate_auth_token("jents-us-east")
        self.assertTrue(token.startswith("JENTS-TOKEN-"))

        info = session.get_session_info()
        self.assertEqual(info["cipher"], "ChaCha20-Poly1305 / Noise_IK")
        print(f"[TEST] Crypto Session generated: {info}")

    def test_multi_node_prober(self):
        """Tests concurrent probing of edge gateways."""
        cfg = ConfigManager()
        gateways = cfg.get_gateways()
        self.assertGreater(len(gateways), 0)

        prober = GatewayProber(timeout_ms=1000)
        best = prober.find_best_node(gateways)
        self.assertIsNotNone(best)
        self.assertIn("latency_ms", best)
        print(f"[TEST] Best Gateway selected: {best.get('name')} ({best.get('latency_ms')} ms)")

    def test_stats_engine(self):
        """Tests live throughput tracking."""
        stats = StatsEngine(sample_interval=0.1)
        stats.start()
        
        stats.record_traffic(1024 * 50, 1024 * 100)
        time.sleep(0.25)
        
        snap = stats.get_snapshot()
        stats.stop()
        
        self.assertIn("speed_down", snap)
        self.assertIn("speed_up", snap)
        print(f"[TEST] Stats snapshot: {snap}")

    def test_engine_connect_lifecycle(self):
        """Tests the single-click automated lifecycle (Probing -> Securing -> Connected -> Disconnected)."""
        states_recorded = []

        def on_state(state, meta):
            states_recorded.append((state, meta))
            print(f"[TEST STATE] -> {state}")

        cfg = ConfigManager()
        engine = JentsEngine(config_manager=cfg, state_callback=on_state)

        # Trigger 1-Click Connect
        engine.trigger_connect()
        
        # Wait for transition to CONNECTED
        timeout = 12.0
        start = time.time()
        while time.time() - start < timeout and engine.state != ConnectionState.CONNECTED:
            time.sleep(0.2)

        self.assertEqual(engine.state, ConnectionState.CONNECTED)
        self.assertTrue(engine.tunnel.is_running)

        # Trigger Disconnect
        engine.trigger_disconnect()
        
        # Wait for DISCONNECTED
        start = time.time()
        while time.time() - start < timeout and engine.state != ConnectionState.DISCONNECTED:
            time.sleep(0.2)

        self.assertEqual(engine.state, ConnectionState.DISCONNECTED)
        self.assertFalse(engine.tunnel.is_running)
        print("[TEST] Full automated Connect/Disconnect lifecycle verified successfully!")

if __name__ == "__main__":
    unittest.main()
