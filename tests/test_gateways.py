import urllib.request
import csv
import io
import time

def test_vpngate():
    try:
        url = 'http://www.vpngate.net/api/iphone/'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = resp.read().decode('utf-8', 'ignore')
            lines = [l for l in data.splitlines() if not l.startswith('*') and l.strip()]
            reader = csv.reader(io.StringIO('\n'.join(lines)))
            header = next(reader)
            servers = []
            for row in reader:
                if len(row) > 14:
                    servers.append({
                        'host': row[1],
                        'ip': row[1],
                        'ping': row[3],
                        'speed': row[4],
                        'country': row[5],
                        'country_long': row[6],
                    })
            print(f'Total VPNGate Global Servers fetched: {len(servers)}')
            for s in servers[:8]:
                spd = float(s['speed'])/1000000.0 if s['speed'].isdigit() else 0
                print(f"  {s['country']} ({s['country_long']}) - IP: {s['ip']} - Ping: {s['ping']}ms - Speed: {spd:.1f} Mbps")
    except Exception as e:
        print('VPNGate fetch failed:', e)

if __name__ == '__main__':
    test_vpngate()
