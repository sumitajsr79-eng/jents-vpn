"""
Jents VPN — Full Diagnostic Test
Runs EXACTLY what the .exe does, step by step, and shows every failure point.
"""
import sys, os, time, socket, winreg, subprocess, urllib.request, ssl

sys.path.insert(0, r'd:\Sandbox\jents_vpn')

print("=" * 60)
print("JENTS VPN FULL DIAGNOSTIC")
print("=" * 60)

PORT = 1088

# ── STEP 1: Is something already occupying port 1088? ──────────
print("\n[1] Checking if port 1088 is free...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind(("127.0.0.1", PORT))
    s.close()
    print("    [OK] Port 1088 is FREE")
except Exception as e:
    s.close()
    print(f"    [FAIL] Port 1088 already in use: {e}")
    print("    Fix: Close the old Jents VPN window first, then relaunch")

# ── STEP 2: Can we write to the proxy registry key? ────────────
print("\n[2] Checking Windows Registry proxy write access...")
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_ALL_ACCESS)
    # Read current state
    try:
        enable_val, _ = winreg.QueryValueEx(key, "ProxyEnable")
    except FileNotFoundError:
        enable_val = 0
    try:
        server_val, _ = winreg.QueryValueEx(key, "ProxyServer")
    except FileNotFoundError:
        server_val = "(not set)"
    winreg.CloseKey(key)
    print(f"    [OK] Registry readable/writable. Current ProxyEnable={enable_val}, ProxyServer={server_val!r}")
except Exception as e:
    print(f"    [FAIL] Registry access denied: {e}")

# ── STEP 3: Simulate exact engine connect sequence ──────────────
print("\n[3] Running engine connect sequence...")
from config.config_manager import ConfigManager
from core.auto_engine import JentsEngine, ConnectionState

states = []
logs = []
def on_state(s, m): states.append(s); print(f"    STATE -> {s}")
def on_log(m): logs.append(m); print(f"    LOG: {m}")

cfg = ConfigManager(r'd:\Sandbox\jents_vpn\config')
engine = JentsEngine(cfg, on_state, on_log)
engine.trigger_connect()

for _ in range(25):
    if engine.state in (ConnectionState.CONNECTED, ConnectionState.ERROR):
        break
    time.sleep(0.1)

print(f"\n    Final state: {engine.state}")
if engine.state == ConnectionState.ERROR:
    print("    ERRORS FOUND:", [l for l in logs if 'Error' in l or 'error' in l or 'FAIL' in l])

# ── STEP 4: Verify proxy registry is set ───────────────────────
print("\n[4] Verifying Windows proxy registry after connect...")
try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
    enable_val, _ = winreg.QueryValueEx(key, "ProxyEnable")
    try:
        server_val, _ = winreg.QueryValueEx(key, "ProxyServer")
    except FileNotFoundError:
        server_val = "(not set)"
    winreg.CloseKey(key)
    print(f"    ProxyEnable={enable_val}, ProxyServer={server_val!r}")
    if enable_val == 1 and "127.0.0.1:1088" in str(server_val):
        print("    [OK] Proxy correctly set in registry!")
    else:
        print("    [FAIL] Proxy not correctly set!")
except Exception as e:
    print(f"    Registry read failed: {e}")

# ── STEP 5: Browse real sites through tunnel ───────────────────
if engine.state == ConnectionState.CONNECTED:
    print("\n[5] Testing real site browse through tunnel...")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    proxy_handler = urllib.request.ProxyHandler({'http': 'http://127.0.0.1:1088', 'https': 'http://127.0.0.1:1088'})
    opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=ctx))
    for url in ["http://example.com", "https://example.com", "https://www.google.com"]:
        try:
            t0 = time.time()
            with opener.open(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=5) as r:
                print(f"    [OK] {url}: {r.status} in {(time.time()-t0)*1000:.0f}ms")
        except Exception as e:
            print(f"    [FAIL] {url}: {e}")

# ── STEP 6: Check if WinHTTP system proxy is also needed ───────
print("\n[6] Checking WinHTTP system proxy (for non-WinINet apps)...")
try:
    r = subprocess.run("netsh winhttp show proxy", shell=True, capture_output=True, text=True)
    print(f"    {r.stdout.strip()}")
except Exception as e:
    print(f"    WinHTTP check failed: {e}")

# ── STEP 7: Disconnect ─────────────────────────────────────────
print("\n[7] Disconnecting...")
engine.trigger_disconnect()
time.sleep(0.5)

key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
enable_final, _ = winreg.QueryValueEx(key, "ProxyEnable")
print(f"    After disconnect: ProxyEnable={enable_final}")
print("\n[DONE]")
