"""
Jents VPN — Live End-to-End Diagnostic
"""
import sys, os, time, urllib.request, ssl, winreg, socket

sys.path.insert(0, r'd:\Sandbox\jents_vpn')
from config.config_manager import ConfigManager
from core.auto_engine import JentsEngine, ConnectionState

def on_state(s, m):
    loc = m.get("location", "")
    ping = m.get("ping", "")
    print(f"  STATE -> {s}  {loc} {ping}")

def on_log(msg):
    print(f"  LOG: {msg}")

cfg = ConfigManager(r'd:\Sandbox\jents_vpn\config')
engine = JentsEngine(cfg, on_state, on_log)
print("[1] Startup cleanup done")

engine.trigger_connect()

# Wait for CONNECTED or ERROR
for _ in range(40):
    if engine.state in (ConnectionState.CONNECTED, ConnectionState.ERROR):
        break
    time.sleep(0.5)

print(f"[2] Engine state: {engine.state}")

# Verify registry
reg_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
server, _ = winreg.QueryValueEx(key, "ProxyServer")
print(f"[3] Registry: ProxyEnable={enable}, ProxyServer={server}")

# Verify port open
s = socket.socket()
s.settimeout(2)
try:
    s.connect(("127.0.0.1", engine.local_port))
    s.close()
    print(f"[4] Port {engine.local_port}: OPEN (tunnel listening)")
except Exception as e:
    print(f"[4] Port {engine.local_port}: FAILED - {e}")

# Browse through tunnel
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
proxy_url = f"http://127.0.0.1:{engine.local_port}"
proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=ctx))

try:
    with opener.open("http://example.com", timeout=8) as r:
        body = r.read(200).decode("utf-8", errors="replace")
        print(f"[5] HTTP browse: OK ({len(body)} bytes) -> {body[:50]}")
except Exception as e:
    print(f"[5] HTTP browse: FAIL - {e}")

try:
    with opener.open("https://example.com", timeout=8) as r:
        print(f"[6] HTTPS browse: OK status={r.status}")
except Exception as e:
    print(f"[6] HTTPS browse: FAIL - {e}")

# Disconnect
engine.trigger_disconnect()
time.sleep(1.5)

key2 = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
enable2, _ = winreg.QueryValueEx(key2, "ProxyEnable")
print(f"[7] After disconnect: ProxyEnable={enable2} (should be 0)")
print("DONE")
