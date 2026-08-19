"""
Comprehensive Live Real-World Browsing Test for Jents VPN
"""
import sys, os, time, urllib.request, ssl, winreg, socket

sys.path.insert(0, r'd:\Sandbox\jents_vpn')
from config.config_manager import ConfigManager
from core.auto_engine import JentsEngine, ConnectionState, GATEWAY_PRESETS

def test_full_vpn_browsing():
    cfg = ConfigManager(r'd:\Sandbox\jents_vpn\config')
    
    logs = []
    states = []
    
    def on_log(msg):
        logs.append(msg)
        print(f"  [LOG] {msg}")

    def on_state(state, meta):
        states.append(state)
        print(f"  [STATE] -> {state} ({meta.get('location', '')})")

    engine = JentsEngine(cfg, state_callback=on_state, log_callback=on_log)
    
    print("=== STEP 1: Connect Jents Quantum VPN ===")
    engine.trigger_connect()

    for _ in range(80):
        if engine.state in (ConnectionState.CONNECTED, ConnectionState.ERROR):
            break
        time.sleep(0.1)

    assert engine.state == ConnectionState.CONNECTED, f"Engine failed to reach CONNECTED: {engine.state}"
    print("[PASS] Engine is CONNECTED!")

    print("\n=== STEP 2: Verify Windows System Proxy ===")
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
    enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
    server, _ = winreg.QueryValueEx(key, "ProxyServer")
    print(f"Registry: ProxyEnable={enable}, ProxyServer={server}")
    assert enable == 1, "ProxyEnable should be 1"
    assert "127.0.0.1:1088" in server, "ProxyServer should point to 127.0.0.1:1088"
    print("[PASS] Windows Registry Proxy active!")

    print("\n=== STEP 3: Real Web Browsing through Tunnel ===")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    proxy_handler = urllib.request.ProxyHandler({
        'http': 'http://127.0.0.1:1088',
        'https': 'http://127.0.0.1:1088'
    })
    opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=ctx))

    test_sites = [
        ("HTTP example.com", "http://example.com"),
        ("HTTPS example.com", "https://example.com"),
        ("HTTPS Cloudflare", "https://www.cloudflare.com"),
        ("HTTPS Httpbin IP", "https://httpbin.org/ip"),
    ]

    for label, url in test_sites:
        t0 = time.perf_counter()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with opener.open(req, timeout=6.0) as resp:
            data = resp.read(256)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            print(f"  [OK] {label}: Status {resp.status} in {elapsed_ms:.1f}ms ({len(data)} bytes received)")

    print("\n=== STEP 4: Test Telemetry ===")
    snap = engine.stats.get_snapshot()
    print(f"Telemetry Snapshot: {snap}")
    assert snap.get("total_down_mb") is not None

    print("\n=== STEP 5: Disconnect and Clean Restore ===")
    engine.trigger_disconnect()
    time.sleep(0.5)

    key2 = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
    enable2, _ = winreg.QueryValueEx(key2, "ProxyEnable")
    print(f"After disconnect: ProxyEnable={enable2}")
    assert enable2 == 0, "ProxyEnable should be restored to 0"
    print("[PASS] System Proxy restored cleanly!")

    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! JENTS VPN IS 100% OPERATIONAL! <<<")

if __name__ == '__main__':
    test_full_vpn_browsing()
